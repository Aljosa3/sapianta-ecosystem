"""Fail-closed runtime serving validation."""

from typing import Any

from .runtime_serving_session import validate_runtime_serving_session


def validate_runtime_serving(*, serving_session: dict, binding: dict, prior_output: dict | None, session_runtime_output: dict) -> dict[str, Any]:
    errors = list(validate_runtime_serving_session(serving_session)["errors"])
    if session_runtime_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "session_runtime", "reason": "runtime continuity invalid"})
    if prior_output is not None:
        if prior_output.get("runtime_serving_session", {}).get("runtime_serving_session_id") != serving_session.get("runtime_serving_session_id"):
            errors.append({"field": "runtime_serving_session_id", "reason": "serving identity changed"})
    for field in ("session_runtime_id","interaction_loop_session_id","interaction_turn_id","live_runtime_session_id","runtime_attachment_session_id","transport_session_id","governed_session_id","execution_gate_id","provider_invocation_id","bounded_runtime_id","result_capture_id","response_return_id"):
        if not isinstance(binding.get(field), str) or not binding[field].strip():
            errors.append({"field": field, "reason": "serving lineage missing"})
    return {"valid": not errors, "errors": errors}
