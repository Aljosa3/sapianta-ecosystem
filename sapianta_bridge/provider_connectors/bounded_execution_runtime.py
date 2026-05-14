"""Bounded local Codex execution runtime."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from .bounded_codex_execution import (
    CODEX_EXEC_CONTRACT,
    CODEX_PROVIDER_ID,
    PREVIOUS_BLOCKED_CONTRACT,
    bounded_codex_command,
    bounded_prompt_from_task_artifact,
    validate_bounded_codex_command,
)
from .bounded_execution_capture import (
    capture_completed_execution,
    capture_timeout,
    validate_bounded_execution_capture,
)
from .bounded_execution_evidence import bounded_execution_evidence
from .bounded_execution_timeout import validate_bounded_execution_timeout
from .bounded_execution_workspace import validate_bounded_execution_workspace
from .execution_gate_request import EXECUTION_GATE_OPERATION_CODEX_CLI_RUN
from .execution_gate_validator import validate_execution_gate_request


def validate_bounded_execution_runtime_request(
    *,
    gate_request: dict[str, Any],
    codex_executable: str = "codex",
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    gate_validation = validate_execution_gate_request(gate_request)
    errors.extend(gate_validation["errors"])
    if gate_request.get("provider_id") != CODEX_PROVIDER_ID:
        errors.append({"field": "provider_id", "reason": "bounded real Codex execution requires provider_id codex_cli"})
    if gate_request.get("operation") != EXECUTION_GATE_OPERATION_CODEX_CLI_RUN:
        errors.append({"field": "operation", "reason": "bounded real Codex execution requires CODEX_CLI_RUN"})
    task_artifact_path = ""
    if isinstance(gate_request.get("connector_request"), dict):
        task_artifact_path = gate_request["connector_request"].get("bounded_task_artifact_path", "")
    workspace_validation = validate_bounded_execution_workspace(
        workspace_path=gate_request.get("workspace_path", ""),
        task_artifact_path=task_artifact_path,
    )
    timeout_validation = validate_bounded_execution_timeout(gate_request.get("timeout_seconds"))
    bounded_prompt = ""
    if Path(task_artifact_path).exists():
        try:
            task_artifact = json.loads(Path(task_artifact_path).read_text(encoding="utf-8"))
            bounded_prompt = bounded_prompt_from_task_artifact(task_artifact)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append({"field": "bounded_task_artifact_path", "reason": f"prepared task artifact unreadable: {exc.__class__.__name__}"})
    command = bounded_codex_command(codex_executable=codex_executable, bounded_prompt=bounded_prompt)
    command_validation = validate_bounded_codex_command(codex_executable=codex_executable, command=command)
    errors.extend(workspace_validation["errors"])
    errors.extend(timeout_validation["errors"])
    errors.extend(command_validation["errors"])
    return {
        "valid": not errors,
        "errors": errors,
        "gate_valid": gate_validation["valid"],
        "provider_identity_valid": gate_request.get("provider_id") == CODEX_PROVIDER_ID,
        "workspace_valid": workspace_validation["valid"],
        "timeout_valid": timeout_validation["valid"],
        "command_valid": command_validation["valid"],
        "command": command,
        "bounded_prompt_sha256": hashlib.sha256(bounded_prompt.encode("utf-8")).hexdigest() if bounded_prompt else "",
        "contract_used": CODEX_EXEC_CONTRACT,
        "previous_blocked_contract": PREVIOUS_BLOCKED_CONTRACT,
        "shell_execution_present": False,
        "arbitrary_command_execution_present": False,
        "network_execution_present": False,
        "routing_present": False,
        "retry_present": False,
        "fallback_present": False,
        "orchestration_present": False,
        "autonomous_execution_present": False,
        "replay_safe": not errors,
    }


def execute_bounded_codex(
    *,
    gate_request: dict[str, Any],
    codex_executable: str = "codex",
) -> dict[str, Any]:
    runtime_validation = validate_bounded_execution_runtime_request(
        gate_request=gate_request,
        codex_executable=codex_executable,
    )
    if not runtime_validation["valid"]:
        capture = capture_completed_execution(
            stdout="",
            stderr="bounded Codex execution validation failed",
            exit_code=1,
        ).to_dict()
        evidence = bounded_execution_evidence(
            gate_request=gate_request,
            runtime_validation=runtime_validation,
            capture=capture,
        )
        return {
            "bounded_execution_status": "BLOCKED",
            "runtime_validation": runtime_validation,
            "capture": capture,
            "bounded_execution_evidence": evidence,
        }
    try:
        completed = subprocess.run(
            runtime_validation["command"],
            cwd=gate_request["workspace_path"],
            capture_output=True,
            text=True,
            timeout=gate_request["timeout_seconds"],
            shell=False,
            check=False,
        )
        capture = capture_completed_execution(
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
        ).to_dict()
        status = "SUCCESS" if completed.returncode == 0 else "FAILED"
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else "bounded codex execution timed out"
        capture = capture_timeout(stdout=stdout, stderr=stderr).to_dict()
        status = "TIMEOUT"
    except OSError as exc:
        capture = capture_completed_execution(
            stdout="",
            stderr=f"bounded Codex execution failed: {exc.__class__.__name__}",
            exit_code=127,
        ).to_dict()
        status = "FAILED"
    capture_validation = validate_bounded_execution_capture(capture)
    evidence = bounded_execution_evidence(
        gate_request=gate_request,
        runtime_validation=runtime_validation,
        capture=capture,
    )
    return {
        "bounded_execution_status": status,
        "runtime_validation": runtime_validation,
        "capture": capture,
        "capture_validation": capture_validation,
        "bounded_execution_evidence": evidence,
        "result_return_ready": status in ("SUCCESS", "FAILED", "TIMEOUT"),
    }
