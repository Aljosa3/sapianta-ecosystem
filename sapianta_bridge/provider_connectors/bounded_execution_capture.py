"""Deterministic capture model for bounded Codex execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


DETERMINISTIC_EXECUTION_STARTED_AT = "1970-01-01T00:00:00Z"
DETERMINISTIC_EXECUTION_ENDED_AT = "1970-01-01T00:00:00Z"


@dataclass(frozen=True)
class BoundedExecutionCapture:
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool
    duration_seconds: int = 0
    completion_state: str = "UNKNOWN"
    suspected_blocker: str = ""
    execution_started_at: str = DETERMINISTIC_EXECUTION_STARTED_AT
    execution_ended_at: str = DETERMINISTIC_EXECUTION_ENDED_AT

    def to_dict(self) -> dict[str, Any]:
        return {
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "timed_out": self.timed_out,
            "duration_seconds": self.duration_seconds,
            "completion_state": self.completion_state,
            "process_terminated": not self.timed_out,
            "stdout_sample": self.stdout[:240],
            "stderr_sample": self.stderr[:240],
            "suspected_blocker": self.suspected_blocker,
            "execution_started_at": self.execution_started_at,
            "execution_ended_at": self.execution_ended_at,
            "immutable": True,
            "replay_safe": True,
        }


def capture_completed_execution(
    *,
    stdout: str,
    stderr: str,
    exit_code: int,
    duration_seconds: int = 0,
    completion_state: str | None = None,
    suspected_blocker: str = "",
) -> BoundedExecutionCapture:
    return BoundedExecutionCapture(
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        timed_out=False,
        duration_seconds=duration_seconds,
        completion_state=completion_state or ("COMPLETED" if exit_code == 0 else "CLI_ERROR"),
        suspected_blocker=suspected_blocker,
    )


def capture_timeout(
    *,
    stdout: str = "",
    stderr: str = "bounded codex execution timed out",
    duration_seconds: int = 0,
    completion_state: str = "TIMEOUT",
    suspected_blocker: str = "timeout",
) -> BoundedExecutionCapture:
    return BoundedExecutionCapture(
        stdout=stdout,
        stderr=stderr,
        exit_code=124,
        timed_out=True,
        duration_seconds=duration_seconds,
        completion_state=completion_state,
        suspected_blocker=suspected_blocker,
    )


def validate_bounded_execution_capture(capture: Any) -> dict[str, Any]:
    value = capture.to_dict() if hasattr(capture, "to_dict") else capture
    errors: list[dict[str, str]] = []
    if not isinstance(value, dict):
        return {"valid": False, "errors": [{"field": "capture", "reason": "must be an object"}]}
    for field in (
        "stdout",
        "stderr",
        "exit_code",
        "timed_out",
        "duration_seconds",
        "completion_state",
        "process_terminated",
        "stdout_sample",
        "stderr_sample",
        "suspected_blocker",
        "execution_started_at",
        "execution_ended_at",
    ):
        if field not in value:
            errors.append({"field": field, "reason": "missing capture field"})
    if not isinstance(value.get("stdout"), str):
        errors.append({"field": "stdout", "reason": "stdout must be a string"})
    if not isinstance(value.get("stderr"), str):
        errors.append({"field": "stderr", "reason": "stderr must be a string"})
    if not isinstance(value.get("exit_code"), int):
        errors.append({"field": "exit_code", "reason": "exit code must be an integer"})
    if not isinstance(value.get("timed_out"), bool):
        errors.append({"field": "timed_out", "reason": "timed_out must be boolean"})
    if not isinstance(value.get("duration_seconds"), int) or value.get("duration_seconds", -1) < 0:
        errors.append({"field": "duration_seconds", "reason": "duration must be non-negative integer"})
    if not isinstance(value.get("completion_state"), str):
        errors.append({"field": "completion_state", "reason": "completion state must be a string"})
    if value.get("immutable") is not True:
        errors.append({"field": "immutable", "reason": "capture must be immutable"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "capture must be replay-safe"})
    return {"valid": not errors, "errors": errors}
