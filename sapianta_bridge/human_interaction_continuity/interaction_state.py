"""Deterministic human interaction continuity states."""

from __future__ import annotations

from typing import Any


INTERACTION_STATES = (
    "REQUEST_RECEIVED",
    "ENVELOPE_BOUND",
    "EXECUTION_AUTHORIZED",
    "PROVIDER_RUNNING",
    "RESULT_CAPTURED",
    "RESULT_RETURNED",
    "BLOCKED",
    "FAILED",
)

SUCCESS_PATH = (
    "REQUEST_RECEIVED",
    "ENVELOPE_BOUND",
    "EXECUTION_AUTHORIZED",
    "PROVIDER_RUNNING",
    "RESULT_CAPTURED",
    "RESULT_RETURNED",
)


def validate_interaction_state(state: Any) -> dict[str, Any]:
    errors = []
    if state not in INTERACTION_STATES:
        errors.append({"field": "interaction_state", "reason": "unknown interaction state"})
    return {"valid": not errors, "errors": errors, "fail_closed": bool(errors)}


def validate_interaction_state_chain(states: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(states, list) or not states:
        return {"valid": False, "errors": [{"field": "interaction_states", "reason": "must be a non-empty list"}]}
    for state in states:
        errors.extend(validate_interaction_state(state)["errors"])
    if states != list(SUCCESS_PATH) and states[-1:] not in (["BLOCKED"], ["FAILED"]):
        errors.append({"field": "interaction_states", "reason": "invalid interaction continuity path"})
    return {"valid": not errors, "errors": errors}
