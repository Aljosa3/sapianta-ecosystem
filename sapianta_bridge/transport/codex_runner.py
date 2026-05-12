"""Bounded Codex subprocess runner for bridge transport."""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .transport_config import TransportConfig


@dataclass(frozen=True)
class CodexExecutionResult:
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False
    failed_closed: bool = False
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_seconds": round(self.duration_seconds, 6),
            "timed_out": self.timed_out,
            "failed_closed": self.failed_closed,
            "error": self.error,
        }


def _tail(value: str, limit: int = 4000) -> str:
    return value[-limit:]


def _target_paths_inside_workspace(task: dict[str, Any], workspace: Path) -> bool:
    root = workspace.resolve()
    for raw_path in task.get("target_paths", []):
        candidate = Path(raw_path)
        target = candidate if candidate.is_absolute() else root / candidate
        try:
            target.resolve().relative_to(root)
        except ValueError:
            return False
    return True


class CodexRunner:
    def __init__(self, config: TransportConfig) -> None:
        self.config = config

    def run(self, task: dict[str, Any]) -> CodexExecutionResult:
        started = time.monotonic()
        workspace = self.config.workspace.resolve()
        if not workspace.exists() or not workspace.is_dir():
            return CodexExecutionResult(
                exit_code=127,
                stdout="",
                stderr="workspace unavailable",
                duration_seconds=time.monotonic() - started,
                failed_closed=True,
                error="workspace unavailable",
            )
        if not _target_paths_inside_workspace(task, workspace):
            return CodexExecutionResult(
                exit_code=126,
                stdout="",
                stderr="target path outside configured workspace",
                duration_seconds=time.monotonic() - started,
                failed_closed=True,
                error="target path outside configured workspace",
            )

        try:
            completed = subprocess.run(
                list(self.config.command),
                input=json.dumps(task, sort_keys=True),
                cwd=workspace,
                capture_output=True,
                text=True,
                shell=False,
                timeout=self.config.timeout_seconds,
            )
            return CodexExecutionResult(
                exit_code=completed.returncode,
                stdout=_tail(completed.stdout),
                stderr=_tail(completed.stderr),
                duration_seconds=time.monotonic() - started,
            )
        except subprocess.TimeoutExpired as exc:
            return CodexExecutionResult(
                exit_code=124,
                stdout=_tail(exc.stdout or ""),
                stderr=_tail(exc.stderr or "codex subprocess timeout"),
                duration_seconds=time.monotonic() - started,
                timed_out=True,
                failed_closed=True,
                error="timeout",
            )
        except Exception as exc:
            return CodexExecutionResult(
                exit_code=125,
                stdout="",
                stderr=f"codex subprocess failed: {exc.__class__.__name__}",
                duration_seconds=time.monotonic() - started,
                failed_closed=True,
                error=exc.__class__.__name__,
            )

