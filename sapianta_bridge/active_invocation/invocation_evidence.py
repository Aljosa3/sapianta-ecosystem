"""Replay-safe active invocation evidence."""

from __future__ import annotations

from typing import Any

from .invocation_lifecycle import validate_lifecycle


def invocation_evidence(
    *,
    request: dict[str, Any],
    result: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    lifecycle = result.get("lifecycle", [])
    lifecycle_validation = validate_lifecycle(lifecycle)
    runtime_result = result.get("runtime_result", {})
    normalized_result = result.get("normalized_result", {})
    return {
        "invocation_executed": result.get("invocation_status") in ("SUCCESS", "FAILED", "NEEDS_REVIEW"),
        "invocation_id": request.get("invocation_id", ""),
        "provider_id": request.get("provider_id", ""),
        "envelope_id": request.get("envelope_id", ""),
        "replay_identity": request.get("replay_identity", ""),
        "lifecycle": lifecycle,
        "lifecycle_valid": lifecycle_validation["valid"],
        "provider_identity_valid": validation.get("provider_identity_valid", False),
        "envelope_valid": validation.get("envelope_valid", False),
        "runtime_binding_valid": validation.get("runtime_binding_valid", False),
        "invocation_binding_valid": validation.get("invocation_binding_valid", False),
        "runtime_status": runtime_result.get("runtime_status", "BLOCKED"),
        "normalized_execution_status": normalized_result.get("execution_status", "BLOCKED"),
        "normalized_result_bound": bool(normalized_result),
        "replay_safe": result.get("replay_safe") is True and lifecycle_validation["valid"],
        "routing_present": False,
        "retry_present": False,
        "fallback_present": False,
        "orchestration_present": False,
        "adaptive_provider_selection_present": False,
    }


def validate_invocation_evidence(evidence: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(evidence, dict):
        return {"valid": False, "errors": [{"field": "invocation_evidence", "reason": "must be an object"}]}
    required = (
        "invocation_executed",
        "invocation_id",
        "provider_id",
        "envelope_id",
        "replay_identity",
        "lifecycle_valid",
        "provider_identity_valid",
        "envelope_valid",
        "runtime_binding_valid",
        "invocation_binding_valid",
        "replay_safe",
    )
    for field in required:
        if field not in evidence:
            errors.append({"field": field, "reason": "missing invocation evidence field"})
    for field in ("routing_present", "retry_present", "fallback_present", "orchestration_present"):
        if evidence.get(field) is not False:
            errors.append({"field": field, "reason": "orchestration behavior is forbidden"})
    return {"valid": not errors, "errors": errors}
