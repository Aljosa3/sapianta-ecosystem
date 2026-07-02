"""Thin Platform Core coordinator for governed validation suites."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.architectural_health_advisory import (
    create_platform_digital_twin_evidence_bundle,
    generate_architectural_health_advisory,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_validation_result import validation_pre_execution_artifact, validation_result_artifact
from aigol.runtime.platform_core_validation_suite_candidate import (
    RUN_GOVERNED_VALIDATION_SUITE,
    create_governed_validation_suite_candidate,
    validate_governed_validation_suite_candidate,
)
from aigol.runtime.platform_core_validation_suite_governance import (
    authorization_for_command,
    create_governed_validation_suite_approval,
    create_governed_validation_suite_authorization_artifact,
    validate_governed_validation_suite_approval,
    validate_governed_validation_suite_authorization_artifact,
)
from aigol.runtime.platform_core_validation_suite_replay import (
    VALIDATION_SUITE_REPLAY_STEPS,
    ensure_validation_suite_replay_available,
    persist_validation_suite_failure_if_possible,
    persist_validation_suite_replay_step,
    reconstruct_governed_validation_suite_replay,
)
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.validation_command_worker import (
    VALIDATION_BLOCKED,
    VALIDATION_COMMAND_WORKER_EXECUTED,
    VALIDATION_FAILED,
    VALIDATION_PASSED,
    VALIDATION_TIMED_OUT,
    create_authorized_validation_request,
    execute_validation_command_request,
    reconstruct_validation_command_worker_replay,
)


GOVERNED_VALIDATION_SUITE_RUNTIME_VERSION = "G9_13_BROADER_GOVERNED_VALIDATION_SUITES_IMPLEMENTATION_V1"
VALIDATION_SUITE_PRE_EXECUTION_ARTIFACT_V1 = "VALIDATION_SUITE_PRE_EXECUTION_ARTIFACT_V1"
VALIDATION_SUITE_COMMAND_EXECUTION_ARTIFACT_V1 = "VALIDATION_SUITE_COMMAND_EXECUTION_ARTIFACT_V1"
VALIDATION_SUITE_SUMMARY_ARTIFACT_V1 = "VALIDATION_SUITE_SUMMARY_ARTIFACT_V1"
GOVERNED_VALIDATION_SUITE_COMPLETION_ARTIFACT_V1 = "GOVERNED_VALIDATION_SUITE_COMPLETION_ARTIFACT_V1"

GOVERNED_VALIDATION_SUITE_COMPLETED = "GOVERNED_VALIDATION_SUITE_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"
VALIDATION_SUITE_PASSED = "VALIDATION_SUITE_PASSED"
VALIDATION_SUITE_FAILED = "VALIDATION_SUITE_FAILED"
VALIDATION_SUITE_TIMED_OUT = "VALIDATION_SUITE_TIMED_OUT"
VALIDATION_SUITE_BLOCKED = "VALIDATION_SUITE_BLOCKED"


def execute_governed_validation_suite(
    *,
    execution_id: str,
    candidate_artifact: dict[str, Any],
    approval_artifact: dict[str, Any] | None,
    repository_root: str | Path,
    executed_by: str,
    executed_at: str,
    replay_dir: str | Path,
    stop_on_failure: bool = True,
) -> dict[str, Any]:
    """Coordinate an ordered validation suite through certified single-command validation."""

    replay_path = Path(replay_dir)
    worker_invoked_count = 0
    try:
        ensure_validation_suite_replay_available(replay_path)
        candidate = validate_governed_validation_suite_candidate(candidate_artifact)
        approval = validate_governed_validation_suite_approval(approval_artifact, candidate)
        pre_suite = _pre_suite_artifact(
            execution_id=execution_id,
            candidate=candidate,
            repository_root=repository_root,
            created_at=executed_at,
        )
        authorization = create_governed_validation_suite_authorization_artifact(
            authorization_id=f"{execution_id}:GOVERNANCE-AUTHORIZATION",
            candidate=candidate,
            approval=approval,
            authorization_timestamp=executed_at,
        )
        validate_governed_validation_suite_authorization_artifact(authorization, candidate, approval)
        persist_validation_suite_replay_step(replay_path, 0, VALIDATION_SUITE_REPLAY_STEPS[0], candidate)
        persist_validation_suite_replay_step(replay_path, 1, VALIDATION_SUITE_REPLAY_STEPS[1], approval)
        persist_validation_suite_replay_step(replay_path, 2, VALIDATION_SUITE_REPLAY_STEPS[2], authorization)
        persist_validation_suite_replay_step(replay_path, 3, VALIDATION_SUITE_REPLAY_STEPS[3], pre_suite)
        command_execution = _execute_commands(
            execution_id=execution_id,
            candidate=candidate,
            approval=approval,
            authorization=authorization,
            repository_root=repository_root,
            replay_path=replay_path,
            executed_at=executed_at,
            stop_on_failure=stop_on_failure,
        )
        worker_invoked_count = command_execution["worker_invoked_count"]
        summary = _suite_summary_artifact(
            execution_id=execution_id,
            candidate=candidate,
            command_execution=command_execution,
            created_at=executed_at,
        )
        advisory = _architectural_health_advisory_artifact(
            execution_id=execution_id,
            summary=summary,
            replay_path=replay_path,
            created_at=executed_at,
        )
        completion = _completion_artifact(
            execution_id=execution_id,
            status=GOVERNED_VALIDATION_SUITE_COMPLETED,
            candidate=candidate,
            approval=approval,
            authorization=authorization,
            pre_suite=pre_suite,
            command_execution=command_execution,
            summary=summary,
            advisory=advisory,
            replay_path=replay_path,
            executed_by=executed_by,
            executed_at=executed_at,
            failure_reason=None,
        )
        persist_validation_suite_replay_step(replay_path, 4, VALIDATION_SUITE_REPLAY_STEPS[4], command_execution)
        persist_validation_suite_replay_step(replay_path, 5, VALIDATION_SUITE_REPLAY_STEPS[5], summary)
        persist_validation_suite_replay_step(replay_path, 6, VALIDATION_SUITE_REPLAY_STEPS[6], advisory)
        persist_validation_suite_replay_step(replay_path, 7, VALIDATION_SUITE_REPLAY_STEPS[7], completion)
        return _capture(completion, summary, advisory, replay_path)
    except Exception as exc:
        completion = _failed_completion_artifact(
            execution_id=execution_id,
            executed_by=executed_by,
            executed_at=executed_at,
            replay_path=replay_path,
            failure_reason=_failure_reason(exc),
            worker_invoked_count=worker_invoked_count,
        )
        persist_validation_suite_failure_if_possible(replay_path, 7, VALIDATION_SUITE_REPLAY_STEPS[7], completion)
        return _capture(completion, None, None, replay_path)


def _pre_suite_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    repository_root: str | Path,
    created_at: str,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    if not root.exists() or not root.is_dir():
        raise FailClosedRuntimeError("governed validation suite failed closed: repository root must exist")
    pre_execution_records = [
        validation_pre_execution_artifact(
            execution_id=f"{execution_id}:{record['command_record_id']}",
            candidate=record["single_command_candidate"],
            repository_root=root,
            created_at=created_at,
        )
        for record in candidate["commands"]
    ]
    artifact = {
        "artifact_type": VALIDATION_SUITE_PRE_EXECUTION_ARTIFACT_V1,
        "runtime_version": GOVERNED_VALIDATION_SUITE_RUNTIME_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "repository_root": str(root),
        "command_count": candidate["command_count"],
        "pre_execution_records": pre_execution_records,
        "all_commands_allowlisted": True,
        "shell_allowed": False,
        "git_allowed": False,
        "deployment_allowed": False,
        "provider_invocation_allowed": False,
        "network_allowed": False,
        "repository_mutation_allowed": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _execute_commands(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    authorization: dict[str, Any],
    repository_root: str | Path,
    replay_path: Path,
    executed_at: str,
    stop_on_failure: bool,
) -> dict[str, Any]:
    command_results = []
    stopped_on_failure = False
    for record in candidate["commands"]:
        command_result = _execute_one_command(
            execution_id=execution_id,
            command_record=record,
            approval=approval,
            authorization=authorization_for_command(authorization, record["command_record_id"]),
            repository_root=repository_root,
            replay_path=replay_path,
            executed_at=executed_at,
            suite_candidate=candidate,
        )
        command_results.append(command_result)
        if stop_on_failure and command_result["validation_status"] != VALIDATION_PASSED:
            stopped_on_failure = True
            break
    artifact = {
        "artifact_type": VALIDATION_SUITE_COMMAND_EXECUTION_ARTIFACT_V1,
        "runtime_version": GOVERNED_VALIDATION_SUITE_RUNTIME_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "planned_command_count": candidate["command_count"],
        "worker_invoked_count": len(command_results),
        "command_results": command_results,
        "stopped_on_failure": stopped_on_failure,
        "stop_on_failure": stop_on_failure,
        "worker_execution_only": True,
        "git_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "package_install_performed": False,
        "network_access_performed": False,
        "repository_mutation_performed": False,
        "executed_at": _require_string(executed_at, "executed_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _execute_one_command(
    *,
    execution_id: str,
    command_record: dict[str, Any],
    approval: dict[str, Any],
    authorization: dict[str, Any],
    repository_root: str | Path,
    replay_path: Path,
    executed_at: str,
    suite_candidate: dict[str, Any],
) -> dict[str, Any]:
    single_candidate = command_record["single_command_candidate"]
    command_replay = replay_path / f"command_{command_record['command_index']:03d}"
    request = create_authorized_validation_request(
        authorization_record=authorization,
        request_id=f"{execution_id}:{command_record['command_record_id']}:WORKER-REQUEST",
        command_id=command_record["command_id"],
        request_timestamp=executed_at,
        proposal_reference={
            "suite_candidate_id": suite_candidate["candidate_id"],
            "suite_candidate_hash": suite_candidate["artifact_hash"],
            "suite_approval_id": approval["approval_id"],
            "suite_approval_hash": approval["artifact_hash"],
            "command_record_id": command_record["command_record_id"],
            "single_command_candidate_hash": command_record["single_command_candidate_hash"],
        },
        replay_reference=str(command_replay),
    )
    worker_capture = execute_validation_command_request(
        authorized_request=request,
        repository_root=repository_root,
        replay_dir=command_replay,
    )
    worker_result = worker_capture["validation_command_worker_execution"]
    if worker_result.get("event_type") != VALIDATION_COMMAND_WORKER_EXECUTED:
        raise FailClosedRuntimeError("governed validation suite failed closed: Worker execution failed")
    worker_replay = reconstruct_validation_command_worker_replay(command_replay)
    validation_result = validation_result_artifact(
        execution_id=f"{execution_id}:{command_record['command_record_id']}",
        candidate=single_candidate,
        worker_result=worker_result,
        worker_replay=worker_replay,
        created_at=executed_at,
    )
    return {
        "command_record_id": command_record["command_record_id"],
        "command_index": command_record["command_index"],
        "command_id": command_record["command_id"],
        "single_command_candidate_hash": command_record["single_command_candidate_hash"],
        "authorization_id": authorization["authorization_id"],
        "authorization_hash": authorization["authorization_hash"],
        "worker_request_hash": request["request_hash"],
        "worker_result_hash": worker_result["artifact_hash"],
        "validation_result": validation_result,
        "validation_result_hash": validation_result["artifact_hash"],
        "worker_replay_hash": worker_replay["replay_hash"],
        "validation_status": validation_result["validation_status"],
        "validation_passed": validation_result["validation_status"] == VALIDATION_PASSED,
        "exit_code": validation_result["exit_code"],
        "timed_out": validation_result["timed_out"],
        "worker_invoked": True,
        "replay_reference": str(command_replay),
        "replay_visible": True,
    }


def _suite_summary_artifact(
    *,
    execution_id: str,
    candidate: dict[str, Any],
    command_execution: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    statuses = [record["validation_status"] for record in command_execution["command_results"]]
    suite_status = _suite_status(statuses, candidate["command_count"], command_execution["worker_invoked_count"])
    artifact = {
        "artifact_type": VALIDATION_SUITE_SUMMARY_ARTIFACT_V1,
        "runtime_version": GOVERNED_VALIDATION_SUITE_RUNTIME_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "command_execution_hash": command_execution["artifact_hash"],
        "planned_command_count": candidate["command_count"],
        "executed_command_count": command_execution["worker_invoked_count"],
        "passed_command_count": sum(1 for status in statuses if status == VALIDATION_PASSED),
        "failed_command_count": sum(1 for status in statuses if status == VALIDATION_FAILED),
        "timed_out_command_count": sum(1 for status in statuses if status == VALIDATION_TIMED_OUT),
        "blocked_command_count": sum(1 for status in statuses if status == VALIDATION_BLOCKED),
        "validation_statuses": statuses,
        "validation_suite_status": suite_status,
        "validation_suite_passed": suite_status == VALIDATION_SUITE_PASSED,
        "stopped_on_failure": command_execution["stopped_on_failure"],
        "git_performed": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "package_install_performed": False,
        "network_access_performed": False,
        "repository_mutation_performed": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _architectural_health_advisory_artifact(
    *,
    execution_id: str,
    summary: dict[str, Any],
    replay_path: Path,
    created_at: str,
) -> dict[str, Any]:
    evidence = create_platform_digital_twin_evidence_bundle(
        bundle_id=f"{execution_id}:PLATFORM-DIGITAL-TWIN-EVIDENCE",
        component_scope="Broader Governed Validation Suites",
        evidence_records=[
            {
                "evidence_id": f"{execution_id}:VALIDATION-SUITE-SUMMARY",
                "source_path": "runtime:governed_validation_suite",
                "source_title": "G9-13 Broader Governed Validation Suites Runtime",
                "milestone_id": "G9_13_BROADER_GOVERNED_VALIDATION_SUITES_IMPLEMENTATION_V1",
                "source_class": "runtime_evidence",
                "status": summary["validation_suite_status"],
                "final_verdict": "BROADER_GOVERNED_VALIDATION_SUITES_IMPLEMENTED",
                "component_scope": "Broader Governed Validation Suites",
                "expected_owner": "Platform Core",
                "observed_owner": "Platform Core",
                "evidence_type": "validation_suite_summary",
                "boundary": "Platform Core coordinates; Worker Platform executes individual commands",
                "replay_reference": str(replay_path),
                "governance_reference": summary["candidate_id"],
                "validation_evidence": summary,
            }
        ],
        created_at=created_at,
    )
    return generate_architectural_health_advisory(
        projection_id=f"{execution_id}:ARCHITECTURAL-HEALTH-ADVISORY",
        digital_twin_evidence=evidence,
        generated_at=created_at,
    )


def _completion_artifact(
    *,
    execution_id: str,
    status: str,
    candidate: dict[str, Any],
    approval: dict[str, Any],
    authorization: dict[str, Any],
    pre_suite: dict[str, Any],
    command_execution: dict[str, Any],
    summary: dict[str, Any],
    advisory: dict[str, Any],
    replay_path: Path,
    executed_by: str,
    executed_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": GOVERNED_VALIDATION_SUITE_COMPLETION_ARTIFACT_V1,
        "runtime_version": GOVERNED_VALIDATION_SUITE_RUNTIME_VERSION,
        "execution_id": _require_string(execution_id, "execution_id"),
        "execution_status": status,
        "operation": candidate["operation"],
        "candidate_id": candidate["candidate_id"],
        "candidate_hash": candidate["artifact_hash"],
        "approval_id": approval["approval_id"],
        "approval_hash": approval["artifact_hash"],
        "authorization_id": authorization["authorization_id"],
        "authorization_hash": authorization["artifact_hash"],
        "pre_suite_hash": pre_suite["artifact_hash"],
        "command_execution_hash": command_execution["artifact_hash"],
        "suite_summary_hash": summary["artifact_hash"],
        "architectural_health_advisory_hash": advisory["artifact_hash"],
        "command_count": candidate["command_count"],
        "worker_invoked_count": command_execution["worker_invoked_count"],
        "validation_suite_status": summary["validation_suite_status"],
        "validation_suite_passed": summary["validation_suite_passed"],
        "architectural_health_advisory_status": advisory["overall_advisory_status"],
        "replay_reference": str(replay_path),
        "worker_invoked": command_execution["worker_invoked_count"] > 0,
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "package_install_performed": False,
        "network_access_performed": False,
        "repository_mutation_performed": False,
        "governance_authorization_observed": True,
        "human_approval_observed": True,
        "architectural_health_advisory_only": True,
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
    worker_invoked_count: int,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": GOVERNED_VALIDATION_SUITE_COMPLETION_ARTIFACT_V1,
        "runtime_version": GOVERNED_VALIDATION_SUITE_RUNTIME_VERSION,
        "execution_id": execution_id if isinstance(execution_id, str) else "INVALID_EXECUTION",
        "execution_status": FAILED_CLOSED,
        "operation": RUN_GOVERNED_VALIDATION_SUITE,
        "candidate_id": None,
        "candidate_hash": None,
        "approval_id": None,
        "approval_hash": None,
        "authorization_id": None,
        "authorization_hash": None,
        "pre_suite_hash": None,
        "command_execution_hash": None,
        "suite_summary_hash": None,
        "architectural_health_advisory_hash": None,
        "command_count": 0,
        "worker_invoked_count": worker_invoked_count,
        "validation_suite_status": FAILED_CLOSED,
        "validation_suite_passed": False,
        "architectural_health_advisory_status": None,
        "replay_reference": str(replay_path),
        "worker_invoked": worker_invoked_count > 0,
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "package_install_performed": False,
        "network_access_performed": False,
        "repository_mutation_performed": False,
        "governance_authorization_observed": False,
        "human_approval_observed": False,
        "architectural_health_advisory_only": True,
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
    summary: dict[str, Any] | None,
    advisory: dict[str, Any] | None,
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": GOVERNED_VALIDATION_SUITE_RUNTIME_VERSION,
        "execution_id": completion["execution_id"],
        "execution_status": completion["execution_status"],
        "operation": completion["operation"],
        "command_count": completion["command_count"],
        "worker_invoked_count": completion["worker_invoked_count"],
        "validation_suite_status": completion["validation_suite_status"],
        "validation_suite_passed": completion["validation_suite_passed"],
        "suite_summary_artifact": deepcopy(summary),
        "architectural_health_advisory_artifact": deepcopy(advisory),
        "completion_artifact": deepcopy(completion),
        "replay_reference": str(replay_path),
        "worker_invoked": completion["worker_invoked"],
        "git_performed": False,
        "commit_created": False,
        "deployment_performed": False,
        "provider_invoked": False,
        "package_install_performed": False,
        "network_access_performed": False,
        "repository_mutation_performed": False,
        "fail_closed": completion["fail_closed"],
        "failure_reason": completion["failure_reason"],
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _suite_status(statuses: list[str], planned_count: int, executed_count: int) -> str:
    if executed_count != planned_count and not statuses:
        return VALIDATION_SUITE_BLOCKED
    if any(status == VALIDATION_BLOCKED for status in statuses):
        return VALIDATION_SUITE_BLOCKED
    if any(status == VALIDATION_TIMED_OUT for status in statuses):
        return VALIDATION_SUITE_TIMED_OUT
    if any(status == VALIDATION_FAILED for status in statuses):
        return VALIDATION_SUITE_FAILED
    if executed_count == planned_count and all(status == VALIDATION_PASSED for status in statuses):
        return VALIDATION_SUITE_PASSED
    return VALIDATION_SUITE_BLOCKED


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"governed validation suite requires {field}")
    return value


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "governed validation suite failed closed"
