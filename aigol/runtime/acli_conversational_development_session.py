"""Conversational development turns inside governed ACLI sessions."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.acli_development_session_lifecycle import (
    ACLI_DEVELOPMENT_SESSION_LIFECYCLE_ARTIFACT_V1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


ACLI_CONVERSATIONAL_DEVELOPMENT_SESSION_RUNTIME_VERSION = (
    "G3_02_IMPLEMENTATION_PHASE_2_CONVERSATIONAL_DEVELOPMENT_SESSION_RUNTIME_V1"
)
ACLI_CONVERSATIONAL_DEVELOPMENT_SESSION_ARTIFACT_V1 = (
    "ACLI_CONVERSATIONAL_DEVELOPMENT_SESSION_ARTIFACT_V1"
)

CONVERSATION_STARTED = "CONVERSATION_STARTED"
TURN_RECORDED = "TURN_RECORDED"
FAILED_CLOSED = "FAILED_CLOSED"

CLARIFICATION_STATUSES = {
    "CLARIFICATION_NOT_REQUIRED",
    "CLARIFICATION_REQUESTED",
    "CLARIFICATION_OPEN",
    "CLARIFICATION_RESOLVED",
    FAILED_CLOSED,
}

PROPOSAL_STATUSES = {
    "PROPOSAL_NOT_CREATED",
    "PROPOSAL_CANDIDATE_RECORDED",
    "PROPOSAL_CONFIRMATION_REQUIRED",
    FAILED_CLOSED,
}

CONFIRMATION_STATUSES = {
    "CONFIRMATION_NOT_REQUIRED",
    "CONFIRMATION_REQUIRED",
    "CONFIRMATION_RECORDED",
    FAILED_CLOSED,
}

CONTINUATION_STATUSES = {
    "NEW_CONVERSATION",
    "CONTINUATION_FROM_PARENT_TURN",
    "CONTINUATION_BLOCKED_NO_PARENT",
    FAILED_CLOSED,
}

EVENT_CONVERSATION_STARTED = "acli_conversational_development_session_started"
EVENT_TURN_RECORDED = "acli_conversational_development_turn_recorded"


def start_conversational_development_session(
    *,
    conversation_id: str,
    session_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Start conversational development context for an existing ACLI session."""

    session = _validated_session_artifact(session_artifact)
    replay_path = Path(replay_dir)
    _ensure_step_available(replay_path, 0, EVENT_CONVERSATION_STARTED)
    event = _event(
        event_index=0,
        event_type=EVENT_CONVERSATION_STARTED,
        occurred_at=created_at,
        previous_event_hash="",
        event_payload={
            "conversation_id": _require_string(conversation_id, "conversation_id"),
            "session_id": session["session_id"],
            "session_artifact_hash": session["artifact_hash"],
            "canonical_semantic_artifact_reference": session["canonical_semantic_artifact_reference"],
            "canonical_semantic_artifact_hash": session["canonical_semantic_artifact_hash"],
        },
    )
    artifact = _conversation_artifact(
        conversation_id=conversation_id,
        session=session,
        turns=[],
        conversation_events=[event],
        conversation_status=CONVERSATION_STARTED,
        current_csa_reference=session["canonical_semantic_artifact_reference"],
        current_csa_hash=session["canonical_semantic_artifact_hash"],
        created_at=created_at,
        updated_at=created_at,
        failure_reason=None,
    )
    _persist_step(replay_path, 0, EVENT_CONVERSATION_STARTED, artifact)
    return _capture(artifact, replay_path)


def record_conversational_development_turn(
    *,
    conversation_artifact: dict[str, Any],
    turn_id: str,
    recorded_at: str,
    replay_dir: str | Path,
    prompt_hash: str,
    canonical_semantic_artifact_reference: str,
    canonical_semantic_artifact_hash: str,
    replay_lineage: list[dict[str, Any]],
    clarification_status: str,
    proposal_status: str,
    confirmation_status: str,
    continuation_status: str,
    parent_turn_id: str | None = None,
    clarification_request_reference: str | None = None,
    proposal_reference: str | None = None,
    confirmation_request_reference: str | None = None,
) -> dict[str, Any]:
    """Record one deterministic conversational development turn."""

    conversation = _validated_conversation_artifact(conversation_artifact)
    if conversation["conversation_status"] == FAILED_CLOSED:
        raise FailClosedRuntimeError("ACLI conversational development failed closed: terminal conversation")
    _validate_turn_statuses(
        clarification_status=clarification_status,
        proposal_status=proposal_status,
        confirmation_status=confirmation_status,
        continuation_status=continuation_status,
    )
    turns = conversation["turns"]
    existing_turn_ids = {turn["turn_id"] for turn in turns}
    if turn_id in existing_turn_ids:
        raise FailClosedRuntimeError("ACLI conversational development failed closed: duplicate turn id")
    if parent_turn_id:
        if parent_turn_id not in existing_turn_ids:
            raise FailClosedRuntimeError("ACLI conversational development failed closed: parent turn not found")
        if continuation_status != "CONTINUATION_FROM_PARENT_TURN":
            raise FailClosedRuntimeError("ACLI conversational development failed closed: continuation status mismatch")
    elif continuation_status == "CONTINUATION_FROM_PARENT_TURN":
        raise FailClosedRuntimeError("ACLI conversational development failed closed: parent turn required")

    event_index = len(conversation["conversation_events"])
    previous_turn_hash = turns[-1]["turn_hash"] if turns else ""
    turn = {
        "turn_id": _require_string(turn_id, "turn_id"),
        "session_id": conversation["session_id"],
        "conversation_id": conversation["conversation_id"],
        "parent_turn_id": parent_turn_id if isinstance(parent_turn_id, str) and parent_turn_id else None,
        "turn_index": len(turns),
        "prompt_hash": _require_hash(prompt_hash, "prompt_hash"),
        "canonical_semantic_artifact_reference": _require_string(
            canonical_semantic_artifact_reference,
            "canonical_semantic_artifact_reference",
        ),
        "canonical_semantic_artifact_hash": _require_hash(
            canonical_semantic_artifact_hash,
            "canonical_semantic_artifact_hash",
        ),
        "previous_turn_hash": previous_turn_hash,
        "previous_csa_hash": conversation["current_csa_hash"],
        "replay_lineage": _normalize_replay_lineage(replay_lineage),
        "clarification_status": clarification_status,
        "proposal_status": proposal_status,
        "confirmation_status": confirmation_status,
        "continuation_status": continuation_status,
        "clarification_request_reference": _optional_string(clarification_request_reference),
        "proposal_reference": _optional_string(proposal_reference),
        "confirmation_request_reference": _optional_string(confirmation_request_reference),
        "recorded_at": _require_string(recorded_at, "recorded_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "product1_workflow_started": False,
    }
    turn["turn_hash"] = replay_hash(turn)
    event = _event(
        event_index=event_index,
        event_type=EVENT_TURN_RECORDED,
        occurred_at=recorded_at,
        previous_event_hash=conversation["conversation_events"][-1]["event_hash"],
        event_payload={
            "turn_id": turn["turn_id"],
            "turn_hash": turn["turn_hash"],
            "parent_turn_id": turn["parent_turn_id"],
            "canonical_semantic_artifact_hash": turn["canonical_semantic_artifact_hash"],
            "clarification_status": clarification_status,
            "proposal_status": proposal_status,
            "confirmation_status": confirmation_status,
            "continuation_status": continuation_status,
        },
    )
    status = FAILED_CLOSED if FAILED_CLOSED in {
        clarification_status,
        proposal_status,
        confirmation_status,
        continuation_status,
    } else TURN_RECORDED
    artifact = _conversation_artifact(
        conversation_id=conversation["conversation_id"],
        session=conversation["session"],
        turns=turns + [turn],
        conversation_events=conversation["conversation_events"] + [event],
        conversation_status=status,
        current_csa_reference=turn["canonical_semantic_artifact_reference"],
        current_csa_hash=turn["canonical_semantic_artifact_hash"],
        created_at=conversation["created_at"],
        updated_at=recorded_at,
        failure_reason="conversational turn failed closed" if status == FAILED_CLOSED else conversation["failure_reason"],
    )
    _persist_step(Path(replay_dir), event_index, EVENT_TURN_RECORDED, artifact)
    return _capture(artifact, Path(replay_dir))


def reconstruct_acli_conversational_development_session_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate conversational development session replay."""

    replay_path = Path(replay_dir)
    wrappers = [_load_verified_wrapper(path) for path in sorted(replay_path.glob("*.json"))]
    if not wrappers:
        raise FailClosedRuntimeError("ACLI conversational development failed closed: replay is empty")
    for index, wrapper in enumerate(wrappers):
        if wrapper.get("replay_index") != index:
            raise FailClosedRuntimeError("ACLI conversational development replay ordering mismatch")
    artifact = _validated_conversation_artifact(wrappers[-1]["artifact"])
    events = artifact["conversation_events"]
    turns = artifact["turns"]
    if len(events) != len(wrappers):
        raise FailClosedRuntimeError("ACLI conversational development event count mismatch")
    for index, event in enumerate(events):
        if event["event_index"] != index:
            raise FailClosedRuntimeError("ACLI conversational development event order mismatch")
        expected_previous = "" if index == 0 else events[index - 1]["event_hash"]
        if event["previous_event_hash"] != expected_previous:
            raise FailClosedRuntimeError("ACLI conversational development event lineage mismatch")
        _verify_hash_field(event, "event_hash", "ACLI conversational development event hash mismatch")
    turn_ids: set[str] = set()
    for index, turn in enumerate(turns):
        if turn["turn_index"] != index:
            raise FailClosedRuntimeError("ACLI conversational development turn order mismatch")
        if turn["turn_id"] in turn_ids:
            raise FailClosedRuntimeError("ACLI conversational development duplicate turn")
        turn_ids.add(turn["turn_id"])
        expected_previous = "" if index == 0 else turns[index - 1]["turn_hash"]
        if turn["previous_turn_hash"] != expected_previous:
            raise FailClosedRuntimeError("ACLI conversational development turn lineage mismatch")
        parent_turn_id = turn.get("parent_turn_id")
        if parent_turn_id is not None and parent_turn_id not in turn_ids:
            raise FailClosedRuntimeError("ACLI conversational development parent turn lineage mismatch")
        _verify_hash_field(turn, "turn_hash", "ACLI conversational development turn hash mismatch")
    return {
        "conversation_id": artifact["conversation_id"],
        "session_id": artifact["session_id"],
        "conversation_status": artifact["conversation_status"],
        "turn_count": len(turns),
        "turn_hash_chain": [turn["turn_hash"] for turn in turns],
        "current_csa_reference": artifact["current_csa_reference"],
        "current_csa_hash": artifact["current_csa_hash"],
        "replay_lineage_count": sum(len(turn["replay_lineage"]) for turn in turns),
        "clarification_statuses": [turn["clarification_status"] for turn in turns],
        "proposal_statuses": [turn["proposal_status"] for turn in turns],
        "confirmation_statuses": [turn["confirmation_status"] for turn in turns],
        "continuation_statuses": [turn["continuation_status"] for turn in turns],
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "product1_workflow_started": False,
        "replay_visible": True,
        "artifact_hash": artifact["artifact_hash"],
        "replay_hash": replay_hash(wrappers),
    }


def _conversation_artifact(
    *,
    conversation_id: str,
    session: dict[str, Any],
    turns: list[dict[str, Any]],
    conversation_events: list[dict[str, Any]],
    conversation_status: str,
    current_csa_reference: str,
    current_csa_hash: str,
    created_at: str,
    updated_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": ACLI_CONVERSATIONAL_DEVELOPMENT_SESSION_ARTIFACT_V1,
        "runtime_version": ACLI_CONVERSATIONAL_DEVELOPMENT_SESSION_RUNTIME_VERSION,
        "migration_batch_id": "G3_02_IMPLEMENTATION_PHASE_2_CONVERSATIONAL_DEVELOPMENT_SESSION_V1",
        "conversation_id": _require_string(conversation_id, "conversation_id"),
        "session_id": session["session_id"],
        "session_artifact_hash": session["artifact_hash"],
        "session": deepcopy(session),
        "conversation_status": _require_string(conversation_status, "conversation_status"),
        "turns": deepcopy(turns),
        "conversation_events": deepcopy(conversation_events),
        "current_csa_reference": _require_string(current_csa_reference, "current_csa_reference"),
        "current_csa_hash": _require_hash(current_csa_hash, "current_csa_hash"),
        "created_at": _require_string(created_at, "created_at"),
        "updated_at": _require_string(updated_at, "updated_at"),
        "conversation_history_associated": True,
        "csa_continuity_preserved": True,
        "replay_turn_lineage_preserved": True,
        "clarification_requests_visible": any(
            turn["clarification_status"] in {"CLARIFICATION_REQUESTED", "CLARIFICATION_OPEN"}
            for turn in turns
        ),
        "proposal_lifecycle_visible": any(
            turn["proposal_status"] != "PROPOSAL_NOT_CREATED" for turn in turns
        ),
        "confirmation_requests_visible": any(
            turn["confirmation_status"] != "CONFIRMATION_NOT_REQUIRED" for turn in turns
        ),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "product1_workflow_started": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _validated_session_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("ACLI conversational development failed closed: session artifact must be object")
    if artifact.get("artifact_type") != ACLI_DEVELOPMENT_SESSION_LIFECYCLE_ARTIFACT_V1:
        raise FailClosedRuntimeError("ACLI conversational development failed closed: invalid session artifact type")
    _verify_hash_field(artifact, "artifact_hash", "ACLI conversational development session hash mismatch")
    for flag in (
        "provider_invoked",
        "worker_invoked",
        "approval_created",
        "authorization_created",
        "execution_requested",
        "governance_modified",
        "repository_mutated",
        "deployment_requested",
        "product1_workflow_started",
    ):
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"ACLI conversational development failed closed: {flag} must be false")
    _require_hash(artifact.get("canonical_semantic_artifact_hash"), "canonical_semantic_artifact_hash")
    return deepcopy(artifact)


def _validated_conversation_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("ACLI conversational development failed closed: artifact must be object")
    if artifact.get("artifact_type") != ACLI_CONVERSATIONAL_DEVELOPMENT_SESSION_ARTIFACT_V1:
        raise FailClosedRuntimeError("ACLI conversational development failed closed: invalid artifact type")
    _verify_hash_field(artifact, "artifact_hash", "ACLI conversational development artifact hash mismatch")
    for flag in (
        "provider_invoked",
        "worker_invoked",
        "approval_created",
        "authorization_created",
        "execution_requested",
        "repository_mutated",
        "deployment_requested",
        "product1_workflow_started",
    ):
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"ACLI conversational development failed closed: {flag} must be false")
    _require_hash(artifact.get("current_csa_hash"), "current_csa_hash")
    return deepcopy(artifact)


def _validate_turn_statuses(
    *,
    clarification_status: str,
    proposal_status: str,
    confirmation_status: str,
    continuation_status: str,
) -> None:
    if clarification_status not in CLARIFICATION_STATUSES:
        raise FailClosedRuntimeError("ACLI conversational development failed closed: invalid clarification status")
    if proposal_status not in PROPOSAL_STATUSES:
        raise FailClosedRuntimeError("ACLI conversational development failed closed: invalid proposal status")
    if confirmation_status not in CONFIRMATION_STATUSES:
        raise FailClosedRuntimeError("ACLI conversational development failed closed: invalid confirmation status")
    if continuation_status not in CONTINUATION_STATUSES:
        raise FailClosedRuntimeError("ACLI conversational development failed closed: invalid continuation status")


def _normalize_replay_lineage(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError("ACLI conversational development failed closed: replay lineage is required")
    lineage = []
    for item in value:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("ACLI conversational development failed closed: replay lineage item must be object")
        lineage.append(
            {
                "replay_reference": _require_string(item.get("replay_reference"), "replay_reference"),
                "replay_hash": _require_hash(item.get("replay_hash"), "replay_hash"),
            }
        )
    return lineage


def _event(
    *,
    event_index: int,
    event_type: str,
    occurred_at: str,
    previous_event_hash: str,
    event_payload: dict[str, Any],
) -> dict[str, Any]:
    event = {
        "event_index": event_index,
        "event_type": event_type,
        "occurred_at": _require_string(occurred_at, "occurred_at"),
        "previous_event_hash": previous_event_hash,
        "event_payload": deepcopy(event_payload),
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "repository_mutated": False,
    }
    event["event_hash"] = replay_hash(event)
    return event


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    _ensure_step_available(replay_path, index, step)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", _wrapper(index, step, artifact))


def _ensure_step_available(replay_path: Path, index: int, step: str) -> None:
    if (replay_path / f"{index:03d}_{step}.json").exists():
        raise FailClosedRuntimeError("ACLI conversational development failed closed: replay already exists")


def _wrapper(index: int, step: str, artifact: dict[str, Any]) -> dict[str, Any]:
    wrapper = {
        "event_type": step.upper(),
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _load_verified_wrapper(path: Path) -> dict[str, Any]:
    wrapper = load_json(path)
    _verify_hash_field(wrapper, "replay_hash", "ACLI conversational development replay hash mismatch")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("ACLI conversational development replay artifact must be object")
    _verify_hash_field(artifact, "artifact_hash", "ACLI conversational development artifact hash mismatch")
    return wrapper


def _verify_hash_field(value: dict[str, Any], field_name: str, message: str) -> None:
    actual = value.get(field_name)
    if not isinstance(actual, str):
        raise FailClosedRuntimeError(message)
    expected = deepcopy(value)
    expected.pop(field_name)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(message)


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": ACLI_CONVERSATIONAL_DEVELOPMENT_SESSION_RUNTIME_VERSION,
        "conversation_artifact": deepcopy(artifact),
        "conversation_id": artifact["conversation_id"],
        "session_id": artifact["session_id"],
        "conversation_status": artifact["conversation_status"],
        "turn_count": len(artifact["turns"]),
        "current_csa_reference": artifact["current_csa_reference"],
        "current_csa_hash": artifact["current_csa_hash"],
        "replay_reference": str(replay_path),
        "conversation_history_associated": artifact["conversation_history_associated"],
        "csa_continuity_preserved": artifact["csa_continuity_preserved"],
        "replay_turn_lineage_preserved": artifact["replay_turn_lineage_preserved"],
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "product1_workflow_started": False,
        "replay_visible": True,
        "failure_reason": artifact["failure_reason"],
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _optional_string(value: str | None) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"ACLI conversational development failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(
            f"ACLI conversational development failed closed: {field_name} must be a replay hash"
        )
    return text
