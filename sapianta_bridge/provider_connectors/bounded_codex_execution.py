"""Whitelisted Codex CLI execution command model."""

from __future__ import annotations

from pathlib import Path
from typing import Any


CODEX_PROVIDER_ID = "codex_cli"
CODEX_EXECUTABLE_NAME = "codex"


def bounded_codex_command(*, codex_executable: str, task_artifact_path: str) -> tuple[str, str, str]:
    return (codex_executable, "run", task_artifact_path)


def validate_bounded_codex_command(*, codex_executable: str, command: tuple[str, ...]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(codex_executable, str) or not codex_executable.strip():
        errors.append({"field": "codex_executable", "reason": "codex executable must be explicit"})
    elif Path(codex_executable).name != CODEX_EXECUTABLE_NAME:
        errors.append({"field": "codex_executable", "reason": "only codex executable is allowed"})
    if not isinstance(command, tuple) or len(command) != 3:
        errors.append({"field": "command", "reason": "command must be the fixed codex run artifact form"})
    elif command[0] != codex_executable or command[1] != "run" or not isinstance(command[2], str) or not command[2]:
        errors.append({"field": "command", "reason": "command must be codex run <prepared_task_artifact>"})
    for part in command if isinstance(command, tuple) else ():
        if not isinstance(part, str) or "\x00" in part:
            errors.append({"field": "command", "reason": "command parts must be safe strings"})
    return {
        "valid": not errors,
        "errors": errors,
        "command": list(command) if isinstance(command, tuple) else [],
        "shell_execution_present": False,
        "arbitrary_command_execution_present": False,
        "network_execution_present": False,
    }
