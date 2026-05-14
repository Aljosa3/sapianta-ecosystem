"""Deterministic Codex process termination states."""

from __future__ import annotations

from typing import Any


CODEX_PROCESS_STATES = (
    "TERMINATED_COMPLETED",
    "TERMINATED_CLI_ERROR",
    "OUTPUT_COMPLETED_PROCESS_RUNNING",
    "OUTPUT_ACTIVE_PROCESS_RUNNING",
    "OUTPUT_QUIESCENT_PROCESS_RUNNING",
    "STREAMING_WAIT",
    "INTERACTIVE_WAIT",
    "AUTH_WAIT",
    "HANGING_PROCESS",
    "TIMEOUT_NO_COMPLETION",
    "UNKNOWN",
)

RESULT_AVAILABLE_STATES = ("TERMINATED_COMPLETED", "OUTPUT_COMPLETED_PROCESS_RUNNING")


def process_state_has_bounded_result(state: str) -> bool:
    return state in RESULT_AVAILABLE_STATES


def validate_codex_process_state(state: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if state not in CODEX_PROCESS_STATES:
        errors.append({"field": "process_state", "reason": "unsupported process state"})
    if state == "UNKNOWN":
        errors.append({"field": "process_state", "reason": "unknown process state must fail closed"})
    return {
        "valid": not errors,
        "errors": errors,
        "bounded_result_available": process_state_has_bounded_result(state) if isinstance(state, str) else False,
        "fail_closed": state not in RESULT_AVAILABLE_STATES,
    }
