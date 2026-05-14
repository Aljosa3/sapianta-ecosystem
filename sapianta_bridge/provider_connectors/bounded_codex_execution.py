"""Whitelisted Codex CLI execution command model."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sapianta_bridge.real_provider_transport.provider_transport_binding import stable_hash


CODEX_PROVIDER_ID = "codex_cli"
CODEX_EXECUTABLE_NAME = "codex"
CODEX_EXEC_CONTRACT = "codex exec <bounded_prompt>"
PREVIOUS_BLOCKED_CONTRACT = "codex run <prepared_task_artifact>"


def bounded_prompt_from_task_artifact(task_artifact: dict[str, Any]) -> str:
    provider_id = task_artifact.get("provider_id", "")
    envelope_id = task_artifact.get("envelope_id", "")
    invocation_id = task_artifact.get("invocation_id", "")
    transport_id = task_artifact.get("transport_id", "")
    replay_identity = task_artifact.get("replay_identity", "")
    artifact_hash = stable_hash(task_artifact)
    return (
        "SAPIANTA bounded live validation task. "
        "Read this prompt and return exactly one deterministic line ending with AIGOL_TASK_COMPLETE: "
        f"SAPIANTA_CODEX_VALIDATION_OK provider_id={provider_id} "
        f"envelope_id={envelope_id} invocation_id={invocation_id} "
        f"transport_id={transport_id} replay_identity={replay_identity} "
        f"artifact_sha256={artifact_hash} AIGOL_TASK_COMPLETE. "
        "Do not modify files. Do not run commands. Do not access network intentionally."
    )


def bounded_codex_command(*, codex_executable: str, bounded_prompt: str) -> tuple[str, str, str]:
    return (codex_executable, "exec", bounded_prompt)


def validate_bounded_codex_command(*, codex_executable: str, command: tuple[str, ...]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(codex_executable, str) or not codex_executable.strip():
        errors.append({"field": "codex_executable", "reason": "codex executable must be explicit"})
    elif Path(codex_executable).name != CODEX_EXECUTABLE_NAME:
        errors.append({"field": "codex_executable", "reason": "only codex executable is allowed"})
    if not isinstance(command, tuple) or len(command) != 3:
        errors.append({"field": "command", "reason": "command must be the fixed codex exec prompt form"})
    elif command[0] != codex_executable or command[1] != "exec" or not isinstance(command[2], str) or not command[2]:
        errors.append({"field": "command", "reason": "command must be codex exec <bounded_prompt>"})
    for part in command if isinstance(command, tuple) else ():
        if not isinstance(part, str) or "\x00" in part:
            errors.append({"field": "command", "reason": "command parts must be safe strings"})
    if isinstance(command, tuple) and len(command) == 3 and command[1] == "run":
        errors.append({"field": "command", "reason": "previous blocked codex run contract is forbidden"})
    return {
        "valid": not errors,
        "errors": errors,
        "command": list(command) if isinstance(command, tuple) else [],
        "contract_used": CODEX_EXEC_CONTRACT,
        "previous_blocked_contract": PREVIOUS_BLOCKED_CONTRACT,
        "shell_execution_present": False,
        "arbitrary_command_execution_present": False,
        "network_execution_present": False,
    }
