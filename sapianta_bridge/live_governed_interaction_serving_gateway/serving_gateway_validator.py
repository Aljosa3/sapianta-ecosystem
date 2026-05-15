"""Fail-closed serving gateway validation."""

from typing import Any

from .serving_gateway_session import validate_serving_gateway_session

LINEAGE_FIELDS = (
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
    "ingress_id",
    "egress_id",
)


def validate_serving_gateway(*, gateway_session: dict, binding: dict, terminal_output: dict, prior_output: dict | None = None) -> dict[str, Any]:
    errors = list(validate_serving_gateway_session(gateway_session)["errors"])
    if terminal_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "terminal_attachment", "reason": "terminal attachment continuity invalid"})
    terminal_binding = terminal_output.get("terminal_attachment_binding", {})
    if terminal_binding.get("runtime_serving_session_id") != gateway_session.get("runtime_serving_session_id"):
        errors.append({"field": "runtime_serving_session_id", "reason": "serving continuity invalid"})
    if terminal_binding.get("terminal_attachment_session_id") != gateway_session.get("terminal_attachment_session_id"):
        errors.append({"field": "terminal_attachment_session_id", "reason": "terminal linkage invalid"})
    if prior_output is not None:
        prior_id = prior_output.get("serving_gateway_session", {}).get("serving_gateway_session_id")
        if prior_id != gateway_session.get("serving_gateway_session_id"):
            errors.append({"field": "serving_gateway_session_id", "reason": "gateway identity changed"})
    for field in LINEAGE_FIELDS:
        if not isinstance(binding.get(field), str) or not binding[field].strip():
            errors.append({"field": field, "reason": "serving gateway lineage missing"})
    return {"valid": not errors, "errors": errors}
