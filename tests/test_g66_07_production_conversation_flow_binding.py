"""Focused G66-07 constitutional production Conversation binding tests."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json
from pathlib import Path

import pytest

from aigol.cli import aicli
from aigol.runtime.human_interface_runtime_entry_service import (
    run_human_interface_runtime_entry,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.platform_core_conversation_interpreter_proposal_runtime_v2 import (
    ADMISSIBLE,
)
from aigol.runtime.production_conversation_flow_binding import (
    CFA_DEVELOPMENT_GOVERNANCE,
    CFA_EXECUTION,
    CFA_FAILURE,
    CFA_OBJECTIVE_COMMITMENT,
    CFA_SELF_KNOWLEDGE,
    CLARIFICATION_REPLY,
    NEW_HUMAN_INTENT,
    compose_production_conversation_flow_binding_v1,
    create_human_intent_precedence_decision_v1,
    create_owner_bound_clarification_envelope_v1,
    reconstruct_production_conversation_flow_binding_v1,
    validate_human_intent_precedence_decision_v1,
    validate_owner_bound_clarification_envelope_v1,
    validate_production_conversation_flow_binding_v1,
)
from aigol.runtime.self_knowledge_request_classification import (
    classify_self_knowledge_request,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-08-03T12:00:00Z"


def _fail_runner(*_args, **_kwargs):
    raise AssertionError("governed runtime must not be entered")


def _entry(tmp_path: Path, request: str, *, session: str = "G66-07") -> dict:
    return run_human_interface_runtime_entry(
        interface_name="G66-07-TEST-INTERFACE",
        session_id=session,
        human_requests=[request],
        created_at=CREATED_AT,
        runtime_root=tmp_path,
        workspace=".",
        governed_runtime_runner=_fail_runner,
    )


def _compose(tmp_path: Path, request: str, *, session: str = "G66-07") -> dict:
    return compose_production_conversation_flow_binding_v1(
        interface_identity="G66-07-TEST-INTERFACE",
        session_identity=session,
        request_text=request,
        runtime_root=tmp_path,
        workspace_identity=".",
        created_at=CREATED_AT,
        prior_workspace_state=None,
    )


def test_canonical_entry_public_signature_retains_legacy_parameters() -> None:
    assert list(inspect.signature(run_human_interface_runtime_entry).parameters) == [
        "interface_name",
        "session_id",
        "human_requests",
        "created_at",
        "runtime_root",
        "workspace",
        "governed_runtime_runner",
        "presentation",
        "operator_context",
        "explicit_canonical_artifacts",
        "explicit_canonical_artifact_references",
        "approved_implementation_turn_binding",
        "approved_development_composition_plan_hash",
        "approved_durable_governed_work_hash",
        "approved_proposal_preview_hash",
        "approved_approval_request_hash",
        "g31_application_state",
        "g31_human_action",
        "g31_human_actor_id",
        "g31_worker_process_runner",
        "g31_synthesis_preflight_prompt",
        "canonical_condensation_proposal_inputs",
        "worker_capability_completion_capture",
        "request_envelope",
        "continuation_envelope",
    ]


def test_default_aicli_first_turn_uses_only_the_canonical_entry() -> None:
    source = inspect.getsource(aicli._submit_composed_request)

    assert "run_human_interface_runtime_entry(" in source
    assert "prepare_unified_human_interface_project_context(" not in source
    assert 'operator_context="AICLI_NEW_TURN_PRE_APPROVAL"' in source


def test_default_aicli_emits_binding_evidence_without_changing_read_only_result(
    tmp_path: Path,
) -> None:
    result = aicli.run_reference_uhi_submit_session(
        session_id="G66-07-DEFAULT",
        created_at=CREATED_AT,
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: "Show architecture.",
        output_writer=lambda _line: None,
    )
    event = next(item for item in result["transcript"] if item["event"] == "message")
    context = result["platform_core_project_services_context"]

    assert event["canonical_human_entry_used"] is True
    assert event["production_conversation_flow_binding_hash"] == context[
        "production_conversation_flow_binding_hash"
    ]
    assert context["human_conversation_experience"]["response_mode"] == (
        "READ_ONLY_RESULT"
    )
    assert context["project_objective_inference"] is None
    assert result["runtime_entered"] is False


def test_exact_self_knowledge_traverses_conversation_binding_without_objective(
    tmp_path: Path,
) -> None:
    result = _entry(tmp_path, "Show architecture.")
    capture = result["production_conversation_binding"]
    binding = result["production_conversation_flow_binding"]
    context = result["platform_core_project_services_context"]

    assert result["human_interface_runtime_entry_service_used"] is True
    assert capture["conversation_identity"]
    assert capture["proposal_validation"]["validation_disposition"] == ADMISSIBLE
    assert capture["proposal_validation_precedes_commit"] is True
    assert capture["proposal_commit"] is not None
    assert capture["platform_flow_selection"]["service_invoked"] is False
    assert capture["g61_proposal_assistance_disposition"] == (
        "NOT_REQUIRED_DETERMINISTIC_PROPOSAL_VALIDATED"
    )
    assert binding["requested_target_flow_id"] == CFA_SELF_KNOWLEDGE
    assert binding["permitted_next_flow_id"] == CFA_SELF_KNOWLEDGE
    assert binding["objective_commitment_required"] is False
    assert context["project_objective_inference"] is None
    assert context["human_conversation_experience"]["response_mode"] == (
        "READ_ONLY_RESULT"
    )
    assert result["canonical_presentation_flow_binding_hash"] == binding[
        "artifact_hash"
    ]
    assert result["canonical_presentation_response_mode"] == "READ_ONLY_RESULT"
    assert result["runtime_entered"] is False


def test_g66_12_restores_common_clarification_without_new_turn_selection(
    tmp_path: Path,
) -> None:
    first = aicli.run_reference_uhi_submit_session(
        session_id="G66-07-PRECEDENCE",
        created_at=CREATED_AT,
        runtime_root=tmp_path,
        workspace=".",
        stdin_reader=lambda: (
            "Analyze Platform Capability Composition Coverage.\nAudit only."
        ),
        input_reader=lambda _prompt: (_ for _ in ()).throw(EOFError()),
        output_writer=lambda _line: None,
    )
    assert first["session_status"] == "REFERENCE_UHI_SUBMIT_AWAITING_HUMAN_INPUT"

    result = _entry(
        tmp_path,
        "Show architecture.",
        session="G66-07-PRECEDENCE",
    )
    decision = result["human_intent_precedence_decision"]
    context = result["platform_core_project_services_context"]

    first_context = first["platform_core_project_services_context"]
    assert first_context["owner_bound_clarification_envelope"][
        "originating_owner"
    ] == (
        "G29_SEMANTIC_CAPABILITY_SELECTION"
    )
    assert first_context["operational_clarification_envelope"] is None
    assert decision == first_context["human_intent_precedence_decision"]
    assert context["production_conversation_flow_binding"] == first_context[
        "production_conversation_flow_binding"
    ]
    assert context["human_intent_precedence_before_restored_context"] is False
    assert context["human_conversation_experience"]["response_mode"] == (
        "CLARIFICATION"
    )


def test_active_clarification_reply_remains_bound_to_originating_owner() -> None:
    classification = classify_self_knowledge_request("/reply validation manifest")
    active = {
        "artifact_type": "PLATFORM_CORE_OPERATIONAL_CLARIFICATION_ENVELOPE_V1",
        "clarification_identity": "CLARIFICATION-1",
        "clarification_owner": "G29_SEMANTIC_CAPABILITY_SELECTION",
        "artifact_hash": replay_hash("active-clarification"),
    }
    decision = create_human_intent_precedence_decision_v1(
        request_text="/reply validation manifest",
        interface_identity="test-interface",
        session_identity="SESSION-1",
        workspace_identity=".",
        request_classification=classification,
        active_clarification_envelope=active,
        created_at=CREATED_AT,
    )
    envelope = create_owner_bound_clarification_envelope_v1(
        originating_flow_id="CFA-CLARIFICATION-V1",
        originating_owner=decision["active_clarification_owner"],
        originating_artifact_reference="/replay/active.json",
        originating_artifact_hash=decision["active_clarification_hash"],
        workspace_identity_hash=decision["workspace_identity_hash"],
        session_identity="SESSION-1",
        conversation_identity="CONVERSATION-1",
        subject_identity="input_artifact_family",
        expected_revision=1,
        reason_code="ACTIVE_OWNER_CLARIFICATION_REPLY",
        required_field_or_evidence_codes=["input_artifact_family"],
        permitted_reply_kind="OWNER_BOUND_REPLY",
        created_at=CREATED_AT,
        expires_at="2026-08-03T13:00:00Z",
    )

    assert decision["decision_disposition"] == CLARIFICATION_REPLY
    assert envelope["originating_owner"] == "G29_SEMANTIC_CAPABILITY_SELECTION"
    with pytest.raises(FailClosedRuntimeError):
        validate_owner_bound_clarification_envelope_v1(
            envelope,
            expected_originating_owner="SUBSTITUTED_OWNER",
        )


def test_development_and_execution_targets_preserve_objective_and_authority_gates(
    tmp_path: Path,
) -> None:
    development = _entry(tmp_path, "Implement a validator.", session="DEV")
    execution = _entry(
        tmp_path,
        "Run the governed execution workflow.",
        session="EXEC",
    )

    development_binding = development["production_conversation_flow_binding"]
    execution_binding = execution["production_conversation_flow_binding"]
    assert development_binding["requested_target_flow_id"] == (
        CFA_DEVELOPMENT_GOVERNANCE
    )
    assert development_binding["permitted_next_flow_id"] == CFA_OBJECTIVE_COMMITMENT
    assert development_binding["objective_commitment_required"] is True
    assert execution_binding["requested_target_flow_id"] == CFA_EXECUTION
    assert execution_binding["permitted_next_flow_id"] == CFA_OBJECTIVE_COMMITMENT
    assert execution_binding["objective_commitment_required"] is True
    development_context = development["platform_core_project_services_context"]
    execution_context = execution["platform_core_project_services_context"]
    for context in (development_context, execution_context):
        assert context["project_objective_inference"] is None
        assert context["admission_precedence"] is None
        assert context["constitutional_development_governance"] is None
        assert context["owner_bound_clarification_envelope"][
            "originating_owner"
        ] == "CONVERSATION_LAYER_PLUS_HUMAN_AUTHORITY"
    for binding in (development_binding, execution_binding):
        assert binding["authorization_created"] is False
        assert binding["worker_invoked"] is False
        assert binding["execution_invoked"] is False
    assert development["runtime_entered"] is False
    assert execution["runtime_entered"] is False


def test_human_stop_fails_closed_before_semantic_commit_or_effect(tmp_path: Path) -> None:
    capture = _compose(tmp_path, "/stop", session="STOP")
    binding = capture["production_conversation_flow_binding"]

    assert capture["proposal_commit"] is None
    assert capture["conversation_state"]["revision"] == 0
    assert binding["requested_target_flow_id"] == CFA_FAILURE
    assert binding["authorization_created"] is False
    assert binding["worker_invoked"] is False
    assert binding["execution_invoked"] is False


def test_binding_replay_reconstructs_and_detects_predecessor_tampering(
    tmp_path: Path,
) -> None:
    capture = _compose(tmp_path, "Show architecture.")
    replay_reference = capture["production_conversation_replay_reference"]

    reconstruction = reconstruct_production_conversation_flow_binding_v1(
        replay_reference
    )
    assert reconstruction["reconstruction_verified"] is True
    proposal_path = Path(replay_reference) / "001_interpreter_proposal.json"
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    proposal["interpreter_version"] = "tampered"
    proposal_path.write_text(json.dumps(proposal), encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError):
        reconstruct_production_conversation_flow_binding_v1(replay_reference)


def test_project_services_revalidates_every_binding_predecessor(
    tmp_path: Path,
) -> None:
    capture = _compose(tmp_path, "Show architecture.", session="PS-TAMPER")
    proposal_path = Path(
        capture["production_conversation_replay_reference"]
    ) / "001_interpreter_proposal.json"
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    proposal["interpreter_version"] = "tampered"
    proposal_path.write_text(json.dumps(proposal), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError):
        prepare_unified_human_interface_project_context(
            interface_name="G66-07-TEST-INTERFACE",
            session_id="PS-TAMPER",
            message="Show architecture.",
            runtime_root=tmp_path,
            workspace=".",
            created_at=CREATED_AT,
            human_intent_precedence_decision=capture[
                "human_intent_precedence_decision"
            ],
            production_conversation_flow_binding=capture[
                "production_conversation_flow_binding"
            ],
        )


def test_all_three_additive_validators_are_closed_and_tamper_evident(
    tmp_path: Path,
) -> None:
    capture = _compose(tmp_path, "Show architecture.")
    decision = capture["human_intent_precedence_decision"]
    binding = capture["production_conversation_flow_binding"]

    validate_human_intent_precedence_decision_v1(decision)
    validate_production_conversation_flow_binding_v1(binding)
    extra = deepcopy(decision)
    extra["unexpected"] = True
    with pytest.raises(FailClosedRuntimeError):
        validate_human_intent_precedence_decision_v1(extra)
    changed = deepcopy(binding)
    changed["requested_target_owner"] = "SUBSTITUTED_OWNER"
    unhashed = dict(changed)
    unhashed.pop("artifact_hash")
    changed["artifact_hash"] = replay_hash(unhashed)
    with pytest.raises(FailClosedRuntimeError):
        validate_production_conversation_flow_binding_v1(changed)


def test_existing_g31_preflight_branch_remains_outside_new_turn_composition(
    tmp_path: Path,
) -> None:
    result = run_human_interface_runtime_entry(
        interface_name="test-human-interface",
        session_id="G66-07-G31",
        human_requests=[],
        created_at=CREATED_AT,
        runtime_root=tmp_path,
        workspace="/workspace/sapianta",
        governed_runtime_runner=lambda **_: {},
        g31_human_actor_id="HUMAN-G66-07",
        g31_synthesis_preflight_prompt="validate the exact runtime",
    )

    assert result["codex_synthesis_preflight_capture"][
        "synthesis_preflight_status"
    ] == "SYNTHESIS_PREFLIGHT_READY"
    assert result["g31_pending_action"] is None
    assert "production_conversation_flow_binding" not in result
    assert not (tmp_path / "production_conversation_flow_binding").exists()
