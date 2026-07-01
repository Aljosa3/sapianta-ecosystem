"""Thin Platform Core coordinator for governed validation execution."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_validation_candidate import (
    RUN_SINGLE_ALLOWLISTED_VALIDATION_COMMAND,
    create_governed_validation_candidate,
    validate_governed_validation_candidate,
)
from aigol.runtime.platform_core_validation_governance import (
    create_governed_validation_approval,
    create_governed_validation_authorization_record,
    validate_governed_validation_approval,
)
from aigol.runtime.platform_core_validation_replay import (
    VALIDATION_REPLAY_STEPS,
    ensure_validation_replay_available,
    persist_validation_failure_if_possible,
    persist_validation_replay_step,
    reconstruct_governed_validation_replay,
)
from aigol.runtime.platform_core_validation_result import (
    validation_pre_execution_artifact,
    validation_result_artifact,
)
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.validation_command_worker import (
    VALIDATION_COMMAND_WORKER_EXECUTED,
    VALIDATION_PASSED,
    create_authorized_validation_request,
    execute_validation_command_request,
    reconstruct_validation_command_worker_replay,
)


GOVERNED_VALIDATION_RUNTIME_VERSION = "G8_14_GOVERNED_VALIDATION_EXECUTION_IMPLEMENTATION_V1"
GOVERNED_VALIDATION_COMPLETION_ARTIFACT_V1 = "GOVERNED_VALIDATION_COMPLETION_ARTIFACT_V1"
GOVERNED_VALIDATION_COMPLETED = "GOVERNED_VALIDATION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"


def execute_governed_validation(
    *,
    execution_id: str,
    candidate_artifact: dict[str, Any],
    approval_artifact: dict[str, Any] | None,
    repository_root: str | Path,
    executed_by: str,
    executed_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Coordinate one governed validation command through certified owners."""

    replay_path = Path(replay_dir)
    try:
        ensure_validation_replay_available(replay_path)
        candidate = validate_governed_validation_candidate(candidate_artifact)
        approval = validate_governed_validation_approval(approval_artifact, candidate)
        pre_execution = validation_pre_execution_artifact(
            execution_id=execution_id,
            candidate=candidate,
            repository_root=repository_root,
            created_at=executed_at,
        )
        authorization = create_governed_validation_authorization_record(
            authorization_id=f"{execution_id}:GOVERNANCE-AUTHORIZATION",
            candidate=candidate,
            authorization_timestamp=executed_at,
        )
        worker_request = create_authorized_validation_request(
            authorization_record=authorization,
            request_id=f"{execution_id}:WORKER-REQUEST",
            command_id=candidate["command_id"],
            request_timestamp=executed_at,
            proposal_reference={
                "candidate_id": candidate["candidate_id"],
                "candidate_hash": candidate["artifact_hash"],
                "approval_id": approval["approval_id"],
                "approval_hash": approval["artifact_hash"],
            },
            replay_reference=str(replay_path),
        )
        persist_validation_replay_step(replay_path, 0, VALIDATION_REPLAY_STEPS[0], candidate)
        persist_validation_replay_step(replay_path, 1, VALIDATION_REPLAY_STEPS[1], approval)
        persist_validation_replay_step(replay_path, 2, VALIDATION_REPLAY_STEPS[2], authorization)
        persist_validation_replay_step(replay_path, 3, VALIDATION_REPLAY_STEPS[3], worker_request)
        persist_validation_replay_step(replay_path, 4, VALIDATION_REPLAY_STEPS[4], pre_execution)
        worker_capture = execute_validation_command_request(
            authorized_request=worker_request,
            repository_root=repository_root,
            replay_dir=replay_path / "validation_command_worker",
        )
        worker_result = worker_capture["validation_command_worker_execution"]
        if worker_result.get("event_type") != VALIDATION_COMMAND_WORKER_EXECUTED:
            raise FailClosedRuntimeError("governed validation failed closed: Worker execution failed")
        worker_replay = reconstruct_validation_command_worker_replay(replay_path / "validation_command_worker")
        validation_result = validation_result_artifact(
            execution_id=execution_id,
            candidate=candidate,
            worker_result=worker_result,
            worker_replay=worker_replay,
            created_at=executed_at,
        )
        completion = _completion_artifact(
            execution_id=execution_id,
            status=GOVERNED_VALIDATION_COMPLETED,
            candidate=candidate,
            approval=approval,
            authorization=authorization,
            worker_request=worker_request,
            pre_execution=pre_execution,
            worker_result=worker_result,
            validation_result=validation_result,
            replay_path=replay_path,
            executed_by=executed_by,
            executed_at=executed_at,
            failure_reason=None,
        )
        persist_validation_replay_step(replay_path, 5, VALIDATION_REPLAY_STEPS[5], worker_result)
        persist_validation_replay_step(replay_path, 6, VALIDATION_REPLAY_STEPS[6], validation_result)
        persist_validation_replay_step(replay_path, 7, VALIDATION_REPLAY_STEPS[7], completion)
        return _capture(completion, validation_result, replay_path)
    except Exception as exc:
        completion = _failed_completion_artifact(
            execution_id=execution_id,
            executed_by=executed_by,
            executed_at=executed_at,
            replay_path=replay_path,
            failure_reason=_failure_reason(exc),
        )
        persist_validation_failure_if_possible(replay_path, 7, VALIDATION_REPLAY_STEPS[7], completion)
        return _capture(completion, None, replay_path)


def _completion_artifact(
    *,
    execution_id: str,
    status: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    authorization: dict[str, Any],
    worker_request: dict[str, Any],
    pre_execution: dict[str, Any],
    worker_result: dict[str, Any],
    validation_result: dict[str, Any],
    replay_path: Path,
    executed_by: str,
    executed_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    validation_status = validation_result["validation_status"]
    artifact = {
        "artifact_type": GOVERNED_VALIDATION_COMPLETION_ARTIFACT_V1,
        "runtime_version": GOVERNED_VALIDATION_RUNTIME_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "execution_status": status,
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "approval_id": approval["approval_id"],
        "approval_hash": approval["artifact_hash"],
        "authorization_id": authorization["authorization_id"],
        "authorization_hash": authorization["authorization_hash"],
        "worker_request_hash": worker_request["request_hash"],
        "pre_execution_hash": pre_execution["artifact_hash"],
        "worker_result_hash": worker_result["artifact_hash"],
        "validation_result_hash": validation_result["artifact_hash"],
        "operation": candidate["operation"],
        "command_id": candidate["command_id"],
        "argv_hash": candidate["argv_hash"],
        "validation_status": validation_status,
        "validation_passed": validation_status == VALIDATION_PASSED,
        "exit_code": validation_result["exit_code"],
        "timed_out": validation_result["timed_out"],
        "replay_reference": str(replay_path),
        "worker_invoked": True,
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "package_install_performed": False,
        "network_access_performed": False,
        "repository_mutation_intended": False,
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
        "artifact_type": GOVERNED_VALIDATION_COMPLETION_ARTIFACT_V1,
        "runtime_version": GOVERNED_VALIDATION_RUNTIME_VERSION,
        "execution_id": execution_id if isinstance(execution_id, str) else "INVALID_EXECUTION",
        "execution_status": FAILED_CLOSED,
        "candidate_id": None,
        "candidate_hash": None,
        "approval_id": None,
        "approval_hash": None,
        "authorization_id": None,
        "authorization_hash": None,
        "worker_request_hash": None,
        "pre_execution_hash": None,
        "worker_result_hash": None,
        "validation_result_hash": None,
        "operation": RUN_SINGLE_ALLOWLISTED_VALIDATION_COMMAND,
        "command_id": None,
        "argv_hash": None,
        "validation_status": FAILED_CLOSED,
        "validation_passed": False,
        "exit_code": None,
        "timed_out": False,
        "replay_reference": str(replay_path),
        "worker_invoked": False,
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "package_install_performed": False,
        "network_access_performed": False,
        "repository_mutation_intended": False,
        "governance_authorization_observed": False,
        "human_approval_observed": False,
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
    validation_result: dict[str, Any] | None,
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": GOVERNED_VALIDATION_RUNTIME_VERSION,
        "execution_id": completion["execution_id"],
        "execution_status": completion["execution_status"],
        "operation": completion["operation"],
        "command_id": completion["command_id"],
        "argv_hash": completion["argv_hash"],
        "validation_status": completion["validation_status"],
        "validation_passed": completion["validation_passed"],
        "exit_code": completion["exit_code"],
        "timed_out": completion["timed_out"],
        "validation_result_artifact": deepcopy(validation_result),
        "completion_artifact": deepcopy(completion),
        "replay_reference": str(replay_path),
        "worker_invoked": completion["worker_invoked"],
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "package_install_performed": False,
        "network_access_performed": False,
        "fail_closed": completion["fail_closed"],
        "failure_reason": completion["failure_reason"],
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed validation requires {field}")
    return value


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "governed validation failed closed"
