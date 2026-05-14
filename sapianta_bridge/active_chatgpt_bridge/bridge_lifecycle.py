"""Active ChatGPT bridge lifecycle."""

from __future__ import annotations

from typing import Any


BRIDGE_SUCCESS_PATH = (
    "CREATED",
    "INGRESS_BOUND",
    "ENVELOPE_PROPOSED",
    "SESSION_CREATED",
    "PROVIDER_INVOKED",
    "RESULT_RETURNED",
    "RESPONSE_CREATED",
    "EVIDENCE_RECORDED",
    "COMPLETED",
)

BRIDGE_FAILURE_STATES = ("BLOCKED", "FAILED")


def complete_bridge_lifecycle() -> list[str]:
    return list(BRIDGE_SUCCESS_PATH)


def blocked_bridge_lifecycle() -> list[str]:
    return ["CREATED", "BLOCKED"]


def validate_bridge_lifecycle(states: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if not isinstance(states, list) or not states:
        return {"valid": False, "errors": [{"field": "bridge_lifecycle", "reason": "must be a non-empty list"}]}
    if states == list(BRIDGE_SUCCESS_PATH):
        return {
            "valid": True,
            "errors": [],
            "hidden_states_present": False,
            "retry_loop_present": False,
            "provider_fallback_present": False,
            "multiple_invocations_present": False,
        }
    if len(states) == 2 and states[0] == "CREATED" and states[1] in BRIDGE_FAILURE_STATES:
        return {
            "valid": True,
            "errors": [],
            "hidden_states_present": False,
            "retry_loop_present": False,
            "provider_fallback_present": False,
            "multiple_invocations_present": False,
        }
    if states != list(BRIDGE_SUCCESS_PATH[: len(states)]):
        errors.append({"field": "bridge_lifecycle", "reason": "bridge lifecycle skips or reorders required states"})
    if len(set(states)) != len(states):
        errors.append({"field": "bridge_lifecycle", "reason": "bridge lifecycle cannot repeat states"})
    unknown = [state for state in states if state not in (*BRIDGE_SUCCESS_PATH, *BRIDGE_FAILURE_STATES)]
    if unknown:
        errors.append({"field": "bridge_lifecycle", "reason": "bridge lifecycle contains hidden states"})
    if states.count("PROVIDER_INVOKED") > 1:
        errors.append({"field": "bridge_lifecycle", "reason": "multiple provider invocations are forbidden"})
    return {
        "valid": not errors,
        "errors": errors,
        "hidden_states_present": bool(unknown),
        "retry_loop_present": False,
        "provider_fallback_present": False,
        "multiple_invocations_present": states.count("PROVIDER_INVOKED") > 1,
    }
