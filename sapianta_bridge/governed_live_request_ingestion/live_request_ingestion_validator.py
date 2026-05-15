"""Fail-closed governed live request ingestion validation."""

from typing import Any

from .live_request_ingestion_session import validate_live_request_ingestion_session

LINEAGE_FIELDS = (
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
    "request_activation_id",
)


def validate_live_request_ingestion(*, ingestion_session: dict, binding: dict, gateway_output: dict, prior_output: dict | None = None) -> dict[str, Any]:
    errors = list(validate_live_request_ingestion_session(ingestion_session)["errors"])
    if gateway_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "serving_gateway", "reason": "gateway continuity invalid"})
    gateway_binding = gateway_output.get("serving_gateway_binding", {})
    if gateway_binding.get("serving_gateway_session_id") != ingestion_session.get("serving_gateway_session_id"):
        errors.append({"field": "serving_gateway_session_id", "reason": "gateway continuity mismatch"})
    if prior_output is not None:
        prior_id = prior_output.get("live_request_ingestion_session", {}).get("live_request_ingestion_session_id")
        if prior_id != ingestion_session.get("live_request_ingestion_session_id"):
            errors.append({"field": "live_request_ingestion_session_id", "reason": "ingestion identity changed"})
    for field in LINEAGE_FIELDS:
        if not isinstance(binding.get(field), str) or not binding[field].strip():
            errors.append({"field": field, "reason": "live ingestion lineage missing"})
    return {"valid": not errors, "errors": errors}
