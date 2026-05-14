"""Replay-safe evidence for bounded Codex execution."""

from __future__ import annotations

from typing import Any


def bounded_execution_evidence(
    *,
    gate_request: dict[str, Any],
    runtime_validation: dict[str, Any],
    capture: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = capture or {}
    return {
        "execution_name": "FIRST_BOUNDED_REAL_CODEX_EXECUTION_V1",
        "execution_gate_id": gate_request.get("execution_gate_id", ""),
        "connector_id": gate_request.get("connector_id", ""),
        "provider_id": gate_request.get("provider_id", ""),
        "envelope_id": gate_request.get("envelope_id", ""),
        "invocation_id": gate_request.get("invocation_id", ""),
        "transport_id": gate_request.get("transport_id", ""),
        "replay_identity": gate_request.get("replay_identity", ""),
        "workspace_path": gate_request.get("workspace_path", ""),
        "timeout_seconds": gate_request.get("timeout_seconds", 0),
        "execution_authorized": gate_request.get("execution_authorized") is True,
        "runtime_valid": runtime_validation.get("valid", False),
        "stdout_captured": isinstance(result.get("stdout", ""), str),
        "stderr_captured": isinstance(result.get("stderr", ""), str),
        "exit_code": result.get("exit_code"),
        "timed_out": result.get("timed_out", False),
        "capture_immutable": result.get("immutable", False),
        "provider_identity_preserved": runtime_validation.get("provider_identity_valid", False),
        "workspace_bounded": runtime_validation.get("workspace_valid", False),
        "timeout_bounded": runtime_validation.get("timeout_valid", False),
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
        "replay_safe": runtime_validation.get("valid", False) and (not result or result.get("replay_safe") is True),
    }


def validate_bounded_execution_evidence(evidence: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(evidence, dict):
        return {"valid": False, "errors": [{"field": "bounded_execution_evidence", "reason": "must be an object"}]}
    for field in (
        "execution_name",
        "execution_gate_id",
        "provider_id",
        "envelope_id",
        "invocation_id",
        "replay_identity",
        "execution_authorized",
        "runtime_valid",
        "stdout_captured",
        "stderr_captured",
        "provider_identity_preserved",
        "workspace_bounded",
        "timeout_bounded",
        "replay_safe",
    ):
        if field not in evidence:
            errors.append({"field": field, "reason": "missing bounded execution evidence field"})
    for field in (
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
            errors.append({"field": field, "reason": "bounded execution evidence reports forbidden behavior"})
    return {"valid": not errors, "errors": errors}
