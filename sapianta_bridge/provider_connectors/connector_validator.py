"""Fail-closed provider connector validation."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.real_provider_transport.provider_transport_validator import (
    validate_provider_transport_request,
    validate_provider_transport_response,
)

from .connector_binding import validate_connector_binding
from .connector_identity import CONNECTOR_MODE_PREPARE_ONLY, CONNECTOR_TYPE_CODEX_CLI, validate_connector_identity
from .connector_response import CONNECTOR_RESPONSE_STATUSES


FORBIDDEN_REQUEST_FLAGS = (
    "connector_artifact_is_execution_authority",
    "provider_auto_selection_present",
    "routing_present",
    "retry_present",
    "fallback_present",
    "orchestration_present",
    "autonomous_execution_present",
    "shell_execution_present",
    "network_execution_present",
)

FORBIDDEN_RESPONSE_FLAGS = (
    "provider_response_is_governance_decision",
    "connector_response_is_execution_authority",
    "routing_present",
    "retry_present",
    "fallback_present",
    "orchestration_present",
    "autonomous_execution_present",
)


def _as_dict(value: Any) -> Any:
    return value.to_dict() if hasattr(value, "to_dict") else value


def _non_empty_string_errors(value: dict[str, Any], fields: tuple[str, ...], *, reason: str) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    for field in fields:
        if not isinstance(value.get(field), str) or not value.get(field, "").strip():
            errors.append({"field": field, "reason": reason})
    return errors


def validate_connector_request(request: Any) -> dict[str, Any]:
    value = _as_dict(request)
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "connector_request", "reason": "must be an object"}]}
    required = (
        "connector_id",
        "provider_id",
        "envelope_id",
        "invocation_id",
        "transport_id",
        "replay_identity",
        "provider_transport_request",
        "bounded_task_artifact_path",
        "expected_result_artifact_path",
        "connector_mode",
        "connector_binding",
    )
    for field in required:
        if field not in value:
            errors.append({"field": field, "reason": "missing connector request field"})
    errors.extend(
        _non_empty_string_errors(
            value,
            (
                "connector_id",
                "provider_id",
                "envelope_id",
                "invocation_id",
                "transport_id",
                "replay_identity",
                "bounded_task_artifact_path",
                "expected_result_artifact_path",
                "connector_mode",
            ),
            reason="connector request field must be non-empty",
        )
    )
    if value.get("connector_mode") != CONNECTOR_MODE_PREPARE_ONLY:
        errors.append({"field": "connector_mode", "reason": "connector request must remain PREPARE_ONLY"})
    transport_validation = validate_provider_transport_request(value.get("provider_transport_request"))
    binding_validation = validate_connector_binding(value.get("connector_binding"))
    identity_validation = validate_connector_identity(
        {
            "connector_id": value.get("connector_id", ""),
            "provider_id": value.get("provider_id", ""),
            "connector_type": CONNECTOR_TYPE_CODEX_CLI,
            "connector_mode": value.get("connector_mode", ""),
            "replay_identity": value.get("replay_identity", ""),
            "connector_is_provider_router": False,
            "connector_artifact_is_execution_authority": False,
            "autonomous_execution_present": False,
            "routing_present": False,
            "retry_present": False,
            "fallback_present": False,
            "shell_execution_present": False,
            "network_execution_present": False,
            "replay_safe": True,
        }
    )
    errors.extend(transport_validation["errors"])
    errors.extend(binding_validation["errors"])
    errors.extend(identity_validation["errors"])
    if transport_validation["valid"]:
        transport_request = value["provider_transport_request"]
        for field in ("transport_id", "provider_id", "envelope_id", "invocation_id", "replay_identity"):
            if value.get(field) != transport_request.get(field):
                errors.append({"field": field, "reason": "connector request/transport request mismatch"})
    if binding_validation["valid"]:
        binding = value["connector_binding"]
        binding_field_map = {
            "connector_id": "connector_id",
            "transport_id": "transport_id",
            "provider_id": "provider_id",
            "envelope_id": "envelope_id",
            "invocation_id": "invocation_id",
            "replay_identity": "replay_identity",
            "bounded_task_artifact_path": "task_artifact_path",
            "expected_result_artifact_path": "expected_result_artifact_path",
        }
        for request_field, binding_field in binding_field_map.items():
            if value.get(request_field) != binding.get(binding_field):
                errors.append({"field": request_field, "reason": "connector request/binding mismatch"})
    for field in FORBIDDEN_REQUEST_FLAGS:
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "connector request contains forbidden behavior"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "connector request must be replay-safe"})
    return {
        "valid": not errors,
        "errors": errors,
        "connector_binding_valid": binding_validation["valid"],
        "provider_transport_request_valid": transport_validation["valid"],
        "replay_safe": not errors,
    }


def validate_connector_response(response: Any, request: dict[str, Any] | None = None) -> dict[str, Any]:
    value = _as_dict(response)
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "connector_response", "reason": "must be an object"}]}
    required = (
        "connector_id",
        "provider_id",
        "envelope_id",
        "invocation_id",
        "transport_id",
        "replay_identity",
        "provider_transport_response",
        "result_artifact_path",
        "status",
    )
    for field in required:
        if field not in value:
            errors.append({"field": field, "reason": "missing connector response field"})
    errors.extend(
        _non_empty_string_errors(
            value,
            (
                "connector_id",
                "provider_id",
                "envelope_id",
                "invocation_id",
                "transport_id",
                "replay_identity",
                "result_artifact_path",
                "status",
            ),
            reason="connector response field must be non-empty",
        )
    )
    if value.get("status") not in CONNECTOR_RESPONSE_STATUSES:
        errors.append({"field": "status", "reason": "unsupported connector response status"})
    provider_transport_request = request.get("provider_transport_request") if request else None
    transport_response_validation = validate_provider_transport_response(
        value.get("provider_transport_response"),
        request=provider_transport_request,
    )
    errors.extend(transport_response_validation["errors"])
    if request is not None:
        for field in ("connector_id", "provider_id", "envelope_id", "invocation_id", "transport_id", "replay_identity"):
            if value.get(field) != request.get(field):
                errors.append({"field": field, "reason": "connector response/request mismatch"})
    if transport_response_validation["valid"]:
        transport_response = value["provider_transport_response"]
        for field in ("transport_id", "provider_id", "envelope_id", "replay_identity", "status"):
            if value.get(field) != transport_response.get(field):
                errors.append({"field": field, "reason": "connector response/transport response mismatch"})
    for field in FORBIDDEN_RESPONSE_FLAGS:
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "connector response contains forbidden behavior"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "connector response must be replay-safe"})
    return {
        "valid": not errors,
        "errors": errors,
        "provider_transport_response_valid": transport_response_validation["valid"],
        "identity_continuity_valid": not any("mismatch" in error["reason"] for error in errors),
        "replay_safe": not errors,
    }
