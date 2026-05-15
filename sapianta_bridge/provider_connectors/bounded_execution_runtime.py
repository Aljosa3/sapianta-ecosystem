"""Bounded local Codex execution runtime."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
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
from .bounded_runtime_state import (
    bounded_runtime_state_env,
    create_bounded_runtime_state,
    ensure_bounded_runtime_state_dirs,
    validate_bounded_runtime_state,
    validate_bounded_runtime_state_env,
)
from .codex_completion_classifier import classify_codex_completion
from .codex_process_termination import classify_codex_process_termination
from .codex_timeout_telemetry import codex_timeout_telemetry
from .execution_gate_request import EXECUTION_GATE_OPERATION_CODEX_CLI_RUN
from .execution_gate_validator import validate_execution_gate_request


GRACEFUL_TERMINATION_TIMEOUT_SECONDS = 2


def _coerce_process_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, str):
        return value
    return str(value)


def _terminate_process_safely(process: subprocess.Popen[str]) -> dict[str, Any]:
    if process.poll() is not None:
        return {
            "attempted": False,
            "succeeded": True,
            "forced_kill": False,
            "returncode": process.returncode,
            "stdout": "",
            "stderr": "",
        }
    process.terminate()
    try:
        stdout, stderr = process.communicate(timeout=GRACEFUL_TERMINATION_TIMEOUT_SECONDS)
        return {
            "attempted": True,
            "succeeded": True,
            "forced_kill": False,
            "returncode": process.returncode,
            "stdout": _coerce_process_text(stdout),
            "stderr": _coerce_process_text(stderr),
        }
    except subprocess.TimeoutExpired as exc:
        process.kill()
        stdout, stderr = process.communicate()
        return {
            "attempted": True,
            "succeeded": True,
            "forced_kill": True,
            "returncode": process.returncode,
            "stdout": _coerce_process_text(exc.stdout) + _coerce_process_text(stdout),
            "stderr": _coerce_process_text(exc.stderr) + _coerce_process_text(stderr),
        }


def validate_bounded_execution_runtime_request(
    *,
    gate_request: dict[str, Any],
    codex_executable: str = "codex",
    runtime_state_root: str | Path = "/tmp/sapianta_codex_runtime",
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
    runtime_state = create_bounded_runtime_state(
        provider_id=gate_request.get("provider_id", ""),
        invocation_id=gate_request.get("invocation_id", ""),
        replay_identity=gate_request.get("replay_identity", ""),
        runtime_state_root=runtime_state_root,
    ).to_dict()
    runtime_state_validation = validate_bounded_runtime_state(runtime_state)
    runtime_state_env = bounded_runtime_state_env(runtime_state)
    runtime_state_env_validation = validate_bounded_runtime_state_env(runtime_state_env, runtime_state)
    errors.extend(workspace_validation["errors"])
    errors.extend(timeout_validation["errors"])
    errors.extend(command_validation["errors"])
    errors.extend(runtime_state_validation["errors"])
    errors.extend(runtime_state_env_validation["errors"])
    return {
        "valid": not errors,
        "errors": errors,
        "gate_valid": gate_validation["valid"],
        "provider_identity_valid": gate_request.get("provider_id") == CODEX_PROVIDER_ID,
        "workspace_valid": workspace_validation["valid"],
        "timeout_valid": timeout_validation["valid"],
        "command_valid": command_validation["valid"],
        "runtime_state_valid": runtime_state_validation["valid"],
        "runtime_state_env_valid": runtime_state_env_validation["valid"],
        "command": command,
        "runtime_state": runtime_state,
        "runtime_state_env": runtime_state_env,
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
    runtime_state_root: str | Path = "/tmp/sapianta_codex_runtime",
) -> dict[str, Any]:
    runtime_validation = validate_bounded_execution_runtime_request(
        gate_request=gate_request,
        codex_executable=codex_executable,
        runtime_state_root=runtime_state_root,
    )
    if not runtime_validation["valid"]:
        classification = classify_codex_completion(
            stdout="",
            stderr="bounded Codex execution validation failed",
            exit_code=1,
            timed_out=False,
            duration_seconds=0,
        )
        capture = capture_completed_execution(
            stdout="",
            stderr="bounded Codex execution validation failed",
            exit_code=1,
            completion_state=classification["completion_state"],
            suspected_blocker=classification["suspected_blocker"],
        ).to_dict()
        timeout_telemetry = codex_timeout_telemetry(
            timeout_seconds=gate_request.get("timeout_seconds", 0) if isinstance(gate_request.get("timeout_seconds"), int) else 0,
            duration_seconds=0,
            timed_out=False,
            stdout="",
            stderr=capture["stderr"],
        )
        evidence = bounded_execution_evidence(
            gate_request=gate_request,
            runtime_validation=runtime_validation,
            capture=capture,
        )
        return {
            "bounded_execution_status": "BLOCKED",
            "runtime_validation": runtime_validation,
            "capture": capture,
            "completion_classification": classification,
            "timeout_telemetry": timeout_telemetry,
            "bounded_execution_evidence": evidence,
        }
    try:
        ensure_bounded_runtime_state_dirs(runtime_validation["runtime_state"])
        execution_env = dict(os.environ)
        execution_env.update(runtime_validation["runtime_state_env"])
        started = time.monotonic()
        process = subprocess.Popen(
            runtime_validation["command"],
            cwd=gate_request["workspace_path"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
            env=execution_env,
        )
        completed_stdout, completed_stderr = process.communicate(timeout=gate_request["timeout_seconds"])
        duration_seconds = int(time.monotonic() - started)
        classification = classify_codex_completion(
            stdout=completed_stdout,
            stderr=completed_stderr,
            exit_code=process.returncode if process.returncode is not None else 1,
            timed_out=False,
            duration_seconds=duration_seconds,
        )
        process_classification = classify_codex_process_termination(
            stdout=completed_stdout,
            stderr=completed_stderr,
            exit_code=process.returncode if process.returncode is not None else 1,
            timed_out=False,
            process_terminated=True,
            idle_window_seconds=0,
        )
        capture = capture_completed_execution(
            stdout=completed_stdout,
            stderr=completed_stderr,
            exit_code=process.returncode if process.returncode is not None else 1,
            duration_seconds=duration_seconds,
            completion_state=classification["completion_state"],
            process_state=process_classification["process_state"],
            suspected_blocker=classification["suspected_blocker"],
            completion_marker_detected=process_classification["completion_marker_detected"],
            bounded_result_captured=process_classification["bounded_result_available"],
        ).to_dict()
        status = "SUCCESS" if process.returncode == 0 else "FAILED"
    except subprocess.TimeoutExpired as exc:
        stdout = _coerce_process_text(exc.stdout)
        stderr = _coerce_process_text(exc.stderr)
        process_classification = classify_codex_process_termination(
            stdout=stdout,
            stderr=stderr,
            exit_code=124,
            timed_out=True,
            process_terminated=False,
            idle_window_seconds=gate_request["timeout_seconds"],
        )
        termination = _terminate_process_safely(process)
        if termination["stdout"]:
            stdout += termination["stdout"]
        if termination["stderr"]:
            stderr += termination["stderr"]
        if not stderr:
            stderr = "bounded codex execution timed out"
        classification = classify_codex_completion(
            stdout=stdout,
            stderr=stderr,
            exit_code=124,
            timed_out=True,
            duration_seconds=gate_request["timeout_seconds"],
        )
        capture = capture_timeout(
            stdout=stdout,
            stderr=stderr,
            duration_seconds=gate_request["timeout_seconds"],
            completion_state=classification["completion_state"],
            process_state=process_classification["process_state"],
            suspected_blocker=process_classification["suspected_blocker"],
            process_terminated=termination["succeeded"],
            completion_marker_detected=process_classification["completion_marker_detected"],
            bounded_result_captured=process_classification["bounded_result_available"],
            graceful_termination_attempted=termination["attempted"],
            graceful_termination_succeeded=termination["succeeded"],
        ).to_dict()
        status = "RESULT_CAPTURED_WITH_TERMINATION" if process_classification["bounded_result_available"] else "TIMEOUT"
    except OSError as exc:
        process_classification = classify_codex_process_termination(
            stdout="",
            stderr=f"bounded Codex execution failed: {exc.__class__.__name__}",
            exit_code=127,
            timed_out=False,
            process_terminated=True,
            idle_window_seconds=0,
        )
        classification = classify_codex_completion(
            stdout="",
            stderr=f"bounded Codex execution failed: {exc.__class__.__name__}",
            exit_code=127,
            timed_out=False,
            duration_seconds=0,
        )
        capture = capture_completed_execution(
            stdout="",
            stderr=f"bounded Codex execution failed: {exc.__class__.__name__}",
            exit_code=127,
            completion_state=classification["completion_state"],
            process_state=process_classification["process_state"],
            suspected_blocker=classification["suspected_blocker"],
        ).to_dict()
        status = "FAILED"
    timeout_telemetry = codex_timeout_telemetry(
        timeout_seconds=gate_request["timeout_seconds"],
        duration_seconds=capture["duration_seconds"],
        timed_out=capture["timed_out"],
        stdout=capture["stdout"],
        stderr=capture["stderr"],
    )
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
        "completion_classification": classification,
        "process_classification": process_classification,
        "timeout_telemetry": timeout_telemetry,
        "bounded_execution_evidence": evidence,
        "result_return_ready": status in ("SUCCESS", "FAILED", "TIMEOUT", "RESULT_CAPTURED_WITH_TERMINATION"),
    }
