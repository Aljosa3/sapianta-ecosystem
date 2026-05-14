"""No-copy/paste loop lifecycle."""

from __future__ import annotations

from typing import Any


LOOP_SUCCESS_PATH = (
    "CREATED",
    "REQUEST_ACCEPTED",
    "BRIDGE_REQUEST_CREATED",
    "INGRESS_PROPAGATED",
    "SESSION_BOUND",
    "PROVIDER_INVOKED",
    "RESULT_PROPAGATED",
    "RESPONSE_DELIVERED",
    "EVIDENCE_RECORDED",
    "COMPLETED",
)

LOOP_FAILURE_STATES = ("BLOCKED", "FAILED")


def complete_loop_lifecycle() -> list[str]:
    return list(LOOP_SUCCESS_PATH)


def blocked_loop_lifecycle() -> list[str]:
    return ["CREATED", "BLOCKED"]


def validate_loop_lifecycle(states: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(states, list) or not states:
        return {"valid": False, "errors": [{"field": "loop_lifecycle", "reason": "must be a non-empty list"}]}
    if states == list(LOOP_SUCCESS_PATH):
        return {
            "valid": True,
            "errors": [],
            "hidden_states_present": False,
            "retry_present": False,
            "fallback_present": False,
            "recursive_execution_present": False,
            "multiple_invocations_present": False,
        }
    if len(states) == 2 and states[0] == "CREATED" and states[1] in LOOP_FAILURE_STATES:
        return {
            "valid": True,
            "errors": [],
            "hidden_states_present": False,
            "retry_present": False,
            "fallback_present": False,
            "recursive_execution_present": False,
            "multiple_invocations_present": False,
        }
    if states != list(LOOP_SUCCESS_PATH[: len(states)]):
        errors.append({"field": "loop_lifecycle", "reason": "loop lifecycle skips or reorders required states"})
    if len(set(states)) != len(states):
        errors.append({"field": "loop_lifecycle", "reason": "loop lifecycle cannot repeat states"})
    unknown = [state for state in states if state not in (*LOOP_SUCCESS_PATH, *LOOP_FAILURE_STATES)]
    if unknown:
        errors.append({"field": "loop_lifecycle", "reason": "loop lifecycle contains hidden states"})
    if states.count("PROVIDER_INVOKED") > 1:
        errors.append({"field": "loop_lifecycle", "reason": "multiple provider invocations are forbidden"})
    return {
        "valid": not errors,
        "errors": errors,
        "hidden_states_present": bool(unknown),
        "retry_present": False,
        "fallback_present": False,
        "recursive_execution_present": False,
        "multiple_invocations_present": states.count("PROVIDER_INVOKED") > 1,
    }
