"""Platform Core execution planning and read-only handoff preview service."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.platform_core_capability_lookup import lookup_readonly_worker_capability
from aigol.runtime.platform_core_governance_preview import (
    execution_plan_authorization,
    execution_risk_summary,
    governance_checkpoints,
    readonly_worker_authorization,
    require_advisory_non_mutating,
    require_confirmed_interactive_session,
)
from aigol.runtime.platform_core_ocs_execution_preview import (
    execution_plan_artifact,
    mutation_preview_artifact,
)
from aigol.runtime.platform_core_replay_preview import (
    execution_plan_replay_plan,
    persist_platform_core_preview_artifact,
)
from aigol.runtime.platform_core_worker_preview import (
    readonly_worker_result,
    require_readonly_worker_result,
    result_summary,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_VERSION = "G8_06D_PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_REFACTORING_V1"

READONLY_WORKER_REQUESTED = "ACLI_NEXT_READONLY_WORKER_REQUESTED"
READONLY_WORKER_HANDOFF_COMPLETED = "ACLI_NEXT_READONLY_WORKER_HANDOFF_COMPLETED"

EXECUTION_PLAN_REQUESTED = "ACLI_NEXT_EXECUTION_PLAN_REQUESTED"
EXECUTION_PLAN_COMPLETED = "ACLI_NEXT_EXECUTION_PLAN_COMPLETED"

DEFAULT_WORKER_SEQUENCE = ["ACLI_NEXT_READONLY_WORKER_HANDOFF"]
DEFAULT_REQUESTED_CAPABILITIES = ["replay_inspection", "validation_summary"]
DEFAULT_EXPECTED_ARTIFACTS = [
    "ACLI_NEXT_EXECUTION_PLAN_ARTIFACT_V1",
    "ACLI_NEXT_MUTATION_PREVIEW_ARTIFACT_V1",
]
DEFAULT_REPOSITORY_IMPACTS = ["DESCRIPTIVE_MUTATION_PREVIEW_ONLY"]


def run_platform_core_readonly_worker_handoff(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    worker_capability: str,
    created_at: str,
    replay_dir: str | Path,
    command_name: str,
    runtime_version: str,
) -> dict[str, Any]:
    """Create a replay-visible read-only Worker handoff preview."""

    replay_path = Path(replay_dir)
    normalized_capability = _normalize_token(worker_capability, "worker_capability")
    capability = lookup_readonly_worker_capability(normalized_capability)
    authorization = readonly_worker_authorization(
        session_id=session_id,
        interactive_result=interactive_result,
        capability_id=normalized_capability,
        created_at=created_at,
        runtime_version=runtime_version,
        platform_core_service_version=PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_VERSION,
    )
    request = _readonly_worker_request(
        session_id=session_id,
        interactive_result=interactive_result,
        capability_id=normalized_capability,
        capability=capability,
        authorization=authorization,
        created_at=created_at,
        command_name=command_name,
        runtime_version=runtime_version,
    )
    _persist(replay_path, "000_acli_next_readonly_worker_request.json", request)

    result = readonly_worker_result(
        session_id=session_id,
        interactive_result=interactive_result,
        capability_id=normalized_capability,
        capability=capability,
        request=request,
        created_at=created_at,
        command_name=command_name,
        runtime_version=runtime_version,
        platform_core_service_version=PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_VERSION,
    )
    _persist(replay_path, "001_acli_next_readonly_worker_result.json", result)

    completion = _readonly_worker_completion(
        session_id=session_id,
        interactive_result=interactive_result,
        request=request,
        result=result,
        replay_path=replay_path,
        created_at=created_at,
        command_name=command_name,
        runtime_version=runtime_version,
    )
    _persist(replay_path, "002_acli_next_readonly_worker_completion.json", completion)
    return _result(completion)


def run_platform_core_execution_plan_preview(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    command_name: str,
    runtime_version: str,
    worker_sequence: list[str] | None = None,
    requested_capabilities: list[str] | None = None,
    expected_artifacts: list[str] | None = None,
    potential_repository_impacts: list[str] | None = None,
) -> dict[str, Any]:
    """Create a replay-visible advisory execution plan preview."""

    replay_path = Path(replay_dir)
    require_confirmed_interactive_session(interactive_result, label="execution plan")
    normalized_workers = _normalize_list(worker_sequence, DEFAULT_WORKER_SEQUENCE, "worker_sequence")
    normalized_capabilities = _normalize_list(
        requested_capabilities,
        DEFAULT_REQUESTED_CAPABILITIES,
        "requested_capabilities",
    )
    normalized_artifacts = _normalize_list(expected_artifacts, DEFAULT_EXPECTED_ARTIFACTS, "expected_artifacts")
    normalized_impacts = _normalize_list(
        potential_repository_impacts,
        DEFAULT_REPOSITORY_IMPACTS,
        "potential_repository_impacts",
    )
    authorization = execution_plan_authorization(
        session_id=session_id,
        interactive_result=interactive_result,
        created_at=created_at,
        runtime_version=runtime_version,
        platform_core_service_version=PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_VERSION,
    )
    request = _execution_plan_request(
        session_id=session_id,
        interactive_result=interactive_result,
        authorization=authorization,
        worker_sequence=normalized_workers,
        requested_capabilities=normalized_capabilities,
        expected_artifacts=normalized_artifacts,
        potential_repository_impacts=normalized_impacts,
        created_at=created_at,
        command_name=command_name,
        runtime_version=runtime_version,
    )
    _persist(replay_path, "000_acli_next_execution_plan_request.json", request)

    plan = execution_plan_artifact(
        session_id=session_id,
        interactive_result=interactive_result,
        request=request,
        worker_sequence=normalized_workers,
        requested_capabilities=normalized_capabilities,
        expected_artifacts=normalized_artifacts,
        potential_repository_impacts=normalized_impacts,
        replay_plan=execution_plan_replay_plan(interactive_result),
        governance_checkpoints=governance_checkpoints(),
        execution_risk_summary=execution_risk_summary(
            worker_sequence=normalized_workers,
            requested_capabilities=normalized_capabilities,
            potential_repository_impacts=normalized_impacts,
        ),
        created_at=created_at,
        command_name=command_name,
        runtime_version=runtime_version,
        platform_core_service_version=PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_VERSION,
    )
    _persist(replay_path, "001_acli_next_execution_plan_recorded.json", plan)

    preview = mutation_preview_artifact(
        session_id=session_id,
        interactive_result=interactive_result,
        plan=plan,
        created_at=created_at,
        command_name=command_name,
        runtime_version=runtime_version,
        platform_core_service_version=PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_VERSION,
    )
    _persist(replay_path, "002_acli_next_mutation_preview_recorded.json", preview)

    completion = _execution_plan_completion(
        session_id=session_id,
        interactive_result=interactive_result,
        request=request,
        plan=plan,
        preview=preview,
        replay_path=replay_path,
        created_at=created_at,
        command_name=command_name,
        runtime_version=runtime_version,
    )
    _persist(replay_path, "003_acli_next_execution_plan_completed.json", completion)
    return _result(completion)


def _readonly_worker_request(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    capability_id: str,
    capability: dict[str, str],
    authorization: dict[str, Any],
    created_at: str,
    command_name: str,
    runtime_version: str,
) -> dict[str, Any]:
    request = {
        "artifact_type": "PLATFORM_CORE_READONLY_WORKER_REQUEST_V1",
        "runtime_version": runtime_version,
        "platform_core_service_version": PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_VERSION,
        "command": command_name,
        "session_id": _require_string(session_id, "session_id"),
        "worker_capability": capability_id,
        "worker_id": capability["worker_id"],
        "worker_type": capability["worker_type"],
        "capability_description": capability["description"],
        "governance_authorization_hash": authorization["artifact_hash"],
        "governance_authorization_status": authorization["authorization_status"],
        "interactive_replay_reference": interactive_result["replay_reference"],
        "interactive_replay_hash": interactive_result["replay_hash"],
        "created_at": _require_string(created_at, "created_at"),
        "handoff_status": READONLY_WORKER_REQUESTED,
        "read_only": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "replay_visible": True,
    }
    request["artifact_hash"] = replay_hash(request)
    return request


def _readonly_worker_completion(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    request: dict[str, Any],
    result: dict[str, Any],
    replay_path: Path,
    created_at: str,
    command_name: str,
    runtime_version: str,
) -> dict[str, Any]:
    require_readonly_worker_result(result)
    completion = {
        "artifact_type": "PLATFORM_CORE_READONLY_WORKER_HANDOFF_COMPLETION_V1",
        "runtime_version": runtime_version,
        "platform_core_service_version": PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_VERSION,
        "command": command_name,
        "session_id": _require_string(session_id, "session_id"),
        "handoff_status": READONLY_WORKER_HANDOFF_COMPLETED,
        "worker_capability": result["worker_capability"],
        "worker_id": result["worker_id"],
        "worker_type": result["worker_type"],
        "worker_request_hash": request["artifact_hash"],
        "worker_result_hash": result["artifact_hash"],
        "worker_result_status": result["worker_result_status"],
        "governance_authorization_status": request["governance_authorization_status"],
        "interactive_replay_reference": interactive_result["replay_reference"],
        "interactive_replay_hash": interactive_result["replay_hash"],
        "replay_reference": str(replay_path),
        "result_summary": result_summary(result),
        "created_at": _require_string(created_at, "created_at"),
        "read_only": True,
        "provider_invoked": False,
        "worker_invoked": True,
        "worker_write_performed": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_authorized": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "fail_closed": False,
        "replay_visible": True,
    }
    completion["artifact_hash"] = replay_hash(completion)
    return completion


def _execution_plan_request(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    authorization: dict[str, Any],
    worker_sequence: list[str],
    requested_capabilities: list[str],
    expected_artifacts: list[str],
    potential_repository_impacts: list[str],
    created_at: str,
    command_name: str,
    runtime_version: str,
) -> dict[str, Any]:
    request = {
        "artifact_type": "PLATFORM_CORE_EXECUTION_PLAN_REQUEST_V1",
        "runtime_version": runtime_version,
        "platform_core_service_version": PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_VERSION,
        "command": command_name,
        "session_id": _require_string(session_id, "session_id"),
        "interactive_replay_reference": interactive_result["replay_reference"],
        "interactive_replay_hash": interactive_result["replay_hash"],
        "governance_authorization_hash": authorization["artifact_hash"],
        "governance_authorization_status": authorization["authorization_status"],
        "selected_worker_sequence": deepcopy(worker_sequence),
        "requested_capabilities": deepcopy(requested_capabilities),
        "expected_artifacts": deepcopy(expected_artifacts),
        "potential_repository_impacts": deepcopy(potential_repository_impacts),
        "created_at": _require_string(created_at, "created_at"),
        "plan_status": EXECUTION_PLAN_REQUESTED,
        "advisory_only": True,
        "execution_authorized": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "replay_visible": True,
    }
    request["artifact_hash"] = replay_hash(request)
    return request


def _execution_plan_completion(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    request: dict[str, Any],
    plan: dict[str, Any],
    preview: dict[str, Any],
    replay_path: Path,
    created_at: str,
    command_name: str,
    runtime_version: str,
) -> dict[str, Any]:
    require_advisory_non_mutating(plan)
    require_advisory_non_mutating(preview)
    completion = {
        "artifact_type": "PLATFORM_CORE_EXECUTION_PLAN_COMPLETION_V1",
        "runtime_version": runtime_version,
        "platform_core_service_version": PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_VERSION,
        "command": command_name,
        "session_id": _require_string(session_id, "session_id"),
        "plan_status": EXECUTION_PLAN_COMPLETED,
        "execution_plan_request_hash": request["artifact_hash"],
        "execution_plan_hash": plan["artifact_hash"],
        "mutation_preview_hash": preview["artifact_hash"],
        "selected_worker_sequence": deepcopy(plan["selected_worker_sequence"]),
        "requested_capabilities": deepcopy(plan["requested_capabilities"]),
        "expected_artifacts": deepcopy(plan["expected_artifacts"]),
        "potential_repository_impact": deepcopy(plan["potential_repository_impact"]),
        "replay_plan": deepcopy(plan["replay_plan"]),
        "governance_checkpoints": deepcopy(plan["governance_checkpoints"]),
        "execution_risk_summary": deepcopy(plan["execution_risk_summary"]),
        "mutation_preview": deepcopy(preview["mutation_preview"]),
        "interactive_replay_reference": interactive_result["replay_reference"],
        "interactive_replay_hash": interactive_result["replay_hash"],
        "replay_reference": str(replay_path),
        "created_at": _require_string(created_at, "created_at"),
        "advisory_only": True,
        "execution_authorized": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "fail_closed": False,
        "replay_visible": True,
    }
    completion["artifact_hash"] = replay_hash(completion)
    return completion


def _normalize_list(value: list[str] | None, default: list[str], field: str) -> list[str]:
    source = default if value is None else value
    if not isinstance(source, list) or not source:
        raise FailClosedRuntimeError(f"Platform Core execution planning requires {field}")
    normalized = [_require_string(item, field).strip() for item in source]
    if len(set(normalized)) != len(normalized):
        raise FailClosedRuntimeError(f"Platform Core execution planning requires unique {field}")
    return normalized


def _normalize_token(value: str, field: str) -> str:
    return _require_string(value, field).strip().lower().replace("-", "_")


def _result(completion: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(completion)
    result["replay_hash"] = completion["artifact_hash"]
    return result


def _persist(replay_path: Path, name: str, artifact: dict[str, Any]) -> None:
    persist_platform_core_preview_artifact(replay_path, name, artifact)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"Platform Core execution planning requires {field}")
    return value
