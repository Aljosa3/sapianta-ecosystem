"""Certification tests for AIGOL_CAPABILITY_ATTACHMENT_GOVERNANCE_CERTIFICATION_V1."""

from __future__ import annotations

from aigol.runtime.capability_attachment_governance_runtime import (
    ATTACHED,
    ATTACHMENT_CANDIDATE_ARTIFACT_V1,
    ATTACHMENT_CANDIDATE_CREATED,
    ATTACHMENT_CANDIDATE_REPLAY_STEPS,
    ATTACHMENT_REPLAY_STEPS,
    CAPABILITY_ATTACHED_ARTIFACT_V1,
    CAPABILITY_DETACHED_ARTIFACT_V1,
    DETACHED,
    DETACHMENT_CANDIDATE_ARTIFACT_V1,
    DETACHMENT_CANDIDATE_CREATED,
    DETACHMENT_CANDIDATE_REPLAY_STEPS,
    DETACHMENT_REPLAY_STEPS,
    HUMAN_APPROVAL_ARTIFACT_V1,
    attach_capability_to_domain,
    create_capability_attachment_candidate,
    create_capability_detachment_candidate,
    detach_capability_from_domain,
    reconstruct_capability_attachment_governance_replay,
)
from aigol.runtime.capability_lifecycle_governance_runtime import (
    activate_capability_candidate,
    create_capability_activation_candidate,
    create_capability_candidate,
)
from aigol.runtime.domain_lifecycle_governance_runtime import (
    activate_domain_candidate,
    create_domain_activation_candidate,
)
from aigol.runtime.domain_proposal_governance_runtime import (
    APPROVED,
    create_domain_proposal,
    review_domain_proposal,
)
from aigol.runtime.proposal_runtime import CREATED, create_proposal
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-14T00:00:00Z"
CHAIN_ID = "CHAIN-CAPABILITY-ATTACHMENT-GOVERNANCE-CERTIFICATION-000001"


def _approval(**fields: object) -> dict:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_status": APPROVED,
        "approval_granted": True,
        "approved_by": "HUMAN_OPERATOR",
        "approved_at": CREATED_AT,
        "capability_executor_invocation_allowed": False,
        "execution_summary_reference": "EXECUTION-SUMMARY-CAPABILITY-ATTACHMENT-000001",
        "execution_summary_hash": replay_hash({"summary": "capability-attachment"}),
        "human_confirmation_reference": "EXECUTION-SUMMARY-CONFIRMATION-CAPABILITY-ATTACHMENT-000001",
        "human_confirmation_hash": replay_hash({"confirmation": "capability-attachment"}),
        "replay_visible": True,
    }
    artifact.update(fields)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _active_capability(tmp_path) -> dict:
    proposal = create_proposal(
        proposal_id="CAPABILITY-PROPOSAL-ATTACHMENT-000001",
        proposal_type="CAPABILITY_PROPOSAL",
        proposal_source="HUMAN_PROMPT",
        proposal_text="Attach bounded read-only inspection capability to a governed domain.",
        created_at=CREATED_AT,
        replay_reference="REPLAY-CAPABILITY-PROPOSAL-ATTACHMENT-000001",
        replay_dir=tmp_path / "capability_proposal",
        created_by="AIGOL",
        status=CREATED,
    )["proposal_runtime_artifact"]
    candidate = create_capability_candidate(
        capability_candidate_id="CAPABILITY-CANDIDATE-ATTACHMENT-000001",
        capability_proposal_artifact=proposal,
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "capability_candidate",
    )["capability_candidate_artifact"]
    activation_candidate = create_capability_activation_candidate(
        activation_candidate_id="CAPABILITY-ACTIVATION-CANDIDATE-ATTACHMENT-000001",
        capability_candidate_artifact=candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-CAPABILITY-ACTIVATION-CANDIDATE-ATTACHMENT-000001",
            source_capability_candidate=candidate["capability_candidate_id"],
            source_capability_candidate_hash=candidate["artifact_hash"],
            approval_scope="CREATE_CAPABILITY_ACTIVATION_CANDIDATE_ONLY",
            capability_activation_allowed=False,
        ),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "capability_activation_candidate",
    )["capability_activation_candidate_artifact"]
    return activate_capability_candidate(
        active_capability_id="CAPABILITY-ACTIVE-ATTACHMENT-000001",
        activation_candidate_artifact=activation_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-CAPABILITY-ACTIVE-ATTACHMENT-000001",
            source_activation_candidate=activation_candidate["activation_candidate_id"],
            source_activation_candidate_hash=activation_candidate["artifact_hash"],
            approval_scope="ACTIVATE_CAPABILITY_ONLY",
            capability_activation_allowed=True,
        ),
        activated_by="HUMAN_OPERATOR",
        activated_at=CREATED_AT,
        replay_dir=tmp_path / "capability_active",
    )["capability_active_artifact"]


def _active_domain(tmp_path) -> dict:
    proposal = create_domain_proposal(
        proposal_id="DOMAIN-PROPOSAL-ATTACHMENT-000001",
        source_type="HUMAN_REQUEST",
        proposed_domain="AttachmentGovernance",
        need_summary="Human requests a governed domain for attachment certification.",
        requested_by="HUMAN_OPERATOR",
        canonical_chain_id=CHAIN_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "domain_proposal",
    )["domain_proposal_artifact"]
    domain_candidate = review_domain_proposal(
        review_id="DOMAIN-REVIEW-ATTACHMENT-000001",
        domain_proposal_artifact=proposal,
        decision=APPROVED,
        decision_reason="Human approves domain candidate staging.",
        reviewed_by="HUMAN_OPERATOR",
        reviewed_at=CREATED_AT,
        human_approval_reference="HUMAN-DOMAIN-PROPOSAL-ATTACHMENT-000001",
        replay_dir=tmp_path / "domain_candidate",
    )["domain_review_outcome_artifact"]
    activation_candidate = create_domain_activation_candidate(
        activation_candidate_id="DOMAIN-ACTIVATION-CANDIDATE-ATTACHMENT-000001",
        domain_candidate_artifact=domain_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-DOMAIN-ACTIVATION-CANDIDATE-ATTACHMENT-000001",
            source_domain_candidate=domain_candidate["domain_candidate_id"],
            source_domain_candidate_hash=domain_candidate["artifact_hash"],
            approval_scope="CREATE_DOMAIN_ACTIVATION_CANDIDATE_ONLY",
            domain_activation_allowed=False,
            live_registry_mutation_allowed=False,
        ),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "domain_activation_candidate",
    )["domain_activation_candidate_artifact"]
    return activate_domain_candidate(
        active_domain_id="DOMAIN-ACTIVE-ATTACHMENT-000001",
        activation_candidate_artifact=activation_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-DOMAIN-ACTIVE-ATTACHMENT-000001",
            source_activation_candidate=activation_candidate["activation_candidate_id"],
            source_activation_candidate_hash=activation_candidate["artifact_hash"],
            approval_scope="ACTIVATE_DOMAIN_ONLY",
            domain_activation_allowed=True,
            live_registry_mutation_allowed=False,
        ),
        activated_by="HUMAN_OPERATOR",
        activated_at=CREATED_AT,
        replay_dir=tmp_path / "domain_active",
    )["domain_active_artifact"]


def _attachment_candidate(tmp_path) -> dict:
    capability = _active_capability(tmp_path)
    domain = _active_domain(tmp_path)
    return create_capability_attachment_candidate(
        attachment_candidate_id="ATTACHMENT-CANDIDATE-000001",
        active_capability_artifact=capability,
        active_domain_artifact=domain,
        attachment_scope="DOMAIN_SCOPED_READ_ONLY_INSPECTION",
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "attachment_candidate",
    )["attachment_candidate_artifact"]


def _attached(tmp_path) -> dict:
    candidate = _attachment_candidate(tmp_path)
    return attach_capability_to_domain(
        attached_id="CAPABILITY-ATTACHED-000001",
        attachment_candidate_artifact=candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-CAPABILITY-ATTACHMENT-000001",
            source_attachment_candidate=candidate["attachment_candidate_id"],
            source_attachment_candidate_hash=candidate["artifact_hash"],
            approval_scope="ATTACH_CAPABILITY_TO_DOMAIN_ONLY",
            capability_attachment_allowed=True,
        ),
        attached_by="HUMAN_OPERATOR",
        attached_at=CREATED_AT,
        replay_dir=tmp_path / "attached",
    )["capability_attached_artifact"]


def test_capability_attachment_without_approval_does_not_attach(tmp_path) -> None:
    candidate = _attachment_candidate(tmp_path)
    capture = attach_capability_to_domain(
        attached_id="CAPABILITY-ATTACHED-NO-APPROVAL",
        attachment_candidate_artifact=candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-CAPABILITY-ATTACHMENT-PENDING",
            approval_status="PENDING",
            approval_granted=False,
            source_attachment_candidate=candidate["attachment_candidate_id"],
            source_attachment_candidate_hash=candidate["artifact_hash"],
            approval_scope="ATTACH_CAPABILITY_TO_DOMAIN_ONLY",
            capability_attachment_allowed=True,
        ),
        attached_by="HUMAN_OPERATOR",
        attached_at=CREATED_AT,
        replay_dir=tmp_path / "attached_no_approval",
    )
    artifact = capture["capability_attached_artifact"]

    assert candidate["artifact_type"] == ATTACHMENT_CANDIDATE_ARTIFACT_V1
    assert candidate["attachment_candidate_status"] == ATTACHMENT_CANDIDATE_CREATED
    assert candidate["attachment_candidate_authoritative"] is False
    assert capture["attachment_status"] == "FAILED_CLOSED"
    assert artifact["capability_attached"] is False
    assert artifact["capability_executor_invoked"] is False
    assert "explicit human approval required" in capture["failure_reason"]


def test_approved_attachment_reaches_attached(tmp_path) -> None:
    candidate = _attachment_candidate(tmp_path)
    capture = attach_capability_to_domain(
        attached_id="CAPABILITY-ATTACHED-000001",
        attachment_candidate_artifact=candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-CAPABILITY-ATTACHMENT-000001",
            source_attachment_candidate=candidate["attachment_candidate_id"],
            source_attachment_candidate_hash=candidate["artifact_hash"],
            approval_scope="ATTACH_CAPABILITY_TO_DOMAIN_ONLY",
            capability_attachment_allowed=True,
        ),
        attached_by="HUMAN_OPERATOR",
        attached_at=CREATED_AT,
        replay_dir=tmp_path / "attached",
    )
    attached = capture["capability_attached_artifact"]
    replay = reconstruct_capability_attachment_governance_replay(tmp_path / "attached", ATTACHMENT_REPLAY_STEPS)

    assert attached["artifact_type"] == CAPABILITY_ATTACHED_ARTIFACT_V1
    assert attached["attachment_status"] == ATTACHED
    assert attached["capability_attached"] is True
    assert attached["capability_detached"] is False
    assert attached["capability_executor_invoked"] is False
    assert replay["status"] == ATTACHED
    assert replay["fail_closed_preserved"] is True


def test_capability_attached_to_domain_preserves_scope(tmp_path) -> None:
    candidate = _attachment_candidate(tmp_path)
    replay = reconstruct_capability_attachment_governance_replay(
        tmp_path / "attachment_candidate",
        ATTACHMENT_CANDIDATE_REPLAY_STEPS,
    )

    assert candidate["attachment_scope"] == "DOMAIN_SCOPED_READ_ONLY_INSPECTION"
    assert candidate["domain_name"] == "AttachmentGovernance"
    assert candidate["source_active_domain"]
    assert candidate["source_active_capability"]
    assert candidate["capability_executor_invoked"] is False
    assert replay["attachment_scope"] == "DOMAIN_SCOPED_READ_ONLY_INSPECTION"
    assert replay["domain_name"] == "AttachmentGovernance"


def test_detachment_without_approval_remains_attached(tmp_path) -> None:
    attached = _attached(tmp_path)
    candidate = create_capability_detachment_candidate(
        detachment_candidate_id="DETACHMENT-CANDIDATE-000001",
        attached_artifact=attached,
        detachment_reason="Certification detachment review.",
        requested_by="HUMAN_OPERATOR",
        requested_at=CREATED_AT,
        replay_dir=tmp_path / "detachment_candidate",
    )["detachment_candidate_artifact"]
    capture = detach_capability_from_domain(
        detached_id="CAPABILITY-DETACHED-NO-APPROVAL",
        detachment_candidate_artifact=candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-CAPABILITY-DETACHMENT-PENDING",
            approval_status="PENDING",
            approval_granted=False,
            source_detachment_candidate=candidate["detachment_candidate_id"],
            source_detachment_candidate_hash=candidate["artifact_hash"],
            approval_scope="DETACH_CAPABILITY_FROM_DOMAIN_ONLY",
            capability_detachment_allowed=True,
        ),
        detached_by="HUMAN_OPERATOR",
        detached_at=CREATED_AT,
        replay_dir=tmp_path / "detached_no_approval",
    )
    failed = capture["capability_detached_artifact"]

    assert attached["attachment_status"] == ATTACHED
    assert candidate["artifact_type"] == DETACHMENT_CANDIDATE_ARTIFACT_V1
    assert candidate["detachment_candidate_status"] == DETACHMENT_CANDIDATE_CREATED
    assert capture["detachment_status"] == "FAILED_CLOSED"
    assert failed["capability_attached"] is True
    assert failed["capability_detached"] is False
    assert "explicit human approval required" in capture["failure_reason"]


def test_approved_detachment_reaches_detached(tmp_path) -> None:
    attached = _attached(tmp_path)
    candidate = create_capability_detachment_candidate(
        detachment_candidate_id="DETACHMENT-CANDIDATE-000001",
        attached_artifact=attached,
        detachment_reason="Certification detachment review.",
        requested_by="HUMAN_OPERATOR",
        requested_at=CREATED_AT,
        replay_dir=tmp_path / "detachment_candidate",
    )["detachment_candidate_artifact"]
    detached = detach_capability_from_domain(
        detached_id="CAPABILITY-DETACHED-000001",
        detachment_candidate_artifact=candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-CAPABILITY-DETACHMENT-000001",
            source_detachment_candidate=candidate["detachment_candidate_id"],
            source_detachment_candidate_hash=candidate["artifact_hash"],
            approval_scope="DETACH_CAPABILITY_FROM_DOMAIN_ONLY",
            capability_detachment_allowed=True,
        ),
        detached_by="HUMAN_OPERATOR",
        detached_at=CREATED_AT,
        replay_dir=tmp_path / "detached",
    )["capability_detached_artifact"]
    replay_candidate = reconstruct_capability_attachment_governance_replay(
        tmp_path / "detachment_candidate",
        DETACHMENT_CANDIDATE_REPLAY_STEPS,
    )
    replay_detached = reconstruct_capability_attachment_governance_replay(tmp_path / "detached", DETACHMENT_REPLAY_STEPS)

    assert detached["artifact_type"] == CAPABILITY_DETACHED_ARTIFACT_V1
    assert detached["detachment_status"] == DETACHED
    assert detached["capability_attached"] is False
    assert detached["capability_detached"] is True
    assert detached["capability_executor_invoked"] is False
    assert replay_candidate["status"] == DETACHMENT_CANDIDATE_CREATED
    assert replay_detached["status"] == DETACHED
    assert replay_detached["fail_closed_preserved"] is True
