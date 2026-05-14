"""Bounded timeout validation for local Codex execution."""

from __future__ import annotations

from typing import Any


MAX_BOUNDED_CODEX_TIMEOUT_SECONDS = 120


def validate_bounded_execution_timeout(timeout_seconds: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(timeout_seconds, int):
        errors.append({"field": "timeout_seconds", "reason": "timeout must be an explicit integer"})
    elif timeout_seconds <= 0 or timeout_seconds > MAX_BOUNDED_CODEX_TIMEOUT_SECONDS:
        errors.append({"field": "timeout_seconds", "reason": "timeout must be positive and bounded"})
    return {
        "valid": not errors,
        "errors": errors,
        "timeout_seconds": timeout_seconds if isinstance(timeout_seconds, int) else None,
        "timeout_bounded": not errors,
    }
