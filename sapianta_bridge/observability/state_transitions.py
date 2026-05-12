"""Readable lifecycle transition visibility derived from replay evidence."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.transport.transport_config import TransportConfig

from .replay_reader import ReplayEvidenceError, find_by_task_id


FINAL_STATE_TRANSITIONS = {
    "COMPLETED": ("CREATED", "VALIDATED", "PROCESSING", "COMPLETED"),
    "FAILED": ("CREATED", "VALIDATED", "PROCESSING", "FAILED"),
}


def transition_history(task_id: str, config: TransportConfig | None = None) -> dict[str, Any]:
    try:
        entries = find_by_task_id(task_id, config)
    except ReplayEvidenceError as exc:
        return {
            "task_id": task_id,
            "transitions": [],
            "transition_count": 0,
            "invalid_transition_detected": True,
            "errors": [exc.to_dict()],
        }

    if not entries:
        return {
            "task_id": task_id,
            "transitions": [],
            "transition_count": 0,
            "invalid_transition_detected": False,
            "errors": [],
        }

    latest = entries[-1]
    final_state = latest["final_state"]
    transitions = list(FINAL_STATE_TRANSITIONS.get(final_state, ()))
    errors = []
    invalid = False
    if not transitions:
        invalid = True
        errors.append({"field": "final_state", "reason": "unknown execution state"})

    return {
        "task_id": task_id,
        "transitions": transitions,
        "transition_count": len(transitions),
        "invalid_transition_detected": invalid,
        "errors": errors,
    }
