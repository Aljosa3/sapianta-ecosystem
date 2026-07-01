"""Thin Platform Core coordinator for governed existing-file mutation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_existing_file_governance import (
    create_existing_file_mutation_approval,
    create_existing_file_mutation_authorization_record,
    validate_existing_file_mutation_approval,
)
from aigol.runtime.platform_core_existing_file_mutation_candidate import (
    REPLACE_SINGLE_EXISTING_TEXT_FILE_IN_GOVERNED_WORKSPACE,
    create_existing_file_mutation_candidate,
    validate_existing_file_mutation_candidate,
)
from aigol.runtime.platform_core_existing_file_replay import (
    EXISTING_FILE_REPLAY_STEPS,
    ensure_existing_file_replay_available,
    persist_existing_file_failure_if_possible,
    persist_existing_file_replay_step,
    reconstruct_existing_file_mutation_replay,
)
from aigol.runtime.platform_core_existing_file_rollback import existing_file_rollback_metadata_artifact
from aigol.runtime.platform_core_existing_file_validation import (
    post_existing_file_mutation_validation_artifact,
    pre_existing_file_mutation_artifact,
    resolve_allowlisted_workspace,
    resolve_existing_file_target,
    resolve_existing_repository_dir,
)
from aigol.runtime.platform_core_ocs_mutation_candidate import DEFAULT_ALLOWLISTED_WORKSPACE
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.filesystem_replace_worker import (
    FILESYSTEM_REPLACE_WORKER_EXECUTED,
    create_authorized_replace_request,
    execute_filesystem_replace_request,
    reconstruct_filesystem_replace_worker_replay,
)


EXISTING_FILE_MUTATION_RUNTIME_VERSION = "G8_12_EXISTING_FILE_MUTATION_IMPLEMENTATION_V1"
EXISTING_FILE_MUTATION_COMPLETION_ARTIFACT_V1 = "EXISTING_FILE_MUTATION_COMPLETION_ARTIFACT_V1"
EXISTING_FILE_MUTATION_COMPLETED = "EXISTING_FILE_MUTATION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"


def execute_existing_file_mutation(
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
    """Coordinate one governed existing-file replacement through Platform Core owners."""

    replay_path = Path(replay_dir)
    try:
        ensure_existing_file_replay_available(replay_path)
        candidate = validate_existing_file_mutation_candidate(candidate_artifact)
        approval = validate_existing_file_mutation_approval(approval_artifact, candidate)
        root = resolve_existing_repository_dir(repository_root)
        workspace_path = resolve_allowlisted_workspace(
            root=root,
            workspace=workspace,
            expected=candidate["allowlisted_workspace"],
        )
        target = resolve_existing_file_target(workspace_path=workspace_path, target_path=candidate["target_path"])
        pre_mutation = pre_existing_file_mutation_artifact(
            execution_id=execution_id,
            candidate=candidate,
            workspace_path=workspace_path,
            target=target,
            created_at=executed_at,
        )
        if pre_mutation["hash_matches_candidate"] is not True:
            raise FailClosedRuntimeError("existing-file mutation failed closed: target hash conflict")
        authorization = create_existing_file_mutation_authorization_record(
            authorization_id=f"{execution_id}:GOVERNANCE-AUTHORIZATION",
            candidate=candidate,
            authorization_timestamp=executed_at,
        )
        worker_request = create_authorized_replace_request(
            authorization_record=authorization,
            request_id=f"{execution_id}:WORKER-REQUEST",
            file_path=candidate["target_path"],
            expected_content_hash=candidate["expected_content_hash"],
            replacement_content=candidate["replacement_content"],
            request_timestamp=executed_at,
            proposal_reference={
                "candidate_id": candidate["candidate_id"],
                "candidate_hash": candidate["artifact_hash"],
                "approval_id": approval["approval_id"],
                "approval_hash": approval["artifact_hash"],
            },
            replay_reference=str(replay_path),
        )
        persist_existing_file_replay_step(replay_path, 0, EXISTING_FILE_REPLAY_STEPS[0], candidate)
        persist_existing_file_replay_step(replay_path, 1, EXISTING_FILE_REPLAY_STEPS[1], approval)
        persist_existing_file_replay_step(replay_path, 2, EXISTING_FILE_REPLAY_STEPS[2], authorization)
        persist_existing_file_replay_step(replay_path, 3, EXISTING_FILE_REPLAY_STEPS[3], worker_request)
        persist_existing_file_replay_step(replay_path, 4, EXISTING_FILE_REPLAY_STEPS[4], pre_mutation)
        worker_capture = execute_filesystem_replace_request(
            authorized_request=worker_request,
            base_dir=workspace_path,
            replay_dir=replay_path / "filesystem_replace_worker",
        )
        worker_result = worker_capture["filesystem_replace_worker_execution"]
        if worker_result.get("event_type") != FILESYSTEM_REPLACE_WORKER_EXECUTED:
            raise FailClosedRuntimeError("existing-file mutation failed closed: Worker execution failed")
        worker_replay = reconstruct_filesystem_replace_worker_replay(replay_path / "filesystem_replace_worker")
        validation = post_existing_file_mutation_validation_artifact(
            execution_id=execution_id,
            candidate=candidate,
            target=target,
            pre_mutation=pre_mutation,
            worker_result=worker_result,
            worker_replay=worker_replay,
            created_at=executed_at,
        )
        rollback = existing_file_rollback_metadata_artifact(
            execution_id=execution_id,
            candidate=candidate,
            target=target,
            pre_mutation=pre_mutation,
            validation=validation,
            created_at=executed_at,
        )
        completion = _completion_artifact(
            execution_id=execution_id,
            status=EXISTING_FILE_MUTATION_COMPLETED,
            candidate=candidate,
            approval=approval,
            authorization=authorization,
            worker_request=worker_request,
            pre_mutation=pre_mutation,
            worker_result=worker_result,
            validation=validation,
            rollback=rollback,
            replay_path=replay_path,
            executed_by=executed_by,
            executed_at=executed_at,
            failure_reason=None,
        )
        persist_existing_file_replay_step(replay_path, 5, EXISTING_FILE_REPLAY_STEPS[5], worker_result)
        persist_existing_file_replay_step(replay_path, 6, EXISTING_FILE_REPLAY_STEPS[6], validation)
        persist_existing_file_replay_step(replay_path, 7, EXISTING_FILE_REPLAY_STEPS[7], rollback)
        persist_existing_file_replay_step(replay_path, 8, EXISTING_FILE_REPLAY_STEPS[8], completion)
        return _capture(completion, validation, rollback, replay_path)
    except Exception as exc:
        completion = _failed_completion_artifact(
            execution_id=execution_id,
            executed_by=executed_by,
            executed_at=executed_at,
            replay_path=replay_path,
            failure_reason=_failure_reason(exc),
        )
        persist_existing_file_failure_if_possible(replay_path, 8, EXISTING_FILE_REPLAY_STEPS[8], completion)
        return _capture(completion, None, None, replay_path)


def _completion_artifact(
    *,
    execution_id: str,
    status: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    authorization: dict[str, Any],
    worker_request: dict[str, Any],
    pre_mutation: dict[str, Any],
    worker_result: dict[str, Any],
    validation: dict[str, Any],
    rollback: dict[str, Any],
    replay_path: Path,
    executed_by: str,
    executed_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXISTING_FILE_MUTATION_COMPLETION_ARTIFACT_V1,
        "runtime_version": EXISTING_FILE_MUTATION_RUNTIME_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "execution_status": status,
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "approval_id": approval["approval_id"],
        "approval_hash": approval["artifact_hash"],
        "authorization_id": authorization["authorization_id"],
        "authorization_hash": authorization["authorization_hash"],
        "worker_request_hash": worker_request["request_hash"],
        "pre_mutation_hash": pre_mutation["artifact_hash"],
        "worker_result_hash": worker_result["artifact_hash"],
        "validation_hash": validation["artifact_hash"],
        "rollback_hash": rollback["artifact_hash"],
        "operation": candidate["operation"],
        "target_path": candidate["target_path"],
        "old_content_hash": candidate["expected_content_hash"],
        "new_content_hash": candidate["replacement_content_hash"],
        "replay_reference": str(replay_path),
        "repository_mutated": True,
        "file_replaced": True,
        "mutated_file_count": 1,
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "additional_worker_dispatched": False,
        "governance_authorization_observed": True,
        "human_approval_observed": True,
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
        "artifact_type": EXISTING_FILE_MUTATION_COMPLETION_ARTIFACT_V1,
        "runtime_version": EXISTING_FILE_MUTATION_RUNTIME_VERSION,
        "execution_id": execution_id if isinstance(execution_id, str) else "INVALID_EXECUTION",
        "execution_status": FAILED_CLOSED,
        "candidate_id": None,
        "candidate_hash": None,
        "approval_id": None,
        "approval_hash": None,
        "authorization_id": None,
        "authorization_hash": None,
        "worker_request_hash": None,
        "pre_mutation_hash": None,
        "worker_result_hash": None,
        "validation_hash": None,
        "rollback_hash": None,
        "operation": REPLACE_SINGLE_EXISTING_TEXT_FILE_IN_GOVERNED_WORKSPACE,
        "target_path": None,
        "old_content_hash": None,
        "new_content_hash": None,
        "replay_reference": str(replay_path),
        "repository_mutated": False,
        "file_replaced": False,
        "mutated_file_count": 0,
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "additional_worker_dispatched": False,
        "governance_authorization_observed": False,
        "human_approval_observed": False,
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
    validation: dict[str, Any] | None,
    rollback: dict[str, Any] | None,
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": EXISTING_FILE_MUTATION_RUNTIME_VERSION,
        "execution_id": completion["execution_id"],
        "execution_status": completion["execution_status"],
        "operation": completion["operation"],
        "target_path": completion["target_path"],
        "old_content_hash": completion["old_content_hash"],
        "new_content_hash": completion["new_content_hash"],
        "validation_artifact": deepcopy(validation),
        "rollback_artifact": deepcopy(rollback),
        "completion_artifact": deepcopy(completion),
        "replay_reference": str(replay_path),
        "repository_mutated": completion["repository_mutated"],
        "file_replaced": completion["file_replaced"],
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "fail_closed": completion["fail_closed"],
        "failure_reason": completion["failure_reason"],
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"existing-file mutation requires {field}")
    return value


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "existing-file mutation failed closed"
