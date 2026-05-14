"""Deterministic bounded completion marker detection."""

from __future__ import annotations

import json
from typing import Any


BOUNDED_COMPLETION_MARKER = "AIGOL_TASK_COMPLETE"


def detect_completion_marker(*, stdout: str, stderr: str) -> dict[str, Any]:
    combined = f"{stdout}\n{stderr}"
    json_line_detected = False
    for line in combined.splitlines():
        stripped = line.strip()
        if not stripped.startswith("{"):
            continue
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if parsed.get("completion_marker") == BOUNDED_COMPLETION_MARKER:
            json_line_detected = True
            break
    marker_detected = BOUNDED_COMPLETION_MARKER in combined or json_line_detected
    return {
        "completion_marker": BOUNDED_COMPLETION_MARKER,
        "marker_detected": marker_detected,
        "json_completion_line_detected": json_line_detected,
        "stdout_contains_marker": BOUNDED_COMPLETION_MARKER in stdout,
        "stderr_contains_marker": BOUNDED_COMPLETION_MARKER in stderr,
        "arbitrary_text_success_inferred": False,
    }


def validate_completion_marker_detection(detection: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(detection, dict):
        return {"valid": False, "errors": [{"field": "completion_marker_detection", "reason": "must be an object"}]}
    for field in (
        "completion_marker",
        "marker_detected",
        "json_completion_line_detected",
        "stdout_contains_marker",
        "stderr_contains_marker",
        "arbitrary_text_success_inferred",
    ):
        if field not in detection:
            errors.append({"field": field, "reason": "missing completion marker detection field"})
    if detection.get("completion_marker") != BOUNDED_COMPLETION_MARKER:
        errors.append({"field": "completion_marker", "reason": "unexpected completion marker"})
    if detection.get("arbitrary_text_success_inferred") is not False:
        errors.append({"field": "arbitrary_text_success_inferred", "reason": "success cannot be inferred from arbitrary text"})
    return {"valid": not errors, "errors": errors}
