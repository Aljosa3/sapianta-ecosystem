"""Fail-closed governed interaction loop validation."""

from typing import Any

from .interaction_loop_session import validate_loop_session


def validate_turn_continuity(*, session: dict[str, Any], turn: dict[str, Any], prior_output: dict[str, Any] | None, binding: dict[str, Any], transport_output: dict[str, Any]) -> dict[str, Any]:
    errors = list(validate_loop_session(session)["errors"])
    if turn.get("interaction_session_id") != session.get("interaction_session_id"):
        errors.append({"field": "interaction_session_id", "reason": "session continuity mismatch"})
    if turn.get("turn_index", 0) > 1:
        if not prior_output:
            errors.append({"field": "prior_output", "reason": "prior lineage required"})
        elif turn.get("prior_turn_id") != prior_output.get("turn", {}).get("turn_id"):
            errors.append({"field": "prior_turn_id", "reason": "prior turn linkage invalid"})
        elif turn.get("prior_response_id") != prior_output.get("binding", {}).get("response_return_id"):
            errors.append({"field": "prior_response_id", "reason": "prior response linkage invalid"})
    if transport_output.get("transport_validation", {}).get("valid") is not True:
        errors.append({"field": "transport", "reason": "execution linkage incomplete"})
    for field in ("transport_session_id", "governed_session_id", "execution_gate_id", "provider_invocation_id", "bounded_runtime_id", "result_capture_id", "response_return_id"):
        if not isinstance(binding.get(field), str) or not binding[field].strip():
            errors.append({"field": field, "reason": "binding lineage missing"})
    return {"valid": not errors, "errors": errors}
