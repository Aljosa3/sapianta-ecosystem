"""Replay-safe local ingress/egress evidence."""

from __future__ import annotations

from typing import Any


def ingress_evidence(*, binding: dict[str, Any], states: list[str], valid: bool, egress_path: str) -> dict[str, Any]:
    return {
        "ingress_session_id": binding.get("ingress_session_id", ""),
        "interaction_session_id": binding.get("interaction_session_id", ""),
        "transport_session_id": binding.get("transport_session_id", ""),
        "governed_session_id": binding.get("governed_session_id", ""),
        "execution_gate_id": binding.get("execution_gate_id", ""),
        "provider_invocation_id": binding.get("provider_invocation_id", ""),
        "result_capture_id": binding.get("result_capture_id", ""),
        "response_return_id": binding.get("response_return_id", ""),
        "egress_path": egress_path,
        "states": states,
        "replay_safe": valid,
        "orchestration_introduced": False,
        "retry_introduced": False,
        "routing_introduced": False,
        "background_daemon_introduced": False,
        "async_execution_introduced": False,
    }


def validate_ingress_evidence(evidence: Any) -> dict[str, Any]:
    errors = []
    if not isinstance(evidence, dict):
        return {"valid": False, "errors": [{"field": "ingress_evidence", "reason": "must be object"}]}
    for field in ("ingress_session_id", "interaction_session_id", "transport_session_id", "governed_session_id", "execution_gate_id", "provider_invocation_id", "result_capture_id", "response_return_id", "egress_path"):
        if not isinstance(evidence.get(field), str) or not evidence[field].strip():
            errors.append({"field": field, "reason": "ingress evidence field must be non-empty"})
    return {"valid": not errors, "errors": errors}
