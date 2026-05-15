"""Replay-safe interaction transport evidence."""

from __future__ import annotations

from typing import Any


def transport_evidence(*, binding: dict[str, Any], response: dict[str, Any], valid: bool, states: list[str]) -> dict[str, Any]:
    return {
        "transport_session_id": binding.get("transport_session_id", ""),
        "interaction_session_id": binding.get("interaction_session_id", ""),
        "governed_session_id": binding.get("governed_session_id", ""),
        "execution_gate_id": binding.get("execution_gate_id", ""),
        "provider_invocation_id": binding.get("provider_invocation_id", ""),
        "bounded_runtime_id": binding.get("bounded_runtime_id", ""),
        "result_capture_id": binding.get("result_capture_id", ""),
        "response_return_id": binding.get("response_return_id", ""),
        "states": states,
        "result_normalized": response.get("transport_state") == "RESULT_RETURNED",
        "replay_safe": valid,
        "orchestration_introduced": False,
        "retry_introduced": False,
        "fallback_introduced": False,
        "routing_introduced": False,
        "provider_switching_introduced": False,
        "autonomous_continuation_introduced": False,
    }


def validate_transport_evidence(evidence: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(evidence, dict):
        return {"valid": False, "errors": [{"field": "transport_evidence", "reason": "must be object"}]}
    for field in ("transport_session_id", "interaction_session_id", "governed_session_id", "execution_gate_id", "provider_invocation_id", "bounded_runtime_id", "result_capture_id", "response_return_id"):
        if not isinstance(evidence.get(field), str) or not evidence[field].strip():
            errors.append({"field": field, "reason": "transport evidence field must be non-empty"})
    for field in ("orchestration_introduced", "retry_introduced", "fallback_introduced", "routing_introduced", "provider_switching_introduced", "autonomous_continuation_introduced"):
        if evidence.get(field) is not False:
            errors.append({"field": field, "reason": "transport evidence reports forbidden behavior"})
    return {"valid": not errors, "errors": errors}
