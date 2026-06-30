"""Operator rendering and confirmation evidence for ACLI conversational sessions."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.acli_uhcl_adapter_rendering import (
    capture_uhcl_human_response,
    render_uhcl_artifact_for_acli,
)
from aigol.runtime.acli_conversational_development_session import (
    ACLI_CONVERSATIONAL_DEVELOPMENT_SESSION_ARTIFACT_V1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.ubtr_human_communication_model_runtime import (
    LEVEL_STANDARD,
    RESPONSE_CLARIFICATION,
    RESPONSE_CONFIRMATION,
    RESPONSE_CONTINUATION,
    RESPONSE_MODIFICATION,
    RESPONSE_REJECTION,
    SECTION_TYPE_CONFIRMATION,
    SECTION_TYPE_EXPLANATION,
    SOURCE_COMPONENT_UBTR,
    create_shared_confirmation_model,
    create_typed_communication_section,
)


ACLI_OPERATOR_RENDERING_CONFIRMATION_RUNTIME_VERSION = (
    "G3_02_IMPLEMENTATION_PHASE_3_OPERATOR_RENDERING_AND_CONFIRMATION_RUNTIME_V1"
)
ACLI_UHCL_COMMAND_CONSUMPTION_MIGRATION_VERSION = "G3_04_PHASE_6_ACLI_COMMAND_UHCL_CONSUMPTION_MIGRATION_V1"
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
CANONICAL_UHCL_CONFIRMATION_CLASSES = {
    CONFIRM: RESPONSE_CONFIRMATION,
    REJECT: RESPONSE_REJECTION,
    CLARIFY: RESPONSE_CLARIFICATION,
    MODIFY: RESPONSE_MODIFICATION,
    CONTINUE: RESPONSE_CONTINUATION,
}

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
    uhcl_consumption = _render_summary_via_uhcl(
        render_id=render_id,
        conversation=conversation,
        summary=summary,
        rendered_at=rendered_at,
        replay_path=replay_path,
        event_index=event_index,
    )
    event = _event(
        event_index=event_index,
        event_type=EVENT_RESPONSE_RENDERED,
        occurred_at=rendered_at,
        event_payload={
            "render_id": _require_string(render_id, "render_id"),
            "session_id": conversation["session_id"],
            "turn_id": summary["turn_id"],
            "required_operator_action": summary["required_operator_action"],
            "uhcl_source_artifact_hash": uhcl_consumption["uhcl_source_artifact_hash"],
            "uhcl_render_artifact_hash": uhcl_consumption["uhcl_render_artifact_hash"],
        },
    )
    artifact = {
        "artifact_type": ACLI_OPERATOR_RENDERING_ARTIFACT_V1,
        "runtime_version": ACLI_OPERATOR_RENDERING_CONFIRMATION_RUNTIME_VERSION,
        "migration_batch_id": "G3_02_IMPLEMENTATION_PHASE_3_OPERATOR_RENDERING_AND_CONFIRMATION_V1",
        "uhcl_command_migration_version": ACLI_UHCL_COMMAND_CONSUMPTION_MIGRATION_VERSION,
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
        "uhcl_consumption": uhcl_consumption,
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
    uhcl_consumption = _classify_confirmation_via_uhcl(
        classification_id=classification_id,
        conversation=conversation,
        latest_turn=latest_turn,
        turn_id=turn_id,
        classification=classification,
        operator_input=operator_input,
        classified_at=classified_at,
        replay_path=replay_path,
        event_index=event_index,
    )
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
            "canonical_uhcl_response_class": uhcl_consumption["canonical_uhcl_response_class"],
            "uhcl_response_capture_status": uhcl_consumption["uhcl_response_capture_status"],
        },
    )
    artifact = {
        "artifact_type": ACLI_OPERATOR_CONFIRMATION_CLASSIFICATION_ARTIFACT_V1,
        "runtime_version": ACLI_OPERATOR_RENDERING_CONFIRMATION_RUNTIME_VERSION,
        "migration_batch_id": "G3_02_IMPLEMENTATION_PHASE_3_OPERATOR_RENDERING_AND_CONFIRMATION_V1",
        "uhcl_command_migration_version": ACLI_UHCL_COMMAND_CONSUMPTION_MIGRATION_VERSION,
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
        "canonical_uhcl_response_class": uhcl_consumption["canonical_uhcl_response_class"],
        "canonical_uhcl_response_class_set": sorted(CANONICAL_UHCL_CONFIRMATION_CLASSES.values()),
        "classification_rationale": _classification_rationale(classification),
        "confirmation_evidence_only": True,
        "uhcl_consumption": uhcl_consumption,
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
        "uhcl_consumption_migrated": all(
            artifact.get("uhcl_consumption", {}).get("acli_role") == "PRESENTATION_ADAPTER"
            for artifact in artifacts
        ),
        "uhcl_source_artifact_hashes": [
            artifact["uhcl_consumption"]["uhcl_source_artifact_hash"]
            for artifact in artifacts
            if "uhcl_consumption" in artifact
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


def _render_summary_via_uhcl(
    *,
    render_id: str,
    conversation: dict[str, Any],
    summary: dict[str, Any],
    rendered_at: str,
    replay_path: Path,
    event_index: int,
) -> dict[str, Any]:
    replay_lineage = summary["replay_lineage"] or [
        {
            "replay_reference": conversation["conversation_id"],
            "replay_hash": conversation["artifact_hash"],
        }
    ]
    section_result = create_typed_communication_section(
        section_id=f"{_require_string(render_id, 'render_id')}:UHCL-SECTION",
        section_type=SECTION_TYPE_EXPLANATION,
        communication_level=LEVEL_STANDARD,
        structured_content={
            "session_id": conversation["session_id"],
            "turn_id": summary["turn_id"],
            "current_lifecycle_state": summary["current_lifecycle_state"],
            "required_operator_action": summary["required_operator_action"],
            "operator_response_lines": list(summary["operator_response_lines"]),
        },
        evidence_references=[
            {
                "evidence_reference": conversation["conversation_id"],
                "evidence_hash": conversation["artifact_hash"],
            },
            {
                "evidence_reference": summary["canonical_semantic_artifact_reference"],
                "evidence_hash": summary["canonical_semantic_artifact_hash"],
            },
        ],
        created_at=rendered_at,
        replay_dir=replay_path / f"{event_index:03d}_uhcl_render_section",
        csa_reference=summary["canonical_semantic_artifact_reference"],
        csa_hash=summary["canonical_semantic_artifact_hash"],
        source_component=SOURCE_COMPONENT_UBTR,
        replay_lineage=replay_lineage,
        rollback_reference=f"ROLLBACK-{_require_string(render_id, 'render_id')}:UHCL-SECTION",
        non_authority_notices=[
            "UHCL section provides communication meaning only.",
            "ACLI renders terminal presentation only.",
        ],
    )
    render_result = render_uhcl_artifact_for_acli(
        render_id=f"{_require_string(render_id, 'render_id')}:UHCL-RENDER",
        uhcl_artifact=section_result["typed_section_artifact"],
        communication_level=LEVEL_STANDARD,
        rendered_at=rendered_at,
        replay_dir=replay_path / f"{event_index:03d}_uhcl_adapter_render",
    )
    render_artifact = render_result["artifact"]
    return {
        "migration_version": ACLI_UHCL_COMMAND_CONSUMPTION_MIGRATION_VERSION,
        "command_surface": "ACLI_OPERATOR_RESPONSE_RENDERING",
        "acli_role": "PRESENTATION_ADAPTER",
        "legacy_wrapper_retained": True,
        "uhcl_source_artifact_type": section_result["typed_section_artifact"]["artifact_type"],
        "uhcl_source_artifact_hash": section_result["typed_section_artifact_hash"],
        "uhcl_source_replay_reference": section_result["typed_section_replay_reference"],
        "uhcl_render_artifact_hash": render_artifact["artifact_hash"],
        "uhcl_render_replay_reference": render_result["replay_reference"],
        "semantic_translation_performed": False,
        "explanation_generated_by_acli": False,
        "confirmation_logic_performed_by_acli": False,
        "provider_orchestration_performed": False,
        "worker_orchestration_performed": False,
        "governance_performed": False,
        "replay_owned_by_acli": False,
    }


def _classify_confirmation_via_uhcl(
    *,
    classification_id: str,
    conversation: dict[str, Any],
    latest_turn: dict[str, Any] | None,
    turn_id: str | None,
    classification: str,
    operator_input: str,
    classified_at: str,
    replay_path: Path,
    event_index: int,
) -> dict[str, Any]:
    csa_reference = (
        latest_turn["canonical_semantic_artifact_reference"]
        if latest_turn is not None
        else conversation["current_csa_reference"]
    )
    csa_hash = (
        latest_turn["canonical_semantic_artifact_hash"]
        if latest_turn is not None
        else conversation["current_csa_hash"]
    )
    lineage = deepcopy(latest_turn["replay_lineage"]) if latest_turn is not None else []
    confirmation_result = create_shared_confirmation_model(
        confirmation_id=f"{_require_string(classification_id, 'classification_id')}:UHCL-CONFIRMATION",
        source_component=SOURCE_COMPONENT_UBTR,
        target_human_context="ACLI_OPERATOR",
        communication_level=LEVEL_STANDARD,
        confirmation_prompt="Confirm, reject, clarify, modify, or continue.",
        required_human_action="map captured terminal input to canonical UHCL response class",
        evidence_references=[
            {
                "evidence_reference": conversation["conversation_id"],
                "evidence_hash": conversation["artifact_hash"],
            },
            {
                "evidence_reference": csa_reference,
                "evidence_hash": csa_hash,
            },
        ],
        created_at=classified_at,
        replay_dir=replay_path / f"{event_index:03d}_uhcl_confirmation",
        csa_reference=csa_reference,
        csa_hash=csa_hash,
        replay_lineage=lineage,
        rollback_reference=f"ROLLBACK-{_require_string(classification_id, 'classification_id')}:UHCL-CONFIRMATION",
        non_authority_notices=[
            "UHCL confirmation is evidence only.",
            "ACLI input capture does not create approval or authorization.",
        ],
    )
    render_result = render_uhcl_artifact_for_acli(
        render_id=f"{_require_string(classification_id, 'classification_id')}:UHCL-RENDER",
        uhcl_artifact=confirmation_result["shared_confirmation_artifact"],
        communication_level=LEVEL_STANDARD,
        rendered_at=classified_at,
        replay_dir=replay_path / f"{event_index:03d}_uhcl_confirmation_render",
    )
    canonical_response = CANONICAL_UHCL_CONFIRMATION_CLASSES.get(classification)
    response_hash = None
    response_reference = None
    response_status = "COMPATIBILITY_UNKNOWN_INPUT_FAILED_CLOSED"
    if canonical_response is not None:
        response_result = capture_uhcl_human_response(
            response_id=f"{_require_string(classification_id, 'classification_id')}:UHCL-RESPONSE",
            rendered_artifact=render_result["artifact"],
            operator_input=operator_input,
            captured_at=classified_at,
            replay_dir=replay_path / f"{event_index:03d}_uhcl_confirmation_response",
        )
        response_hash = response_result["artifact_hash"]
        response_reference = response_result["replay_reference"]
        response_status = "CANONICAL_RESPONSE_CAPTURED"
    return {
        "migration_version": ACLI_UHCL_COMMAND_CONSUMPTION_MIGRATION_VERSION,
        "command_surface": "ACLI_OPERATOR_CONFIRMATION_CLASSIFICATION",
        "acli_role": "PRESENTATION_ADAPTER",
        "legacy_wrapper_retained": True,
        "uhcl_source_artifact_type": confirmation_result["shared_confirmation_artifact"]["artifact_type"],
        "uhcl_source_artifact_hash": confirmation_result["shared_confirmation_artifact_hash"],
        "uhcl_source_replay_reference": confirmation_result["shared_confirmation_replay_reference"],
        "uhcl_render_artifact_hash": render_result["artifact"]["artifact_hash"],
        "uhcl_render_replay_reference": render_result["replay_reference"],
        "uhcl_response_artifact_hash": response_hash,
        "uhcl_response_replay_reference": response_reference,
        "uhcl_response_capture_status": response_status,
        "legacy_confirmation_classification": classification,
        "canonical_uhcl_response_class": canonical_response,
        "turn_id": turn_id,
        "semantic_translation_performed": False,
        "explanation_generated_by_acli": False,
        "confirmation_logic_performed_by_acli": False,
        "provider_orchestration_performed": False,
        "worker_orchestration_performed": False,
        "governance_performed": False,
        "replay_owned_by_acli": False,
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
