"""Thin Platform Core coordinator for governed multi-file mutation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.authorization.authorization_record import create_authorization_record
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_multi_file_mutation_candidate import (
    OP_CREATE,
    OP_PATCH,
    OP_REPLACE,
    create_multi_file_mutation_candidate,
    validate_multi_file_mutation_candidate,
)
from aigol.runtime.platform_core_multi_file_mutation_governance import (
    authorization_for_operation,
    create_multi_file_mutation_approval,
    create_multi_file_mutation_authorization_artifact,
    validate_multi_file_mutation_approval,
    validate_multi_file_mutation_authorization_artifact,
)
from aigol.runtime.platform_core_multi_file_mutation_replay import (
    MULTI_FILE_REPLAY_STEPS,
    ensure_multi_file_replay_available,
    persist_multi_file_failure_if_possible,
    persist_multi_file_replay_step,
    reconstruct_multi_file_mutation_replay,
)
from aigol.runtime.platform_core_multi_file_mutation_validation import (
    multi_file_rollback_metadata_artifact,
    post_multi_file_validation_artifact,
    pre_multi_file_validation_artifact,
    resolve_allowlisted_workspace,
    resolve_existing_repository_dir,
)
from aigol.runtime.platform_core_ocs_mutation_candidate import DEFAULT_ALLOWLISTED_WORKSPACE
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.filesystem_patch_worker import (
    FILESYSTEM_PATCH_WORKER_EXECUTED,
    create_authorized_patch_request,
    execute_filesystem_patch_request,
    reconstruct_filesystem_patch_worker_replay,
)
from aigol.workers.filesystem_replace_worker import (
    FILESYSTEM_REPLACE_WORKER_EXECUTED,
    create_authorized_replace_request,
    execute_filesystem_replace_request,
    reconstruct_filesystem_replace_worker_replay,
)
from aigol.workers.filesystem_worker import (
    FILESYSTEM_WORKER_EXECUTED,
    create_authorized_worker_request,
    execute_filesystem_create_request,
    reconstruct_filesystem_worker_replay,
)


MULTI_FILE_MUTATION_RUNTIME_VERSION = "G9_11_GOVERNED_MULTI_FILE_MUTATION_IMPLEMENTATION_V1"
MULTI_FILE_EXECUTION_ARTIFACT_V1 = "MULTI_FILE_EXECUTION_ARTIFACT_V1"
MULTI_FILE_COMPLETION_ARTIFACT_V1 = "MULTI_FILE_COMPLETION_ARTIFACT_V1"
MULTI_FILE_MUTATION_COMPLETED = "MULTI_FILE_MUTATION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"


def create_governed_multi_file_mutation_candidate(
    *,
    candidate_id: str,
    session_id: str,
    operations: list[dict[str, Any]],
    created_by: str,
    created_at: str,
    workspace: str = DEFAULT_ALLOWLISTED_WORKSPACE,
) -> dict[str, Any]:
    return create_multi_file_mutation_candidate(
        candidate_id=candidate_id,
        session_id=session_id,
        operations=operations,
        created_by=created_by,
        created_at=created_at,
        workspace=workspace,
    )


def create_governed_multi_file_mutation_approval(
    *,
    approval_id: str,
    candidate_artifact: dict[str, Any],
    confirmation_text: str,
    approved_by: str,
    approved_at: str,
) -> dict[str, Any]:
    return create_multi_file_mutation_approval(
        approval_id=approval_id,
        candidate_artifact=candidate_artifact,
        confirmation_text=confirmation_text,
        approved_by=approved_by,
        approved_at=approved_at,
    )


def execute_governed_multi_file_mutation(
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
    """Coordinate one governed multi-file transaction through certified owners."""

    replay_path = Path(replay_dir)
    executed_count = 0
    try:
        ensure_multi_file_replay_available(replay_path)
        candidate = validate_multi_file_mutation_candidate(candidate_artifact)
        approval = validate_multi_file_mutation_approval(approval_artifact, candidate)
        root = resolve_existing_repository_dir(repository_root)
        workspace_path = resolve_allowlisted_workspace(
            root=root,
            workspace=workspace,
            expected=candidate["allowlisted_workspace"],
        )
        pre_validation = pre_multi_file_validation_artifact(
            execution_id=execution_id,
            candidate=candidate,
            workspace_path=workspace_path,
            created_at=executed_at,
        )
        if pre_validation["all_operations_ready"] is not True:
            raise FailClosedRuntimeError("multi-file mutation failed closed: pre-transaction validation conflict")
        authorization = create_multi_file_mutation_authorization_artifact(
            authorization_id=f"{execution_id}:GOVERNANCE-AUTHORIZATION",
            candidate=candidate,
            approval=approval,
            authorization_timestamp=executed_at,
        )
        validate_multi_file_mutation_authorization_artifact(authorization, candidate, approval)
        persist_multi_file_replay_step(replay_path, 0, MULTI_FILE_REPLAY_STEPS[0], candidate)
        persist_multi_file_replay_step(replay_path, 1, MULTI_FILE_REPLAY_STEPS[1], approval)
        persist_multi_file_replay_step(replay_path, 2, MULTI_FILE_REPLAY_STEPS[2], authorization)
        persist_multi_file_replay_step(replay_path, 3, MULTI_FILE_REPLAY_STEPS[3], pre_validation)
        execution = _execute_per_file_operations(
            execution_id=execution_id,
            candidate=candidate,
            authorization=authorization,
            workspace_path=workspace_path,
            replay_path=replay_path,
            executed_at=executed_at,
        )
        executed_count = execution["worker_invoked_count"]
        if execution["execution_status"] != "PER_FILE_EXECUTION_COMPLETED":
            raise FailClosedRuntimeError("multi-file mutation failed closed: per-file execution failed")
        post_validation = post_multi_file_validation_artifact(
            execution_id=execution_id,
            candidate=candidate,
            workspace_path=workspace_path,
            execution_artifact=execution,
            created_at=executed_at,
        )
        if post_validation["all_operations_valid"] is not True:
            raise FailClosedRuntimeError("multi-file mutation failed closed: post-transaction validation failed")
        rollback = multi_file_rollback_metadata_artifact(
            execution_id=execution_id,
            candidate=candidate,
            post_validation=post_validation,
            created_at=executed_at,
        )
        completion = _completion_artifact(
            execution_id=execution_id,
            status=MULTI_FILE_MUTATION_COMPLETED,
            candidate=candidate,
            approval=approval,
            authorization=authorization,
            pre_validation=pre_validation,
            execution=execution,
            post_validation=post_validation,
            rollback=rollback,
            replay_path=replay_path,
            executed_by=executed_by,
            executed_at=executed_at,
            failure_reason=None,
        )
        persist_multi_file_replay_step(replay_path, 4, MULTI_FILE_REPLAY_STEPS[4], execution)
        persist_multi_file_replay_step(replay_path, 5, MULTI_FILE_REPLAY_STEPS[5], post_validation)
        persist_multi_file_replay_step(replay_path, 6, MULTI_FILE_REPLAY_STEPS[6], rollback)
        persist_multi_file_replay_step(replay_path, 7, MULTI_FILE_REPLAY_STEPS[7], completion)
        return _capture(completion, post_validation, rollback, replay_path)
    except Exception as exc:
        completion = _failed_completion_artifact(
            execution_id=execution_id,
            executed_by=executed_by,
            executed_at=executed_at,
            replay_path=replay_path,
            failure_reason=_failure_reason(exc),
            executed_count=executed_count,
        )
        persist_multi_file_failure_if_possible(replay_path, 7, MULTI_FILE_REPLAY_STEPS[7], completion)
        return _capture(completion, None, None, replay_path)


def _execute_per_file_operations(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    authorization: dict[str, Any],
    workspace_path: Path,
    replay_path: Path,
    executed_at: str,
) -> dict[str, Any]:
    records = []
    for operation in candidate["operations"]:
        records.append(
            _execute_one_operation(
                execution_id=execution_id,
                operation=operation,
                authorization=authorization_for_operation(authorization, operation["operation_id"]),
                workspace_path=workspace_path,
                replay_path=replay_path,
                executed_at=executed_at,
                transaction_candidate=candidate,
            )
        )
    artifact = {
        "artifact_type": MULTI_FILE_EXECUTION_ARTIFACT_V1,
        "runtime_version": MULTI_FILE_MUTATION_RUNTIME_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "execution_status": "PER_FILE_EXECUTION_COMPLETED",
        "operation_count": candidate["operation_count"],
        "worker_invoked_count": len(records),
        "operation_results": records,
        "git_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "dependency_installation_performed": False,
        "automatic_rollback_performed": False,
        "executed_at": _require_string(executed_at, "executed_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _execute_one_operation(
    *,
    execution_id: str,
    operation: dict[str, Any],
    authorization: dict[str, Any],
    workspace_path: Path,
    replay_path: Path,
    executed_at: str,
    transaction_candidate: dict[str, Any],
) -> dict[str, Any]:
    candidate = operation["single_file_candidate"]
    op_replay = replay_path / f"operation_{operation['operation_index']:03d}_{operation['operation_type']}"
    proposal_reference = {
        "transaction_candidate_id": transaction_candidate["candidate_id"],
        "transaction_candidate_hash": transaction_candidate["artifact_hash"],
        "operation_id": operation["operation_id"],
        "operation_index": operation["operation_index"],
        "single_file_candidate_hash": operation["single_file_candidate_hash"],
    }
    if operation["operation_type"] == OP_CREATE:
        request = create_authorized_worker_request(
            authorization_record=authorization,
            request_id=f"{execution_id}:{operation['operation_id']}:WORKER-REQUEST",
            file_path=candidate["target_filename"],
            content=candidate["content"],
            request_timestamp=executed_at,
            proposal_reference=proposal_reference,
            replay_reference=str(op_replay),
        )
        capture = execute_filesystem_create_request(
            authorized_request=request,
            base_dir=workspace_path,
            replay_dir=op_replay,
        )
        result = capture["filesystem_worker_execution"]
        if result.get("event_type") != FILESYSTEM_WORKER_EXECUTED:
            raise FailClosedRuntimeError("multi-file mutation failed closed: create Worker failed")
        worker_replay = reconstruct_filesystem_worker_replay(op_replay)
        post_hash = result["content_hash"]
    elif operation["operation_type"] == OP_REPLACE:
        request = create_authorized_replace_request(
            authorization_record=authorization,
            request_id=f"{execution_id}:{operation['operation_id']}:WORKER-REQUEST",
            file_path=candidate["target_path"],
            expected_content_hash=candidate["expected_content_hash"],
            replacement_content=candidate["replacement_content"],
            request_timestamp=executed_at,
            proposal_reference=proposal_reference,
            replay_reference=str(op_replay),
        )
        capture = execute_filesystem_replace_request(
            authorized_request=request,
            base_dir=workspace_path,
            replay_dir=op_replay,
        )
        result = capture["filesystem_replace_worker_execution"]
        if result.get("event_type") != FILESYSTEM_REPLACE_WORKER_EXECUTED:
            raise FailClosedRuntimeError("multi-file mutation failed closed: replace Worker failed")
        worker_replay = reconstruct_filesystem_replace_worker_replay(op_replay)
        post_hash = result["new_content_hash"]
    else:
        request = create_authorized_patch_request(
            authorization_record=authorization,
            request_id=f"{execution_id}:{operation['operation_id']}:WORKER-REQUEST",
            file_path=candidate["target_path"],
            pre_content_hash=candidate["pre_content_hash"],
            old_text=candidate["old_text"],
            new_text=candidate["new_text"],
            expected_post_content_hash=candidate["expected_post_content_hash"],
            request_timestamp=executed_at,
            proposal_reference=proposal_reference,
            replay_reference=str(op_replay),
        )
        capture = execute_filesystem_patch_request(
            authorized_request=request,
            base_dir=workspace_path,
            replay_dir=op_replay,
        )
        result = capture["filesystem_patch_worker_execution"]
        if result.get("event_type") != FILESYSTEM_PATCH_WORKER_EXECUTED:
            raise FailClosedRuntimeError("multi-file mutation failed closed: patch Worker failed")
        worker_replay = reconstruct_filesystem_patch_worker_replay(op_replay)
        post_hash = result["post_content_hash"]
    return {
        "operation_id": operation["operation_id"],
        "operation_index": operation["operation_index"],
        "operation_type": operation["operation_type"],
        "target_path": operation["target_path"],
        "authorization_hash": authorization["authorization_hash"],
        "request_hash": request["request_hash"],
        "worker_result_hash": result["artifact_hash"],
        "worker_replay_hash": worker_replay["replay_hash"],
        "post_content_hash": post_hash,
        "expected_post_content_hash": operation["expected_post_content_hash"],
        "worker_invoked": True,
        "replay_reference": str(op_replay),
    }


def _completion_artifact(
    *,
    execution_id: str,
    status: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    authorization: dict[str, Any],
    pre_validation: dict[str, Any],
    execution: dict[str, Any],
    post_validation: dict[str, Any],
    rollback: dict[str, Any],
    replay_path: Path,
    executed_by: str,
    executed_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": MULTI_FILE_COMPLETION_ARTIFACT_V1,
        "runtime_version": MULTI_FILE_MUTATION_RUNTIME_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "execution_status": status,
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "approval_id": approval["approval_id"],
        "approval_hash": approval["artifact_hash"],
        "authorization_hash": authorization["artifact_hash"],
        "pre_validation_hash": pre_validation["artifact_hash"],
        "execution_hash": execution["artifact_hash"],
        "post_validation_hash": post_validation["artifact_hash"],
        "rollback_hash": rollback["artifact_hash"],
        "operation_count": candidate["operation_count"],
        "target_paths": deepcopy(candidate["target_paths"]),
        "repository_mutated": True,
        "mutated_file_count": candidate["operation_count"],
        "rollback_metadata_present": True,
        "automatic_rollback_performed": False,
        "git_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "dependency_installation_performed": False,
        "governance_authorization_observed": True,
        "human_approval_observed": True,
        "fail_closed": False,
        "replay_reference": str(replay_path),
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
    executed_count: int,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": MULTI_FILE_COMPLETION_ARTIFACT_V1,
        "runtime_version": MULTI_FILE_MUTATION_RUNTIME_VERSION,
        "execution_id": execution_id if isinstance(execution_id, str) else "INVALID_EXECUTION",
        "execution_status": FAILED_CLOSED,
        "candidate_id": None,
        "candidate_hash": None,
        "repository_mutated": executed_count > 0,
        "mutated_file_count": executed_count,
        "rollback_metadata_present": False,
        "automatic_rollback_performed": False,
        "git_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "dependency_installation_performed": False,
        "governance_authorization_observed": False,
        "human_approval_observed": False,
        "fail_closed": True,
        "replay_reference": str(replay_path),
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
    rollback: dict[str, Any] | None,
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "execution_id": completion["execution_id"],
        "execution_status": completion["execution_status"],
        "repository_mutated": completion["repository_mutated"],
        "mutated_file_count": completion["mutated_file_count"],
        "rollback_metadata_present": completion["rollback_metadata_present"],
        "automatic_rollback_performed": completion["automatic_rollback_performed"],
        "git_performed": completion["git_performed"],
        "deployment_performed": completion["deployment_performed"],
        "provider_invoked": completion["provider_invoked"],
        "dependency_installation_performed": completion["dependency_installation_performed"],
        "fail_closed": completion["fail_closed"],
        "failure_reason": completion["failure_reason"],
        "replay_reference": str(replay_path),
        "completion_artifact": deepcopy(completion),
        "validation_artifact": deepcopy(validation),
        "rollback_artifact": deepcopy(rollback),
    }
    if completion["execution_status"] == MULTI_FILE_MUTATION_COMPLETED:
        capture["reconstructed_replay"] = reconstruct_multi_file_mutation_replay(replay_path)
    return capture


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"multi-file mutation requires {field}")
    return value


def _failure_reason(exc: Exception) -> str:
    message = str(exc).strip()
    return message or exc.__class__.__name__


__all__ = [
    "FAILED_CLOSED",
    "MULTI_FILE_MUTATION_COMPLETED",
    "create_governed_multi_file_mutation_approval",
    "create_governed_multi_file_mutation_candidate",
    "execute_governed_multi_file_mutation",
    "reconstruct_multi_file_mutation_replay",
]
