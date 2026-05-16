"""Fail-closed governed runtime execution commit validation."""

from typing import Any

from .runtime_execution_commit_session import validate_runtime_execution_commit_session

LINEAGE_FIELDS = (
    "runtime_execution_commit_id",
    "runtime_activation_gate_id",
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


def validate_runtime_execution_commit(*, commit_session: dict, binding: dict, activation_output: dict, prior_output: dict | None = None) -> dict[str, Any]:
    errors = list(validate_runtime_execution_commit_session(commit_session)["errors"])
    if activation_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "runtime_activation_gate", "reason": "activation gate continuity invalid"})
    activation_binding = activation_output.get("runtime_activation_gate_binding", {})
    if activation_binding.get("runtime_activation_gate_id") != commit_session.get("runtime_activation_gate_id"):
        errors.append({"field": "runtime_activation_gate_id", "reason": "activation linkage mismatch"})
    if prior_output is not None:
        prior_id = prior_output.get("runtime_execution_commit_session", {}).get("runtime_execution_commit_id")
        if prior_id != commit_session.get("runtime_execution_commit_id"):
            errors.append({"field": "runtime_execution_commit_id", "reason": "execution commit identity changed"})
    for field in LINEAGE_FIELDS:
        if not isinstance(binding.get(field), str) or not binding[field].strip():
            errors.append({"field": field, "reason": "runtime execution commit lineage missing"})
    if binding.get("activation_authorized") is not True:
        errors.append({"field": "activation_authorized", "reason": "activation authorization absent"})
    if binding.get("approved_by") != "human":
        errors.append({"field": "approved_by", "reason": "activation approval must remain human"})
    return {"valid": not errors, "errors": errors}
