"""Fail-closed runtime attachment validation."""

from typing import Any

from .runtime_attachment_session import validate_runtime_attachment_session


def validate_runtime_attachment(*, session: dict[str, Any], live_runtime_output: dict[str, Any], binding: dict[str, Any]) -> dict[str, Any]:
    errors = list(validate_runtime_attachment_session(session)["errors"])
    if live_runtime_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "live_runtime", "reason": "runtime lineage invalid"})
    for field in ("live_runtime_session_id","interaction_loop_session_id","interaction_turn_id","transport_session_id","governed_session_id","execution_gate_id","provider_invocation_id","bounded_runtime_id","result_capture_id","response_return_id"):
        if not isinstance(binding.get(field), str) or not binding[field].strip():
            errors.append({"field": field, "reason": "attachment lineage missing"})
    return {"valid": not errors, "errors": errors}
