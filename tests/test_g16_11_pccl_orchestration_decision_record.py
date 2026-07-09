"""Regression coverage for G16-11 PCCL orchestration decision records."""

from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
    platform_capability_certification_evidence,
)
from aigol.runtime.platform_core_cognition_layer import (
    PCCL_ORCHESTRATION_DECISION_RECORD_ARTIFACT_V1,
    PCCL_ORCHESTRATION_DECISION_RECORD_VERSION,
    PCCL_PROPOSAL_CANCELLED,
    PCCL_PROPOSAL_CONTEXT_READY,
    PCCL_PROPOSAL_CREATED,
    PCCL_PROPOSAL_ESCALATED,
    PCCL_PROPOSAL_POLICY_READY,
    PlatformCoreCognitionLayer,
    create_canonical_context_envelope,
    create_canonical_policy_envelope,
    create_pccl_orchestration_decision_record,
    create_pccl_proposal_lifecycle,
    create_pccl_reference_binding,
    create_pccl_session,
    mark_pccl_proposal_completed,
    mark_pccl_proposal_context_ready,
    mark_pccl_proposal_policy_ready,
    mark_pccl_proposal_provider_completed,
    mark_pccl_proposal_provider_pending,
    mark_pccl_proposal_review_pending,
    mark_pccl_proposal_approval_pending,
    validate_pccl_orchestration_decision_record,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-09T00:00:00Z"


def _pccl_artifacts() -> tuple[dict, dict, dict, dict, dict]:
    session = create_pccl_session(
        session_id="PCCL-G16-11-SESSION-001",
        creation_timestamp=CREATED_AT,
        originating_human_goal_reference="HUMAN-GOAL-G16-11-001",
        replay_reference=".runtime/aicli/g16-11/project_context",
        runtime_reference="RUNTIME-G16-11-001",
        certification_reference="CERT-G16-11-PCCL",
        provider_budget=1,
    )
    context = create_canonical_context_envelope(
        envelope_id="CONTEXT-ENVELOPE-G16-11-001",
        created_at=CREATED_AT,
        pccl_session=session,
        context_references=[
            {
                "reference_type": "KNOWLEDGE_REUSE",
                "reference": "KNOWLEDGE-REUSE-G16-11-001",
                "artifact_hash": replay_hash({"artifact": "KNOWLEDGE_REUSE_G16_11"}),
                "certification_reference": "G14-08",
            }
        ],
    )
    policy = create_canonical_policy_envelope(
        policy_envelope_id="POLICY-ENVELOPE-G16-11-001",
        created_at=CREATED_AT,
        pccl_session=session,
        context_envelope=context,
        policy_references=[
            {
                "reference_type": "GOVERNANCE_POLICY",
                "reference": "GOVERNANCE-POLICY-G16-11-001",
                "artifact_hash": replay_hash({"artifact": "GOVERNANCE_POLICY_G16_11"}),
                "certification_reference": "CERT-GOVERNANCE-G16-11",
            }
        ],
    )
    binding = create_pccl_reference_binding(
        binding_id="PCCL-REFERENCE-BINDING-G16-11-001",
        created_at=CREATED_AT,
        pccl_session=session,
        context_envelope=context,
        policy_envelope=policy,
        service_references=[
            {
                "reference_type": "PROVIDER_PLATFORM",
                "reference": "aigol.provider.certified_provider_attachment",
                "artifact_hash": replay_hash({"artifact": "PROVIDER_PLATFORM_G16_11"}),
                "certification_reference": "G14-44",
            },
            {
                "reference_type": "GOVERNANCE",
                "reference": "docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md",
                "artifact_hash": replay_hash({"artifact": "GOVERNANCE_G16_11"}),
                "certification_reference": "CERT-GOVERNANCE-G16-11",
            },
        ],
    )
    proposal = create_pccl_proposal_lifecycle(
        proposal_id="PCCL-PROPOSAL-G16-11-001",
        created_at=CREATED_AT,
        pccl_session=session,
        reference_binding=binding,
        proposal_reference="PROPOSAL-TRACKING-REFERENCE-G16-11-001",
    )
    return session, context, policy, binding, proposal


def _advance_to_completed(proposal: dict) -> dict:
    context_ready = mark_pccl_proposal_context_ready(
        proposal_lifecycle=proposal,
        context_reference="CONTEXT-ENVELOPE-G16-11-001",
        updated_at="2026-07-09T00:01:00Z",
    )
    policy_ready = mark_pccl_proposal_policy_ready(
        proposal_lifecycle=context_ready,
        policy_reference="POLICY-ENVELOPE-G16-11-001",
        updated_at="2026-07-09T00:02:00Z",
    )
    provider_pending = mark_pccl_proposal_provider_pending(
        proposal_lifecycle=policy_ready,
        provider_request_reference="PROVIDER-REQUEST-G16-11-001",
        updated_at="2026-07-09T00:03:00Z",
    )
    provider_completed = mark_pccl_proposal_provider_completed(
        proposal_lifecycle=provider_pending,
        provider_completion_reference="PROVIDER-COMPLETION-G16-11-001",
        updated_at="2026-07-09T00:04:00Z",
    )
    review_pending = mark_pccl_proposal_review_pending(
        proposal_lifecycle=provider_completed,
        review_reference="REVIEW-G16-11-001",
        updated_at="2026-07-09T00:05:00Z",
    )
    approval_pending = mark_pccl_proposal_approval_pending(
        proposal_lifecycle=review_pending,
        approval_reference="APPROVAL-G16-11-001",
        updated_at="2026-07-09T00:06:00Z",
    )
    return mark_pccl_proposal_completed(
        proposal_lifecycle=approval_pending,
        completion_reference="COMPLETION-G16-11-001",
        updated_at="2026-07-09T00:07:00Z",
    )


def _decision_record(
    *,
    proposal: dict | None = None,
    selected_next_lifecycle_transition: str = "",
) -> dict:
    session, context, policy, binding, created_proposal = _pccl_artifacts()
    return create_pccl_orchestration_decision_record(
        decision_id="PCCL-DECISION-G16-11-001",
        created_at="2026-07-09T00:08:00Z",
        pccl_session=session,
        context_envelope=context,
        policy_envelope=policy,
        reference_binding=binding,
        proposal_lifecycle=proposal or created_proposal,
        selected_next_lifecycle_transition=selected_next_lifecycle_transition,
        decision_rationale_reference="DECISION-RATIONALE-G16-11-001",
        supporting_evidence_references=[
            {
                "reference_type": "PROVIDER_PLATFORM",
                "reference": "PROVIDER-EVIDENCE-G16-11-001",
                "artifact_hash": replay_hash({"artifact": "PROVIDER_EVIDENCE_G16_11"}),
                "certification_reference": "G14-44",
            }
        ],
    )


def test_pccl_orchestration_decision_record_identifies_admissible_transition_without_execution() -> None:
    decision = _decision_record()

    assert decision["artifact_type"] == PCCL_ORCHESTRATION_DECISION_RECORD_ARTIFACT_V1
    assert decision["pccl_orchestration_decision_record_version"] == PCCL_ORCHESTRATION_DECISION_RECORD_VERSION
    assert decision["current_lifecycle_state"] == PCCL_PROPOSAL_CREATED
    assert decision["admissible_next_lifecycle_transitions"] == [
        PCCL_PROPOSAL_CONTEXT_READY,
        PCCL_PROPOSAL_ESCALATED,
        PCCL_PROPOSAL_CANCELLED,
    ]
    assert decision["selected_next_lifecycle_transition"] == PCCL_PROPOSAL_CONTEXT_READY
    assert decision["transition_executed"] is False
    assert decision["platform_core_service_invoked"] is False
    assert decision["provider_selected"] is False
    assert decision["provider_invoked"] is False
    assert decision["governance_executed"] is False
    assert decision["prompt_generated"] is False
    assert validate_pccl_orchestration_decision_record(decision) == decision


def test_pccl_orchestration_decision_record_accepts_explicit_admissible_transition() -> None:
    decision = _decision_record(selected_next_lifecycle_transition=PCCL_PROPOSAL_ESCALATED)

    assert decision["selected_next_lifecycle_transition"] == PCCL_PROPOSAL_ESCALATED
    assert validate_pccl_orchestration_decision_record(decision) == decision


def test_pccl_orchestration_decision_record_records_terminal_fail_closed_state() -> None:
    session, context, policy, binding, proposal = _pccl_artifacts()
    completed = _advance_to_completed(proposal)
    decision = create_pccl_orchestration_decision_record(
        decision_id="PCCL-DECISION-G16-11-TERMINAL",
        created_at="2026-07-09T00:08:00Z",
        pccl_session=session,
        context_envelope=context,
        policy_envelope=policy,
        reference_binding=binding,
        proposal_lifecycle=completed,
    )

    assert decision["current_lifecycle_state"] == "COMPLETED"
    assert decision["admissible_next_lifecycle_transitions"] == []
    assert decision["selected_next_lifecycle_transition"] == ""
    assert decision["fail_closed_reason"] == "TERMINAL_PROPOSAL_LIFECYCLE_STATE"
    assert validate_pccl_orchestration_decision_record(decision) == decision


def test_pccl_orchestration_decision_record_fails_closed_on_inadmissible_selected_transition() -> None:
    with pytest.raises(FailClosedRuntimeError, match="selected transition is not admissible"):
        _decision_record(selected_next_lifecycle_transition=PCCL_PROPOSAL_POLICY_READY)


def test_pccl_orchestration_decision_record_fails_closed_on_proposal_binding_mismatch() -> None:
    session, context, policy, binding, _proposal = _pccl_artifacts()
    other_session = create_pccl_session(
        session_id="PCCL-G16-11-OTHER-SESSION",
        creation_timestamp=CREATED_AT,
        originating_human_goal_reference="HUMAN-GOAL-G16-11-OTHER",
    )
    other_context = create_canonical_context_envelope(
        envelope_id="CONTEXT-ENVELOPE-G16-11-OTHER",
        created_at=CREATED_AT,
        pccl_session=other_session,
    )
    other_policy = create_canonical_policy_envelope(
        policy_envelope_id="POLICY-ENVELOPE-G16-11-OTHER",
        created_at=CREATED_AT,
        pccl_session=other_session,
        context_envelope=other_context,
    )
    other_binding = create_pccl_reference_binding(
        binding_id="PCCL-REFERENCE-BINDING-G16-11-OTHER",
        created_at=CREATED_AT,
        pccl_session=other_session,
        context_envelope=other_context,
        policy_envelope=other_policy,
    )
    mismatched_proposal = create_pccl_proposal_lifecycle(
        proposal_id="PCCL-PROPOSAL-G16-11-MISMATCH",
        created_at=CREATED_AT,
        pccl_session=other_session,
        reference_binding=other_binding,
    )

    with pytest.raises(FailClosedRuntimeError, match="proposal session mismatch"):
        create_pccl_orchestration_decision_record(
            decision_id="PCCL-DECISION-G16-11-MISMATCH",
            created_at="2026-07-09T00:08:00Z",
            pccl_session=session,
            context_envelope=context,
            policy_envelope=policy,
            reference_binding=binding,
            proposal_lifecycle=mismatched_proposal,
        )


def test_pccl_orchestration_decision_record_fails_closed_on_tampered_execution_flag() -> None:
    tampered = deepcopy(_decision_record())
    tampered["provider_invoked"] = True
    tampered["artifact_hash"] = replay_hash({key: value for key, value in tampered.items() if key != "artifact_hash"})

    with pytest.raises(FailClosedRuntimeError, match="provider_invoked must be false"):
        validate_pccl_orchestration_decision_record(tampered)


def test_platform_core_cognition_layer_exposes_orchestration_decision_record() -> None:
    service = PlatformCoreCognitionLayer()
    session, context, policy, binding, proposal = _pccl_artifacts()
    decision = service.create_orchestration_decision_record(
        decision_id="PCCL-DECISION-G16-11-SERVICE",
        created_at="2026-07-09T00:08:00Z",
        pccl_session=session,
        context_envelope=context,
        policy_envelope=policy,
        reference_binding=binding,
        proposal_lifecycle=proposal,
    )

    assert decision["decision_id"] == "PCCL-DECISION-G16-11-SERVICE"
    assert decision["decision_record_only"] is True
    assert decision["transition_executed"] is False


def test_pccl_orchestration_decision_record_registry_certification_is_replay_visible() -> None:
    assert is_platform_capability_certified("PCCL_ORCHESTRATION_DECISION_RECORD") is True
    assert platform_capability_certification_evidence("PCCL_ORCHESTRATION_DECISION_RECORD") == (
        "docs/governance/G16_11_PCCL_ORCHESTRATION_DECISION_RECORD.md",
    )
