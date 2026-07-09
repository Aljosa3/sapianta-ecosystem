"""Regression coverage for G16-09 PCCL proposal lifecycle foundation."""

from __future__ import annotations

from copy import deepcopy

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    is_platform_capability_certified,
    platform_capability_certification_evidence,
)
from aigol.runtime.platform_core_cognition_layer import (
    PCCL_PROPOSAL_APPROVAL_PENDING,
    PCCL_PROPOSAL_COMPLETED,
    PCCL_PROPOSAL_CONTEXT_READY,
    PCCL_PROPOSAL_CREATED,
    PCCL_PROPOSAL_LIFECYCLE_ARTIFACT_V1,
    PCCL_PROPOSAL_LIFECYCLE_VERSION,
    PCCL_PROPOSAL_POLICY_READY,
    PCCL_PROPOSAL_PROVIDER_COMPLETED,
    PCCL_PROPOSAL_PROVIDER_PENDING,
    PCCL_PROPOSAL_REVIEW_PENDING,
    PlatformCoreCognitionLayer,
    create_canonical_context_envelope,
    create_canonical_policy_envelope,
    create_pccl_proposal_lifecycle,
    create_pccl_reference_binding,
    create_pccl_session,
    mark_pccl_proposal_approval_pending,
    mark_pccl_proposal_completed,
    mark_pccl_proposal_context_ready,
    mark_pccl_proposal_policy_ready,
    mark_pccl_proposal_provider_completed,
    mark_pccl_proposal_provider_pending,
    mark_pccl_proposal_review_pending,
    validate_pccl_proposal_lifecycle,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-09T00:00:00Z"


def _session() -> dict:
    return create_pccl_session(
        session_id="PCCL-G16-09-SESSION-001",
        creation_timestamp=CREATED_AT,
        originating_human_goal_reference="HUMAN-GOAL-G16-09-001",
        replay_reference=".runtime/aicli/g16-09/project_context",
        runtime_reference="RUNTIME-G16-09-001",
        certification_reference="CERT-G16-09-PCCL",
        provider_budget=2,
    )


def _context_envelope(session: dict) -> dict:
    return create_canonical_context_envelope(
        envelope_id="CONTEXT-ENVELOPE-G16-09-001",
        created_at=CREATED_AT,
        pccl_session=session,
    )


def _policy_envelope(session: dict, context: dict) -> dict:
    return create_canonical_policy_envelope(
        policy_envelope_id="POLICY-ENVELOPE-G16-09-001",
        created_at=CREATED_AT,
        pccl_session=session,
        context_envelope=context,
    )


def _binding(session: dict | None = None) -> dict:
    active_session = session or _session()
    context = _context_envelope(active_session)
    policy = _policy_envelope(active_session, context)
    return create_pccl_reference_binding(
        binding_id="PCCL-REFERENCE-BINDING-G16-09-001",
        created_at=CREATED_AT,
        pccl_session=active_session,
        context_envelope=context,
        policy_envelope=policy,
        service_references=[
            {
                "reference_type": "PROVIDER_PLATFORM",
                "reference": "aigol.provider.certified_provider_attachment",
                "artifact_hash": replay_hash({"artifact": "PROVIDER_PLATFORM_G16_09"}),
                "certification_reference": "G14-44",
            },
            {
                "reference_type": "GOVERNANCE",
                "reference": "docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md",
                "artifact_hash": replay_hash({"artifact": "GOVERNANCE_G16_09"}),
                "certification_reference": "CERT-GOVERNANCE-G16-09",
            },
        ],
    )


def _proposal() -> dict:
    session = _session()
    return create_pccl_proposal_lifecycle(
        proposal_id="PCCL-PROPOSAL-G16-09-001",
        created_at=CREATED_AT,
        pccl_session=session,
        reference_binding=_binding(session),
        proposal_reference="PROPOSAL-TRACKING-REFERENCE-G16-09-001",
    )


def _advance_to_completed(proposal: dict) -> dict:
    context_ready = mark_pccl_proposal_context_ready(
        proposal_lifecycle=proposal,
        context_reference="CONTEXT-ENVELOPE-G16-09-001",
        updated_at="2026-07-09T00:01:00Z",
    )
    policy_ready = mark_pccl_proposal_policy_ready(
        proposal_lifecycle=context_ready,
        policy_reference="POLICY-ENVELOPE-G16-09-001",
        updated_at="2026-07-09T00:02:00Z",
    )
    provider_pending = mark_pccl_proposal_provider_pending(
        proposal_lifecycle=policy_ready,
        provider_request_reference="PROVIDER-REQUEST-G16-09-001",
        updated_at="2026-07-09T00:03:00Z",
    )
    provider_completed = mark_pccl_proposal_provider_completed(
        proposal_lifecycle=provider_pending,
        provider_completion_reference="PROVIDER-COMPLETION-G16-09-001",
        updated_at="2026-07-09T00:04:00Z",
    )
    review_pending = mark_pccl_proposal_review_pending(
        proposal_lifecycle=provider_completed,
        review_reference="REVIEW-G16-09-001",
        updated_at="2026-07-09T00:05:00Z",
    )
    approval_pending = mark_pccl_proposal_approval_pending(
        proposal_lifecycle=review_pending,
        approval_reference="APPROVAL-G16-09-001",
        updated_at="2026-07-09T00:06:00Z",
    )
    return mark_pccl_proposal_completed(
        proposal_lifecycle=approval_pending,
        completion_reference="COMPLETION-G16-09-001",
        updated_at="2026-07-09T00:07:00Z",
    )


def test_pccl_proposal_lifecycle_created_tracks_references_only() -> None:
    proposal = _proposal()

    assert proposal["artifact_type"] == PCCL_PROPOSAL_LIFECYCLE_ARTIFACT_V1
    assert proposal["pccl_proposal_lifecycle_version"] == PCCL_PROPOSAL_LIFECYCLE_VERSION
    assert proposal["proposal_status"] == PCCL_PROPOSAL_CREATED
    assert proposal["proposal_reference"] == "PROPOSAL-TRACKING-REFERENCE-G16-09-001"
    assert proposal["proposal_lifecycle_tracked"] is True
    assert proposal["reference_only_lifecycle"] is True
    assert proposal["proposal_payload_embedded"] is False
    assert proposal["proposal_generated"] is False
    assert proposal["provider_invoked"] is False
    assert proposal["provider_selected"] is False
    assert proposal["governance_executed"] is False
    assert proposal["worker_invoked"] is False
    assert proposal["prompt_generated"] is False
    assert proposal["lifecycle_event_count"] == 1
    assert proposal["artifact_hash"].startswith("sha256:")
    assert validate_pccl_proposal_lifecycle(proposal) == proposal


def test_pccl_proposal_lifecycle_supports_deterministic_state_transitions() -> None:
    completed = _advance_to_completed(_proposal())

    assert completed["proposal_status"] == PCCL_PROPOSAL_COMPLETED
    assert [event["to_status"] for event in completed["lifecycle_events"]] == [
        PCCL_PROPOSAL_CREATED,
        PCCL_PROPOSAL_CONTEXT_READY,
        PCCL_PROPOSAL_POLICY_READY,
        PCCL_PROPOSAL_PROVIDER_PENDING,
        PCCL_PROPOSAL_PROVIDER_COMPLETED,
        PCCL_PROPOSAL_REVIEW_PENDING,
        PCCL_PROPOSAL_APPROVAL_PENDING,
        PCCL_PROPOSAL_COMPLETED,
    ]
    assert completed["provider_request_reference"] == "PROVIDER-REQUEST-G16-09-001"
    assert completed["provider_completion_reference"] == "PROVIDER-COMPLETION-G16-09-001"
    assert completed["completion_reference"] == "COMPLETION-G16-09-001"
    assert completed["provider_invoked"] is False
    assert completed["governance_executed"] is False
    assert validate_pccl_proposal_lifecycle(completed) == completed


def test_platform_core_cognition_layer_exposes_proposal_lifecycle_without_generation() -> None:
    service = PlatformCoreCognitionLayer()
    session = service.create_session(
        session_id="PCCL-G16-09-SERVICE-001",
        creation_timestamp=CREATED_AT,
        originating_human_goal_reference="HUMAN-GOAL-G16-09-SERVICE",
    )
    context = service.create_context_envelope(
        envelope_id="CONTEXT-ENVELOPE-G16-09-SERVICE",
        created_at=CREATED_AT,
        pccl_session=session,
    )
    policy = service.create_policy_envelope(
        policy_envelope_id="POLICY-ENVELOPE-G16-09-SERVICE",
        created_at=CREATED_AT,
        pccl_session=session,
        context_envelope=context,
    )
    binding = service.create_reference_binding(
        binding_id="PCCL-REFERENCE-BINDING-G16-09-SERVICE",
        created_at=CREATED_AT,
        pccl_session=session,
        context_envelope=context,
        policy_envelope=policy,
    )
    proposal = service.create_proposal_lifecycle(
        proposal_id="PCCL-PROPOSAL-G16-09-SERVICE",
        created_at=CREATED_AT,
        pccl_session=session,
        reference_binding=binding,
    )

    assert proposal["pccl_session_id"] == "PCCL-G16-09-SERVICE-001"
    assert proposal["proposal_status"] == PCCL_PROPOSAL_CREATED
    assert proposal["proposal_generated"] is False
    assert proposal["provider_invoked"] is False


def test_pccl_proposal_lifecycle_fails_closed_on_invalid_transition_and_terminal_transition() -> None:
    proposal = _proposal()
    with pytest.raises(FailClosedRuntimeError, match="invalid proposal transition"):
        mark_pccl_proposal_policy_ready(
            proposal_lifecycle=proposal,
            policy_reference="POLICY-ENVELOPE-G16-09-001",
            updated_at="2026-07-09T00:02:00Z",
        )

    completed = _advance_to_completed(proposal)
    with pytest.raises(FailClosedRuntimeError, match="terminal proposal cannot transition"):
        mark_pccl_proposal_review_pending(
            proposal_lifecycle=completed,
            review_reference="REVIEW-AFTER-COMPLETION",
            updated_at="2026-07-09T00:08:00Z",
        )


def test_pccl_proposal_lifecycle_fails_closed_on_binding_session_mismatch() -> None:
    session = _session()
    other_session = create_pccl_session(
        session_id="PCCL-G16-09-OTHER-SESSION",
        creation_timestamp=CREATED_AT,
        originating_human_goal_reference="HUMAN-GOAL-G16-09-OTHER",
    )
    with pytest.raises(FailClosedRuntimeError, match="binding session mismatch"):
        create_pccl_proposal_lifecycle(
            proposal_id="PCCL-PROPOSAL-G16-09-MISMATCH",
            created_at=CREATED_AT,
            pccl_session=session,
            reference_binding=_binding(other_session),
        )


def test_pccl_proposal_lifecycle_fails_closed_on_rehashed_provider_invocation_tampering() -> None:
    tampered = deepcopy(_proposal())
    tampered["provider_invoked"] = True
    tampered["artifact_hash"] = replay_hash({key: value for key, value in tampered.items() if key != "artifact_hash"})

    with pytest.raises(FailClosedRuntimeError, match="provider_invoked must be false"):
        validate_pccl_proposal_lifecycle(tampered)


def test_pccl_proposal_lifecycle_registry_certification_is_replay_visible() -> None:
    assert is_platform_capability_certified("PCCL_PROPOSAL_LIFECYCLE") is True
    assert platform_capability_certification_evidence("PCCL_PROPOSAL_LIFECYCLE") == (
        "docs/governance/G16_09_PCCL_PROPOSAL_LIFECYCLE_FOUNDATION.md",
    )
