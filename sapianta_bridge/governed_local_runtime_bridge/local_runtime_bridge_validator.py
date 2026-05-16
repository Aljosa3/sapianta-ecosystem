"""Fail-closed governed local runtime bridge validation."""

from typing import Any

from .local_runtime_bridge_session import validate_local_runtime_bridge_session

LINEAGE_FIELDS = (
    "local_runtime_bridge_session_id",
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
    "runtime_transport_bridge_id",
)


def validate_local_runtime_bridge(*, bridge_session: dict, binding: dict, relay_output: dict, prior_output: dict | None = None) -> dict[str, Any]:
    errors = list(validate_local_runtime_bridge_session(bridge_session)["errors"])
    if relay_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "execution_relay", "reason": "relay continuity invalid"})
    relay_binding = relay_output.get("execution_relay_binding", {})
    if relay_binding.get("execution_relay_session_id") != bridge_session.get("execution_relay_session_id"):
        errors.append({"field": "execution_relay_session_id", "reason": "relay linkage mismatch"})
    if prior_output is not None:
        prior_id = prior_output.get("local_runtime_bridge_session", {}).get("local_runtime_bridge_session_id")
        if prior_id != bridge_session.get("local_runtime_bridge_session_id"):
            errors.append({"field": "local_runtime_bridge_session_id", "reason": "bridge identity changed"})
    for field in LINEAGE_FIELDS:
        if not isinstance(binding.get(field), str) or not binding[field].strip():
            errors.append({"field": field, "reason": "local runtime bridge lineage missing"})
    return {"valid": not errors, "errors": errors}
