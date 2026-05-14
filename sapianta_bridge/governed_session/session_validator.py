"""Fail-closed governed execution session validation."""

from __future__ import annotations

from typing import Any

from .session_context import validate_session_context
from .session_identity import validate_session_identity
from .session_lifecycle import validate_session_lifecycle


def validate_session_artifacts(
    *,
    identity: dict[str, Any],
    context: dict[str, Any],
    lifecycle: list[str],
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    identity_validation = validate_session_identity(identity)
    context_validation = validate_session_context(context)
    lifecycle_validation = validate_session_lifecycle(lifecycle)
    if not identity_validation["valid"]:
        errors.append({"field": "identity", "reason": "session identity invalid"})
    if not context_validation["valid"]:
        errors.append({"field": "context", "reason": "session context invalid"})
    if not lifecycle_validation["valid"]:
        errors.append({"field": "lifecycle", "reason": "session lifecycle invalid"})
    if identity_validation["valid"] and context_validation["valid"]:
        ingress = context["ingress_reference"]
        envelope = context["envelope_reference"]
        invocation = context["provider_invocation_reference"]
        result = context["result_loop_reference"]
        if identity["ingress_id"] != ingress.get("session_id"):
            errors.append({"field": "ingress_id", "reason": "session ingress identity mismatch"})
        if identity["semantic_request_id"] != ingress.get("semantic_request_id"):
            errors.append({"field": "semantic_request_id", "reason": "semantic request identity mismatch"})
        if identity["envelope_id"] != envelope.get("envelope_id"):
            errors.append({"field": "envelope_id", "reason": "session envelope identity mismatch"})
        if identity["provider_id"] != envelope.get("provider_id") or identity["provider_id"] != invocation.get("provider_id"):
            errors.append({"field": "provider_id", "reason": "session provider identity mismatch"})
        if identity["invocation_id"] != invocation.get("invocation_id") or identity["invocation_id"] != result.get("invocation_id"):
            errors.append({"field": "invocation_id", "reason": "session invocation identity mismatch"})
        if identity["result_return_id"] != result.get("result_return_id"):
            errors.append({"field": "result_return_id", "reason": "session result identity mismatch"})
        if identity["replay_identity"] != envelope.get("replay_identity"):
            errors.append({"field": "replay_identity", "reason": "session replay identity mismatch"})
        if invocation.get("envelope_id") != envelope.get("envelope_id") or result.get("envelope_id") != envelope.get("envelope_id"):
            errors.append({"field": "envelope_id", "reason": "session artifact envelope mismatch"})
    return {
        "valid": not errors,
        "errors": errors,
        "identity_valid": identity_validation["valid"],
        "context_valid": context_validation["valid"],
        "lifecycle_valid": lifecycle_validation["valid"],
        "provider_identity_consistent": not any(error["field"] == "provider_id" for error in errors),
        "envelope_identity_consistent": not any(error["field"] == "envelope_id" for error in errors),
        "replay_safe": not errors,
        "routing_present": False,
        "retry_present": False,
        "orchestration_present": False,
        "autonomous_execution_present": False,
    }
