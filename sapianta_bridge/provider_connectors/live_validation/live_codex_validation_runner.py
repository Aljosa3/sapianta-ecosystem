"""Live bounded Codex execution validation runner."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sapianta_bridge.provider_connectors.bounded_execution_runtime import execute_bounded_codex

from .live_codex_validation_case import VALIDATION_NAME, create_live_codex_validation_case, detect_codex_cli
from .live_codex_validation_evidence import live_codex_validation_evidence, validate_live_codex_validation_evidence


def run_live_codex_validation(
    *,
    workspace_path: str | Path,
    codex_executable: str | None = None,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    detected = bool(codex_executable or detect_codex_cli())
    case = create_live_codex_validation_case(
        workspace_path=workspace_path,
        codex_executable=codex_executable,
        timeout_seconds=timeout_seconds,
    )
    if isinstance(case, dict) and case.get("status") == "BLOCKED":
        evidence = live_codex_validation_evidence(
            status="BLOCKED",
            codex_cli_detected=False,
            case=None,
            blocked_reason=case["blocked_reason"],
        )
        return {
            "validation_name": VALIDATION_NAME,
            "status": "BLOCKED",
            "blocked_reason": case["blocked_reason"],
            "case": case,
            "bounded_execution_result": {},
            "evidence": evidence,
            "evidence_validation": validate_live_codex_validation_evidence(evidence),
        }
    case_dict = case.to_dict()
    execution = execute_bounded_codex(
        gate_request=case_dict["execution_gate_request"],
        codex_executable=case_dict["codex_executable"],
    )
    if execution["bounded_execution_status"] == "SUCCESS":
        status = "PASSED"
        blocked_reason = ""
    elif execution["bounded_execution_status"] == "BLOCKED":
        status = "BLOCKED"
        blocked_reason = "bounded Codex runtime validation blocked execution"
    else:
        status = "BLOCKED"
        blocked_reason = f"live Codex execution did not complete successfully: {execution['bounded_execution_status']}"
    evidence = live_codex_validation_evidence(
        status=status,
        codex_cli_detected=detected,
        case=case_dict,
        bounded_execution_result=execution,
        blocked_reason=blocked_reason,
    )
    return {
        "validation_name": VALIDATION_NAME,
        "status": status,
        "blocked_reason": blocked_reason,
        "case": case_dict,
        "bounded_execution_result": execution,
        "evidence": evidence,
        "evidence_validation": validate_live_codex_validation_evidence(evidence),
    }
