"""Thin Platform Core coordinator for governed local Git commits."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_git_commit_candidate import (
    CREATE_SINGLE_GOVERNED_LOCAL_GIT_COMMIT,
    create_governed_git_commit_candidate,
    validate_governed_git_commit_candidate,
)
from aigol.runtime.platform_core_git_commit_governance import (
    create_governed_git_commit_approval,
    create_governed_git_commit_authorization_record,
    validate_governed_git_commit_approval,
)
from aigol.runtime.platform_core_git_commit_replay import (
    GIT_COMMIT_REPLAY_STEPS,
    ensure_git_commit_replay_available,
    persist_git_commit_failure_if_possible,
    persist_git_commit_replay_step,
    reconstruct_governed_git_commit_replay,
)
from aigol.runtime.platform_core_git_commit_result import (
    git_commit_pre_execution_artifact,
    git_commit_result_artifact,
    git_commit_rollback_metadata_artifact,
)
from aigol.runtime.platform_core_validation_result import VALIDATION_RESULT_ARTIFACT_V1
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.git_commit_worker import (
    GIT_COMMIT_WORKER_EXECUTED,
    create_authorized_git_commit_request,
    execute_git_commit_request,
    reconstruct_git_commit_worker_replay,
)


GOVERNED_GIT_COMMIT_RUNTIME_VERSION = "G8_16_GOVERNED_GIT_COMMIT_IMPLEMENTATION_V1"
GOVERNED_GIT_COMMIT_COMPLETION_ARTIFACT_V1 = "GOVERNED_GIT_COMMIT_COMPLETION_ARTIFACT_V1"
GOVERNED_GIT_COMMIT_COMPLETED = "GOVERNED_GIT_COMMIT_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"


def execute_governed_git_commit(
    *,
    execution_id: str,
    candidate_artifact: dict[str, Any],
    approval_artifact: dict[str, Any] | None,
    validation_artifact: dict[str, Any],
    repository_root: str | Path,
    executed_by: str,
    executed_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Coordinate one governed local Git commit through certified owners."""

    replay_path = Path(replay_dir)
    try:
        ensure_git_commit_replay_available(replay_path)
        candidate = validate_governed_git_commit_candidate(candidate_artifact)
        validation = _validate_validation_evidence(validation_artifact, candidate)
        approval = validate_governed_git_commit_approval(approval_artifact, candidate)
        pre_execution = git_commit_pre_execution_artifact(
            execution_id=execution_id,
            candidate=candidate,
            repository_root=repository_root,
            created_at=executed_at,
        )
        authorization = create_governed_git_commit_authorization_record(
            authorization_id=f"{execution_id}:GOVERNANCE-AUTHORIZATION",
            candidate=candidate,
            authorization_timestamp=executed_at,
        )
        worker_request = create_authorized_git_commit_request(
            authorization_record=authorization,
            request_id=f"{execution_id}:WORKER-REQUEST",
            candidate=candidate,
            request_timestamp=executed_at,
            proposal_reference={
                "candidate_id": candidate["candidate_id"],
                "candidate_hash": candidate["artifact_hash"],
                "approval_id": approval["approval_id"],
                "approval_hash": approval["artifact_hash"],
                "validation_artifact_hash": validation["artifact_hash"],
            },
            replay_reference=str(replay_path),
        )
        persist_git_commit_replay_step(replay_path, 0, GIT_COMMIT_REPLAY_STEPS[0], candidate)
        persist_git_commit_replay_step(replay_path, 1, GIT_COMMIT_REPLAY_STEPS[1], approval)
        persist_git_commit_replay_step(replay_path, 2, GIT_COMMIT_REPLAY_STEPS[2], validation)
        persist_git_commit_replay_step(replay_path, 3, GIT_COMMIT_REPLAY_STEPS[3], authorization)
        persist_git_commit_replay_step(replay_path, 4, GIT_COMMIT_REPLAY_STEPS[4], worker_request)
        persist_git_commit_replay_step(replay_path, 5, GIT_COMMIT_REPLAY_STEPS[5], pre_execution)
        worker_capture = execute_git_commit_request(
            authorized_request=worker_request,
            repository_root=repository_root,
            replay_dir=replay_path / "git_commit_worker",
        )
        worker_result = worker_capture["git_commit_worker_execution"]
        if worker_result.get("event_type") != GIT_COMMIT_WORKER_EXECUTED:
            reason = worker_result.get("failure_reason") or "Worker execution failed"
            raise FailClosedRuntimeError(f"governed Git commit failed closed: {reason}")
        worker_replay = reconstruct_git_commit_worker_replay(replay_path / "git_commit_worker")
        commit_result = git_commit_result_artifact(
            execution_id=execution_id,
            candidate=candidate,
            worker_result=worker_result,
            worker_replay=worker_replay,
            created_at=executed_at,
        )
        rollback = git_commit_rollback_metadata_artifact(
            execution_id=execution_id,
            candidate=candidate,
            commit_result=commit_result,
            created_at=executed_at,
        )
        completion = _completion_artifact(
            execution_id=execution_id,
            status=GOVERNED_GIT_COMMIT_COMPLETED,
            candidate=candidate,
            approval=approval,
            validation=validation,
            authorization=authorization,
            worker_request=worker_request,
            pre_execution=pre_execution,
            worker_result=worker_result,
            commit_result=commit_result,
            rollback=rollback,
            replay_path=replay_path,
            executed_by=executed_by,
            executed_at=executed_at,
            failure_reason=None,
        )
        persist_git_commit_replay_step(replay_path, 6, GIT_COMMIT_REPLAY_STEPS[6], worker_result)
        persist_git_commit_replay_step(replay_path, 7, GIT_COMMIT_REPLAY_STEPS[7], commit_result)
        persist_git_commit_replay_step(replay_path, 8, GIT_COMMIT_REPLAY_STEPS[8], rollback)
        persist_git_commit_replay_step(replay_path, 9, GIT_COMMIT_REPLAY_STEPS[9], completion)
        return _capture(completion, commit_result, rollback, replay_path)
    except Exception as exc:
        completion = _failed_completion_artifact(
            execution_id=execution_id,
            executed_by=executed_by,
            executed_at=executed_at,
            replay_path=replay_path,
            failure_reason=_failure_reason(exc),
        )
        persist_git_commit_failure_if_possible(replay_path, 9, GIT_COMMIT_REPLAY_STEPS[9], completion)
        return _capture(completion, None, None, replay_path)


def _completion_artifact(
    *,
    execution_id: str,
    status: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    validation: dict[str, Any],
    authorization: dict[str, Any],
    worker_request: dict[str, Any],
    pre_execution: dict[str, Any],
    worker_result: dict[str, Any],
    commit_result: dict[str, Any],
    rollback: dict[str, Any],
    replay_path: Path,
    executed_by: str,
    executed_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": GOVERNED_GIT_COMMIT_COMPLETION_ARTIFACT_V1,
        "runtime_version": GOVERNED_GIT_COMMIT_RUNTIME_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "execution_status": status,
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "approval_id": approval["approval_id"],
        "approval_hash": approval["artifact_hash"],
        "validation_artifact_hash": validation["artifact_hash"],
        "authorization_id": authorization["authorization_id"],
        "authorization_hash": authorization["authorization_hash"],
        "worker_request_hash": worker_request["request_hash"],
        "pre_execution_hash": pre_execution["artifact_hash"],
        "worker_result_hash": worker_result["artifact_hash"],
        "commit_result_hash": commit_result["artifact_hash"],
        "rollback_hash": rollback["artifact_hash"],
        "operation": candidate["operation"],
        "repository_id": candidate["repository_id"],
        "branch_name": candidate["branch_name"],
        "parent_head": commit_result["parent_head"],
        "commit_hash": commit_result["commit_hash"],
        "post_commit_head": commit_result["post_commit_head"],
        "file_set_hash": candidate["file_set_hash"],
        "commit_message_hash": candidate["commit_message_hash"],
        "replay_reference": str(replay_path),
        "worker_invoked": True,
        "git_performed": True,
        "commit_created": True,
        "commit_count": 1,
        "push_performed": False,
        "remote_interaction_performed": False,
        "branch_management_performed": False,
        "merge_performed": False,
        "rebase_performed": False,
        "checkout_performed": False,
        "reset_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "governance_authorization_observed": True,
        "human_approval_observed": True,
        "validation_evidence_observed": True,
        "rollback_metadata_present": True,
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
        "artifact_type": GOVERNED_GIT_COMMIT_COMPLETION_ARTIFACT_V1,
        "runtime_version": GOVERNED_GIT_COMMIT_RUNTIME_VERSION,
        "execution_id": execution_id if isinstance(execution_id, str) else "INVALID_EXECUTION",
        "execution_status": FAILED_CLOSED,
        "candidate_id": None,
        "candidate_hash": None,
        "approval_id": None,
        "approval_hash": None,
        "validation_artifact_hash": None,
        "authorization_id": None,
        "authorization_hash": None,
        "worker_request_hash": None,
        "pre_execution_hash": None,
        "worker_result_hash": None,
        "commit_result_hash": None,
        "rollback_hash": None,
        "operation": CREATE_SINGLE_GOVERNED_LOCAL_GIT_COMMIT,
        "repository_id": None,
        "branch_name": None,
        "parent_head": None,
        "commit_hash": None,
        "post_commit_head": None,
        "file_set_hash": None,
        "commit_message_hash": None,
        "replay_reference": str(replay_path),
        "worker_invoked": False,
        "git_performed": False,
        "commit_created": False,
        "commit_count": 0,
        "push_performed": False,
        "remote_interaction_performed": False,
        "branch_management_performed": False,
        "merge_performed": False,
        "rebase_performed": False,
        "checkout_performed": False,
        "reset_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "governance_authorization_observed": False,
        "human_approval_observed": False,
        "validation_evidence_observed": False,
        "rollback_metadata_present": False,
        "fail_closed": True,
        "executed_by": executed_by if isinstance(executed_by, str) else None,
        "executed_at": executed_at if isinstance(executed_at, str) else None,
        "failure_reason": failure_reason,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    completion: dict[str, Any],
    commit_result: dict[str, Any] | None,
    rollback: dict[str, Any] | None,
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": GOVERNED_GIT_COMMIT_RUNTIME_VERSION,
        "execution_id": completion["execution_id"],
        "execution_status": completion["execution_status"],
        "operation": completion["operation"],
        "repository_id": completion["repository_id"],
        "branch_name": completion["branch_name"],
        "parent_head": completion["parent_head"],
        "commit_hash": completion["commit_hash"],
        "post_commit_head": completion["post_commit_head"],
        "commit_result_artifact": deepcopy(commit_result),
        "rollback_artifact": deepcopy(rollback),
        "completion_artifact": deepcopy(completion),
        "replay_reference": str(replay_path),
        "worker_invoked": completion["worker_invoked"],
        "git_performed": completion["git_performed"],
        "commit_created": completion["commit_created"],
        "push_performed": False,
        "remote_interaction_performed": False,
        "branch_management_performed": False,
        "merge_performed": False,
        "rebase_performed": False,
        "checkout_performed": False,
        "reset_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "fail_closed": completion["fail_closed"],
        "failure_reason": completion["failure_reason"],
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _validate_validation_evidence(validation_artifact: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(validation_artifact, dict):
        raise FailClosedRuntimeError("governed Git commit failed closed: validation evidence required")
    artifact = deepcopy(validation_artifact)
    actual = _require_string(artifact.get("artifact_hash"), "artifact_hash")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("governed Git commit failed closed: validation evidence hash mismatch")
    if artifact.get("artifact_type") != VALIDATION_RESULT_ARTIFACT_V1:
        raise FailClosedRuntimeError("governed Git commit failed closed: validation result artifact required")
    if artifact.get("validation_status") != "VALIDATION_PASSED":
        raise FailClosedRuntimeError("governed Git commit failed closed: successful validation required")
    if artifact["artifact_hash"] != candidate["validation_artifact_hash"]:
        raise FailClosedRuntimeError("governed Git commit failed closed: validation candidate mismatch")
    return artifact


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed Git commit requires {field}")
    return value


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "governed Git commit failed closed"
