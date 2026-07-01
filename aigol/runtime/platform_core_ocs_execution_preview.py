"""OCS-owned advisory execution planning preview helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


PLATFORM_CORE_OCS_EXECUTION_PREVIEW_VERSION = "G8_06D_PLATFORM_CORE_OCS_EXECUTION_PREVIEW_V1"

EXECUTION_PLAN_RECORDED = "ACLI_NEXT_EXECUTION_PLAN_RECORDED"
MUTATION_PREVIEW_RECORDED = "ACLI_NEXT_MUTATION_PREVIEW_RECORDED"


def execution_plan_artifact(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    request: dict[str, Any],
    worker_sequence: list[str],
    requested_capabilities: list[str],
    expected_artifacts: list[str],
    potential_repository_impacts: list[str],
    replay_plan: dict[str, Any],
    governance_checkpoints: list[dict[str, str]],
    execution_risk_summary: dict[str, Any],
    created_at: str,
    command_name: str,
    runtime_version: str,
    platform_core_service_version: str,
) -> dict[str, Any]:
    """Construct the advisory execution plan artifact without execution authority."""

    plan = {
        "artifact_type": "PLATFORM_CORE_EXECUTION_PLAN_ARTIFACT_V1",
        "runtime_version": runtime_version,
        "platform_core_service_version": platform_core_service_version,
        "ocs_execution_preview_version": PLATFORM_CORE_OCS_EXECUTION_PREVIEW_VERSION,
        "command": command_name,
        "session_id": _require_string(session_id, "session_id"),
        "execution_plan_request_hash": request["artifact_hash"],
        "selected_worker_sequence": deepcopy(worker_sequence),
        "requested_capabilities": deepcopy(requested_capabilities),
        "expected_artifacts": deepcopy(expected_artifacts),
        "potential_repository_impact": deepcopy(potential_repository_impacts),
        "replay_plan": deepcopy(replay_plan),
        "governance_checkpoints": deepcopy(governance_checkpoints),
        "execution_risk_summary": deepcopy(execution_risk_summary),
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


def mutation_preview_artifact(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    plan: dict[str, Any],
    created_at: str,
    command_name: str,
    runtime_version: str,
    platform_core_service_version: str,
) -> dict[str, Any]:
    """Construct descriptive mutation preview evidence without mutation authority."""

    preview = {
        "artifact_type": "PLATFORM_CORE_MUTATION_PREVIEW_ARTIFACT_V1",
        "runtime_version": runtime_version,
        "platform_core_service_version": platform_core_service_version,
        "ocs_execution_preview_version": PLATFORM_CORE_OCS_EXECUTION_PREVIEW_VERSION,
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


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"Platform Core OCS execution preview requires {field}")
    return value
