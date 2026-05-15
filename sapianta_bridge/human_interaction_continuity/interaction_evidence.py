"""Replay-safe human interaction continuity evidence."""

from __future__ import annotations

from typing import Any


def interaction_evidence(*, request: dict[str, Any], session: dict[str, Any], binding: dict[str, Any], response: dict[str, Any], valid: bool) -> dict[str, Any]:
    return {
        "interaction_session_id": session.get("interaction_session_id", ""),
        "interaction_request_id": request.get("interaction_request_id", ""),
        "governed_session_id": binding.get("governed_session_id", ""),
        "execution_gate_id": binding.get("execution_gate_id", ""),
        "provider_id": binding.get("provider_id", ""),
        "envelope_id": binding.get("envelope_id", ""),
        "invocation_id": binding.get("invocation_id", ""),
        "result_return_id": binding.get("result_return_id", ""),
        "current_state": response.get("current_state", "BLOCKED"),
        "request_result_associated": bool(binding.get("interaction_request_id") and binding.get("result_return_id")),
        "bounded_execution_visible": bool(response.get("execution_phases")),
        "lineage_preserved": valid,
        "replay_safe": valid,
        "orchestration_introduced": False,
        "autonomous_continuation_introduced": False,
        "retry_introduced": False,
        "routing_introduced": False,
    }


def validate_interaction_evidence(evidence: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(evidence, dict):
        return {"valid": False, "errors": [{"field": "interaction_evidence", "reason": "must be an object"}]}
    for field in ("interaction_session_id", "interaction_request_id", "governed_session_id", "execution_gate_id", "provider_id", "envelope_id", "invocation_id", "result_return_id", "current_state"):
        if not isinstance(evidence.get(field), str) or not evidence[field].strip():
            errors.append({"field": field, "reason": "interaction evidence field must be non-empty"})
    for field in ("orchestration_introduced", "autonomous_continuation_introduced", "retry_introduced", "routing_introduced"):
        if evidence.get(field) is not False:
            errors.append({"field": field, "reason": "interaction evidence reports forbidden behavior"})
    return {"valid": not errors, "errors": errors}
