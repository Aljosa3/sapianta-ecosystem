"""Replay-safe live runtime evidence."""

from typing import Any


def live_runtime_evidence(*, binding: dict[str, Any], valid: bool, states: tuple[str, ...]) -> dict[str, Any]:
    return {
        **{field: binding.get(field, "") for field in (
            "live_runtime_session_id","interaction_loop_session_id","interaction_turn_id","transport_session_id",
            "governed_session_id","execution_gate_id","provider_invocation_id","bounded_runtime_id","result_capture_id","response_return_id"
        )},
        "states": list(states),
        "replay_safe": valid,
        "continuity_fabricated": False,
        "provider_hidden_state_trusted": False,
        "autonomous_continuation_introduced": False,
        "orchestration_introduced": False,
    }


def validate_live_runtime_evidence(evidence: Any) -> dict[str, Any]:
    errors = []
    if not isinstance(evidence, dict):
        return {"valid": False, "errors": [{"field": "evidence", "reason": "must be object"}]}
    for field in ("live_runtime_session_id","interaction_loop_session_id","interaction_turn_id","transport_session_id","governed_session_id","execution_gate_id","provider_invocation_id","bounded_runtime_id","result_capture_id","response_return_id"):
        if not isinstance(evidence.get(field), str) or not evidence[field].strip():
            errors.append({"field": field, "reason": "evidence lineage missing"})
    return {"valid": not errors, "errors": errors}
