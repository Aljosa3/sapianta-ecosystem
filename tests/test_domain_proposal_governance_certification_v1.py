"""Certification tests for AIGOL_DOMAIN_PROPOSAL_GOVERNANCE_CERTIFICATION_V1."""

from __future__ import annotations

from aigol.runtime.domain_proposal_governance_runtime import (
    APPROVED,
    DOMAIN_CANDIDATE_ARTIFACT_V1,
    DOMAIN_CANDIDATE_CREATED,
    DOMAIN_PROPOSAL_ARCHIVE_ARTIFACT_V1,
    DOMAIN_PROPOSAL_ARCHIVED,
    DOMAIN_PROPOSAL_ARTIFACT_V1,
    DOMAIN_PROPOSAL_CREATED,
    REJECTED,
    create_domain_proposal,
    reconstruct_domain_proposal_replay,
    reconstruct_domain_proposal_review_replay,
    review_domain_proposal,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-13T00:00:00Z"
CHAIN_ID = "CHAIN-DOMAIN-PROPOSAL-GOVERNANCE-CERTIFICATION-000001"


def _source_replay() -> tuple[list[str], list[str]]:
    payload = {
        "improvement_intent_id": "IMPROVEMENT-INTENT-DOMAIN-PROPOSAL-000001",
        "intent_status": "IMPROVEMENT_INTENT_CREATED",
        "improvement_class": "DOMAIN_MODEL",
        "human_review_required": True,
    }
    return ["replay/improvement-intent-domain-proposal-000001.json"], [replay_hash(payload)]


def _human_proposal(tmp_path) -> dict:
    return create_domain_proposal(
        proposal_id="DOMAIN-PROPOSAL-HUMAN-000001",
        source_type="HUMAN_REQUEST",
        proposed_domain="RegulatoryCompliance",
        need_summary="Human requests a governed regulatory compliance domain.",
        requested_by="HUMAN_OPERATOR",
        canonical_chain_id=CHAIN_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "human_proposal",
    )["domain_proposal_artifact"]


def _replay_proposal(tmp_path) -> dict:
    references, hashes = _source_replay()
    return create_domain_proposal(
        proposal_id="DOMAIN-PROPOSAL-REPLAY-000001",
        source_type="REPLAY_DERIVED_IMPROVEMENT",
        proposed_domain="DomainEffectiveness",
        need_summary="Replay-derived improvement suggests a governed domain model refinement.",
        requested_by="REPLAY_IMPROVEMENT_REVIEW",
        canonical_chain_id=CHAIN_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "replay_proposal",
        source_replay_references=references,
        source_replay_hashes=hashes,
    )["domain_proposal_artifact"]


def _review(tmp_path, proposal: dict, *, decision: str = APPROVED) -> dict:
    return review_domain_proposal(
        review_id=f"DOMAIN-REVIEW-{decision}-000001",
        domain_proposal_artifact=proposal,
        decision=decision,
        decision_reason=f"Human governance review {decision.lower()} the domain proposal.",
        reviewed_by="HUMAN_OPERATOR",
        reviewed_at=CREATED_AT,
        human_approval_reference=f"HUMAN-DOMAIN-REVIEW-{decision}-000001",
        replay_dir=tmp_path / f"review_{decision.lower()}",
    )


def test_human_request_creates_non_authoritative_domain_proposal(tmp_path) -> None:
    proposal = _human_proposal(tmp_path)
    replay = reconstruct_domain_proposal_replay(tmp_path / "human_proposal")

    assert proposal["artifact_type"] == DOMAIN_PROPOSAL_ARTIFACT_V1
    assert proposal["proposal_status"] == DOMAIN_PROPOSAL_CREATED
    assert proposal["source_type"] == "HUMAN_REQUEST"
    assert proposal["proposed_domain"] == "RegulatoryCompliance"
    assert proposal["proposal_authoritative"] is False
    assert proposal["approval_required"] is True
    assert proposal["domain_created"] is False
    assert proposal["domain_registered"] is False
    assert proposal["live_registry_mutated"] is False
    assert proposal["worker_invoked"] is False
    assert replay["proposal_status"] == DOMAIN_PROPOSAL_CREATED
    assert replay["domain_created"] is False


def test_replay_derived_improvement_creates_lineage_bound_domain_proposal(tmp_path) -> None:
    proposal = _replay_proposal(tmp_path)
    replay = reconstruct_domain_proposal_replay(tmp_path / "replay_proposal")

    assert proposal["proposal_status"] == DOMAIN_PROPOSAL_CREATED
    assert proposal["source_type"] == "REPLAY_DERIVED_IMPROVEMENT"
    assert proposal["source_replay_references"]
    assert proposal["source_replay_hashes"]
    assert proposal["approval_required"] is True
    assert proposal["proposal_authoritative"] is False
    assert proposal["domain_created"] is False
    assert replay["source_type"] == "REPLAY_DERIVED_IMPROVEMENT"
    assert replay["replay_visible"] is True


def test_domain_proposal_without_approval_cannot_create_candidate_or_domain(tmp_path) -> None:
    proposal = _human_proposal(tmp_path)
    capture = review_domain_proposal(
        review_id="DOMAIN-REVIEW-NO-APPROVAL-000001",
        domain_proposal_artifact=proposal,
        decision=APPROVED,
        decision_reason="Missing explicit human approval reference.",
        reviewed_by="HUMAN_OPERATOR",
        reviewed_at=CREATED_AT,
        human_approval_reference="",
        replay_dir=tmp_path / "review_no_approval",
    )
    outcome = capture["domain_review_outcome_artifact"]

    assert capture["review_status"] == "FAILED_CLOSED"
    assert capture["domain_candidate_created"] is False
    assert capture["domain_created"] is False
    assert outcome["artifact_type"] == DOMAIN_PROPOSAL_ARCHIVE_ARTIFACT_V1
    assert outcome["outcome_status"] == "FAILED_CLOSED"
    assert outcome["domain_created"] is False
    assert outcome["worker_invoked"] is False
    assert "human_approval_reference is required" in capture["failure_reason"]


def test_approved_domain_proposal_creates_candidate_only(tmp_path) -> None:
    proposal = _human_proposal(tmp_path)
    capture = _review(tmp_path, proposal, decision=APPROVED)
    outcome = capture["domain_review_outcome_artifact"]
    replay = reconstruct_domain_proposal_review_replay(tmp_path / "review_approved")

    assert capture["review_status"] == APPROVED
    assert capture["domain_candidate_created"] is True
    assert outcome["artifact_type"] == DOMAIN_CANDIDATE_ARTIFACT_V1
    assert outcome["outcome_status"] == DOMAIN_CANDIDATE_CREATED
    assert outcome["candidate_scope"] == "DOMAIN_CANDIDATE_ONLY"
    assert outcome["required_next_step"] == "SEPARATE_DOMAIN_CREATION_AUTHORIZATION"
    assert outcome["domain_created"] is False
    assert outcome["domain_registered"] is False
    assert outcome["live_registry_mutated"] is False
    assert replay["domain_candidate_created"] is True
    assert replay["domain_created"] is False


def test_rejected_domain_proposal_is_archived_without_domain_creation(tmp_path) -> None:
    proposal = _replay_proposal(tmp_path)
    capture = _review(tmp_path, proposal, decision=REJECTED)
    outcome = capture["domain_review_outcome_artifact"]
    replay = reconstruct_domain_proposal_review_replay(tmp_path / "review_rejected")

    assert capture["review_status"] == REJECTED
    assert capture["proposal_archived"] is True
    assert capture["domain_candidate_created"] is False
    assert outcome["artifact_type"] == DOMAIN_PROPOSAL_ARCHIVE_ARTIFACT_V1
    assert outcome["outcome_status"] == DOMAIN_PROPOSAL_ARCHIVED
    assert outcome["domain_created"] is False
    assert outcome["domain_registered"] is False
    assert outcome["worker_invoked"] is False
    assert replay["proposal_archived"] is True
    assert replay["domain_created"] is False
