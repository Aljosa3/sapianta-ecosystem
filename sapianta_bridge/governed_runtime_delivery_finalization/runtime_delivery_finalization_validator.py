"""Fail-closed governed runtime delivery finalization validation."""

from typing import Any

from .runtime_delivery_finalization_session import validate_runtime_delivery_finalization_session

LINEAGE_FIELDS = (
    "runtime_delivery_finalization_id",
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


def validate_runtime_delivery_finalization(*, finalization_session: dict, binding: dict, commit_output: dict, prior_output: dict | None = None) -> dict[str, Any]:
    errors = list(validate_runtime_delivery_finalization_session(finalization_session)["errors"])
    if commit_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "runtime_execution_commit", "reason": "execution commit continuity invalid"})
    commit_binding = commit_output.get("runtime_execution_commit_binding", {})
    if commit_binding.get("runtime_execution_commit_id") != finalization_session.get("runtime_execution_commit_id"):
        errors.append({"field": "runtime_execution_commit_id", "reason": "execution commit linkage mismatch"})
    if prior_output is not None:
        prior_id = prior_output.get("runtime_delivery_finalization_session", {}).get("runtime_delivery_finalization_id")
        if prior_id != finalization_session.get("runtime_delivery_finalization_id"):
            errors.append({"field": "runtime_delivery_finalization_id", "reason": "delivery finalization identity changed"})
    for field in LINEAGE_FIELDS:
        if not isinstance(binding.get(field), str) or not binding[field].strip():
            errors.append({"field": field, "reason": "runtime delivery finalization lineage missing"})
    if binding.get("activation_authorized") is not True:
        errors.append({"field": "activation_authorized", "reason": "activation authorization absent"})
    if binding.get("approved_by") != "human":
        errors.append({"field": "approved_by", "reason": "activation approval must remain human"})
    return {"valid": not errors, "errors": errors}
