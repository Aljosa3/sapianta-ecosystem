"""Lifecycle state machine for SAPIANTA CODEX BRIDGE PROTOCOL v0.1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SUCCESS_STATES = (
    "CREATED",
    "VALIDATED",
    "SENT_TO_CODEX",
    "EXECUTING",
    "RESULT_RECEIVED",
    "ANALYSIS_CONTEXT_CREATED",
    "INTERPRETED",
    "NEXT_TASK_PROPOSED",
    "CLOSED",
)

FAILURE_STATES = (
    "VALIDATION_FAILED",
    "EXECUTION_FAILED",
    "TEST_FAILED",
    "RESULT_MISSING",
    "CONTEXT_MISSING",
    "ESCALATED",
    "BLOCKED",
    "QUARANTINED",
)

LIFECYCLE_STATES = SUCCESS_STATES + FAILURE_STATES
TERMINAL_STATES = frozenset({"CLOSED", "QUARANTINED"})
FAILURE_STATE_SET = frozenset(FAILURE_STATES)

SUCCESS_TRANSITIONS = {
    "CREATED": {"VALIDATED"},
    "VALIDATED": {"SENT_TO_CODEX"},
    "SENT_TO_CODEX": {"EXECUTING"},
    "EXECUTING": {"RESULT_RECEIVED"},
    "RESULT_RECEIVED": {"ANALYSIS_CONTEXT_CREATED"},
    "ANALYSIS_CONTEXT_CREATED": {"INTERPRETED"},
    "INTERPRETED": {"NEXT_TASK_PROPOSED"},
    "NEXT_TASK_PROPOSED": {"CLOSED"},
    "CLOSED": set(),
}


@dataclass(frozen=True)
class TransitionValidation:
    valid: bool
    errors: tuple[dict[str, str], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "errors": list(self.errors)}


def _error(field: str, reason: str) -> dict[str, str]:
    return {"field": field, "reason": reason}


def is_known_state(state: Any) -> bool:
    return isinstance(state, str) and state in LIFECYCLE_STATES


def validate_transition(
    current_state: str,
    next_state: str,
    *,
    evidence: Any = None,
) -> TransitionValidation:
    errors: list[dict[str, str]] = []

    if not is_known_state(current_state):
        errors.append(_error("current_state", "unknown lifecycle state"))
    if not is_known_state(next_state):
        errors.append(_error("next_state", "unknown lifecycle state"))
    if errors:
        return TransitionValidation(False, tuple(errors))

    if current_state in TERMINAL_STATES:
        return TransitionValidation(
            False,
            (_error("current_state", f"{current_state} is terminal"),),
        )

    if current_state in FAILURE_STATE_SET:
        return TransitionValidation(
            False,
            (_error("current_state", "failure states cannot continue"),),
        )

    if next_state in FAILURE_STATE_SET:
        if not evidence:
            return TransitionValidation(
                False,
                (_error("evidence", "failure transitions require evidence"),),
            )
        return TransitionValidation(True)

    allowed_next = SUCCESS_TRANSITIONS.get(current_state, set())
    if next_state not in allowed_next:
        return TransitionValidation(
            False,
            (_error("next_state", "invalid lifecycle transition"),),
        )

    return TransitionValidation(True)

