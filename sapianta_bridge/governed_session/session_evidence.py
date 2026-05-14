"""Replay-safe governed execution session evidence."""

from __future__ import annotations

from typing import Any


def session_evidence(
    *,
    identity: dict[str, Any],
    context: dict[str, Any],
    lifecycle: list[str],
    validation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "session_id": identity.get("session_id", ""),
        "session_status": "COMPLETED" if validation.get("valid") and lifecycle[-1:] == ["COMPLETED"] else "BLOCKED",
        "ingress_bound": bool(context.get("ingress_reference")),
        "envelope_bound": bool(context.get("envelope_reference")),
        "provider_invocation_bound": bool(context.get("provider_invocation_reference")),
        "result_return_bound": bool(context.get("result_loop_reference")),
        "lifecycle": lifecycle,
        "identity_valid": validation.get("identity_valid", False),
        "context_valid": validation.get("context_valid", False),
        "lifecycle_valid": validation.get("lifecycle_valid", False),
        "provider_identity_consistent": validation.get("provider_identity_consistent", False),
        "envelope_identity_consistent": validation.get("envelope_identity_consistent", False),
        "replay_safe": validation.get("valid") is True,
        "orchestration_introduced": False,
        "retry_introduced": False,
        "provider_routing_introduced": False,
        "autonomous_execution_introduced": False,
        "hidden_memory_mutation_introduced": False,
        "multiple_provider_invocations_present": False,
    }


def validate_session_evidence(evidence: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(evidence, dict):
        return {"valid": False, "errors": [{"field": "session_evidence", "reason": "must be an object"}]}
    required = (
        "session_id",
        "session_status",
        "ingress_bound",
        "envelope_bound",
        "provider_invocation_bound",
        "result_return_bound",
        "replay_safe",
    )
    for field in required:
        if field not in evidence:
            errors.append({"field": field, "reason": "missing session evidence field"})
    for field in (
        "orchestration_introduced",
        "retry_introduced",
        "provider_routing_introduced",
        "autonomous_execution_introduced",
        "hidden_memory_mutation_introduced",
        "multiple_provider_invocations_present",
    ):
        if evidence.get(field) is not False:
            errors.append({"field": field, "reason": "session evidence reports forbidden behavior"})
    return {"valid": not errors, "errors": errors}
