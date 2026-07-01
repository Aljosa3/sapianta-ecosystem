"""Platform Core execution planning and read-only handoff preview service."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_VERSION = "G8_06B_PLATFORM_CORE_EXECUTION_PLAN_PREVIEW_SERVICE_V1"

INTERACTIVE_COMPLETED = "ACLI_NEXT_INTERACTIVE_COMPLETED"

READONLY_WORKER_REQUESTED = "ACLI_NEXT_READONLY_WORKER_REQUESTED"
READONLY_WORKER_COMPLETED = "ACLI_NEXT_READONLY_WORKER_COMPLETED"
READONLY_WORKER_HANDOFF_COMPLETED = "ACLI_NEXT_READONLY_WORKER_HANDOFF_COMPLETED"
AUTHORIZED_READONLY_WORKER = "AUTHORIZED_READONLY_WORKER"

EXECUTION_PLAN_REQUESTED = "ACLI_NEXT_EXECUTION_PLAN_REQUESTED"
EXECUTION_PLAN_RECORDED = "ACLI_NEXT_EXECUTION_PLAN_RECORDED"
MUTATION_PREVIEW_RECORDED = "ACLI_NEXT_MUTATION_PREVIEW_RECORDED"
EXECUTION_PLAN_COMPLETED = "ACLI_NEXT_EXECUTION_PLAN_COMPLETED"
AUTHORIZED_ADVISORY_EXECUTION_PLAN = "AUTHORIZED_ADVISORY_EXECUTION_PLAN"

SUPPORTED_READONLY_CAPABILITIES: dict[str, dict[str, str]] = {
    "replay_inspection": {
        "worker_id": "ACLI_NEXT_REPLAY_INSPECTION_WORKER",
        "worker_type": "READONLY_REPLAY_INSPECTION_SUMMARY",
        "description": "Summarize replay references without mutation.",
    },
    "validation_summary": {
        "worker_id": "ACLI_NEXT_VALIDATION_SUMMARY_WORKER",
        "worker_type": "READONLY_VALIDATION_SUMMARY",
        "description": "Summarize validation evidence already present in replay.",
    },
    "canonical_mapping_lookup": {
        "worker_id": "ACLI_NEXT_CANONICAL_MAPPING_LOOKUP_WORKER",
        "worker_type": "READONLY_CANONICAL_MAPPING_LOOKUP",
        "description": "Summarize canonical mapping evidence already present in replay.",
    },
}

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
    capability = _lookup_readonly_capability(normalized_capability)
    authorization = _readonly_worker_authorization(
        session_id=session_id,
        interactive_result=interactive_result,
        capability_id=normalized_capability,
        created_at=created_at,
        runtime_version=runtime_version,
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

    result = _readonly_worker_result(
        session_id=session_id,
        interactive_result=interactive_result,
        capability_id=normalized_capability,
        capability=capability,
        request=request,
        created_at=created_at,
        command_name=command_name,
        runtime_version=runtime_version,
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
    _require_confirmed_interactive_session(interactive_result, label="execution plan")
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
    authorization = _execution_plan_authorization(
        session_id=session_id,
        interactive_result=interactive_result,
        created_at=created_at,
        runtime_version=runtime_version,
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

    plan = _execution_plan(
        session_id=session_id,
        interactive_result=interactive_result,
        request=request,
        worker_sequence=normalized_workers,
        requested_capabilities=normalized_capabilities,
        expected_artifacts=normalized_artifacts,
        potential_repository_impacts=normalized_impacts,
        created_at=created_at,
        command_name=command_name,
        runtime_version=runtime_version,
    )
    _persist(replay_path, "001_acli_next_execution_plan_recorded.json", plan)

    preview = _mutation_preview(
        session_id=session_id,
        interactive_result=interactive_result,
        plan=plan,
        created_at=created_at,
        command_name=command_name,
        runtime_version=runtime_version,
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


def _readonly_worker_authorization(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    capability_id: str,
    created_at: str,
    runtime_version: str,
) -> dict[str, Any]:
    _require_confirmed_interactive_session(interactive_result, label="read-only Worker")
    authorization = {
        "artifact_type": "PLATFORM_CORE_READONLY_WORKER_GOVERNANCE_AUTHORIZATION_V1",
        "runtime_version": runtime_version,
        "platform_core_service_version": PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_VERSION,
        "session_id": _require_string(session_id, "session_id"),
        "worker_capability": capability_id,
        "authorization_status": AUTHORIZED_READONLY_WORKER,
        "authorization_scope": "READ_ONLY_CONFIRMED_INTERACTIVE_SESSION",
        "authorization_basis": _authorization_basis(interactive_result),
        "human_confirmation_required": True,
        "human_confirmation_observed": True,
        "execution_authorized": False,
        "mutation_authorized": False,
        "provider_authorized": False,
        "worker_write_authorized": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    authorization["artifact_hash"] = replay_hash(authorization)
    return authorization


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


def _readonly_worker_result(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    capability_id: str,
    capability: dict[str, str],
    request: dict[str, Any],
    created_at: str,
    command_name: str,
    runtime_version: str,
) -> dict[str, Any]:
    summary = _readonly_worker_summary(capability_id, interactive_result)
    result = {
        "artifact_type": "PLATFORM_CORE_READONLY_WORKER_RESULT_V1",
        "runtime_version": runtime_version,
        "platform_core_service_version": PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_VERSION,
        "command": command_name,
        "session_id": _require_string(session_id, "session_id"),
        "worker_capability": capability_id,
        "worker_id": capability["worker_id"],
        "worker_type": capability["worker_type"],
        "worker_request_hash": request["artifact_hash"],
        "worker_result_status": READONLY_WORKER_COMPLETED,
        "result_summary": summary,
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
        "replay_visible": True,
    }
    result["artifact_hash"] = replay_hash(result)
    return result


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
    _require_readonly_worker_result(result)
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
        "result_summary": deepcopy(result["result_summary"]),
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


def _execution_plan_authorization(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    created_at: str,
    runtime_version: str,
) -> dict[str, Any]:
    authorization = {
        "artifact_type": "PLATFORM_CORE_EXECUTION_PLAN_GOVERNANCE_AUTHORIZATION_V1",
        "runtime_version": runtime_version,
        "platform_core_service_version": PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_VERSION,
        "session_id": _require_string(session_id, "session_id"),
        "authorization_status": AUTHORIZED_ADVISORY_EXECUTION_PLAN,
        "authorization_scope": "ADVISORY_PLAN_AND_DESCRIPTIVE_MUTATION_PREVIEW_ONLY",
        "authorization_basis": _authorization_basis(interactive_result),
        "human_confirmation_required": True,
        "human_confirmation_observed": True,
        "execution_authorized": False,
        "mutation_authorized": False,
        "worker_dispatch_authorized": False,
        "provider_authorized": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    authorization["artifact_hash"] = replay_hash(authorization)
    return authorization


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


def _execution_plan(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    request: dict[str, Any],
    worker_sequence: list[str],
    requested_capabilities: list[str],
    expected_artifacts: list[str],
    potential_repository_impacts: list[str],
    created_at: str,
    command_name: str,
    runtime_version: str,
) -> dict[str, Any]:
    plan = {
        "artifact_type": "PLATFORM_CORE_EXECUTION_PLAN_ARTIFACT_V1",
        "runtime_version": runtime_version,
        "platform_core_service_version": PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_VERSION,
        "command": command_name,
        "session_id": _require_string(session_id, "session_id"),
        "execution_plan_request_hash": request["artifact_hash"],
        "selected_worker_sequence": deepcopy(worker_sequence),
        "requested_capabilities": deepcopy(requested_capabilities),
        "expected_artifacts": deepcopy(expected_artifacts),
        "potential_repository_impact": deepcopy(potential_repository_impacts),
        "replay_plan": _replay_plan(interactive_result),
        "governance_checkpoints": _governance_checkpoints(),
        "execution_risk_summary": _risk_summary(worker_sequence, requested_capabilities, potential_repository_impacts),
        "mutation_preview_required": True,
        "created_at": _require_string(created_at, "created_at"),
        "plan_status": EXECUTION_PLAN_RECORDED,
        "advisory_only": True,
        "execution_authorized": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "replay_visible": True,
    }
    plan["artifact_hash"] = replay_hash(plan)
    return plan


def _mutation_preview(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    plan: dict[str, Any],
    created_at: str,
    command_name: str,
    runtime_version: str,
) -> dict[str, Any]:
    preview = {
        "artifact_type": "PLATFORM_CORE_MUTATION_PREVIEW_ARTIFACT_V1",
        "runtime_version": runtime_version,
        "platform_core_service_version": PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_VERSION,
        "command": command_name,
        "session_id": _require_string(session_id, "session_id"),
        "execution_plan_hash": plan["artifact_hash"],
        "interactive_replay_reference": interactive_result["replay_reference"],
        "preview_status": MUTATION_PREVIEW_RECORDED,
        "mutation_preview": {
            "preview_status": MUTATION_PREVIEW_RECORDED,
            "descriptive_only": True,
            "repository_files_to_modify": [],
            "git_operations": [],
            "deployment_operations": [],
            "potential_repository_impact": deepcopy(plan["potential_repository_impact"]),
            "requires_future_mutation_certification": True,
        },
        "created_at": _require_string(created_at, "created_at"),
        "advisory_only": True,
        "execution_authorized": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
        "deployment_performed": False,
        "replay_visible": True,
    }
    preview["artifact_hash"] = replay_hash(preview)
    return preview


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
    _require_advisory_non_mutating(plan)
    _require_advisory_non_mutating(preview)
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


def _authorization_basis(interactive_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "interactive_session_status": interactive_result.get("session_status"),
        "final_response_class": interactive_result.get("final_response_class"),
        "interactive_replay_reference": interactive_result.get("replay_reference"),
        "interactive_replay_hash": interactive_result.get("replay_hash"),
    }


def _readonly_worker_summary(capability_id: str, interactive_result: dict[str, Any]) -> dict[str, Any]:
    turns = interactive_result.get("turns")
    if not isinstance(turns, list) or not turns:
        raise FailClosedRuntimeError("Platform Core read-only Worker failed closed: turn history missing")
    if capability_id == "replay_inspection":
        return {
            "summary_type": "READONLY_REPLAY_INSPECTION_SUMMARY",
            "inspected_replay_reference": interactive_result["replay_reference"],
            "turn_count": interactive_result["turn_count"],
            "final_response_class": interactive_result["final_response_class"],
            "turn_response_classes": [turn.get("canonical_response_class") for turn in turns],
            "all_turns_replay_visible": all(bool(turn.get("turn_replay_reference")) for turn in turns),
            "mutation_detected": False,
        }
    if capability_id == "validation_summary":
        return {
            "summary_type": "READONLY_VALIDATION_SUMMARY",
            "inspected_replay_reference": interactive_result["replay_reference"],
            "validation_basis": "interactive session replay metadata",
            "turn_count": interactive_result["turn_count"],
            "completion_non_mutating": interactive_result.get("repository_mutated") is False,
            "mutation_detected": False,
        }
    if capability_id == "canonical_mapping_lookup":
        return {
            "summary_type": "READONLY_CANONICAL_MAPPING_LOOKUP",
            "inspected_replay_reference": interactive_result["replay_reference"],
            "mapping_basis": "canonical response classes",
            "final_response_class": interactive_result["final_response_class"],
            "continuation_profile": [
                {
                    "turn_id": turn.get("turn_id"),
                    "canonical_response_class": turn.get("canonical_response_class"),
                    "continuation_allowed": turn.get("continuation_allowed"),
                    "terminal_turn": turn.get("terminal_turn"),
                }
                for turn in turns
            ],
            "mutation_detected": False,
        }
    raise FailClosedRuntimeError("Platform Core read-only Worker failed closed: unsupported capability")


def _lookup_readonly_capability(capability_id: str) -> dict[str, str]:
    capability = SUPPORTED_READONLY_CAPABILITIES.get(capability_id)
    if capability is None:
        raise FailClosedRuntimeError(
            f"Platform Core read-only Worker failed closed: unsupported capability {capability_id}"
        )
    return capability


def _replay_plan(interactive_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "interactive_replay_reference": interactive_result["replay_reference"],
        "interactive_replay_hash": interactive_result["replay_hash"],
        "planned_artifacts": [
            "000_acli_next_execution_plan_request.json",
            "001_acli_next_execution_plan_recorded.json",
            "002_acli_next_mutation_preview_recorded.json",
            "003_acli_next_execution_plan_completed.json",
        ],
        "replay_append_only": True,
        "replay_reconstruction_owner": "Replay",
    }


def _governance_checkpoints() -> list[dict[str, str]]:
    return [
        {"checkpoint": "human_confirmation", "required_state": "CONFIRMATION"},
        {"checkpoint": "execution_authorization", "required_state": "not_created"},
        {"checkpoint": "worker_dispatch", "required_state": "not_performed"},
        {"checkpoint": "provider_invocation", "required_state": "not_performed"},
        {"checkpoint": "repository_mutation", "required_state": "not_performed"},
        {"checkpoint": "deployment", "required_state": "not_performed"},
    ]


def _risk_summary(
    worker_sequence: list[str],
    requested_capabilities: list[str],
    potential_repository_impacts: list[str],
) -> dict[str, Any]:
    has_mutation_language = any(
        token in item.lower()
        for item in [*worker_sequence, *requested_capabilities, *potential_repository_impacts]
        for token in ("mutat", "write", "patch", "commit", "deploy")
    )
    return {
        "risk_level": "MEDIUM" if has_mutation_language else "LOW",
        "risk_basis": "descriptive mutation preview only",
        "mutation_possible_in_this_milestone": False,
        "requires_future_certification_before_execution": True,
        "fail_closed_if_execution_requested": True,
    }


def _require_confirmed_interactive_session(interactive_result: dict[str, Any], *, label: str) -> None:
    if interactive_result.get("session_status") != INTERACTIVE_COMPLETED:
        raise FailClosedRuntimeError(f"Platform Core {label} failed closed: interactive session incomplete")
    if interactive_result.get("final_response_class") != "CONFIRMATION":
        raise FailClosedRuntimeError(f"Platform Core {label} failed closed: human confirmation missing")
    if not interactive_result.get("replay_reference") or not interactive_result.get("replay_hash"):
        raise FailClosedRuntimeError(f"Platform Core {label} failed closed: interactive replay evidence missing")
    _require_advisory_non_mutating(interactive_result, label=label)


def _require_advisory_non_mutating(artifact: dict[str, Any], *, label: str = "execution plan") -> None:
    for key in (
        "provider_invoked",
        "worker_invoked",
        "execution_authorized",
        "repository_mutated",
        "deployment_performed",
    ):
        if artifact.get(key) is not False:
            raise FailClosedRuntimeError(f"Platform Core {label} failed closed: {key} was not false")
    for optional_key in ("approval_created", "authorization_created"):
        if optional_key in artifact and artifact.get(optional_key) is not False:
            raise FailClosedRuntimeError(f"Platform Core {label} failed closed: {optional_key} was not false")


def _require_readonly_worker_result(result: dict[str, Any]) -> None:
    for key in (
        "provider_invoked",
        "worker_write_performed",
        "approval_created",
        "authorization_created",
        "execution_authorized",
        "repository_mutated",
        "deployment_performed",
    ):
        if result.get(key) is not False:
            raise FailClosedRuntimeError(f"Platform Core read-only Worker failed closed: {key} was not false")
    if result.get("worker_invoked") is not True:
        raise FailClosedRuntimeError("Platform Core read-only Worker failed closed: Worker result missing")
    if result.get("read_only") is not True or result.get("replay_visible") is not True:
        raise FailClosedRuntimeError("Platform Core read-only Worker failed closed: read-only replay evidence missing")


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
    write_json_immutable(replay_path / name, artifact)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"Platform Core execution planning requires {field}")
    return value
