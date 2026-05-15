"""Fail-closed persistent runtime validation."""

from typing import Any

from .session_runtime_session import validate_session_runtime_session


def validate_session_runtime(*, session_runtime: dict, turn: dict, binding: dict, prior_output: dict | None, attachment_output: dict) -> dict[str, Any]:
    errors = list(validate_session_runtime_session(session_runtime)["errors"])
    if attachment_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "attachment", "reason": "runtime attachment invalid"})
    if turn.get("session_runtime_id") != session_runtime.get("session_runtime_id"):
        errors.append({"field": "session_runtime_id", "reason": "runtime identity changed"})
    if prior_output is not None:
        if prior_output.get("session_runtime", {}).get("session_runtime_id") != session_runtime.get("session_runtime_id"):
            errors.append({"field": "session_runtime_id", "reason": "prior runtime identity mismatch"})
        if not turn.get("prior_interaction_turn_id"):
            errors.append({"field": "prior_interaction_turn_id", "reason": "prior turn lineage absent"})
    for field in ("interaction_loop_session_id","interaction_turn_id","live_runtime_session_id","runtime_attachment_session_id","transport_session_id","governed_session_id","execution_gate_id","provider_invocation_id","bounded_runtime_id","result_capture_id","response_return_id"):
        if not isinstance(binding.get(field), str) or not binding[field].strip():
            errors.append({"field": field, "reason": "runtime binding lineage missing"})
    return {"valid": not errors, "errors": errors}
