"""Deterministic output quiescence classification for bounded Codex execution."""

from __future__ import annotations

from typing import Any


def classify_output_quiescence(
    *,
    stdout: str,
    stderr: str,
    marker_detected: bool,
    process_running: bool,
    idle_window_seconds: int,
) -> dict[str, Any]:
    output_present = bool(stdout or stderr)
    output_quiescent = process_running and marker_detected and output_present and idle_window_seconds > 0
    return {
        "output_present": output_present,
        "marker_detected": marker_detected,
        "process_running": process_running,
        "idle_window_seconds": idle_window_seconds,
        "output_quiescent": output_quiescent,
        "bounded_result_available": output_quiescent and marker_detected,
        "replay_safe": True,
    }


def validate_output_quiescence(quiescence: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(quiescence, dict):
        return {"valid": False, "errors": [{"field": "output_quiescence", "reason": "must be an object"}]}
    for field in (
        "output_present",
        "marker_detected",
        "process_running",
        "idle_window_seconds",
        "output_quiescent",
        "bounded_result_available",
        "replay_safe",
    ):
        if field not in quiescence:
            errors.append({"field": field, "reason": "missing output quiescence field"})
    if not isinstance(quiescence.get("idle_window_seconds"), int) or quiescence.get("idle_window_seconds", -1) < 0:
        errors.append({"field": "idle_window_seconds", "reason": "idle window must be non-negative integer"})
    if quiescence.get("replay_safe") is not True:
        errors.append({"field": "replay_safe", "reason": "quiescence evidence must be replay-safe"})
    return {"valid": not errors, "errors": errors}
