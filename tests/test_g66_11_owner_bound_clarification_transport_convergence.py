"""Focused G66-11 owner-bound clarification transport convergence tests."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from aigol.cli.aicli import run_reference_uhi_submit_session
from aigol.runtime.human_interface_runtime_entry_service import (
    run_human_interface_runtime_entry,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    reconstruct_operational_turn_binding,
)
from aigol.runtime.production_conversation_flow_binding import (
    CFA_CLARIFICATION,
    CFA_DEVELOPMENT_GOVERNANCE,
    CFA_OBJECTIVE_COMMITMENT,
    reconstruct_production_conversation_flow_binding_v1,
    validate_owner_bound_clarification_envelope_v1,
)
from aigol.runtime.transport.serialization import load_json, replay_hash


CREATED_AT = "2026-08-03T17:00:00Z"
PROJECT_CLARIFICATION_REQUEST = (
    "Analyze Platform Capability Composition Coverage.\nAudit only."
)
ACTIONABLE_CLARIFICATION_REQUEST = "Implement a validator."


def _fail_runner(*_args, **_kwargs):
    raise AssertionError("clarification must stop before the governed runner")


def _submit(
    tmp_path: Path,
    request: str,
    *,
    session: str,
    output: list[str] | None = None,
) -> dict:
    sink = output if isinstance(output, list) else []
    return run_reference_uhi_submit_session(
        session_id=session,
        created_at=CREATED_AT,
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: request,
        input_reader=lambda _prompt: (_ for _ in ()).throw(EOFError()),
        output_writer=sink.append,
        runtime_runner=_fail_runner,
    )


def _latest_workspace_state(tmp_path: Path, session: str) -> dict:
    path = sorted(
        (tmp_path / session / "workspace_state").glob(
            "*_platform_core_workspace_state_recorded.json"
        )
    )[-1]
    return load_json(path)


@pytest.mark.parametrize(
    ("request_text", "expected_owner"),
    [
        (
            ACTIONABLE_CLARIFICATION_REQUEST,
            "CONVERSATION_LAYER_PLUS_HUMAN_AUTHORITY",
        ),
        (
            PROJECT_CLARIFICATION_REQUEST,
            "G29_SEMANTIC_CAPABILITY_SELECTION",
        ),
    ],
)
def test_every_production_clarification_uses_only_owner_bound_transport(
    tmp_path: Path,
    request_text: str,
    expected_owner: str,
) -> None:
    session = "G66-11-ALL-CLARIFICATIONS-" + replay_hash(request_text)[7:19]
    result = _submit(tmp_path, request_text, session=session)
    context = result["platform_core_project_services_context"]
    conversation = context["human_conversation_experience"]
    envelope = context["owner_bound_clarification_envelope"]
    pending = _latest_workspace_state(tmp_path, session)[
        "pending_clarification_request"
    ]

    assert validate_owner_bound_clarification_envelope_v1(
        envelope,
        expected_session_identity=session,
        expected_originating_owner=expected_owner,
    ) == envelope
    assert context["operational_clarification_envelope"] is None
    assert conversation["owner_bound_clarification_envelope"] == envelope
    assert conversation.get("operational_clarification_envelope") is None
    assert pending["owner_bound_clarification_envelope"] == envelope
    assert pending.get("operational_clarification_envelope") is None
    assert result["transcript"][0][
        "owner_bound_clarification_envelope_hash"
    ] == envelope["artifact_hash"]
    assert result["session_status"] == "REFERENCE_UHI_SUBMIT_AWAITING_HUMAN_INPUT"


def test_project_clarification_preserves_originating_owner_and_source_lineage(
    tmp_path: Path,
) -> None:
    result = _submit(
        tmp_path,
        PROJECT_CLARIFICATION_REQUEST,
        session="G66-11-PROJECT-OWNER",
    )
    context = result["platform_core_project_services_context"]
    envelope = context["owner_bound_clarification_envelope"]
    turn = context["operational_turn_binding"]
    source = turn["operational_clarification_envelope"]

    assert envelope["originating_owner"] == source["clarification_owner"]
    assert envelope["originating_artifact_reference"] == context[
        "operational_turn_binding_reference"
    ]
    assert envelope["originating_artifact_hash"] == source["artifact_hash"]
    assert envelope["subject_identity"] == source["semantic_slot"]
    assert turn["owner_bound_clarification_envelope"] == envelope
    assert turn["owner_bound_clarification_envelope_hash"] == envelope[
        "artifact_hash"
    ]

    substituted = deepcopy(envelope)
    substituted["originating_owner"] = "PLATFORM_CORE_PROJECT_SERVICES"
    unhashed = dict(substituted)
    unhashed.pop("artifact_hash")
    substituted["artifact_hash"] = replay_hash(unhashed)
    with pytest.raises(
        FailClosedRuntimeError,
        match="owner substitution",
    ):
        validate_owner_bound_clarification_envelope_v1(
            substituted,
            expected_session_identity="G66-11-PROJECT-OWNER",
            expected_originating_owner="G29_SEMANTIC_CAPABILITY_SELECTION",
        )


def test_conversation_identity_cwm_revision_and_state_hash_are_preserved(
    tmp_path: Path,
) -> None:
    result = run_human_interface_runtime_entry(
        interface_name="G66-11-TEST-INTERFACE",
        session_id="G66-11-CONVERSATION",
        human_requests=[PROJECT_CLARIFICATION_REQUEST],
        created_at=CREATED_AT,
        runtime_root=tmp_path,
        workspace=".",
        governed_runtime_runner=_fail_runner,
    )
    capture = result["production_conversation_binding"]
    context = result["platform_core_project_services_context"]
    binding = context["production_conversation_flow_binding"]
    envelope = context["owner_bound_clarification_envelope"]
    state = capture["conversation_state"]

    assert binding["requested_target_flow_id"] == CFA_CLARIFICATION
    assert envelope["conversation_identity"] == binding["conversation_identity"]
    assert envelope["expected_revision"] == binding["cwm_revision"]
    assert state["envelope"]["conversation_identity"] == binding[
        "conversation_identity"
    ]
    assert state["revision"] == binding["cwm_revision"]
    assert replay_hash(state) == binding["cwm_state_hash"]
    assert capture["proposal_commit"] is not None


def test_clarification_presentation_is_unchanged_and_transport_only(
    tmp_path: Path,
) -> None:
    output: list[str] = []
    result = _submit(
        tmp_path,
        PROJECT_CLARIFICATION_REQUEST,
        session="G66-11-PRESENTATION",
        output=output,
    )
    context = result["platform_core_project_services_context"]
    envelope = context["owner_bound_clarification_envelope"]
    rendered = "\n".join(output)

    assert "Clarification required before governed execution." in rendered
    assert "questions:" in rendered
    assert context["human_conversation_experience"]["response_mode"] == (
        "CLARIFICATION"
    )
    assert envelope["clarification_authority_created"] is False
    assert envelope["human_interface_authority"] is False
    assert envelope["originating_owner"] != "PLATFORM_CORE_PROJECT_SERVICES"
    assert context["project_workspace_authority"] == "PLATFORM_CORE"


def test_query_router_flow_binding_and_governance_behavior_are_unchanged(
    tmp_path: Path,
) -> None:
    project_result = run_human_interface_runtime_entry(
        interface_name="G66-11-TEST-INTERFACE",
        session_id="G66-11-ROUTER",
        human_requests=[PROJECT_CLARIFICATION_REQUEST],
        created_at=CREATED_AT,
        runtime_root=tmp_path,
        workspace=".",
        governed_runtime_runner=_fail_runner,
    )
    actionable_result = run_human_interface_runtime_entry(
        interface_name="G66-11-TEST-INTERFACE",
        session_id="G66-11-ACTIONABLE",
        human_requests=[ACTIONABLE_CLARIFICATION_REQUEST],
        created_at=CREATED_AT,
        runtime_root=tmp_path,
        workspace=".",
        governed_runtime_runner=_fail_runner,
    )
    project_capture = project_result["production_conversation_binding"]
    project_context = project_result["platform_core_project_services_context"]
    actionable_context = actionable_result["platform_core_project_services_context"]

    assert project_capture["platform_flow_selection"]["selection_only"] is True
    assert project_capture["platform_flow_selection"]["service_invoked"] is False
    assert project_context["production_conversation_flow_binding"][
        "requested_target_flow_id"
    ] == CFA_CLARIFICATION
    assert actionable_context["production_conversation_flow_binding"][
        "requested_target_flow_id"
    ] == CFA_DEVELOPMENT_GOVERNANCE
    assert actionable_context["production_conversation_flow_binding"][
        "permitted_next_flow_id"
    ] == CFA_OBJECTIVE_COMMITMENT
    for context in (project_context, actionable_context):
        assert context["constitutional_development_governance"] is None
        assert context["admission_precedence"] is None


def test_clarification_replay_reconstruction_is_deterministic(
    tmp_path: Path,
) -> None:
    result = _submit(
        tmp_path,
        PROJECT_CLARIFICATION_REQUEST,
        session="G66-11-REPLAY",
    )
    context = result["platform_core_project_services_context"]
    binding = context["production_conversation_flow_binding"]
    replay_root = Path(binding["owner_local_replay_references"][0]).parent
    turn_reference = context["operational_turn_binding_reference"]

    first_binding = reconstruct_production_conversation_flow_binding_v1(replay_root)
    second_binding = reconstruct_production_conversation_flow_binding_v1(replay_root)
    first_turn = reconstruct_operational_turn_binding(turn_reference)
    second_turn = reconstruct_operational_turn_binding(turn_reference)

    assert first_binding == second_binding
    assert first_binding["reconstruction_verified"] is True
    assert first_turn == second_turn
    assert first_turn["owner_bound_clarification_envelope_hash"] == context[
        "owner_bound_clarification_envelope"
    ]["artifact_hash"]


def test_g66_12_reuses_g66_11_transport_without_changing_its_artifacts(
    tmp_path: Path,
) -> None:
    session = "G66-11-D1-UNCHANGED"
    first = _submit(tmp_path, PROJECT_CLARIFICATION_REQUEST, session=session)
    second = run_human_interface_runtime_entry(
        interface_name="G66-11-TEST-INTERFACE",
        session_id=session,
        human_requests=["Show architecture."],
        created_at=CREATED_AT,
        runtime_root=tmp_path,
        workspace=".",
        governed_runtime_runner=_fail_runner,
    )

    assert first["platform_core_project_services_context"][
        "owner_bound_clarification_envelope"
    ] is not None
    assert second["human_intent_precedence_decision"] == first[
        "platform_core_project_services_context"
    ]["human_intent_precedence_decision"]
    assert second["production_conversation_flow_binding"] == first[
        "platform_core_project_services_context"
    ]["production_conversation_flow_binding"]
    assert second["production_conversation_binding"][
        "clarification_continuation_restored"
    ] is True
    assert second["production_conversation_binding"][
        "human_intent_reclassified"
    ] is False
