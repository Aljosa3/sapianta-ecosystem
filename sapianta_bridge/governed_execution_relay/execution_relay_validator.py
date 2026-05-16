"""Fail-closed governed execution relay validation."""

from typing import Any

from .execution_relay_session import validate_execution_relay_session

LINEAGE_FIELDS = (
    "execution_relay_session_id",
    "execution_exchange_session_id",
    "live_request_ingestion_session_id",
    "serving_gateway_session_id",
    "runtime_serving_session_id",
    "terminal_attachment_session_id",
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
    "stdin_relay_id",
    "stdout_relay_id",
)


def validate_execution_relay(*, relay_session: dict, binding: dict, exchange_output: dict, terminal_output: dict, prior_output: dict | None = None) -> dict[str, Any]:
    errors = list(validate_execution_relay_session(relay_session)["errors"])
    if exchange_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "execution_exchange", "reason": "exchange continuity invalid"})
    if terminal_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "terminal_attachment", "reason": "terminal attachment continuity invalid"})
    exchange_binding = exchange_output.get("execution_exchange_binding", {})
    terminal_binding = terminal_output.get("terminal_attachment_binding", {})
    if exchange_binding.get("execution_exchange_session_id") != relay_session.get("execution_exchange_session_id"):
        errors.append({"field": "execution_exchange_session_id", "reason": "exchange linkage mismatch"})
    if exchange_binding.get("terminal_attachment_session_id") != terminal_binding.get("terminal_attachment_session_id"):
        errors.append({"field": "terminal_attachment_session_id", "reason": "terminal linkage mismatch"})
    if terminal_binding.get("stdin_binding_id") != relay_session.get("stdin_relay_id"):
        errors.append({"field": "stdin_relay_id", "reason": "stdin relay continuity absent"})
    if terminal_binding.get("stdout_binding_id") != relay_session.get("stdout_relay_id"):
        errors.append({"field": "stdout_relay_id", "reason": "stdout relay continuity absent"})
    if prior_output is not None:
        prior_id = prior_output.get("execution_relay_session", {}).get("execution_relay_session_id")
        if prior_id != relay_session.get("execution_relay_session_id"):
            errors.append({"field": "execution_relay_session_id", "reason": "relay identity changed"})
    for field in LINEAGE_FIELDS:
        if not isinstance(binding.get(field), str) or not binding[field].strip():
            errors.append({"field": field, "reason": "execution relay lineage missing"})
    return {"valid": not errors, "errors": errors}
