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
        "runtime_state": runtime_validation.get("runtime_state", {}),
        "runtime_state_valid": runtime_validation.get("runtime_state_valid", False),
        "runtime_state_env_valid": runtime_validation.get("runtime_state_env_valid", False),
        "runtime_state_root": runtime_validation.get("runtime_state", {}).get("runtime_state_root", ""),
        "runtime_state_dir": runtime_validation.get("runtime_state", {}).get("runtime_state_dir", ""),
        "contract_used": runtime_validation.get("contract_used", ""),
        "previous_blocked_contract": runtime_validation.get("previous_blocked_contract", ""),
        "execution_authorized": gate_request.get("execution_authorized") is True,
        "runtime_valid": runtime_validation.get("valid", False),
        "stdout_captured": isinstance(result.get("stdout", ""), str),
        "stderr_captured": isinstance(result.get("stderr", ""), str),
        "exit_code": result.get("exit_code"),
        "timed_out": result.get("timed_out", False),
        "completion_state": result.get("completion_state", "UNKNOWN"),
        "process_state": result.get("process_state", "UNKNOWN"),
        "timeout_duration": result.get("duration_seconds", 0),
        "stdout_sample": result.get("stdout_sample", ""),
        "stderr_sample": result.get("stderr_sample", ""),
        "process_terminated": result.get("process_terminated", False),
        "completion_marker_detected": result.get("completion_marker_detected", False),
        "bounded_result_captured": result.get("bounded_result_captured", False),
        "graceful_termination_attempted": result.get("graceful_termination_attempted", False),
        "graceful_termination_succeeded": result.get("graceful_termination_succeeded", False),
        "suspected_blocker": result.get("suspected_blocker", ""),
        "capture_immutable": result.get("immutable", False),
        "provider_identity_preserved": runtime_validation.get("provider_identity_valid", False),
        "workspace_bounded": runtime_validation.get("workspace_valid", False),
        "timeout_bounded": runtime_validation.get("timeout_valid", False),
        "shell_used": False,
        "home_directory_mutation_allowed": False,
        "repo_root_state_allowed": False,
        "global_state_mutation_allowed": False,
        "arbitrary_env_mutation_allowed": False,
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
        "completion_state",
        "process_state",
        "process_terminated",
        "completion_marker_detected",
        "bounded_result_captured",
        "graceful_termination_attempted",
        "graceful_termination_succeeded",
        "runtime_state_valid",
        "runtime_state_env_valid",
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
        "home_directory_mutation_allowed",
        "repo_root_state_allowed",
        "global_state_mutation_allowed",
        "arbitrary_env_mutation_allowed",
    ):
        if evidence.get(field) is not False:
            errors.append({"field": field, "reason": "bounded execution evidence reports forbidden behavior"})
    return {"valid": not errors, "errors": errors}
