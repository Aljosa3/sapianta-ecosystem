"""Replay-safe execution gate evidence."""

from __future__ import annotations

from typing import Any


def execution_gate_evidence(
    *,
    request: dict[str, Any],
    response: dict[str, Any] | None = None,
    request_validation: dict[str, Any] | None = None,
    response_validation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = response or {}
    request_status = request_validation or {"valid": False}
    response_status = response_validation or {"valid": False}
    return {
        "execution_gate_id": request.get("execution_gate_id", ""),
        "connector_id": request.get("connector_id", ""),
        "provider_id": request.get("provider_id", ""),
        "envelope_id": request.get("envelope_id", ""),
        "invocation_id": request.get("invocation_id", ""),
        "transport_id": request.get("transport_id", ""),
        "replay_identity": request.get("replay_identity", ""),
        "workspace_path": request.get("workspace_path", ""),
        "timeout_seconds": request.get("timeout_seconds", 0),
        "execution_authorized": request.get("execution_authorized") is True,
        "approved_by": request.get("approved_by", ""),
        "request_valid": request_status.get("valid", False),
        "response_valid": response_status.get("valid", False),
        "execution_status": result.get("status", "BLOCKED"),
        "exit_code": result.get("exit_code"),
        "stdout_captured": isinstance(result.get("stdout", ""), str),
        "stderr_captured": isinstance(result.get("stderr", ""), str),
        "authorization_valid": request_status.get("authorization_valid", False),
        "workspace_boundary_valid": request_status.get("workspace_boundary_valid", False),
        "identity_continuity_valid": response_status.get("identity_continuity_valid", False),
        "prepared_artifact_is_execution_authority": False,
        "arbitrary_command_execution_present": False,
        "shell_execution_present": False,
        "network_execution_present": False,
        "routing_present": False,
        "retry_present": False,
        "fallback_present": False,
        "orchestration_present": False,
        "autonomous_execution_present": False,
        "background_execution_present": False,
        "concurrent_execution_present": False,
        "memory_mutation_present": False,
        "replay_safe": request_status.get("valid") is True and (not response or response_status.get("valid") is True),
    }


def validate_execution_gate_evidence(evidence: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(evidence, dict):
        return {"valid": False, "errors": [{"field": "execution_gate_evidence", "reason": "must be an object"}]}
    for field in (
        "execution_gate_id",
        "connector_id",
        "provider_id",
        "envelope_id",
        "invocation_id",
        "transport_id",
        "replay_identity",
        "workspace_path",
        "timeout_seconds",
        "execution_authorized",
        "request_valid",
        "execution_status",
        "authorization_valid",
        "workspace_boundary_valid",
        "replay_safe",
    ):
        if field not in evidence:
            errors.append({"field": field, "reason": "missing execution gate evidence field"})
    for field in (
        "prepared_artifact_is_execution_authority",
        "arbitrary_command_execution_present",
        "shell_execution_present",
        "network_execution_present",
        "routing_present",
        "retry_present",
        "fallback_present",
        "orchestration_present",
        "autonomous_execution_present",
        "background_execution_present",
        "concurrent_execution_present",
        "memory_mutation_present",
    ):
        if evidence.get(field) is not False:
            errors.append({"field": field, "reason": "execution gate evidence reports forbidden behavior"})
    return {"valid": not errors, "errors": errors}
