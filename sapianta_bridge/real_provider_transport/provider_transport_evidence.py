"""Replay-safe provider transport evidence."""

from __future__ import annotations

from typing import Any


def provider_transport_evidence(
    *,
    request: dict[str, Any],
    response: dict[str, Any],
    request_validation: dict[str, Any],
    response_validation: dict[str, Any],
    task_artifact_path: str = "",
    result_artifact_path: str = "",
) -> dict[str, Any]:
    return {
        "transport_id": request.get("transport_id", ""),
        "provider_id": request.get("provider_id", ""),
        "envelope_id": request.get("envelope_id", ""),
        "invocation_id": request.get("invocation_id", ""),
        "replay_identity": request.get("replay_identity", ""),
        "provider_transport_request_valid": request_validation.get("valid", False),
        "provider_transport_response_valid": response_validation.get("valid", False),
        "task_artifact_path": task_artifact_path,
        "result_artifact_path": result_artifact_path,
        "identity_continuity_valid": response_validation.get("identity_continuity_valid", False),
        "local_file_transport_used": True,
        "real_external_api_call_present": False,
        "shell_execution_present": False,
        "routing_present": False,
        "retry_present": False,
        "fallback_present": False,
        "orchestration_present": False,
        "autonomous_execution_present": False,
        "replay_safe": request_validation.get("valid") is True and response_validation.get("valid") is True,
    }


def validate_provider_transport_evidence(evidence: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(evidence, dict):
        return {"valid": False, "errors": [{"field": "transport_evidence", "reason": "must be an object"}]}
    for field in (
        "transport_id",
        "provider_id",
        "envelope_id",
        "invocation_id",
        "replay_identity",
        "provider_transport_request_valid",
        "provider_transport_response_valid",
        "identity_continuity_valid",
        "replay_safe",
    ):
        if field not in evidence:
            errors.append({"field": field, "reason": "missing provider transport evidence field"})
    for field in (
        "real_external_api_call_present",
        "shell_execution_present",
        "routing_present",
        "retry_present",
        "fallback_present",
        "orchestration_present",
        "autonomous_execution_present",
    ):
        if evidence.get(field) is not False:
            errors.append({"field": field, "reason": "provider transport evidence reports forbidden behavior"})
    return {"valid": not errors, "errors": errors}
