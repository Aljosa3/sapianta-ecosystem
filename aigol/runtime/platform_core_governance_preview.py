"""Governance preview helpers for non-mutating Platform Core planning."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


PLATFORM_CORE_GOVERNANCE_PREVIEW_VERSION = "G8_06D_PLATFORM_CORE_GOVERNANCE_PREVIEW_V1"

INTERACTIVE_COMPLETED = "ACLI_NEXT_INTERACTIVE_COMPLETED"
AUTHORIZED_READONLY_WORKER = "AUTHORIZED_READONLY_WORKER"
AUTHORIZED_ADVISORY_EXECUTION_PLAN = "AUTHORIZED_ADVISORY_EXECUTION_PLAN"


def readonly_worker_authorization(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    capability_id: str,
    created_at: str,
    runtime_version: str,
    platform_core_service_version: str,
) -> dict[str, Any]:
    """Create governance evidence for a read-only Worker preview."""

    require_confirmed_interactive_session(interactive_result, label="read-only Worker")
    authorization = {
        "artifact_type": "PLATFORM_CORE_READONLY_WORKER_GOVERNANCE_AUTHORIZATION_V1",
        "runtime_version": runtime_version,
        "platform_core_service_version": platform_core_service_version,
        "governance_preview_version": PLATFORM_CORE_GOVERNANCE_PREVIEW_VERSION,
        "session_id": _require_string(session_id, "session_id"),
        "worker_capability": capability_id,
        "authorization_status": AUTHORIZED_READONLY_WORKER,
        "authorization_scope": "READ_ONLY_CONFIRMED_INTERACTIVE_SESSION",
        "authorization_basis": authorization_basis(interactive_result),
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


def execution_plan_authorization(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    created_at: str,
    runtime_version: str,
    platform_core_service_version: str,
) -> dict[str, Any]:
    """Create governance evidence for an advisory execution plan preview."""

    authorization = {
        "artifact_type": "PLATFORM_CORE_EXECUTION_PLAN_GOVERNANCE_AUTHORIZATION_V1",
        "runtime_version": runtime_version,
        "platform_core_service_version": platform_core_service_version,
        "governance_preview_version": PLATFORM_CORE_GOVERNANCE_PREVIEW_VERSION,
        "session_id": _require_string(session_id, "session_id"),
        "authorization_status": AUTHORIZED_ADVISORY_EXECUTION_PLAN,
        "authorization_scope": "ADVISORY_PLAN_AND_DESCRIPTIVE_MUTATION_PREVIEW_ONLY",
        "authorization_basis": authorization_basis(interactive_result),
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


def authorization_basis(interactive_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "interactive_session_status": interactive_result.get("session_status"),
        "final_response_class": interactive_result.get("final_response_class"),
        "interactive_replay_reference": interactive_result.get("replay_reference"),
        "interactive_replay_hash": interactive_result.get("replay_hash"),
    }


def governance_checkpoints() -> list[dict[str, str]]:
    return [
        {"checkpoint": "human_confirmation", "required_state": "CONFIRMATION"},
        {"checkpoint": "execution_authorization", "required_state": "not_created"},
        {"checkpoint": "worker_dispatch", "required_state": "not_performed"},
        {"checkpoint": "provider_invocation", "required_state": "not_performed"},
        {"checkpoint": "repository_mutation", "required_state": "not_performed"},
        {"checkpoint": "deployment", "required_state": "not_performed"},
    ]


def execution_risk_summary(
    *,
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


def require_confirmed_interactive_session(interactive_result: dict[str, Any], *, label: str) -> None:
    if interactive_result.get("session_status") != INTERACTIVE_COMPLETED:
        raise FailClosedRuntimeError(f"Platform Core {label} failed closed: interactive session incomplete")
    if interactive_result.get("final_response_class") != "CONFIRMATION":
        raise FailClosedRuntimeError(f"Platform Core {label} failed closed: human confirmation missing")
    if not interactive_result.get("replay_reference") or not interactive_result.get("replay_hash"):
        raise FailClosedRuntimeError(f"Platform Core {label} failed closed: interactive replay evidence missing")
    require_advisory_non_mutating(interactive_result, label=label)


def require_advisory_non_mutating(artifact: dict[str, Any], *, label: str = "execution plan") -> None:
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


def immutable_checkpoints() -> list[dict[str, str]]:
    return deepcopy(governance_checkpoints())


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"Platform Core governance preview requires {field}")
    return value
