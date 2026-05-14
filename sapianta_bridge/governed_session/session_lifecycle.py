"""Deterministic governed session lifecycle validation."""

from __future__ import annotations

from typing import Any

from .session_state import CANONICAL_SUCCESS_PATH, TERMINAL_FAILURE_STATES


def complete_session_lifecycle() -> list[str]:
    return list(CANONICAL_SUCCESS_PATH)


def blocked_session_lifecycle() -> list[str]:
    return ["CREATED", "BLOCKED"]


def validate_session_lifecycle(states: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(states, list) or not states:
        return {"valid": False, "errors": [{"field": "session_lifecycle", "reason": "must be a non-empty list"}]}
    if states == list(CANONICAL_SUCCESS_PATH):
        return {
            "valid": True,
            "errors": [],
            "hidden_states_present": False,
            "retry_present": False,
            "multiple_provider_invocations_present": False,
        }
    if len(states) == 2 and states[0] == "CREATED" and states[1] in TERMINAL_FAILURE_STATES:
        return {
            "valid": True,
            "errors": [],
            "hidden_states_present": False,
            "retry_present": False,
            "multiple_provider_invocations_present": False,
        }
    if states != list(CANONICAL_SUCCESS_PATH[: len(states)]):
        errors.append({"field": "session_lifecycle", "reason": "session lifecycle skips or reorders required states"})
    if len(set(states)) != len(states):
        errors.append({"field": "session_lifecycle", "reason": "session lifecycle cannot repeat states"})
    unknown = [state for state in states if state not in (*CANONICAL_SUCCESS_PATH, *TERMINAL_FAILURE_STATES)]
    if unknown:
        errors.append({"field": "session_lifecycle", "reason": "session lifecycle contains hidden states"})
    if states.count("PROVIDER_INVOKED") > 1:
        errors.append({"field": "session_lifecycle", "reason": "multiple provider invocations are forbidden"})
    return {
        "valid": not errors,
        "errors": errors,
        "hidden_states_present": bool(unknown),
        "retry_present": False,
        "multiple_provider_invocations_present": states.count("PROVIDER_INVOKED") > 1,
    }
