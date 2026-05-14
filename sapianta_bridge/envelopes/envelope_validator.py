"""Fail-closed execution envelope validation."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.providers.provider_identity import validate_provider_identity

from .authority_scope import validate_authority_scope
from .envelope_constraints import validate_constraints
from .execution_envelope import ExecutionEnvelope
from .replay_binding import validate_replay_binding
from .workspace_scope import validate_workspace_scope


REQUIRED_ENVELOPE_FIELDS = (
    "envelope_id",
    "provider_id",
    "workspace_scope",
    "authority_scope",
    "allowed_actions",
    "forbidden_actions",
    "timeout_seconds",
    "replay_identity",
    "validation_requirements",
    "human_approval_required",
    "replay_safe",
    "constraints",
)


def validate_execution_envelope(envelope: Any) -> dict[str, Any]:
    value = envelope.to_dict() if isinstance(envelope, ExecutionEnvelope) else envelope
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {
            "envelope_valid": False,
            "errors": [{"field": "envelope", "reason": "envelope must be an object"}],
        }
    for field in REQUIRED_ENVELOPE_FIELDS:
        if field not in value:
            errors.append({"field": field, "reason": "missing envelope field"})
    for field in ("envelope_id", "provider_id", "replay_identity"):
        if field in value and (not isinstance(value[field], str) or not value[field].strip()):
            errors.append({"field": field, "reason": "field must be non-empty"})
    provider_result = validate_provider_identity(
        {"provider_id": value.get("provider_id"), "provider_type": "ENVELOPE_PROVIDER"}
    )
    errors.extend(error for error in provider_result["errors"] if error["field"] == "provider_id")
    authority_result = validate_authority_scope(value.get("authority_scope"))
    workspace_result = validate_workspace_scope(value.get("workspace_scope"))
    constraints_result = validate_constraints(value.get("constraints"), value.get("timeout_seconds"))
    replay_result = validate_replay_binding(value)
    for result in (authority_result, workspace_result, constraints_result, replay_result):
        errors.extend(result["errors"])
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "execution envelope must be replay-safe"})
    if not isinstance(value.get("allowed_actions"), list):
        errors.append({"field": "allowed_actions", "reason": "allowed actions must be a list"})
    if not isinstance(value.get("forbidden_actions"), list):
        errors.append({"field": "forbidden_actions", "reason": "forbidden actions must be a list"})
    allowed = set(value.get("allowed_actions", [])) if isinstance(value.get("allowed_actions"), list) else set()
    forbidden = set(value.get("forbidden_actions", [])) if isinstance(value.get("forbidden_actions"), list) else set()
    if allowed & forbidden:
        errors.append({"field": "actions", "reason": "action cannot be both allowed and forbidden"})
    if not isinstance(value.get("validation_requirements"), list) or not value.get("validation_requirements"):
        errors.append(
            {"field": "validation_requirements", "reason": "validation requirements must be non-empty"}
        )
    envelope_valid = not errors
    return {
        "envelope_valid": envelope_valid,
        "valid": envelope_valid,
        "errors": errors,
        "provider_bound": not any(error["field"] == "provider_id" for error in errors),
        "authority_scope_valid": authority_result["valid"],
        "workspace_scope_valid": workspace_result["valid"],
        "replay_binding_valid": replay_result["valid"],
        "hidden_authority_detected": bool(errors),
        "provider_independent_semantics": True,
        "routing_present": False,
        "orchestration_present": False,
    }
