"""Certification tests for AIGOL_CAPABILITY_LIFECYCLE_GOVERNANCE_CERTIFICATION_V1."""

from __future__ import annotations

from aigol.runtime.capability_lifecycle_governance_runtime import (
    ACTIVATION_CANDIDATE_REPLAY_STEPS,
    ACTIVATION_REPLAY_STEPS,
    CAPABILITY_ACTIVATION_CANDIDATE_ARTIFACT_V1,
    CAPABILITY_ACTIVATION_CANDIDATE_CREATED,
    CAPABILITY_ACTIVE,
    CAPABILITY_ACTIVE_ARTIFACT_V1,
    CAPABILITY_CANDIDATE_ARTIFACT_V1,
    CAPABILITY_CANDIDATE_CREATED,
    CAPABILITY_OPERATION_AVAILABLE,
    CAPABILITY_OPERATION_ARTIFACT_V1,
    CAPABILITY_RETIREMENT_CANDIDATE_ARTIFACT_V1,
    CAPABILITY_RETIREMENT_CANDIDATE_CREATED,
    CAPABILITY_RETIRED,
    CAPABILITY_RETIRED_ARTIFACT_V1,
    HUMAN_APPROVAL_ARTIFACT_V1,
    RETIREMENT_CANDIDATE_REPLAY_STEPS,
    RETIREMENT_REPLAY_STEPS,
    activate_capability_candidate,
    create_capability_activation_candidate,
    create_capability_candidate,
    reconstruct_capability_lifecycle_governance_replay,
    request_capability_retirement,
    retire_capability_candidate,
)
from aigol.runtime.proposal_runtime import CREATED, create_proposal
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-13T00:00:00Z"


def _approval(**fields: object) -> dict:
    artifact = {
        "artifact_type": HUMAN_APPROVAL_ARTIFACT_V1,
        "approval_status": "APPROVED",
        "approval_granted": True,
        "approved_by": "HUMAN_OPERATOR",
        "approved_at": CREATED_AT,
        "capability_executor_invocation_allowed": False,
        "execution_summary_reference": "EXECUTION-SUMMARY-CAPABILITY-LIFECYCLE-000001",
        "execution_summary_hash": replay_hash({"summary": "capability-lifecycle"}),
        "human_confirmation_reference": "EXECUTION-SUMMARY-CONFIRMATION-CAPABILITY-LIFECYCLE-000001",
        "human_confirmation_hash": replay_hash({"confirmation": "capability-lifecycle"}),
        "replay_visible": True,
    }
    artifact.update(fields)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _proposal(tmp_path) -> dict:
    return create_proposal(
        proposal_id="CAPABILITY-PROPOSAL-LIFECYCLE-000001",
        proposal_type="CAPABILITY_PROPOSAL",
        proposal_source="HUMAN_PROMPT",
        proposal_text="Create a bounded read-only inspection capability candidate.",
        created_at=CREATED_AT,
        replay_reference="REPLAY-CAPABILITY-PROPOSAL-LIFECYCLE-000001",
        replay_dir=tmp_path / "proposal",
        created_by="AIGOL",
        status=CREATED,
    )["proposal_runtime_artifact"]


def _candidate(tmp_path) -> dict:
    return create_capability_candidate(
        capability_candidate_id="CAPABILITY-CANDIDATE-LIFECYCLE-000001",
        capability_proposal_artifact=_proposal(tmp_path),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "candidate",
    )["capability_candidate_artifact"]


def _activation_candidate(tmp_path, candidate: dict | None = None) -> dict:
    candidate = candidate or _candidate(tmp_path)
    return create_capability_activation_candidate(
        activation_candidate_id="CAPABILITY-ACTIVATION-CANDIDATE-000001",
        capability_candidate_artifact=candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-CAPABILITY-ACTIVATION-CANDIDATE-000001",
            source_capability_candidate=candidate["capability_candidate_id"],
            source_capability_candidate_hash=candidate["artifact_hash"],
            approval_scope="CREATE_CAPABILITY_ACTIVATION_CANDIDATE_ONLY",
            capability_activation_allowed=False,
        ),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "activation_candidate",
    )["capability_activation_candidate_artifact"]


def _active_capability(tmp_path, activation_candidate: dict | None = None) -> dict:
    activation_candidate = activation_candidate or _activation_candidate(tmp_path)
    return activate_capability_candidate(
        active_capability_id="CAPABILITY-ACTIVE-LIFECYCLE-000001",
        activation_candidate_artifact=activation_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-ACTIVATE-CAPABILITY-000001",
            source_activation_candidate=activation_candidate["activation_candidate_id"],
            source_activation_candidate_hash=activation_candidate["artifact_hash"],
            approval_scope="ACTIVATE_CAPABILITY_ONLY",
            capability_activation_allowed=True,
        ),
        activated_by="HUMAN_OPERATOR",
        activated_at=CREATED_AT,
        replay_dir=tmp_path / "activation",
    )["capability_active_artifact"]


def _retirement_candidate(tmp_path, active: dict | None = None) -> dict:
    active = active or _active_capability(tmp_path)
    return request_capability_retirement(
        retirement_candidate_id="CAPABILITY-RETIREMENT-CANDIDATE-000001",
        active_capability_artifact=active,
        requested_by="HUMAN_OPERATOR",
        requested_at=CREATED_AT,
        retirement_reason="Capability lifecycle certification retirement request.",
        replay_dir=tmp_path / "retirement_candidate",
    )["capability_retirement_candidate_artifact"]


def test_capability_candidate_without_approval_does_not_activate(tmp_path) -> None:
    candidate = _candidate(tmp_path)
    capture = create_capability_activation_candidate(
        activation_candidate_id="CAPABILITY-ACTIVATION-CANDIDATE-NO-APPROVAL",
        capability_candidate_artifact=candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-CAPABILITY-ACTIVATION-PENDING",
            approval_status="PENDING",
            approval_granted=False,
            source_capability_candidate=candidate["capability_candidate_id"],
            source_capability_candidate_hash=candidate["artifact_hash"],
            approval_scope="CREATE_CAPABILITY_ACTIVATION_CANDIDATE_ONLY",
            capability_activation_allowed=False,
        ),
        requested_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "activation_no_approval",
    )
    artifact = capture["capability_activation_candidate_artifact"]

    assert candidate["artifact_type"] == CAPABILITY_CANDIDATE_ARTIFACT_V1
    assert candidate["candidate_status"] == CAPABILITY_CANDIDATE_CREATED
    assert candidate["candidate_authoritative"] is False
    assert capture["activation_candidate_status"] == "FAILED_CLOSED"
    assert artifact["capability_active"] is False
    assert artifact["capability_executor_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert "explicit human approval required" in capture["failure_reason"]


def test_approved_capability_candidate_creates_activation_candidate_only(tmp_path) -> None:
    candidate = _candidate(tmp_path)
    activation_candidate = _activation_candidate(tmp_path, candidate)
    replay = reconstruct_capability_lifecycle_governance_replay(
        tmp_path / "activation_candidate",
        ACTIVATION_CANDIDATE_REPLAY_STEPS,
    )

    assert activation_candidate["artifact_type"] == CAPABILITY_ACTIVATION_CANDIDATE_ARTIFACT_V1
    assert activation_candidate["activation_candidate_status"] == CAPABILITY_ACTIVATION_CANDIDATE_CREATED
    assert activation_candidate["source_capability_candidate"] == candidate["capability_candidate_id"]
    assert activation_candidate["activation_approval_required"] is True
    assert activation_candidate["capability_active"] is False
    assert activation_candidate["capability_executor_invoked"] is False
    assert replay["status"] == CAPABILITY_ACTIVATION_CANDIDATE_CREATED
    assert replay["fail_closed_preserved"] is True


def test_activation_approval_creates_active_capability_and_operation_evidence(tmp_path) -> None:
    activation_candidate = _activation_candidate(tmp_path)
    capture = activate_capability_candidate(
        active_capability_id="CAPABILITY-ACTIVE-LIFECYCLE-000001",
        activation_candidate_artifact=activation_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-ACTIVATE-CAPABILITY-000001",
            source_activation_candidate=activation_candidate["activation_candidate_id"],
            source_activation_candidate_hash=activation_candidate["artifact_hash"],
            approval_scope="ACTIVATE_CAPABILITY_ONLY",
            capability_activation_allowed=True,
        ),
        activated_by="HUMAN_OPERATOR",
        activated_at=CREATED_AT,
        replay_dir=tmp_path / "activation",
    )
    active = capture["capability_active_artifact"]
    operation = capture["capability_operation_artifact"]
    replay = reconstruct_capability_lifecycle_governance_replay(tmp_path / "activation", ACTIVATION_REPLAY_STEPS)

    assert active["artifact_type"] == CAPABILITY_ACTIVE_ARTIFACT_V1
    assert active["active_capability_status"] == CAPABILITY_ACTIVE
    assert active["capability_active"] is True
    assert active["capability_operation_available"] is True
    assert active["capability_executor_invoked"] is False
    assert operation["artifact_type"] == CAPABILITY_OPERATION_ARTIFACT_V1
    assert operation["operation_status"] == CAPABILITY_OPERATION_AVAILABLE
    assert operation["source_active_capability"] == active["active_capability_id"]
    assert operation["capability_executor_invoked"] is False
    assert replay["status"] == CAPABILITY_OPERATION_AVAILABLE
    assert replay["capability_executor_invoked"] is False


def test_retirement_request_creates_retirement_candidate_only(tmp_path) -> None:
    active = _active_capability(tmp_path)
    retirement_candidate = _retirement_candidate(tmp_path, active)
    replay = reconstruct_capability_lifecycle_governance_replay(
        tmp_path / "retirement_candidate",
        RETIREMENT_CANDIDATE_REPLAY_STEPS,
    )

    assert retirement_candidate["artifact_type"] == CAPABILITY_RETIREMENT_CANDIDATE_ARTIFACT_V1
    assert retirement_candidate["retirement_candidate_status"] == CAPABILITY_RETIREMENT_CANDIDATE_CREATED
    assert retirement_candidate["source_active_capability"] == active["active_capability_id"]
    assert retirement_candidate["retirement_approval_required"] is True
    assert retirement_candidate["capability_active"] is True
    assert retirement_candidate["capability_retired"] is False
    assert retirement_candidate["capability_executor_invoked"] is False
    assert replay["status"] == CAPABILITY_RETIREMENT_CANDIDATE_CREATED


def test_retirement_approval_retires_capability_without_executor_invocation(tmp_path) -> None:
    retirement_candidate = _retirement_candidate(tmp_path)
    capture = retire_capability_candidate(
        retired_capability_id="CAPABILITY-RETIRED-LIFECYCLE-000001",
        retirement_candidate_artifact=retirement_candidate,
        human_approval_artifact=_approval(
            approval_id="HUMAN-APPROVAL-RETIRE-CAPABILITY-000001",
            source_retirement_candidate=retirement_candidate["retirement_candidate_id"],
            source_retirement_candidate_hash=retirement_candidate["artifact_hash"],
            approval_scope="RETIRE_CAPABILITY_ONLY",
            capability_retirement_allowed=True,
        ),
        retired_by="HUMAN_OPERATOR",
        retired_at=CREATED_AT,
        replay_dir=tmp_path / "retirement",
    )
    retired = capture["capability_retired_artifact"]
    replay = reconstruct_capability_lifecycle_governance_replay(tmp_path / "retirement", RETIREMENT_REPLAY_STEPS)

    assert retired["artifact_type"] == CAPABILITY_RETIRED_ARTIFACT_V1
    assert retired["retired_capability_status"] == CAPABILITY_RETIRED
    assert retired["capability_active"] is False
    assert retired["capability_retired"] is True
    assert retired["retirement_approval_required"] is True
    assert retired["capability_executor_invoked"] is False
    assert retired["provider_invoked"] is False
    assert retired["worker_invoked"] is False
    assert replay["status"] == CAPABILITY_RETIRED
    assert replay["fail_closed_preserved"] is True
