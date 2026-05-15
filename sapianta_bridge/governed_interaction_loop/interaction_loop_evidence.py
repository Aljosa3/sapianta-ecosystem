"""Replay-visible governed interaction loop evidence."""

from typing import Any


def loop_evidence(*, session: dict[str, Any], binding: dict[str, Any], valid: bool, states: tuple[str, ...]) -> dict[str, Any]:
    return {
        "interaction_session_id": session.get("interaction_session_id", ""),
        "turn_id": binding.get("turn_id", ""),
        "prior_turn_id": binding.get("prior_turn_id"),
        "prior_response_id": binding.get("prior_response_id"),
        "transport_session_id": binding.get("transport_session_id", ""),
        "governed_session_id": binding.get("governed_session_id", ""),
        "execution_gate_id": binding.get("execution_gate_id", ""),
        "provider_invocation_id": binding.get("provider_invocation_id", ""),
        "bounded_runtime_id": binding.get("bounded_runtime_id", ""),
        "result_capture_id": binding.get("result_capture_id", ""),
        "response_return_id": binding.get("response_return_id", ""),
        "states": list(states),
        "replay_safe": valid,
        "implicit_memory_present": False,
        "continuity_fabricated": False,
        "autonomous_continuation_introduced": False,
        "orchestration_introduced": False,
    }


def validate_loop_evidence(evidence: Any) -> dict[str, Any]:
    errors = []
    if not isinstance(evidence, dict):
        return {"valid": False, "errors": [{"field": "loop_evidence", "reason": "must be object"}]}
    for field in ("interaction_session_id","turn_id","transport_session_id","governed_session_id","execution_gate_id","provider_invocation_id","bounded_runtime_id","result_capture_id","response_return_id"):
        if not isinstance(evidence.get(field), str) or not evidence[field].strip():
            errors.append({"field": field, "reason": "loop evidence field missing"})
    for field in ("implicit_memory_present","continuity_fabricated","autonomous_continuation_introduced","orchestration_introduced"):
        if evidence.get(field) is not False:
            errors.append({"field": field, "reason": "forbidden loop behavior"})
    return {"valid": not errors, "errors": errors}
