"""Governed execution session states."""

from __future__ import annotations

from typing import Any


SESSION_STATES = (
    "CREATED",
    "INGRESS_CAPTURED",
    "ENVELOPE_PROPOSED",
    "ENVELOPE_VALIDATED",
    "PROVIDER_INVOKED",
    "RESULT_RETURNED",
    "EVIDENCE_RECORDED",
    "COMPLETED",
    "BLOCKED",
    "FAILED",
)

CANONICAL_SUCCESS_PATH = (
    "CREATED",
    "INGRESS_CAPTURED",
    "ENVELOPE_PROPOSED",
    "ENVELOPE_VALIDATED",
    "PROVIDER_INVOKED",
    "RESULT_RETURNED",
    "EVIDENCE_RECORDED",
    "COMPLETED",
)

TERMINAL_FAILURE_STATES = ("BLOCKED", "FAILED")


def validate_session_state(state: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if state not in SESSION_STATES:
        errors.append({"field": "session_state", "reason": "unknown session state"})
    return {
        "valid": not errors,
        "errors": errors,
        "hidden_state_detected": bool(errors),
    }
