from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.cli import aicli
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    G29_SEMANTIC_SELECTION_CLARIFICATION_OWNER,
    OPERATIONAL_CLARIFICATION_REPLY,
    OPERATIONAL_GOVERNED_WORK,
    OPERATIONAL_PLATFORM_QUERY,
    PLATFORM_QUERY_ROUTER_BINDING,
    prepare_unified_human_interface_project_context,
    reconstruct_operational_turn_binding,
    validate_operational_clarification_envelope,
    validate_operational_turn_binding,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-15T00:00:00Z"
AUDIT_REQUEST = "Analyze Platform Capability Composition Coverage.\nAudit only."
AUDIT_REPLY = "I am supplying a described implementation change."


def _context(tmp_path: Path, request: str, name: str) -> dict:
    return prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=f"G30-04-{name}",
        message=request,
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
    )


def _reader(values: list[str]):
    iterator = iter(values)
    return lambda _prompt: next(iterator)


@pytest.mark.parametrize(
    "prompt",
    [
        "Show the current Platform Core runtime status.",
        "What capabilities are currently registered in Platform Core?",
        "What is Platform Core?",
    ],
)
def test_informational_turns_use_existing_platform_query_router(
    tmp_path: Path, prompt: str
) -> None:
    context = _context(tmp_path, prompt, replay_hash(prompt)[-12:])
    turn = context["operational_turn_binding"]
    result = context["governed_read_only_work_result"]

    assert turn["turn_kind"] == OPERATIONAL_PLATFORM_QUERY
    assert turn["binding_destination"] == PLATFORM_QUERY_ROUTER_BINDING
    assert turn["selected_query_class"] == "ARCHITECTURAL_KNOWLEDGE"
    assert result["selected_read_only_service"] == "PLATFORM_KNOWLEDGE_RUNTIME"
    assert result["work_type"] == "INFORMATIONAL_QUERY"
    assert context["project_objective_inference"] is None
    assert context["human_conversation_experience"]["response_mode"] == "READ_ONLY_RESULT"
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["repository_mutated"] is False
    assert reconstruct_operational_turn_binding(
        context["operational_turn_binding_reference"]
    )["artifact_hash"] == turn["artifact_hash"]


def test_implementation_request_preserves_existing_approval_workflow(
    tmp_path: Path,
) -> None:
    context = _context(
        tmp_path,
        "Implement a new read-only Platform Core capability.",
        "IMPLEMENTATION",
    )
    turn = context["operational_turn_binding"]
    resolution = context["development_intent_resolution"]

    assert turn["turn_kind"] == OPERATIONAL_GOVERNED_WORK
    assert turn["binding_destination"] == "PLATFORM_CORE_PROJECT_SERVICES"
    assert resolution["summary_admissible"] is True
    assert resolution["requires_human_approval"] is True
    assert context["human_conversation_experience"]["response_mode"] == (
        "APPROVAL_PREPARATION"
    )
    assert turn["human_interface_authority"] is False


def test_g29_clarification_reply_preserves_owner_slot_and_objective(
    tmp_path: Path,
) -> None:
    output: list[str] = []
    result = aicli.run_reference_uhi_session(
        session_id="G30-04-G29-CONTINUITY",
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
        input_reader=_reader(
            [
                "Analyze Platform Capability Composition Coverage.",
                "Audit only.",
                "/send",
                AUDIT_REPLY,
                "/send",
                "/exit",
            ]
        ),
        output_writer=output.append,
    )
    context = result["platform_core_project_services_context"]
    turn = context["operational_turn_binding"]
    route = context["semantic_capability_runtime_route"]
    continuity = context["clarification_continuity"]

    assert turn["turn_kind"] == OPERATIONAL_CLARIFICATION_REPLY
    assert turn["binding_destination"] == G29_SEMANTIC_SELECTION_CLARIFICATION_OWNER
    assert turn["originating_semantic_slot"] == "input_artifact_family"
    assert turn["continuation_semantic_slot"] == "input_artifact_family"
    assert continuity["owner_specific_continuation"] is True
    assert continuity["semantic_slot"] == "input_artifact_family"
    assert context["development_intent_resolution"]["project_objective_restarted"] is False
    assert route["route_status"] == "SEMANTIC_CAPABILITY_ROUTE_CLARIFICATION_REQUIRED"
    assert context["project_objective_inference"]["source_request"] == AUDIT_REQUEST
    assert "desired_outcome" not in "\n".join(output)
    assert reconstruct_operational_turn_binding(turn["turn_reference"])[
        "artifact_hash"
    ] == turn["artifact_hash"]


def test_textual_input_family_reply_fails_closed_with_canonical_transport_guidance(
    tmp_path: Path,
) -> None:
    output: list[str] = []
    result = aicli.run_reference_uhi_session(
        session_id="G30-04-G29-TEXTUAL-INPUT-FAMILY",
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
        input_reader=_reader(
            [
                "Analyze Platform Capability Composition Coverage.",
                "Audit only.",
                "/send",
                "I am supplying a described implementation change.",
                "/send",
                "described implementation change",
                "/send",
            ]
        ),
        output_writer=output.append,
    )
    context = result["platform_core_project_services_context"]
    turn = context["operational_turn_binding"]
    route = context["semantic_capability_runtime_route"]
    envelope = context["operational_clarification_envelope"]
    conversation = context["human_conversation_experience"]
    rendered = "\n".join(output)

    assert result["session_status"] == (
        "REFERENCE_UHI_SESSION_AWAITING_HUMAN_CLARIFICATION"
    )
    assert turn["binding_destination"] == G29_SEMANTIC_SELECTION_CLARIFICATION_OWNER
    assert turn["originating_semantic_slot"] == "input_artifact_family"
    assert turn["continuation_semantic_slot"] == "input_artifact_family"
    assert envelope["original_message"] == AUDIT_REQUEST
    assert rendered.count(f"original_request: {AUDIT_REQUEST}") == 3
    assert "original_request: described implementation change" not in rendered
    assert route["route_status"] == "SEMANTIC_CAPABILITY_ROUTE_CLARIFICATION_REQUIRED"
    assert route["lifecycle_status"] is None
    assert context["development_intent_resolution"]["clarification_reply_bound"] is True
    assert conversation["clarification_reply_satisfied_semantic_slot"] is False
    assert conversation["canonical_artifact_transport_required"] is True
    assert "descriptive text is bound to the clarification owner" in rendered
    assert "Use /attach <reference>" in rendered
    assert route["provider_invoked"] is False
    assert route["worker_invoked"] is False
    assert route["repository_mutated"] is False
    assert reconstruct_operational_turn_binding(turn["turn_reference"])[
        "artifact_hash"
    ] == turn["artifact_hash"]


def test_clarification_envelope_rejects_owner_slot_and_session_substitution(
    tmp_path: Path,
) -> None:
    context = _context(tmp_path, AUDIT_REQUEST, "SUBSTITUTION")
    envelope = context["operational_clarification_envelope"]

    owner = deepcopy(envelope)
    owner["clarification_owner"] = "GENERIC_PLATFORM_CORE_CLARIFICATION"
    owner["artifact_hash"] = replay_hash({k: v for k, v in owner.items() if k != "artifact_hash"})
    with pytest.raises(FailClosedRuntimeError, match="owner substitution"):
        validate_operational_clarification_envelope(owner)

    slot = deepcopy(envelope)
    slot["semantic_slot"] = "desired_outcome"
    slot["artifact_hash"] = replay_hash({k: v for k, v in slot.items() if k != "artifact_hash"})
    with pytest.raises(FailClosedRuntimeError, match="slot substitution"):
        validate_operational_clarification_envelope(slot)

    with pytest.raises(FailClosedRuntimeError, match="cross-session"):
        validate_operational_clarification_envelope(
            envelope,
            expected_session_id="ANOTHER-SESSION",
        )


def test_reconstruction_rejects_stale_reply_and_route_tampering(
    tmp_path: Path,
) -> None:
    output: list[str] = []
    result = aicli.run_reference_uhi_session(
        session_id="G30-04-REPLAY-TAMPER",
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
        input_reader=_reader(
            [
                "Analyze Platform Capability Composition Coverage.",
                "Audit only.",
                "/send",
                AUDIT_REPLY,
                "/send",
                "/exit",
            ]
        ),
        output_writer=output.append,
    )
    turn = result["platform_core_project_services_context"]["operational_turn_binding"]
    turn_path = Path(turn["turn_reference"])

    stale = deepcopy(turn)
    stale["originating_clarification_envelope_hash"] = replay_hash("stale")
    stale["artifact_hash"] = replay_hash({k: v for k, v in stale.items() if k != "artifact_hash"})
    turn_path.write_text(json.dumps(stale), encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError, match="stale clarification lineage"):
        reconstruct_operational_turn_binding(turn_path)

    turn_path.write_text(json.dumps(turn), encoding="utf-8")
    route_path = Path(turn["continuation_route_reference"]) / (
        "project_context_semantic_capability_route.json"
    )
    route = json.loads(route_path.read_text(encoding="utf-8"))
    route["failure_reason"] = "tampered"
    route_path.write_text(json.dumps(route), encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError, match="artifact hash mismatch"):
        reconstruct_operational_turn_binding(turn_path)


def test_aicli_transports_platform_core_envelope_without_semantic_authority(
    tmp_path: Path,
) -> None:
    output: list[str] = []
    result = aicli.run_reference_uhi_session(
        session_id="G30-04-HI-BOUNDARY",
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
        input_reader=_reader(
            [
                "Analyze Platform Capability Composition Coverage.",
                "Audit only.",
                "/send",
                "/exit",
            ]
        ),
        output_writer=output.append,
    )
    context = result["platform_core_project_services_context"]
    envelope = context["operational_clarification_envelope"]

    assert envelope["clarification_owner"] == G29_SEMANTIC_SELECTION_CLARIFICATION_OWNER
    assert envelope["semantic_slot"] == "input_artifact_family"
    assert envelope["human_interface_authority"] is False
    assert result["aicli_authorizes"] is False
    assert result["aicli_executes"] is False
    assert result["aicli_owns_replay"] is False
    assert context["interface_authority"] is False
