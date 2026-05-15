"""Runtime attachment evidence."""

from typing import Any


FIELDS = ("runtime_attachment_session_id","live_runtime_session_id","interaction_loop_session_id","interaction_turn_id","transport_session_id","governed_session_id","execution_gate_id","provider_invocation_id","bounded_runtime_id","result_capture_id","response_return_id")


def runtime_attachment_evidence(*, binding: dict[str, Any], valid: bool, states: tuple[str, ...]) -> dict[str, Any]:
    return {
        **{field: binding.get(field, "") for field in FIELDS},
        "states": list(states),
        "replay_safe": valid,
        "continuity_fabricated": False,
        "hidden_memory_present": False,
        "orchestration_introduced": False,
    }


def validate_runtime_attachment_evidence(evidence: Any) -> dict[str, Any]:
    errors = []
    if not isinstance(evidence, dict):
        return {"valid": False, "errors": [{"field": "evidence", "reason": "must be object"}]}
    for field in FIELDS:
        if not isinstance(evidence.get(field), str) or not evidence[field].strip():
            errors.append({"field": field, "reason": "attachment evidence lineage missing"})
    return {"valid": not errors, "errors": errors}
