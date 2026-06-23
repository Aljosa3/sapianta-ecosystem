"""Tests for AIGOL_GOVERNANCE_ARTIFACT_CREATION_RUNTIME_V1."""

from __future__ import annotations

import subprocess

import pytest

from aigol.runtime.governance_artifact_creation_runtime import (
    APPROVED,
    FAILED_CLOSED,
    GOVERNANCE_ARTIFACT_APPROVAL_ARTIFACT_V1,
    GOVERNANCE_ARTIFACT_CREATION_COMPLETED,
    GOVERNANCE_ARTIFACT_PROPOSAL_ARTIFACT_V1,
    create_governance_artifact,
    create_governance_artifact_approval,
    create_governance_artifact_proposal,
    reconstruct_governance_artifact_creation_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-23T00:00:00Z"


def _repo(tmp_path):
    repo = tmp_path / "repo"
    (repo / "docs" / "governance").mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    return repo


def _proposal(target_path: str = "docs/governance/EXAMPLE_GOVERNANCE_ARTIFACT_V1.md"):
    return create_governance_artifact_proposal(
        proposal_id="GOVERNANCE-ARTIFACT-PROPOSAL-000001",
        original_request_reference="REQUEST-000001",
        resolved_intent_reference="INTENT-000001",
        target_path=target_path,
        artifact_title="EXAMPLE_GOVERNANCE_ARTIFACT_V1",
        artifact_purpose="Define an example governance artifact.",
        proposed_content="# EXAMPLE_GOVERNANCE_ARTIFACT_V1\n\nStatus: Defined\n",
        expected_sections=["Status"],
        replay_references=["replay/request.json"],
        replay_hashes=[replay_hash({"request": "governance artifact"})],
        created_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
    )


def _approval(proposal, decision: str = APPROVED):
    return create_governance_artifact_approval(
        approval_id="GOVERNANCE-ARTIFACT-APPROVAL-000001",
        proposal_artifact=proposal,
        decision=decision,
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
        replay_references=["replay/proposal.json"],
        replay_hashes=[proposal["artifact_hash"]],
    )


def _create(repo, replay_dir, proposal, approval):
    return create_governance_artifact(
        creation_id="GOVERNANCE-ARTIFACT-CREATION-000001",
        request_artifact={"request_id": "REQUEST-000001", "artifact_hash": replay_hash({"request_id": "REQUEST-000001"})},
        intent_artifact={"intent_id": "INTENT-000001", "artifact_hash": replay_hash({"intent_id": "INTENT-000001"})},
        workflow_artifact={"workflow_id": "GOVERNANCE_ARTIFACT_CREATION"},
        repository_context_artifact={
            "context_id": "CONTEXT-000001",
            "target_path": proposal["target_path"],
            "context_fresh": True,
        },
        proposal_artifact=proposal,
        approval_artifact=approval,
        repository_root=repo,
        created_by="AIGOL_GOVERNANCE_ARTIFACT_CREATION_RUNTIME",
        created_at=CREATED_AT,
        replay_dir=replay_dir,
    )


def test_proposal_creation_records_required_controls() -> None:
    proposal = _proposal()

    assert proposal["artifact_type"] == GOVERNANCE_ARTIFACT_PROPOSAL_ARTIFACT_V1
    assert proposal["workflow_id"] == "GOVERNANCE_ARTIFACT_CREATION"
    assert proposal["target_path"] == "docs/governance/EXAMPLE_GOVERNANCE_ARTIFACT_V1.md"
    assert proposal["human_approval_required"] is True
    assert proposal["mutation_allowed_before_approval"] is False
    assert proposal["validation_plan"]["required_commands"] == [["git", "diff", "--check"]]


def test_proposal_rejects_paths_outside_governance() -> None:
    with pytest.raises(FailClosedRuntimeError):
        _proposal("aigol/runtime/unsafe.py")


def test_proposal_rejects_non_markdown_path() -> None:
    with pytest.raises(FailClosedRuntimeError):
        _proposal("docs/governance/unsafe.txt")


def test_approval_binds_to_proposal_hash() -> None:
    proposal = _proposal()
    approval = _approval(proposal)

    assert approval["artifact_type"] == GOVERNANCE_ARTIFACT_APPROVAL_ARTIFACT_V1
    assert approval["proposal_id"] == proposal["proposal_id"]
    assert approval["proposal_hash"] == proposal["artifact_hash"]
    assert approval["decision"] == APPROVED


def test_approved_creation_writes_one_artifact_validates_and_reconstructs_replay(tmp_path) -> None:
    repo = _repo(tmp_path)
    proposal = _proposal()
    approval = _approval(proposal)

    capture = _create(repo, tmp_path / "replay", proposal, approval)
    reconstructed = reconstruct_governance_artifact_creation_replay(tmp_path / "replay")

    target = repo / proposal["target_path"]
    assert capture["creation_status"] == GOVERNANCE_ARTIFACT_CREATION_COMPLETED
    assert capture["repository_mutation_performed"] is True
    assert capture["approval_bypassed"] is False
    assert target.read_text(encoding="utf-8") == proposal["proposed_content"]
    assert capture["governance_artifact_creation_artifact"]["mutated_files"] == [proposal["target_path"]]
    assert capture["validation_capture"]["validation_command_result_artifact"]["exit_code"] == 0
    assert reconstructed["creation_status"] == GOVERNANCE_ARTIFACT_CREATION_COMPLETED
    assert reconstructed["target_path"] == proposal["target_path"]
    assert reconstructed["replay_artifact_count"] == 9


def test_missing_approval_fails_closed_without_writing(tmp_path) -> None:
    repo = _repo(tmp_path)
    proposal = _proposal()

    capture = _create(repo, tmp_path / "replay", proposal, None)

    assert capture["creation_status"] == FAILED_CLOSED
    assert capture["repository_mutation_performed"] is False
    assert not (repo / proposal["target_path"]).exists()
    assert "FAIL_CLOSED_NO_APPROVAL" in capture["failure_reason"]


def test_rejected_approval_fails_closed_without_writing(tmp_path) -> None:
    repo = _repo(tmp_path)
    proposal = _proposal()
    approval = _approval(proposal, "REJECTED")

    capture = _create(repo, tmp_path / "replay", proposal, approval)

    assert capture["creation_status"] == FAILED_CLOSED
    assert capture["repository_mutation_performed"] is False
    assert not (repo / proposal["target_path"]).exists()


def test_corrupted_replay_fails_closed(tmp_path) -> None:
    repo = _repo(tmp_path)
    proposal = _proposal()
    approval = _approval(proposal)
    _create(repo, tmp_path / "replay", proposal, approval)
    replay_file = tmp_path / "replay" / "008_governance_artifact_creation_outcome_recorded.json"
    replay_file.write_text(replay_file.read_text(encoding="utf-8").replace("sha256:", "broken:"), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError):
        reconstruct_governance_artifact_creation_replay(tmp_path / "replay")
