"""Fail-closed live runtime validation."""

from typing import Any

from .live_runtime_session import validate_live_runtime_session


def validate_live_runtime(*, session: dict[str, Any], loop_output: dict[str, Any], binding: dict[str, Any]) -> dict[str, Any]:
    errors = list(validate_live_runtime_session(session)["errors"])
    if loop_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "loop_output", "reason": "prior turn continuity invalid"})
    for field in ("interaction_loop_session_id","interaction_turn_id","transport_session_id","governed_session_id","execution_gate_id","provider_invocation_id","bounded_runtime_id","result_capture_id","response_return_id"):
        if not isinstance(binding.get(field), str) or not binding[field].strip():
            errors.append({"field": field, "reason": "runtime lineage missing"})
    return {"valid": not errors, "errors": errors}
