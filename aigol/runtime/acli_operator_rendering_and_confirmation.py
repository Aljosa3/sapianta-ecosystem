"""Operator rendering and confirmation evidence for ACLI conversational sessions."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.acli_conversational_development_session import (
    ACLI_CONVERSATIONAL_DEVELOPMENT_SESSION_ARTIFACT_V1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


ACLI_OPERATOR_RENDERING_CONFIRMATION_RUNTIME_VERSION = (
    "G3_02_IMPLEMENTATION_PHASE_3_OPERATOR_RENDERING_AND_CONFIRMATION_RUNTIME_V1"
)
ACLI_OPERATOR_RENDERING_ARTIFACT_V1 = "ACLI_OPERATOR_RENDERING_ARTIFACT_V1"
ACLI_OPERATOR_CONFIRMATION_CLASSIFICATION_ARTIFACT_V1 = (
    "ACLI_OPERATOR_CONFIRMATION_CLASSIFICATION_ARTIFACT_V1"
)

OPERATOR_RESPONSE_RENDERED = "OPERATOR_RESPONSE_RENDERED"
OPERATOR_CONFIRMATION_CLASSIFIED = "OPERATOR_CONFIRMATION_CLASSIFIED"

CONFIRM = "confirm"
REJECT = "reject"
CLARIFY = "clarify"
MODIFY = "modify"
CONTINUE = "continue"
UNKNOWN = "unknown"

CONFIRMATION_CLASSES = {CONFIRM, REJECT, CLARIFY, MODIFY, CONTINUE, UNKNOWN}

EVENT_RESPONSE_RENDERED = "acli_operator_response_rendered"
EVENT_CONFIRMATION_CLASSIFIED = "acli_operator_confirmation_classified"


def render_operator_response(
    *,
    render_id: str,
    conversation_artifact: dict[str, Any],
    rendered_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Render deterministic operator-facing session and turn state."""

    conversation = _validated_conversation_artifact(conversation_artifact)
    replay_path = Path(replay_dir)
    event_index = _next_event_index(replay_path)
    latest_turn = _latest_turn(conversation)
    summary = _render_summary(conversation, latest_turn)
    event = _event(
        event_index=event_index,
        event_type=EVENT_RESPONSE_RENDERED,
        occurred_at=rendered_at,
        event_payload={
            "render_id": _require_string(render_id, "render_id"),
            "session_id": conversation["session_id"],
            "turn_id": summary["turn_id"],
            "required_operator_action": summary["required_operator_action"],
        },
    )
    artifact = {
        "artifact_type": ACLI_OPERATOR_RENDERING_ARTIFACT_V1,
        "runtime_version": ACLI_OPERATOR_RENDERING_CONFIRMATION_RUNTIME_VERSION,
        "migration_batch_id": "G3_02_IMPLEMENTATION_PHASE_3_OPERATOR_RENDERING_AND_CONFIRMATION_V1",
        "render_id": _require_string(render_id, "render_id"),
        "conversation_reference": conversation["conversation_id"],
        "conversation_hash": conversation["artifact_hash"],
        "session_id": conversation["session_id"],
        "turn_id": summary["turn_id"],
        "canonical_semantic_artifact_reference": summary["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": summary["canonical_semantic_artifact_hash"],
        "current_lifecycle_state": summary["current_lifecycle_state"],
        "required_operator_action": summary["required_operator_action"],
        "safe_fallback_rendered": summary["safe_fallback_rendered"],
        "rendered_sections": summary["rendered_sections"],
        "operator_response_lines": summary["operator_response_lines"],
        "replay_lineage": summary["replay_lineage"],
        "rendered_at": _require_string(rendered_at, "rendered_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "product1_workflow_started": False,
        "replay_visible": True,
        "event": event,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _persist_step(replay_path, event_index, EVENT_RESPONSE_RENDERED, artifact)
    return _capture(artifact, replay_path)


def classify_operator_confirmation(
    *,
    classification_id: str,
    conversation_artifact: dict[str, Any],
    operator_input: str,
    classified_at: str,
    replay_dir: str | Path,
    active_turn_id: str | None = None,
) -> dict[str, Any]:
    """Classify operator confirmation text as non-authoritative evidence."""

    conversation = _validated_conversation_artifact(conversation_artifact)
    replay_path = Path(replay_dir)
    event_index = _next_event_index(replay_path)
    latest_turn = _latest_turn(conversation)
    turn_id = active_turn_id if isinstance(active_turn_id, str) and active_turn_id.strip() else (
        latest_turn["turn_id"] if latest_turn else None
    )
    classification = _confirmation_class(operator_input)
    input_hash = replay_hash({"operator_input": _require_string(operator_input, "operator_input")})
    event = _event(
        event_index=event_index,
        event_type=EVENT_CONFIRMATION_CLASSIFIED,
        occurred_at=classified_at,
        event_payload={
            "classification_id": _require_string(classification_id, "classification_id"),
            "session_id": conversation["session_id"],
            "turn_id": turn_id,
            "confirmation_classification": classification,
            "operator_input_hash": input_hash,
        },
    )
    artifact = {
        "artifact_type": ACLI_OPERATOR_CONFIRMATION_CLASSIFICATION_ARTIFACT_V1,
        "runtime_version": ACLI_OPERATOR_RENDERING_CONFIRMATION_RUNTIME_VERSION,
        "migration_batch_id": "G3_02_IMPLEMENTATION_PHASE_3_OPERATOR_RENDERING_AND_CONFIRMATION_V1",
        "classification_id": _require_string(classification_id, "classification_id"),
        "conversation_reference": conversation["conversation_id"],
        "conversation_hash": conversation["artifact_hash"],
        "session_id": conversation["session_id"],
        "turn_id": turn_id,
        "canonical_semantic_artifact_reference": conversation["current_csa_reference"],
        "canonical_semantic_artifact_hash": conversation["current_csa_hash"],
        "operator_input_hash": input_hash,
        "confirmation_classification": classification,
        "confirmation_classification_set": sorted(CONFIRMATION_CLASSES),
        "classification_rationale": _classification_rationale(classification),
        "confirmation_evidence_only": True,
        "classified_at": _require_string(classified_at, "classified_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "product1_workflow_started": False,
        "replay_visible": True,
        "event": event,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _persist_step(replay_path, event_index, EVENT_CONFIRMATION_CLASSIFIED, artifact)
    return _capture(artifact, replay_path)


def reconstruct_operator_rendering_confirmation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate operator rendering and confirmation replay."""

    replay_path = Path(replay_dir)
    wrappers = [_load_verified_wrapper(path) for path in sorted(replay_path.glob("*.json"))]
    if not wrappers:
        raise FailClosedRuntimeError("ACLI operator rendering failed closed: replay is empty")
    artifacts = [wrapper["artifact"] for wrapper in wrappers]
    render_count = sum(1 for artifact in artifacts if artifact["artifact_type"] == ACLI_OPERATOR_RENDERING_ARTIFACT_V1)
    classification_count = sum(
        1
        for artifact in artifacts
        if artifact["artifact_type"] == ACLI_OPERATOR_CONFIRMATION_CLASSIFICATION_ARTIFACT_V1
    )
    for index, wrapper in enumerate(wrappers):
        if wrapper.get("replay_index") != index:
            raise FailClosedRuntimeError("ACLI operator rendering replay ordering mismatch")
        event = wrapper["artifact"].get("event")
        if not isinstance(event, dict) or event.get("event_index") != index:
            raise FailClosedRuntimeError("ACLI operator rendering event ordering mismatch")
        _verify_hash_field(event, "event_hash", "ACLI operator rendering event hash mismatch")
    return {
        "render_count": render_count,
        "classification_count": classification_count,
        "artifact_count": len(artifacts),
        "session_ids": sorted({artifact["session_id"] for artifact in artifacts}),
        "turn_ids": [artifact.get("turn_id") for artifact in artifacts],
        "confirmation_classifications": [
            artifact["confirmation_classification"]
            for artifact in artifacts
            if artifact["artifact_type"] == ACLI_OPERATOR_CONFIRMATION_CLASSIFICATION_ARTIFACT_V1
        ],
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "product1_workflow_started": False,
        "replay_visible": True,
        "replay_hash": replay_hash(wrappers),
    }


def _render_summary(conversation: dict[str, Any], latest_turn: dict[str, Any] | None) -> dict[str, Any]:
    if latest_turn is None:
        csa_ref = conversation["current_csa_reference"]
        csa_hash = conversation["current_csa_hash"]
        lifecycle_state = conversation["conversation_status"]
        required_action = "provide first governed development request"
        replay_lineage = []
        turn_id = None
        safe_fallback = True
        sections = ["session_state", "csa_summary", "safe_fallback", "non_authority_flags"]
    else:
        csa_ref = latest_turn["canonical_semantic_artifact_reference"]
        csa_hash = latest_turn["canonical_semantic_artifact_hash"]
        lifecycle_state = _turn_lifecycle_state(latest_turn)
        required_action = _required_operator_action(latest_turn)
        replay_lineage = deepcopy(latest_turn["replay_lineage"])
        turn_id = latest_turn["turn_id"]
        safe_fallback = latest_turn["clarification_status"] == "FAILED_CLOSED" or latest_turn["proposal_status"] == "FAILED_CLOSED"
        sections = [
            "session_state",
            "turn_state",
            "csa_summary",
            "clarification",
            "proposal",
            "confirmation",
            "continuation",
            "non_authority_flags",
        ]
    lines = [
        f"Session: {conversation['session_id']}",
        f"Turn: {turn_id or 'none'}",
        f"CSA: {csa_ref} {csa_hash}",
        f"State: {lifecycle_state}",
        f"Required action: {required_action}",
        "Authority: evidence only; no provider, worker, execution, mutation, Product 1, or deployment action.",
    ]
    return {
        "turn_id": turn_id,
        "canonical_semantic_artifact_reference": csa_ref,
        "canonical_semantic_artifact_hash": csa_hash,
        "current_lifecycle_state": lifecycle_state,
        "required_operator_action": required_action,
        "safe_fallback_rendered": safe_fallback,
        "rendered_sections": sections,
        "operator_response_lines": lines,
        "replay_lineage": replay_lineage,
    }


def _turn_lifecycle_state(turn: dict[str, Any]) -> str:
    if turn["clarification_status"] in {"CLARIFICATION_REQUESTED", "CLARIFICATION_OPEN"}:
        return "CLARIFICATION_PENDING"
    if turn["proposal_status"] in {"PROPOSAL_CANDIDATE_RECORDED", "PROPOSAL_CONFIRMATION_REQUIRED"}:
        return "PROPOSAL_PENDING"
    if turn["confirmation_status"] == "CONFIRMATION_REQUIRED":
        return "CONFIRMATION_PENDING"
    if turn["continuation_status"] == "CONTINUATION_FROM_PARENT_TURN":
        return "CONTINUATION_ACTIVE"
    if "FAILED_CLOSED" in {
        turn["clarification_status"],
        turn["proposal_status"],
        turn["confirmation_status"],
        turn["continuation_status"],
    }:
        return "FAILED_CLOSED"
    return "TURN_RECORDED"


def _required_operator_action(turn: dict[str, Any]) -> str:
    if turn["clarification_status"] in {"CLARIFICATION_REQUESTED", "CLARIFICATION_OPEN"}:
        return "answer clarification request"
    if turn["proposal_status"] in {"PROPOSAL_CANDIDATE_RECORDED", "PROPOSAL_CONFIRMATION_REQUIRED"}:
        return "review proposal summary"
    if turn["confirmation_status"] == "CONFIRMATION_REQUIRED":
        return "confirm, reject, clarify, modify, or continue"
    if turn["continuation_status"] == "CONTINUATION_BLOCKED_NO_PARENT":
        return "select prior turn or start new request"
    if "FAILED_CLOSED" in {
        turn["clarification_status"],
        turn["proposal_status"],
        turn["confirmation_status"],
        turn["continuation_status"],
    }:
        return "inspect failure evidence and choose safe recovery"
    return "continue, clarify, modify, or stop"


def _confirmation_class(operator_input: str) -> str:
    text = _require_string(operator_input, "operator_input").strip().lower()
    words = set(text.replace(".", " ").replace(",", " ").replace("!", " ").replace("?", " ? ").split())
    if words & {"reject", "deny", "no", "cancel", "stop", "zavrni", "ne"}:
        return REJECT
    if words & {"clarify", "explain", "question", "why", "pojasni", "razlozi", "?"}:
        return CLARIFY
    if words & {"modify", "change", "instead", "adjust", "update", "spremeni", "popravi"}:
        return MODIFY
    if words & {"continue", "proceed", "next", "nadaljuj"}:
        return CONTINUE
    if words & {"confirm", "approve", "yes", "ok", "okay", "odobri", "potrjujem", "da"}:
        return CONFIRM
    return UNKNOWN


def _classification_rationale(classification: str) -> str:
    return {
        CONFIRM: "operator input matched confirmation wording; evidence only",
        REJECT: "operator input matched rejection wording; evidence only",
        CLARIFY: "operator input requested clarification; evidence only",
        MODIFY: "operator input requested modification; evidence only",
        CONTINUE: "operator input requested continuation; evidence only",
        UNKNOWN: "operator input did not match a supported confirmation class",
    }[classification]


def _latest_turn(conversation: dict[str, Any]) -> dict[str, Any] | None:
    turns = conversation.get("turns")
    if not isinstance(turns, list) or not turns:
        return None
    return deepcopy(turns[-1])


def _validated_conversation_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("ACLI operator rendering failed closed: conversation artifact must be object")
    if artifact.get("artifact_type") != ACLI_CONVERSATIONAL_DEVELOPMENT_SESSION_ARTIFACT_V1:
        raise FailClosedRuntimeError("ACLI operator rendering failed closed: invalid conversation artifact")
    _verify_hash_field(artifact, "artifact_hash", "ACLI operator rendering conversation hash mismatch")
    _require_hash(artifact.get("current_csa_hash"), "current_csa_hash")
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
            raise FailClosedRuntimeError(f"ACLI operator rendering failed closed: {flag} must be false")
    return deepcopy(artifact)


def _event(
    *,
    event_index: int,
    event_type: str,
    occurred_at: str,
    event_payload: dict[str, Any],
) -> dict[str, Any]:
    event = {
        "event_index": event_index,
        "event_type": event_type,
        "occurred_at": _require_string(occurred_at, "occurred_at"),
        "event_payload": deepcopy(event_payload),
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "repository_mutated": False,
    }
    event["event_hash"] = replay_hash(event)
    return event


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    path = replay_path / f"{index:03d}_{step}.json"
    if path.exists():
        raise FailClosedRuntimeError("ACLI operator rendering failed closed: replay already exists")
    write_json_immutable(path, _wrapper(index, step, artifact))


def _next_event_index(replay_path: Path) -> int:
    return len(sorted(replay_path.glob("*.json"))) if replay_path.exists() else 0


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
    _verify_hash_field(wrapper, "replay_hash", "ACLI operator rendering replay hash mismatch")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("ACLI operator rendering replay artifact must be object")
    _verify_hash_field(artifact, "artifact_hash", "ACLI operator rendering artifact hash mismatch")
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
        "runtime_version": ACLI_OPERATOR_RENDERING_CONFIRMATION_RUNTIME_VERSION,
        "artifact": deepcopy(artifact),
        "artifact_type": artifact["artifact_type"],
        "session_id": artifact["session_id"],
        "turn_id": artifact.get("turn_id"),
        "canonical_semantic_artifact_reference": artifact["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": artifact["canonical_semantic_artifact_hash"],
        "replay_reference": str(replay_path),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "product1_workflow_started": False,
        "replay_visible": True,
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"ACLI operator rendering failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"ACLI operator rendering failed closed: {field_name} must be a replay hash")
    return text
