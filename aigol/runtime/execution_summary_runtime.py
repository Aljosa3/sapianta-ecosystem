"""Canonical execution summary and human confirmation runtime."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


EXECUTION_SUMMARY_ARTIFACT_V1 = "EXECUTION_SUMMARY_ARTIFACT_V1"
EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1 = "EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1"
PENDING_HUMAN_CONFIRMATION = "PENDING_HUMAN_CONFIRMATION"
HUMAN_CONFIRMED = "HUMAN_CONFIRMED"

HUMAN_RESPONSE_OPTIONS = (
    "APPROVE",
    "CLARIFY",
    "MODIFY",
    "EXPAND_SCOPE",
    "REDUCE_SCOPE",
    "REJECT",
    "CONTINUE_CONVERSATION",
)

AUTHORITY_FLAGS = {
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "authorizes_worker_invocation": False,
    "authorizes_provider_invocation": False,
    "authorizes_governance_mutation": False,
    "authorizes_replay_mutation": False,
    "creates_execution_authorization": False,
    "confirms_human_intent": False,
}


def create_execution_summary(
    *,
    summary_id: str,
    original_request: str,
    interpreted_intent: dict[str, Any],
    selected_route: dict[str, Any],
    planned_actions: list[Any],
    expected_outputs: list[Any],
    assumptions: list[Any],
    constraints: list[Any],
    risk_classification: dict[str, Any],
    execution_scope: dict[str, Any],
    replay_references: list[str],
    created_by: str,
    created_at: str,
) -> dict[str, Any]:
    """Create a canonical execution summary with no execution authority."""

    artifact = {
        "artifact_type": EXECUTION_SUMMARY_ARTIFACT_V1,
        "schema_version": "1.0",
        "summary_id": _require_string(summary_id, "summary_id"),
        "created_at": _require_string(created_at, "created_at"),
        "created_by": _require_string(created_by, "created_by"),
        "original_request": _require_string(original_request, "original_request"),
        "interpreted_intent": _require_object(interpreted_intent, "interpreted_intent"),
        "selected_route": _require_object(selected_route, "selected_route"),
        "planned_actions": _require_list(planned_actions, "planned_actions"),
        "expected_outputs": _require_list(expected_outputs, "expected_outputs"),
        "assumptions": _require_list(assumptions, "assumptions"),
        "constraints": _require_list(constraints, "constraints"),
        "risk_classification": _require_object(risk_classification, "risk_classification"),
        "authorization_required": True,
        "human_review_required": True,
        "human_response_options": list(HUMAN_RESPONSE_OPTIONS),
        "execution_scope": _require_object(execution_scope, "execution_scope"),
        "replay_references": _require_string_list(replay_references, "replay_references"),
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "summary_status": PENDING_HUMAN_CONFIRMATION,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    verify_execution_summary(artifact)
    return artifact


def create_execution_summary_confirmation(
    *,
    confirmation_id: str,
    execution_summary_artifact: dict[str, Any],
    decision: str,
    confirmed_by: str,
    confirmed_at: str,
) -> dict[str, Any]:
    """Create summary-bound human confirmation evidence."""

    summary = verify_execution_summary(execution_summary_artifact)
    normalized_decision = _require_string(decision, "decision").upper()
    if normalized_decision != "APPROVE":
        raise FailClosedRuntimeError("execution summary confirmation failed closed: APPROVE decision required")
    artifact = {
        "artifact_type": EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1,
        "schema_version": "1.0",
        "confirmation_id": _require_string(confirmation_id, "confirmation_id"),
        "execution_summary_reference": summary["summary_id"],
        "execution_summary_hash": summary["artifact_hash"],
        "decision": normalized_decision,
        "confirmed_by": _require_string(confirmed_by, "confirmed_by"),
        "confirmed_at": _require_string(confirmed_at, "confirmed_at"),
        "confirmation_status": HUMAN_CONFIRMED,
        "authorization_created": False,
        "execution_authorized": False,
        "worker_invoked": False,
        "execution_started": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    verify_execution_summary_confirmation(summary, artifact)
    return artifact


def verify_execution_summary(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("execution summary failed closed: summary artifact required")
    if artifact.get("artifact_type") != EXECUTION_SUMMARY_ARTIFACT_V1:
        raise FailClosedRuntimeError("execution summary failed closed: invalid artifact type")
    for field in (
        "summary_id",
        "created_at",
        "created_by",
        "original_request",
        "interpreted_intent",
        "selected_route",
        "planned_actions",
        "expected_outputs",
        "assumptions",
        "constraints",
        "risk_classification",
        "authorization_required",
        "human_review_required",
        "human_response_options",
        "execution_scope",
        "replay_references",
        "authority_flags",
        "summary_status",
        "artifact_hash",
    ):
        if field not in artifact:
            raise FailClosedRuntimeError(f"execution summary failed closed: {field} missing")
    if artifact.get("authorization_required") is not True:
        raise FailClosedRuntimeError("execution summary failed closed: authorization required")
    if artifact.get("human_review_required") is not True:
        raise FailClosedRuntimeError("execution summary failed closed: human review required")
    if artifact.get("summary_status") != PENDING_HUMAN_CONFIRMATION:
        raise FailClosedRuntimeError("execution summary failed closed: invalid summary status")
    if set(artifact.get("human_response_options") or []) != set(HUMAN_RESPONSE_OPTIONS):
        raise FailClosedRuntimeError("execution summary failed closed: human response options incomplete")
    if not _all_authority_flags_false(artifact.get("authority_flags")):
        raise FailClosedRuntimeError("execution summary failed closed: authority flags invalid")
    _require_object(artifact.get("interpreted_intent"), "interpreted_intent")
    _require_object(artifact.get("selected_route"), "selected_route")
    _require_list(artifact.get("planned_actions"), "planned_actions")
    _require_list(artifact.get("expected_outputs"), "expected_outputs")
    _require_list(artifact.get("assumptions"), "assumptions")
    _require_list(artifact.get("constraints"), "constraints")
    _require_object(artifact.get("risk_classification"), "risk_classification")
    _require_object(artifact.get("execution_scope"), "execution_scope")
    _require_string_list(artifact.get("replay_references"), "replay_references")
    _verify_artifact_hash(artifact, "execution summary")
    return deepcopy(artifact)


def verify_execution_summary_confirmation(
    execution_summary_artifact: dict[str, Any],
    confirmation_artifact: dict[str, Any],
) -> dict[str, Any]:
    summary = verify_execution_summary(execution_summary_artifact)
    if not isinstance(confirmation_artifact, dict):
        raise FailClosedRuntimeError("execution summary confirmation failed closed: confirmation artifact required")
    if confirmation_artifact.get("artifact_type") != EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("execution summary confirmation failed closed: invalid artifact type")
    if confirmation_artifact.get("execution_summary_reference") != summary["summary_id"]:
        raise FailClosedRuntimeError("execution summary confirmation failed closed: summary reference mismatch")
    if confirmation_artifact.get("execution_summary_hash") != summary["artifact_hash"]:
        raise FailClosedRuntimeError("execution summary confirmation failed closed: summary hash mismatch")
    if confirmation_artifact.get("decision") != "APPROVE":
        raise FailClosedRuntimeError("execution summary confirmation failed closed: approval required")
    if confirmation_artifact.get("confirmation_status") != HUMAN_CONFIRMED:
        raise FailClosedRuntimeError("execution summary confirmation failed closed: confirmation status invalid")
    _require_string(confirmation_artifact.get("confirmed_by"), "confirmed_by")
    _require_string(confirmation_artifact.get("confirmed_at"), "confirmed_at")
    _verify_artifact_hash(confirmation_artifact, "execution summary confirmation")
    return deepcopy(confirmation_artifact)


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError(f"{label} failed closed: artifact hash missing")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash", None)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(f"{label} failed closed: artifact hash mismatch")


def _all_authority_flags_false(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    for key in AUTHORITY_FLAGS:
        if value.get(key) is not False:
            return False
    return True


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"execution summary failed closed: {field_name} required")
    return value.strip()


def _require_object(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not value:
        raise FailClosedRuntimeError(f"execution summary failed closed: {field_name} required")
    return deepcopy(value)


def _require_list(value: Any, field_name: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError(f"execution summary failed closed: {field_name} required")
    return deepcopy(value)


def _require_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"execution summary failed closed: {field_name} required")
    cleaned = [item.strip() for item in value if isinstance(item, str) and item.strip()]
    if not cleaned:
        raise FailClosedRuntimeError(f"execution summary failed closed: {field_name} required")
    return cleaned

