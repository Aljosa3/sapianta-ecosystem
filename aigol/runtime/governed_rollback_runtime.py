"""Thin Platform Core coordinator for governed rollback execution."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_ocs_mutation_candidate import DEFAULT_ALLOWLISTED_WORKSPACE
from aigol.runtime.platform_core_rollback_candidate import (
    create_governed_rollback_candidate_from_replay,
    validate_governed_rollback_candidate,
)
from aigol.runtime.platform_core_rollback_governance import (
    create_governed_rollback_approval,
    create_governed_rollback_authorization_record,
    validate_governed_rollback_approval,
)
from aigol.runtime.platform_core_rollback_replay import (
    ROLLBACK_REPLAY_STEPS,
    ensure_rollback_replay_available,
    persist_rollback_failure_if_possible,
    persist_rollback_replay_step,
    reconstruct_governed_rollback_replay,
)
from aigol.runtime.platform_core_rollback_validation import (
    post_rollback_validation_artifact,
    pre_rollback_validation_artifact,
    resolve_allowlisted_workspace,
    resolve_existing_repository_dir,
    resolve_rollback_target,
)
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.filesystem_rollback_worker import (
    FILESYSTEM_ROLLBACK_WORKER_EXECUTED,
    create_authorized_rollback_request,
    execute_filesystem_rollback_request,
    reconstruct_filesystem_rollback_worker_replay,
)


ROLLBACK_RUNTIME_VERSION = "G9_09_GOVERNED_ROLLBACK_EXECUTION_IMPLEMENTATION_V1"
ROLLBACK_COMPLETION_ARTIFACT_V1 = "ROLLBACK_COMPLETION_ARTIFACT_V1"
GOVERNED_ROLLBACK_EXECUTION_COMPLETED = "GOVERNED_ROLLBACK_EXECUTION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"


def create_governed_rollback_candidate(
    *,
    candidate_id: str,
    session_id: str,
    prior_mutation_type: str,
    prior_replay_dir: str | Path,
    target_path: str,
    created_by: str,
    created_at: str,
    workspace: str = DEFAULT_ALLOWLISTED_WORKSPACE,
) -> dict[str, Any]:
    return create_governed_rollback_candidate_from_replay(
        candidate_id=candidate_id,
        session_id=session_id,
        prior_mutation_type=prior_mutation_type,
        prior_replay_dir=prior_replay_dir,
        target_path=target_path,
        created_by=created_by,
        created_at=created_at,
        workspace=workspace,
    )


def create_governed_rollback_human_approval(
    *,
    approval_id: str,
    candidate_artifact: dict[str, Any],
    confirmation_text: str,
    approved_by: str,
    approved_at: str,
) -> dict[str, Any]:
    return create_governed_rollback_approval(
        approval_id=approval_id,
        candidate_artifact=candidate_artifact,
        confirmation_text=confirmation_text,
        approved_by=approved_by,
        approved_at=approved_at,
    )


def execute_governed_rollback(
    *,
    execution_id: str,
    candidate_artifact: dict[str, Any],
    approval_artifact: dict[str, Any] | None,
    repository_root: str | Path,
    workspace: str | Path = DEFAULT_ALLOWLISTED_WORKSPACE,
    executed_by: str,
    executed_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Coordinate one governed rollback through certified Platform Core owners."""

    replay_path = Path(replay_dir)
    try:
        ensure_rollback_replay_available(replay_path)
        candidate = validate_governed_rollback_candidate(candidate_artifact)
        approval = validate_governed_rollback_approval(approval_artifact, candidate)
        root = resolve_existing_repository_dir(repository_root)
        workspace_path = resolve_allowlisted_workspace(
            root=root,
            workspace=workspace,
            expected=candidate["allowlisted_workspace"],
        )
        target = resolve_rollback_target(workspace_path=workspace_path, target_path=candidate["target_path"])
        pre_validation = pre_rollback_validation_artifact(
            execution_id=execution_id,
            candidate=candidate,
            workspace_path=workspace_path,
            target=target,
            created_at=executed_at,
        )
        if pre_validation["current_hash_matches_authorized_state"] is not True:
            raise FailClosedRuntimeError("governed rollback failed closed: current hash conflict")
        authorization = create_governed_rollback_authorization_record(
            authorization_id=f"{execution_id}:GOVERNANCE-AUTHORIZATION",
            candidate=candidate,
            authorization_timestamp=executed_at,
        )
        worker_request = create_authorized_rollback_request(
            authorization_record=authorization,
            request_id=f"{execution_id}:WORKER-REQUEST",
            rollback_action=candidate["rollback_action"],
            file_path=candidate["target_path"],
            authorized_current_hash=candidate["authorized_current_hash"],
            expected_rollback_result_hash=candidate["expected_rollback_result_hash"],
            restore_content=candidate["restore_content"],
            request_timestamp=executed_at,
            proposal_reference={
                "candidate_id": candidate["candidate_id"],
                "candidate_hash": candidate["artifact_hash"],
                "approval_id": approval["approval_id"],
                "approval_hash": approval["artifact_hash"],
                "prior_execution_id": candidate["prior_execution_id"],
                "rollback_metadata_hash": candidate["rollback_metadata_hash"],
            },
            replay_reference=str(replay_path),
        )
        persist_rollback_replay_step(replay_path, 0, ROLLBACK_REPLAY_STEPS[0], candidate)
        persist_rollback_replay_step(replay_path, 1, ROLLBACK_REPLAY_STEPS[1], approval)
        persist_rollback_replay_step(replay_path, 2, ROLLBACK_REPLAY_STEPS[2], authorization)
        persist_rollback_replay_step(replay_path, 3, ROLLBACK_REPLAY_STEPS[3], pre_validation)
        persist_rollback_replay_step(replay_path, 4, ROLLBACK_REPLAY_STEPS[4], worker_request)
        worker_capture = execute_filesystem_rollback_request(
            authorized_request=worker_request,
            base_dir=workspace_path,
            replay_dir=replay_path / "filesystem_rollback_worker",
        )
        worker_result = worker_capture["filesystem_rollback_worker_execution"]
        if worker_result.get("artifact_type") != FILESYSTEM_ROLLBACK_WORKER_EXECUTED:
            raise FailClosedRuntimeError("governed rollback failed closed: Worker execution failed")
        worker_replay = reconstruct_filesystem_rollback_worker_replay(replay_path / "filesystem_rollback_worker")
        validation = post_rollback_validation_artifact(
            execution_id=execution_id,
            candidate=candidate,
            target=target,
            pre_validation=pre_validation,
            worker_result=worker_result,
            worker_replay=worker_replay,
            created_at=executed_at,
        )
        completion = _completion_artifact(
            execution_id=execution_id,
            status=GOVERNED_ROLLBACK_EXECUTION_COMPLETED,
            candidate=candidate,
            approval=approval,
            authorization=authorization,
            pre_validation=pre_validation,
            worker_request=worker_request,
            worker_result=worker_result,
            validation=validation,
            replay_path=replay_path,
            executed_by=executed_by,
            executed_at=executed_at,
            failure_reason=None,
        )
        persist_rollback_replay_step(replay_path, 5, ROLLBACK_REPLAY_STEPS[5], worker_result)
        persist_rollback_replay_step(replay_path, 6, ROLLBACK_REPLAY_STEPS[6], validation)
        persist_rollback_replay_step(replay_path, 7, ROLLBACK_REPLAY_STEPS[7], completion)
        return _capture(completion, validation, replay_path)
    except Exception as exc:
        completion = _failed_completion_artifact(
            execution_id=execution_id,
            executed_by=executed_by,
            executed_at=executed_at,
            replay_path=replay_path,
            failure_reason=_failure_reason(exc),
        )
        persist_rollback_failure_if_possible(replay_path, 7, ROLLBACK_REPLAY_STEPS[7], completion)
        return _capture(completion, None, replay_path)


def _completion_artifact(
    *,
    execution_id: str,
    status: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    authorization: dict[str, Any],
    pre_validation: dict[str, Any],
    worker_request: dict[str, Any],
    worker_result: dict[str, Any],
    validation: dict[str, Any],
    replay_path: Path,
    executed_by: str,
    executed_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": ROLLBACK_COMPLETION_ARTIFACT_V1,
        "runtime_version": ROLLBACK_RUNTIME_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "execution_status": status,
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "approval_id": approval["approval_id"],
        "approval_hash": approval["artifact_hash"],
        "authorization_id": authorization["authorization_id"],
        "authorization_hash": authorization["authorization_hash"],
        "pre_validation_hash": pre_validation["artifact_hash"],
        "worker_request_hash": worker_request["request_hash"],
        "worker_result_hash": worker_result["artifact_hash"],
        "validation_hash": validation["artifact_hash"],
        "operation": candidate["operation"],
        "prior_mutation_type": candidate["prior_mutation_type"],
        "prior_execution_id": candidate["prior_execution_id"],
        "target_path": candidate["target_path"],
        "rollback_action": candidate["rollback_action"],
        "authorized_current_hash": candidate["authorized_current_hash"],
        "expected_rollback_result_hash": candidate["expected_rollback_result_hash"],
        "post_rollback_hash": validation["post_rollback_hash"],
        "replay_reference": str(replay_path),
        "repository_mutated": True,
        "rollback_executed": True,
        "mutated_file_count": 1,
        "git_performed": False,
        "branch_manipulation_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "dependency_rollback_performed": False,
        "automatic_rollback_performed": False,
        "governance_authorization_observed": True,
        "human_approval_observed": True,
        "fail_closed": False,
        "executed_by": _require_string(executed_by, "executed_by"),
        "executed_at": _require_string(executed_at, "executed_at"),
        "failure_reason": failure_reason,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_completion_artifact(
    *,
    execution_id: str,
    executed_by: str,
    executed_at: str,
    replay_path: Path,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": ROLLBACK_COMPLETION_ARTIFACT_V1,
        "runtime_version": ROLLBACK_RUNTIME_VERSION,
        "execution_id": execution_id if isinstance(execution_id, str) else "INVALID_EXECUTION",
        "execution_status": FAILED_CLOSED,
        "candidate_id": None,
        "candidate_hash": None,
        "approval_id": None,
        "approval_hash": None,
        "authorization_id": None,
        "authorization_hash": None,
        "pre_validation_hash": None,
        "worker_request_hash": None,
        "worker_result_hash": None,
        "validation_hash": None,
        "operation": "EXECUTE_SINGLE_GOVERNED_MUTATION_ROLLBACK",
        "prior_mutation_type": None,
        "prior_execution_id": None,
        "target_path": None,
        "rollback_action": None,
        "authorized_current_hash": None,
        "expected_rollback_result_hash": None,
        "post_rollback_hash": None,
        "replay_reference": str(replay_path),
        "repository_mutated": False,
        "rollback_executed": False,
        "mutated_file_count": 0,
        "git_performed": False,
        "branch_manipulation_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "dependency_rollback_performed": False,
        "automatic_rollback_performed": False,
        "governance_authorization_observed": False,
        "human_approval_observed": False,
        "fail_closed": True,
        "executed_by": executed_by if isinstance(executed_by, str) else "INVALID_EXECUTOR",
        "executed_at": executed_at if isinstance(executed_at, str) else "INVALID_TIMESTAMP",
        "failure_reason": failure_reason,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    completion: dict[str, Any],
    validation: dict[str, Any] | None,
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "execution_id": completion["execution_id"],
        "execution_status": completion["execution_status"],
        "rollback_executed": completion["rollback_executed"],
        "repository_mutated": completion["repository_mutated"],
        "mutated_file_count": completion["mutated_file_count"],
        "git_performed": completion["git_performed"],
        "branch_manipulation_performed": completion["branch_manipulation_performed"],
        "deployment_performed": completion["deployment_performed"],
        "provider_invoked": completion["provider_invoked"],
        "dependency_rollback_performed": completion["dependency_rollback_performed"],
        "automatic_rollback_performed": completion["automatic_rollback_performed"],
        "fail_closed": completion["fail_closed"],
        "failure_reason": completion["failure_reason"],
        "replay_reference": str(replay_path),
        "completion_artifact": deepcopy(completion),
        "validation_artifact": deepcopy(validation),
    }
    if completion["execution_status"] == GOVERNED_ROLLBACK_EXECUTION_COMPLETED:
        capture["reconstructed_replay"] = reconstruct_governed_rollback_replay(replay_path)
    return capture


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed rollback requires {field}")
    return value


def _failure_reason(exc: Exception) -> str:
    message = str(exc).strip()
    return message or exc.__class__.__name__


__all__ = [
    "FAILED_CLOSED",
    "GOVERNED_ROLLBACK_EXECUTION_COMPLETED",
    "create_governed_rollback_candidate",
    "create_governed_rollback_human_approval",
    "execute_governed_rollback",
    "reconstruct_governed_rollback_replay",
]
