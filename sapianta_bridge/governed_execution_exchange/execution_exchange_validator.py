"""Fail-closed governed execution exchange validation."""

from typing import Any

from .execution_exchange_session import validate_execution_exchange_session

LINEAGE_FIELDS = (
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
)


def validate_execution_exchange(*, exchange_session: dict, binding: dict, ingestion_output: dict, prior_output: dict | None = None) -> dict[str, Any]:
    errors = list(validate_execution_exchange_session(exchange_session)["errors"])
    if ingestion_output.get("validation", {}).get("valid") is not True:
        errors.append({"field": "live_request_ingestion", "reason": "exchange continuity invalid"})
    ingestion_binding = ingestion_output.get("live_request_ingestion_binding", {})
    if ingestion_binding.get("live_request_ingestion_session_id") != exchange_session.get("live_request_ingestion_session_id"):
        errors.append({"field": "live_request_ingestion_session_id", "reason": "ingestion continuity mismatch"})
    if prior_output is not None:
        prior_id = prior_output.get("execution_exchange_session", {}).get("execution_exchange_session_id")
        if prior_id != exchange_session.get("execution_exchange_session_id"):
            errors.append({"field": "execution_exchange_session_id", "reason": "exchange identity changed"})
    for field in LINEAGE_FIELDS:
        if not isinstance(binding.get(field), str) or not binding[field].strip():
            errors.append({"field": field, "reason": "execution exchange lineage missing"})
    return {"valid": not errors, "errors": errors}
