"""Deterministic interaction transport states."""

from __future__ import annotations

from typing import Any


TRANSPORT_STATES = (
    "REQUEST_RECEIVED",
    "TRANSPORT_BOUND",
    "EXECUTION_LINKED",
    "PROVIDER_ACTIVE",
    "RESULT_NORMALIZED",
    "RESULT_RETURNED",
    "BLOCKED",
    "FAILED",
)

SUCCESS_PATH = (
    "REQUEST_RECEIVED",
    "TRANSPORT_BOUND",
    "EXECUTION_LINKED",
    "PROVIDER_ACTIVE",
    "RESULT_NORMALIZED",
    "RESULT_RETURNED",
)


def validate_transport_state(state: Any) -> dict[str, Any]:
    errors = []
    if state not in TRANSPORT_STATES:
        errors.append({"field": "transport_state", "reason": "unknown transport state"})
    return {"valid": not errors, "errors": errors}


def validate_transport_state_chain(states: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(states, list) or not states:
        return {"valid": False, "errors": [{"field": "transport_states", "reason": "must be non-empty list"}]}
    for state in states:
        errors.extend(validate_transport_state(state)["errors"])
    if states != list(SUCCESS_PATH) and states[-1:] not in (["BLOCKED"], ["FAILED"]):
        errors.append({"field": "transport_states", "reason": "invalid transport state path"})
    return {"valid": not errors, "errors": errors}
