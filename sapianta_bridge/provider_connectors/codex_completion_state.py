"""Deterministic Codex exec completion states."""

from __future__ import annotations

from typing import Any


CODEX_COMPLETION_STATES = (
    "COMPLETED",
    "TIMEOUT",
    "INTERACTIVE_WAIT",
    "AUTH_WAIT",
    "APP_SERVER_WAIT",
    "STREAMING_WAIT",
    "HANGING_PROCESS",
    "CLI_ERROR",
    "UNKNOWN",
)

FAIL_CLOSED_STATES = (
    "TIMEOUT",
    "INTERACTIVE_WAIT",
    "AUTH_WAIT",
    "APP_SERVER_WAIT",
    "STREAMING_WAIT",
    "HANGING_PROCESS",
    "CLI_ERROR",
    "UNKNOWN",
)


def completion_state_is_success(state: str) -> bool:
    return state == "COMPLETED"


def validate_codex_completion_state(state: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if state not in CODEX_COMPLETION_STATES:
        errors.append({"field": "completion_state", "reason": "unsupported completion state"})
    if state == "UNKNOWN":
        errors.append({"field": "completion_state", "reason": "unknown completion state must fail closed"})
    return {
        "valid": not errors,
        "errors": errors,
        "completion_success": completion_state_is_success(state) if isinstance(state, str) else False,
        "fail_closed": state in FAIL_CLOSED_STATES,
    }
