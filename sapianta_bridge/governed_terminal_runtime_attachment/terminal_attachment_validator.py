"""Fail-closed terminal attachment validation."""

from typing import Any

from .terminal_attachment_session import validate_terminal_attachment_session

LINEAGE_FIELDS = (
    "terminal_attachment_session_id",
    "runtime_serving_session_id",
    "session_runtime_id",
    "interaction_loop_session_id",
    "interaction_turn_id",
    "live_runtime_session_id",
    "runtime_attachment_session_id",
    "transport_session_id",
    "governed_session_id",
    "execution_gate_id",
    "provider_invocation_id",
    "bounded_runtime_id",
    "result_capture_id",
    "response_return_id",
)


def validate_terminal_attachment(*, terminal_session: dict, binding: dict, runtime_serving_output: dict, prior_output: dict | None = None) -> dict[str, Any]:
    errors = list(validate_terminal_attachment_session(terminal_session)["errors"])
    if runtime_serving_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "runtime_serving", "reason": "runtime serving continuity invalid"})
    if prior_output is not None:
        prior_id = prior_output.get("terminal_attachment_session", {}).get("terminal_attachment_session_id")
        if prior_id != terminal_session.get("terminal_attachment_session_id"):
            errors.append({"field": "terminal_attachment_session_id", "reason": "terminal attachment identity changed"})
    for field in LINEAGE_FIELDS:
        if not isinstance(binding.get(field), str) or not binding[field].strip():
            errors.append({"field": field, "reason": "terminal lineage missing"})
    for field in ("stdin_binding_id", "stdout_binding_id"):
        if not isinstance(binding.get(field), str) or not binding[field].strip():
            errors.append({"field": field, "reason": "terminal continuity missing"})
    return {"valid": not errors, "errors": errors}
