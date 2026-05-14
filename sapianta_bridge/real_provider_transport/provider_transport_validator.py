"""Fail-closed provider transport validation."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.envelopes.envelope_validator import validate_execution_envelope

from .provider_transport_binding import validate_provider_transport_binding
from .provider_transport_response import TRANSPORT_RESPONSE_STATUSES


def validate_provider_transport_request(request: Any) -> dict[str, Any]:
    value = request.to_dict() if hasattr(request, "to_dict") else request
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "transport_request", "reason": "must be an object"}]}
    required = (
        "transport_id",
        "provider_id",
        "envelope_id",
        "invocation_id",
        "replay_identity",
        "bounded_task_payload",
        "authority_scope",
        "workspace_scope",
        "validation_requirements",
        "transport_binding",
    )
    for field in required:
        if field not in value:
            errors.append({"field": field, "reason": "missing provider transport request field"})
    for field in ("transport_id", "provider_id", "envelope_id", "invocation_id", "replay_identity"):
        if field in value and (not isinstance(value[field], str) or not value[field].strip()):
            errors.append({"field": field, "reason": "transport request field must be non-empty"})
    if not isinstance(value.get("bounded_task_payload"), dict):
        errors.append({"field": "bounded_task_payload", "reason": "bounded task payload must be an object"})
    if not isinstance(value.get("authority_scope"), list) or not value.get("authority_scope"):
        errors.append({"field": "authority_scope", "reason": "authority scope must be a non-empty list"})
    if not isinstance(value.get("workspace_scope"), dict) or not value.get("workspace_scope"):
        errors.append({"field": "workspace_scope", "reason": "workspace scope must be an object"})
    if not isinstance(value.get("validation_requirements"), list) or not value.get("validation_requirements"):
        errors.append({"field": "validation_requirements", "reason": "validation requirements must be non-empty"})
    binding_validation = validate_provider_transport_binding(value.get("transport_binding"))
    errors.extend(binding_validation["errors"])
    if binding_validation["valid"]:
        binding = value["transport_binding"]
        for field in ("transport_id", "provider_id", "envelope_id", "invocation_id", "replay_identity"):
            if value.get(field) != binding.get(field):
                errors.append({"field": field, "reason": "transport request/binding mismatch"})
    for field in (
        "transport_artifact_is_execution_authority",
        "routing_present",
        "retry_present",
        "fallback_present",
        "real_external_api_call_present",
        "shell_execution_present",
    ):
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "provider transport request contains forbidden behavior"})
    return {
        "valid": not errors,
        "errors": errors,
        "transport_binding_valid": binding_validation["valid"],
        "routing_present": False,
        "retry_present": False,
        "fallback_present": False,
        "replay_safe": not errors,
    }


def validate_provider_transport_response(response: Any, request: dict[str, Any] | None = None) -> dict[str, Any]:
    value = response.to_dict() if hasattr(response, "to_dict") else response
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "transport_response", "reason": "must be an object"}]}
    required = ("transport_id", "provider_id", "envelope_id", "status", "result_payload", "evidence_references", "replay_identity")
    for field in required:
        if field not in value:
            errors.append({"field": field, "reason": "missing provider transport response field"})
    if value.get("status") not in TRANSPORT_RESPONSE_STATUSES:
        errors.append({"field": "status", "reason": "unsupported provider transport response status"})
    if not isinstance(value.get("result_payload"), dict):
        errors.append({"field": "result_payload", "reason": "result payload must be an object"})
    if not isinstance(value.get("evidence_references"), dict) or not value.get("evidence_references"):
        errors.append({"field": "evidence_references", "reason": "evidence references must be present"})
    if request is not None:
        for field in ("transport_id", "provider_id", "envelope_id", "replay_identity"):
            if value.get(field) != request.get(field):
                errors.append({"field": field, "reason": "provider transport response/request mismatch"})
    for field in ("provider_response_is_governance_decision", "routing_present", "retry_present", "fallback_present"):
        if value.get(field) is not False:
            errors.append({"field": field, "reason": "provider transport response contains forbidden behavior"})
    return {
        "valid": not errors,
        "errors": errors,
        "identity_continuity_valid": not any("mismatch" in error["reason"] for error in errors),
        "routing_present": False,
        "retry_present": False,
        "fallback_present": False,
        "replay_safe": not errors,
    }


def validate_envelope_for_transport(envelope: dict[str, Any]) -> dict[str, Any]:
    validation = validate_execution_envelope(envelope)
    return {
        "valid": validation["valid"],
        "errors": validation["errors"],
        "envelope_valid": validation["valid"],
        "provider_bound": validation.get("provider_bound", False),
        "replay_binding_valid": validation.get("replay_binding_valid", False),
    }
