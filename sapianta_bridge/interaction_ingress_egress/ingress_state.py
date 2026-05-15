"""Deterministic local ingress/egress states."""

from __future__ import annotations

from typing import Any


INGRESS_STATES = (
    "INGRESS_RECEIVED",
    "INGRESS_VALIDATED",
    "TRANSPORT_LINKED",
    "EXECUTION_LINKED",
    "RESULT_NORMALIZED",
    "EGRESS_EXPORTED",
    "BLOCKED",
    "FAILED",
)

SUCCESS_PATH = (
    "INGRESS_RECEIVED",
    "INGRESS_VALIDATED",
    "TRANSPORT_LINKED",
    "EXECUTION_LINKED",
    "RESULT_NORMALIZED",
    "EGRESS_EXPORTED",
)


def validate_ingress_state_chain(states: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(states, list) or not states:
        return {"valid": False, "errors": [{"field": "ingress_states", "reason": "must be non-empty list"}]}
    if any(state not in INGRESS_STATES for state in states):
        errors.append({"field": "ingress_states", "reason": "unknown ingress state"})
    if states != list(SUCCESS_PATH) and states[-1:] not in (["BLOCKED"], ["FAILED"]):
        errors.append({"field": "ingress_states", "reason": "invalid ingress path"})
    return {"valid": not errors, "errors": errors}
