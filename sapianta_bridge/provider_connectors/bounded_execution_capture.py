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
    process_state: str = "UNKNOWN"
    suspected_blocker: str = ""
    process_terminated: bool | None = None
    completion_marker_detected: bool = False
    bounded_result_captured: bool = False
    graceful_termination_attempted: bool = False
    graceful_termination_succeeded: bool = False
    execution_started_at: str = DETERMINISTIC_EXECUTION_STARTED_AT
    execution_ended_at: str = DETERMINISTIC_EXECUTION_ENDED_AT

    def to_dict(self) -> dict[str, Any]:
        process_terminated = self.process_terminated if self.process_terminated is not None else not self.timed_out
        return {
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "timed_out": self.timed_out,
            "duration_seconds": self.duration_seconds,
            "completion_state": self.completion_state,
            "process_state": self.process_state,
            "process_terminated": process_terminated,
            "completion_marker_detected": self.completion_marker_detected,
            "bounded_result_captured": self.bounded_result_captured,
            "graceful_termination_attempted": self.graceful_termination_attempted,
            "graceful_termination_succeeded": self.graceful_termination_succeeded,
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
    process_state: str | None = None,
    suspected_blocker: str = "",
    completion_marker_detected: bool = False,
    bounded_result_captured: bool | None = None,
) -> BoundedExecutionCapture:
    resolved_process_state = process_state or ("TERMINATED_COMPLETED" if exit_code == 0 else "TERMINATED_CLI_ERROR")
    return BoundedExecutionCapture(
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        timed_out=False,
        duration_seconds=duration_seconds,
        completion_state=completion_state or ("COMPLETED" if exit_code == 0 else "CLI_ERROR"),
        process_state=resolved_process_state,
        suspected_blocker=suspected_blocker,
        process_terminated=True,
        completion_marker_detected=completion_marker_detected,
        bounded_result_captured=bounded_result_captured if bounded_result_captured is not None else exit_code == 0,
    )


def capture_timeout(
    *,
    stdout: str = "",
    stderr: str = "bounded codex execution timed out",
    duration_seconds: int = 0,
    completion_state: str = "TIMEOUT",
    process_state: str = "TIMEOUT_NO_COMPLETION",
    suspected_blocker: str = "timeout",
    process_terminated: bool = False,
    completion_marker_detected: bool = False,
    bounded_result_captured: bool = False,
    graceful_termination_attempted: bool = False,
    graceful_termination_succeeded: bool = False,
) -> BoundedExecutionCapture:
    return BoundedExecutionCapture(
        stdout=stdout,
        stderr=stderr,
        exit_code=124,
        timed_out=True,
        duration_seconds=duration_seconds,
        completion_state=completion_state,
        process_state=process_state,
        suspected_blocker=suspected_blocker,
        process_terminated=process_terminated,
        completion_marker_detected=completion_marker_detected,
        bounded_result_captured=bounded_result_captured,
        graceful_termination_attempted=graceful_termination_attempted,
        graceful_termination_succeeded=graceful_termination_succeeded,
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
        "process_state",
        "process_terminated",
        "completion_marker_detected",
        "bounded_result_captured",
        "graceful_termination_attempted",
        "graceful_termination_succeeded",
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
    if not isinstance(value.get("process_state"), str):
        errors.append({"field": "process_state", "reason": "process state must be a string"})
    for field in (
        "process_terminated",
        "completion_marker_detected",
        "bounded_result_captured",
        "graceful_termination_attempted",
        "graceful_termination_succeeded",
    ):
        if not isinstance(value.get(field), bool):
            errors.append({"field": field, "reason": "capture flag must be boolean"})
    if value.get("immutable") is not True:
        errors.append({"field": "immutable", "reason": "capture must be immutable"})
    if value.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "capture must be replay-safe"})
    return {"valid": not errors, "errors": errors}
