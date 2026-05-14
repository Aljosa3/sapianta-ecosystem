"""Deterministic active invocation lifecycle."""

from __future__ import annotations

from typing import Any


INVOCATION_LIFECYCLE_STATES = (
    "PROPOSED",
    "VALIDATED",
    "INVOKED",
    "RESULT_RECEIVED",
    "EVIDENCE_RECORDED",
)

ALLOWED_TRANSITIONS = {
    "PROPOSED": "VALIDATED",
    "VALIDATED": "INVOKED",
    "INVOKED": "RESULT_RECEIVED",
    "RESULT_RECEIVED": "EVIDENCE_RECORDED",
}


def next_lifecycle_state(current_state: str) -> str | None:
    return ALLOWED_TRANSITIONS.get(current_state)


def complete_invocation_lifecycle() -> list[str]:
    return list(INVOCATION_LIFECYCLE_STATES)


def validate_lifecycle(states: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(states, list) or not states:
        return {"valid": False, "errors": [{"field": "lifecycle", "reason": "lifecycle must be a non-empty list"}]}
    if states != list(INVOCATION_LIFECYCLE_STATES[: len(states)]):
        errors.append({"field": "lifecycle", "reason": "lifecycle contains hidden or out-of-order states"})
    if len(set(states)) != len(states):
        errors.append({"field": "lifecycle", "reason": "lifecycle cannot repeat states"})
    unknown = [state for state in states if state not in INVOCATION_LIFECYCLE_STATES]
    if unknown:
        errors.append({"field": "lifecycle", "reason": "lifecycle contains unknown states"})
    return {
        "valid": not errors,
        "errors": errors,
        "hidden_states_present": bool(unknown),
        "retry_present": False,
        "concurrency_present": False,
    }
