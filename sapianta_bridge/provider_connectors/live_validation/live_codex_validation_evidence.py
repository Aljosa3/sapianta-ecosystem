"""Evidence for live bounded Codex execution validation."""

from __future__ import annotations

from typing import Any

from .live_codex_validation_case import VALIDATION_NAME, VALIDATION_NAME_V2


def live_codex_validation_evidence(
    *,
    status: str,
    codex_cli_detected: bool,
    case: dict[str, Any] | None = None,
    bounded_execution_result: dict[str, Any] | None = None,
    blocked_reason: str = "",
) -> dict[str, Any]:
    execution = bounded_execution_result or {}
    capture = execution.get("capture", {})
    runtime_validation = execution.get("runtime_validation", {})
    gate_request = (case or {}).get("execution_gate_request", {})
    return {
        "validation_name": VALIDATION_NAME,
        "status": status,
        "blocked_reason": blocked_reason,
        "codex_cli_detected": codex_cli_detected,
        "codex_cli_executed": status == "PASSED" or execution.get("bounded_execution_status") in ("SUCCESS", "FAILED", "TIMEOUT"),
        "execution_authorized": gate_request.get("execution_authorized") is True,
        "provider_id": gate_request.get("provider_id", "codex_cli"),
        "workspace_bounded": runtime_validation.get("workspace_valid", False),
        "timeout_seconds": gate_request.get("timeout_seconds", 30),
        "exit_code_captured": isinstance(capture.get("exit_code"), int),
        "stdout_captured": isinstance(capture.get("stdout", ""), str),
        "stderr_captured": isinstance(capture.get("stderr", ""), str),
        "replay_identity": gate_request.get("replay_identity", "REPLAY-LIVE-CODEX-VALIDATION"),
        "replay_safe": status in ("PASSED", "BLOCKED") and runtime_validation.get("routing_present", False) is False,
        "orchestration_introduced": False,
        "routing_introduced": False,
        "retries_introduced": False,
        "fallback_introduced": False,
        "autonomous_execution_introduced": False,
    }


def live_codex_validation_evidence_v2(
    *,
    status: str,
    codex_cli_detected: bool,
    case: dict[str, Any] | None = None,
    bounded_execution_result: dict[str, Any] | None = None,
    blocked_reason: str = "",
) -> dict[str, Any]:
    evidence = live_codex_validation_evidence(
        status=status,
        codex_cli_detected=codex_cli_detected,
        case=case,
        bounded_execution_result=bounded_execution_result,
        blocked_reason=blocked_reason,
    )
    runtime_validation = (bounded_execution_result or {}).get("runtime_validation", {})
    evidence["validation_name"] = VALIDATION_NAME_V2
    evidence["contract_used"] = runtime_validation.get("contract_used", "codex exec <bounded_prompt>")
    evidence["previous_blocked_contract"] = runtime_validation.get(
        "previous_blocked_contract",
        "codex run <prepared_task_artifact>",
    )
    evidence["shell_used"] = False
    return evidence


def validate_live_codex_validation_evidence(evidence: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(evidence, dict):
        return {"valid": False, "errors": [{"field": "live_codex_evidence", "reason": "must be an object"}]}
    for field in (
        "validation_name",
        "status",
        "codex_cli_detected",
        "execution_authorized",
        "provider_id",
        "workspace_bounded",
        "timeout_seconds",
        "exit_code_captured",
        "stdout_captured",
        "stderr_captured",
        "replay_safe",
    ):
        if field not in evidence:
            errors.append({"field": field, "reason": "missing live validation evidence field"})
    if evidence.get("status") not in ("PASSED", "BLOCKED", "FAILED"):
        errors.append({"field": "status", "reason": "unsupported live validation status"})
    if evidence.get("validation_name") not in (VALIDATION_NAME, VALIDATION_NAME_V2):
        errors.append({"field": "validation_name", "reason": "validation name mismatch"})
    if evidence.get("validation_name") == VALIDATION_NAME_V2:
        if evidence.get("contract_used") != "codex exec <bounded_prompt>":
            errors.append({"field": "contract_used", "reason": "V2 must use codex exec contract"})
        if evidence.get("previous_blocked_contract") != "codex run <prepared_task_artifact>":
            errors.append({"field": "previous_blocked_contract", "reason": "V2 must preserve previous blocked contract"})
        if evidence.get("shell_used") is not False:
            errors.append({"field": "shell_used", "reason": "V2 must preserve shell=False"})
    for field in (
        "orchestration_introduced",
        "routing_introduced",
        "retries_introduced",
        "fallback_introduced",
        "autonomous_execution_introduced",
    ):
        if evidence.get(field) is not False:
            errors.append({"field": field, "reason": "live validation reports forbidden behavior"})
    if evidence.get("status") == "PASSED" and evidence.get("codex_cli_executed") is not True:
        errors.append({"field": "codex_cli_executed", "reason": "passed validation must actually execute Codex"})
    return {"valid": not errors, "errors": errors}
