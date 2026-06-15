"""Certification tests for AIGOL_DOMAIN_LIFECYCLE_GOVERNANCE_CERTIFICATION_V1."""

from __future__ import annotations

from aigol.runtime.domain_lifecycle_governance_runtime import (
    ACTIVATION_CANDIDATE_REPLAY_STEPS,
    ACTIVATION_REPLAY_STEPS,
    DOMAIN_ACTIVATION_CANDIDATE_ARTIFACT_V1,
    DOMAIN_ACTIVATION_CANDIDATE_CREATED,
    DOMAIN_ACTIVE,
    DOMAIN_ACTIVE_ARTIFACT_V1,
    DOMAIN_OPERATION_AVAILABLE,
    DOMAIN_OPERATION_ARTIFACT_V1,
    DOMAIN_RETIREMENT_CANDIDATE_ARTIFACT_V1,
    DOMAIN_RETIREMENT_CANDIDATE_CREATED,
    DOMAIN_RETIRED,
    DOMAIN_RETIRED_ARTIFACT_V1,
    HUMAN_APPROVAL_ARTIFACT_V1,
    RETIREMENT_CANDIDATE_REPLAY_STEPS,
    RETIREMENT_REPLAY_STEPS,
    activate_domain_candidate,
    create_domain_activation_candidate,
    reconstruct_domain_lifecycle_governance_replay,
    request_domain_retirement,
    retire_domain_candidate,
)
from aigol.runtime.domain_proposal_governance_runtime import (
    APPROVED,
    DOMAIN_CANDIDATE_CREATED,
    create_domain_proposal,
    review_domain_proposal,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-13T00:00:00Z"
CHAIN_ID = "CHAIN-DOMAIN-LIFECYCLE-GOVERNANCE-CERTIFICATION-000001"


def _approval(**fields: object) -> dict:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_status": APPROVED,
        "approval_granted": True,
        "approved_by": "HUMAN_OPERATOR",
        "approved_at": CREATED_AT,
        "live_registry_mutation_allowed": False,
        "execution_summary_reference": "EXECUTION-SUMMARY-DOMAIN-LIFECYCLE-000001",
        "execution_summary_hash": replay_hash({"summary": "domain-lifecycle"}),
        "human_confirmation_reference": "EXECUTION-SUMMARY-CONFIRMATION-DOMAIN-LIFECYCLE-000001",
        "human_confirmation_hash": replay_hash({"confirmation": "domain-lifecycle"}),
        "replay_visible": True,
    }
    artifact.update(fields)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _domain_candidate(tmp_path) -> dict:
    proposal = create_domain_proposal(
        proposal_id="DOMAIN-PROPOSAL-LIFECYCLE-000001",
        source_type="HUMAN_REQUEST",
        proposed_domain="LifecycleGovernance",
        need_summary="Human requests a governed lifecycle domain.",
        requested_by="HUMAN_OPERATOR",
        canonical_chain_id=CHAIN_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "domain_proposal",
    )["domain_proposal_artifact"]
    review = review_domain_proposal(
        review_id="DOMAIN-REVIEW-LIFECYCLE-000001",
        domain_proposal_artifact=proposal,
        decision=APPROVED,
        decision_reason="Human approves lifecycle candidate staging only.",
        reviewed_by="HUMAN_OPERATOR",
        reviewed_at=CREATED_AT,
        human_approval_reference="HUMAN-DOMAIN-PROPOSAL-LIFECYCLE-000001",
        replay_dir=tmp_path / "domain_candidate",
    )
    return review["domain_review_outcome_artifact"]


def _activation_candidate(tmp_path, domain_candidate: dict | None = None) -> dict:
    domain_candidate = domain_candidate or _domain_candidate(tmp_path)
    return create_domain_activation_candidate(
        activation_candidate_id="DOMAIN-ACTIVATION-CANDIDATE-000001",
        domain_candidate_artifact=domain_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-ACTIVATION-CANDIDATE-000001",
            source_domain_candidate=domain_candidate["domain_candidate_id"],
            source_domain_candidate_hash=domain_candidate["artifact_hash"],
            approval_scope="CREATE_DOMAIN_ACTIVATION_CANDIDATE_ONLY",
            domain_activation_allowed=False,
        ),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "activation_candidate",
    )["domain_activation_candidate_artifact"]


def _active_domain(tmp_path, activation_candidate: dict | None = None) -> dict:
    activation_candidate = activation_candidate or _activation_candidate(tmp_path)
    return activate_domain_candidate(
        active_domain_id="DOMAIN-ACTIVE-LIFECYCLE-000001",
        activation_candidate_artifact=activation_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-ACTIVATE-DOMAIN-000001",
            source_activation_candidate=activation_candidate["activation_candidate_id"],
            source_activation_candidate_hash=activation_candidate["artifact_hash"],
            approval_scope="ACTIVATE_DOMAIN_ONLY",
            domain_activation_allowed=True,
        ),
        activated_by="HUMAN_OPERATOR",
        activated_at=CREATED_AT,
        replay_dir=tmp_path / "activation",
    )["domain_active_artifact"]


def _retirement_candidate(tmp_path, active_domain: dict | None = None) -> dict:
    active_domain = active_domain or _active_domain(tmp_path)
    return request_domain_retirement(
        retirement_candidate_id="DOMAIN-RETIREMENT-CANDIDATE-000001",
        active_domain_artifact=active_domain,
        requested_by="HUMAN_OPERATOR",
        requested_at=CREATED_AT,
        retirement_reason="Lifecycle certification retirement request.",
        replay_dir=tmp_path / "retirement_candidate",
    )["domain_retirement_candidate_artifact"]


def test_candidate_without_approval_cannot_create_activation_candidate(tmp_path) -> None:
    domain_candidate = _domain_candidate(tmp_path)
    capture = create_domain_activation_candidate(
        activation_candidate_id="DOMAIN-ACTIVATION-CANDIDATE-NO-APPROVAL",
        domain_candidate_artifact=domain_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-ACTIVATION-CANDIDATE-PENDING",
            approval_status="PENDING",
            approval_granted=False,
            source_domain_candidate=domain_candidate["domain_candidate_id"],
            source_domain_candidate_hash=domain_candidate["artifact_hash"],
            approval_scope="CREATE_DOMAIN_ACTIVATION_CANDIDATE_ONLY",
            domain_activation_allowed=False,
        ),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "activation_no_approval",
    )
    artifact = capture["domain_activation_candidate_artifact"]

    assert domain_candidate["outcome_status"] == DOMAIN_CANDIDATE_CREATED
    assert domain_candidate["domain_created"] is False
    assert capture["activation_candidate_status"] == "FAILED_CLOSED"
    assert artifact["artifact_type"] == DOMAIN_ACTIVATION_CANDIDATE_ARTIFACT_V1
    assert artifact["domain_active"] is False
    assert artifact["live_registry_mutated"] is False
    assert artifact["worker_invoked"] is False
    assert "explicit human approval required" in capture["failure_reason"]


def test_approved_candidate_creates_activation_candidate_only(tmp_path) -> None:
    domain_candidate = _domain_candidate(tmp_path)
    activation_candidate = _activation_candidate(tmp_path, domain_candidate)
    replay = reconstruct_domain_lifecycle_governance_replay(
        tmp_path / "activation_candidate",
        ACTIVATION_CANDIDATE_REPLAY_STEPS,
    )

    assert activation_candidate["artifact_type"] == DOMAIN_ACTIVATION_CANDIDATE_ARTIFACT_V1
    assert activation_candidate["activation_candidate_status"] == DOMAIN_ACTIVATION_CANDIDATE_CREATED
    assert activation_candidate["source_domain_candidate"] == domain_candidate["domain_candidate_id"]
    assert activation_candidate["activation_approval_required"] is True
    assert activation_candidate["domain_active"] is False
    assert activation_candidate["live_registry_mutated"] is False
    assert replay["status"] == DOMAIN_ACTIVATION_CANDIDATE_CREATED
    assert replay["fail_closed_preserved"] is True


def test_activation_approval_creates_active_domain_and_operation_evidence(tmp_path) -> None:
    activation_candidate = _activation_candidate(tmp_path)
    capture = activate_domain_candidate(
        active_domain_id="DOMAIN-ACTIVE-LIFECYCLE-000001",
        activation_candidate_artifact=activation_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-ACTIVATE-DOMAIN-000001",
            source_activation_candidate=activation_candidate["activation_candidate_id"],
            source_activation_candidate_hash=activation_candidate["artifact_hash"],
            approval_scope="ACTIVATE_DOMAIN_ONLY",
            domain_activation_allowed=True,
        ),
        activated_by="HUMAN_OPERATOR",
        activated_at=CREATED_AT,
        replay_dir=tmp_path / "activation",
    )
    active = capture["domain_active_artifact"]
    operation = capture["domain_operation_artifact"]
    replay = reconstruct_domain_lifecycle_governance_replay(tmp_path / "activation", ACTIVATION_REPLAY_STEPS)

    assert active["artifact_type"] == DOMAIN_ACTIVE_ARTIFACT_V1
    assert active["active_domain_status"] == DOMAIN_ACTIVE
    assert active["domain_active"] is True
    assert active["domain_operation_available"] is True
    assert active["live_registry_mutated"] is False
    assert operation["artifact_type"] == DOMAIN_OPERATION_ARTIFACT_V1
    assert operation["operation_status"] == DOMAIN_OPERATION_AVAILABLE
    assert operation["source_active_domain"] == active["active_domain_id"]
    assert replay["status"] == DOMAIN_OPERATION_AVAILABLE
    assert replay["live_registry_mutated"] is False


def test_retirement_request_creates_retirement_candidate_only(tmp_path) -> None:
    active = _active_domain(tmp_path)
    retirement_candidate = _retirement_candidate(tmp_path, active)
    replay = reconstruct_domain_lifecycle_governance_replay(
        tmp_path / "retirement_candidate",
        RETIREMENT_CANDIDATE_REPLAY_STEPS,
    )

    assert retirement_candidate["artifact_type"] == DOMAIN_RETIREMENT_CANDIDATE_ARTIFACT_V1
    assert retirement_candidate["retirement_candidate_status"] == DOMAIN_RETIREMENT_CANDIDATE_CREATED
    assert retirement_candidate["source_active_domain"] == active["active_domain_id"]
    assert retirement_candidate["retirement_approval_required"] is True
    assert retirement_candidate["domain_active"] is True
    assert retirement_candidate["domain_retired"] is False
    assert retirement_candidate["live_registry_mutated"] is False
    assert replay["status"] == DOMAIN_RETIREMENT_CANDIDATE_CREATED


def test_retirement_approval_retires_domain_without_registry_mutation(tmp_path) -> None:
    retirement_candidate = _retirement_candidate(tmp_path)
    capture = retire_domain_candidate(
        retired_domain_id="DOMAIN-RETIRED-LIFECYCLE-000001",
        retirement_candidate_artifact=retirement_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-RETIRE-DOMAIN-000001",
            source_retirement_candidate=retirement_candidate["retirement_candidate_id"],
            source_retirement_candidate_hash=retirement_candidate["artifact_hash"],
            approval_scope="RETIRE_DOMAIN_ONLY",
            domain_retirement_allowed=True,
        ),
        retired_by="HUMAN_OPERATOR",
        retired_at=CREATED_AT,
        replay_dir=tmp_path / "retirement",
    )
    retired = capture["domain_retired_artifact"]
    replay = reconstruct_domain_lifecycle_governance_replay(tmp_path / "retirement", RETIREMENT_REPLAY_STEPS)

    assert retired["artifact_type"] == DOMAIN_RETIRED_ARTIFACT_V1
    assert retired["retired_domain_status"] == DOMAIN_RETIRED
    assert retired["domain_active"] is False
    assert retired["domain_retired"] is True
    assert retired["retirement_approval_required"] is True
    assert retired["live_registry_mutated"] is False
    assert retired["provider_invoked"] is False
    assert retired["worker_invoked"] is False
    assert replay["status"] == DOMAIN_RETIRED
    assert replay["fail_closed_preserved"] is True
