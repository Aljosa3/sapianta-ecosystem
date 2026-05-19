"""Deterministic lifecycle transitions for AGOL Bridge v0.1."""

from __future__ import annotations

from copy import deepcopy

LIFECYCLE_STATES = {
    "CREATED",
    "NORMALIZED",
    "WAITING_FOR_APPROVAL",
    "APPROVED",
    "DISPATCHED",
    "EXECUTING",
    "RETURNED",
    "VALIDATED",
    "FINALIZED",
    "QUARANTINED",
    "FAILED",
}

ALLOWED_TRANSITIONS = {
    "CREATED": {"NORMALIZED", "WAITING_FOR_APPROVAL", "APPROVED", "QUARANTINED"},
    "NORMALIZED": {"WAITING_FOR_APPROVAL", "APPROVED", "QUARANTINED"},
    "WAITING_FOR_APPROVAL": {"APPROVED", "QUARANTINED"},
    "APPROVED": {"DISPATCHED", "QUARANTINED"},
    "DISPATCHED": {"EXECUTING", "RETURNED", "FAILED"},
    "EXECUTING": {"RETURNED", "FAILED"},
    "RETURNED": {"VALIDATED", "FAILED", "QUARANTINED"},
    "VALIDATED": {"FINALIZED", "QUARANTINED"},
    "FINALIZED": set(),
    "QUARANTINED": set(),
    "FAILED": set(),
}


def current_state(package: dict) -> str:
    metadata = package.get("metadata", {}) if isinstance(package, dict) else {}
    return metadata.get("lifecycle_state", "CREATED")


def with_lifecycle_state(package: dict, state: str) -> dict:
    updated = deepcopy(package)
    updated.setdefault("metadata", {})
    updated["metadata"]["lifecycle_state"] = state
    return updated


def transition_lifecycle(package: dict, next_state: str) -> dict:
    previous_state = current_state(package)
    if previous_state not in LIFECYCLE_STATES or next_state not in LIFECYCLE_STATES:
        return {
            "status": "BLOCKED",
            "previous_state": previous_state,
            "next_state": next_state,
            "package": package,
            "errors": [{"field": "lifecycle_state", "error": "unknown lifecycle state"}],
        }
    if next_state not in ALLOWED_TRANSITIONS[previous_state]:
        return {
            "status": "QUARANTINE",
            "previous_state": previous_state,
            "next_state": "QUARANTINED",
            "package": with_lifecycle_state(package, "QUARANTINED"),
            "errors": [{"field": "lifecycle_state", "error": "unexpected lifecycle transition"}],
        }
    return {
        "status": "TRANSITIONED",
        "previous_state": previous_state,
        "next_state": next_state,
        "package": with_lifecycle_state(package, next_state),
        "errors": [],
    }
