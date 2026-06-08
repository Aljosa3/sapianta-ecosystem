"""Clarification lifecycle resolution for replay-derived session state."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash
from aigol.runtime.unknown_domain_clarification_runtime import (
    CLARIFICATION_REQUIRED,
    UNKNOWN_DOMAIN_ARTIFACT_V1,
)


AIGOL_CLARIFICATION_LIFECYCLE_RESOLUTION_RUNTIME_VERSION = (
    "AIGOL_CLARIFICATION_LIFECYCLE_RESOLUTION_RUNTIME_V1"
)
CLARIFICATION_LIFECYCLE_RESOLUTION_STATUS = "CLARIFICATION_LIFECYCLE_RESOLUTION_STATUS"

CLARIFICATION_ACTIVE = "ACTIVE"
CLARIFICATION_OPEN = "OPEN"
CLARIFICATION_RESPONDED = "RESPONDED"
CLARIFICATION_RESOLVED = "RESOLVED"
CLARIFICATION_SUPERSEDED = "SUPERSEDED"


def resolve_clarification_lifecycle(
    *,
    session_root: str | Path,
) -> dict[str, Any]:
    """Resolve replay-derived clarification lifecycle state for one session."""

    root = Path(session_root)
    if not root.exists():
        return _capture(root, [])
    if not root.is_dir():
        raise FailClosedRuntimeError("clarification lifecycle resolution failed closed: session root is not a directory")
    states = _clarification_states(root)
    _apply_lifecycle_resolution(states)
    return _capture(root, states)


def active_clarification_state(
    *,
    session_root: str | Path,
) -> dict[str, Any] | None:
    """Return the single active clarification state after lifecycle resolution."""

    capture = resolve_clarification_lifecycle(session_root=session_root)
    active = capture.get("active_clarification")
    return deepcopy(active) if isinstance(active, dict) else None


def _clarification_states(session_root: Path) -> list[dict[str, Any]]:
    resolved = _resolved_refs(session_root)
    responded = _responded_refs(session_root)
    states: list[dict[str, Any]] = []
    for turn_root in sorted((path for path in session_root.glob("TURN-*") if path.is_dir()), key=lambda path: path.name):
        clarification_root = turn_root / "unknown_domain_clarification"
        request_path = clarification_root / "001_clarification_request_recorded.json"
        unknown_path = clarification_root / "000_unknown_domain_recorded.json"
        if not request_path.exists() or not unknown_path.exists():
            continue
        unknown = _artifact_from_wrapper(
            _load_verified_wrapper(unknown_path, 0, "unknown_domain_recorded"),
            "unknown domain",
        )
        request = _artifact_from_wrapper(
            _load_verified_wrapper(request_path, 1, "clarification_request_recorded"),
            "clarification request",
        )
        if unknown.get("artifact_type") != UNKNOWN_DOMAIN_ARTIFACT_V1:
            raise FailClosedRuntimeError("clarification lifecycle resolution failed closed: workflow mismatch")
        if request.get("clarification_status") != CLARIFICATION_REQUIRED:
            continue
        if request.get("unknown_domain_reference") != unknown.get("unknown_domain_id"):
            raise FailClosedRuntimeError("clarification lifecycle resolution failed closed: clarification reference mismatch")
        if request.get("unknown_domain_hash") != unknown.get("artifact_hash"):
            raise FailClosedRuntimeError("clarification lifecycle resolution failed closed: replay mismatch")
        workflow_id = _workflow_id(turn_root)
        clarification_id = request["clarification_id"]
        if clarification_id in resolved:
            lifecycle_status = CLARIFICATION_RESOLVED
        elif clarification_id in responded:
            lifecycle_status = CLARIFICATION_RESPONDED
        else:
            lifecycle_status = CLARIFICATION_OPEN
        states.append(
            {
                "turn_id": turn_root.name,
                "turn_root": str(turn_root),
                "clarification_id": clarification_id,
                "clarification_request_hash": request["artifact_hash"],
                "unknown_domain_hash": unknown["artifact_hash"],
                "originating_workflow_id": workflow_id,
                "originating_replay_reference": str(clarification_root),
                "lifecycle_status": lifecycle_status,
                "active": False,
                "unknown_domain_artifact": deepcopy(unknown),
                "clarification_request_artifact": deepcopy(request),
            }
        )
    return states


def _apply_lifecycle_resolution(states: list[dict[str, Any]]) -> None:
    open_states = [state for state in states if state["lifecycle_status"] == CLARIFICATION_OPEN]
    if not open_states:
        return
    active = open_states[-1]
    for state in open_states[:-1]:
        state["lifecycle_status"] = CLARIFICATION_SUPERSEDED
        state["active"] = False
        state["superseded_by_clarification_reference"] = active["clarification_id"]
    active["lifecycle_status"] = CLARIFICATION_ACTIVE
    active["active"] = True


def _resolved_refs(session_root: Path) -> set[str]:
    refs: set[str] = set()
    for path in session_root.glob("TURN-*/clarification_continuity/002_clarification_resolution_recorded.json"):
        resolution = _artifact_from_wrapper(
            _load_verified_wrapper(path, 2, "clarification_resolution_recorded"),
            "clarification resolution",
        )
        reference = resolution.get("clarification_request_reference")
        if isinstance(reference, str):
            refs.add(reference)
    return refs


def _responded_refs(session_root: Path) -> set[str]:
    refs: set[str] = set()
    for path in session_root.glob("TURN-*/clarification_continuity/001_clarification_response_recorded.json"):
        response = _artifact_from_wrapper(
            _load_verified_wrapper(path, 1, "clarification_response_recorded"),
            "clarification response",
        )
        reference = response.get("clarification_request_reference")
        if isinstance(reference, str):
            refs.add(reference)
    return refs


def _workflow_id(turn_root: Path) -> str | None:
    routing_path = turn_root / "conversational_cli_routing" / "001_conversational_workflow_selection_recorded.json"
    if not routing_path.exists():
        return None
    routing = _artifact_from_wrapper(
        _load_verified_wrapper(routing_path, 1, "conversational_workflow_selection_recorded"),
        "workflow selection",
    )
    workflow_id = routing.get("workflow_id")
    return workflow_id if isinstance(workflow_id, str) else None


def _capture(session_root: Path, states: list[dict[str, Any]]) -> dict[str, Any]:
    active_states = [state for state in states if state.get("active") is True]
    if len(active_states) > 1:
        raise FailClosedRuntimeError("clarification lifecycle resolution failed closed: multiple active clarifications")
    lifecycle_summary = [
        {
            "turn_id": state["turn_id"],
            "clarification_id": state["clarification_id"],
            "lifecycle_status": state["lifecycle_status"],
            "active": state["active"],
            "originating_workflow_id": state.get("originating_workflow_id"),
            "proposed_domain": state["clarification_request_artifact"].get("proposed_domain"),
            "superseded_by_clarification_reference": state.get("superseded_by_clarification_reference"),
        }
        for state in states
    ]
    capture = {
        "runtime_version": AIGOL_CLARIFICATION_LIFECYCLE_RESOLUTION_RUNTIME_VERSION,
        "final_classification": CLARIFICATION_LIFECYCLE_RESOLUTION_STATUS,
        "session_root": str(session_root),
        "clarification_count": len(states),
        "active_clarification_count": len(active_states),
        "active_clarification": deepcopy(active_states[0]) if active_states else None,
        "lifecycle_summary": lifecycle_summary,
        "at_most_one_active_clarification": len(active_states) <= 1,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "domain_created": False,
        "fail_closed": False,
        "failure_reason": None,
    }
    capture["lifecycle_hash"] = replay_hash(capture)
    return capture


def _load_verified_wrapper(path: Path, replay_index: int, replay_step: str) -> dict[str, Any]:
    wrapper = load_json(path)
    if wrapper.get("replay_index") != replay_index or wrapper.get("replay_step") != replay_step:
        raise FailClosedRuntimeError("clarification lifecycle resolution failed closed: replay mismatch")
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("clarification lifecycle resolution replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("clarification lifecycle resolution failed closed: replay mismatch")
    return wrapper


def _artifact_from_wrapper(wrapper: dict[str, Any], label: str) -> dict[str, Any]:
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"clarification lifecycle resolution failed closed: {label} artifact missing")
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("clarification lifecycle resolution failed closed: replay mismatch")
    return artifact
