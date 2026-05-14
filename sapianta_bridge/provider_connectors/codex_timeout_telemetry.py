"""Timeout telemetry for bounded Codex execution."""

from __future__ import annotations

from typing import Any


def codex_timeout_telemetry(
    *,
    timeout_seconds: int,
    duration_seconds: int,
    timed_out: bool,
    stdout: str,
    stderr: str,
) -> dict[str, Any]:
    return {
        "timeout_seconds": timeout_seconds,
        "duration_seconds": duration_seconds,
        "timed_out": timed_out,
        "stdout_sample": stdout[:240],
        "stderr_sample": stderr[:240],
        "timeout_exceeded": timed_out or duration_seconds >= timeout_seconds,
        "replay_safe": True,
    }


def validate_codex_timeout_telemetry(telemetry: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(telemetry, dict):
        return {"valid": False, "errors": [{"field": "timeout_telemetry", "reason": "must be an object"}]}
    for field in ("timeout_seconds", "duration_seconds", "timed_out", "stdout_sample", "stderr_sample", "timeout_exceeded"):
        if field not in telemetry:
            errors.append({"field": field, "reason": "missing timeout telemetry field"})
    if not isinstance(telemetry.get("timeout_seconds"), int) or telemetry.get("timeout_seconds", 0) <= 0:
        errors.append({"field": "timeout_seconds", "reason": "timeout must be positive integer"})
    if not isinstance(telemetry.get("duration_seconds"), int) or telemetry.get("duration_seconds", -1) < 0:
        errors.append({"field": "duration_seconds", "reason": "duration must be non-negative integer"})
    if not isinstance(telemetry.get("timed_out"), bool):
        errors.append({"field": "timed_out", "reason": "timed_out must be boolean"})
    if telemetry.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "telemetry must be replay-safe"})
    return {"valid": not errors, "errors": errors}
