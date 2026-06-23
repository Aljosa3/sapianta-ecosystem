"""Tests for AIGOL_GOVERNED_DEVELOPMENT_WORKFLOW_RUNTIME_V1."""

from __future__ import annotations

import json
import subprocess

import pytest

from aigol.runtime.governed_development_workflow_runtime import (
    APPROVED,
    FAILED_CLOSED,
    GOVERNED_DEVELOPMENT_APPROVAL_ARTIFACT_V1,
    GOVERNED_DEVELOPMENT_PROPOSAL_ARTIFACT_V1,
    GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED,
    create_governed_development_approval,
    create_governed_development_proposal,
    execute_governed_development_workflow,
    reconstruct_governed_development_workflow_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-23T00:00:00Z"


def _repo(tmp_path):
    repo = tmp_path / "repo"
    (repo / "docs" / "governance").mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    return repo


def _artifact_hash(payload: dict):
    artifact = dict(payload)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _file_mutation(target_path: str = "aigol/runtime/generated_development_change.py", content: str = "VALUE = 1\n"):
    return {
        "target_path": target_path,
        "operation": "CREATE_OR_REPLACE",
        "new_content": content,
        "new_content_hash": replay_hash(content),
        "approved": True,
    }


def _governance_artifact(target_path: str = "docs/governance/GENERATED_DEVELOPMENT_ARTIFACT_V1.md"):
    return {
        "target_path": target_path,
        "artifact_title": "GENERATED_DEVELOPMENT_ARTIFACT_V1",
        "artifact_purpose": "Record the governed development change.",
        "proposed_content": "# GENERATED_DEVELOPMENT_ARTIFACT_V1\n\nStatus: Defined\n",
        "expected_sections": ["Status"],
    }


def _proposal(governance_artifact=None, repository_file_mutations=None):
    return create_governed_development_proposal(
        proposal_id="GOVERNED-DEVELOPMENT-PROPOSAL-000001",
        original_request_reference="REQUEST-000001",
        resolved_intent_reference="INTENT-000001",
        governance_artifact=governance_artifact or _governance_artifact(),
        repository_file_mutations=repository_file_mutations or [_file_mutation()],
        repository_validation_command=["git", "diff", "--check"],
        replay_references=["replay/request.json"],
        replay_hashes=[replay_hash({"request": "governed development"})],
        created_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
    )


def _approval(proposal, decision: str = APPROVED):
    return create_governed_development_approval(
        approval_id="GOVERNED-DEVELOPMENT-APPROVAL-000001",
        proposal_artifact=proposal,
        decision=decision,
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
        replay_references=["replay/proposal.json"],
        replay_hashes=[proposal["artifact_hash"]],
    )


def _execute(repo, replay_dir, proposal, approval):
    return execute_governed_development_workflow(
        execution_id="GOVERNED-DEVELOPMENT-000001",
        request_artifact=_artifact_hash({"request_id": "REQUEST-000001"}),
        intent_artifact=_artifact_hash({"intent_id": "INTENT-000001"}),
        workflow_artifact=_artifact_hash({"workflow_id": "GOVERNED_DEVELOPMENT_WORKFLOW"}),
        repository_context_artifact=_artifact_hash({"context_id": "CONTEXT-000001", "context_fresh": True}),
        proposal_artifact=proposal,
        approval_artifact=approval,
        repository_root=repo,
        executed_by="AIGOL_GOVERNED_DEVELOPMENT_WORKFLOW_RUNTIME",
        executed_at=CREATED_AT,
        replay_dir=replay_dir,
    )


def test_governed_development_proposal_contains_component_proposals() -> None:
    proposal = _proposal()

    assert proposal["artifact_type"] == GOVERNED_DEVELOPMENT_PROPOSAL_ARTIFACT_V1
    assert proposal["workflow_id"] == "GOVERNED_DEVELOPMENT_WORKFLOW"
    assert proposal["component_order"] == ["GOVERNANCE_ARTIFACT_CREATION", "GOVERNED_REPOSITORY_MUTATION"]
    assert proposal["human_approval_required"] is True
    assert proposal["mutation_allowed_before_approval"] is False
    assert proposal["governance_artifact_proposal"]["artifact_hash"].startswith("sha256:")
    assert proposal["repository_mutation_proposal"]["artifact_hash"].startswith("sha256:")


def test_governed_development_approval_binds_top_level_and_components() -> None:
    proposal = _proposal()
    approval = _approval(proposal)

    assert approval["artifact_type"] == GOVERNED_DEVELOPMENT_APPROVAL_ARTIFACT_V1
    assert approval["proposal_hash"] == proposal["artifact_hash"]
    assert approval["approved_governance_artifact_proposal_hash"] == proposal["governance_artifact_proposal"]["artifact_hash"]
    assert approval["approved_repository_mutation_proposal_hash"] == proposal["repository_mutation_proposal"]["artifact_hash"]
    assert approval["decision"] == APPROVED
    assert approval["approval_bypassed"] is False


def test_governed_development_executes_components_in_order_and_reconstructs(tmp_path) -> None:
    repo = _repo(tmp_path)
    proposal = _proposal()
    approval = _approval(proposal)

    capture = _execute(repo, tmp_path / "replay", proposal, approval)
    reconstructed = reconstruct_governed_development_workflow_replay(tmp_path / "replay")

    governance_target = repo / proposal["governance_artifact_proposal"]["target_path"]
    repository_target = repo / proposal["repository_mutation_proposal"]["target_paths"][0]
    assert capture["execution_status"] == GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED
    assert governance_target.exists()
    assert repository_target.exists()
    assert capture["approval_bypassed"] is False
    assert capture["repository_mutation_worker_protections_preserved"] is True
    assert capture["validation_allowlists_preserved"] is True
    assert reconstructed["execution_status"] == GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED
    assert reconstructed["component_order"] == ["GOVERNANCE_ARTIFACT_CREATION", "GOVERNED_REPOSITORY_MUTATION"]
    assert reconstructed["replay_artifact_count"] == 9


def test_missing_approval_fails_closed_before_components(tmp_path) -> None:
    repo = _repo(tmp_path)
    proposal = _proposal()

    capture = _execute(repo, tmp_path / "replay", proposal, None)

    assert capture["execution_status"] == FAILED_CLOSED
    assert "FAIL_CLOSED_NO_APPROVAL" in capture["failure_reason"]
    assert not (repo / proposal["governance_artifact_proposal"]["target_path"]).exists()
    assert not (repo / proposal["repository_mutation_proposal"]["target_paths"][0]).exists()


def test_repository_component_failure_fails_closed_after_governance_component(tmp_path) -> None:
    repo = _repo(tmp_path)
    proposal = _proposal(repository_file_mutations=[_file_mutation("aigol/runtime/bad.py", "def nope(:\n")])
    proposal["repository_mutation_proposal"]["validation_plan"]["required_command"] = [
        "python",
        "-m",
        "py_compile",
        "aigol/runtime/bad.py",
    ]
    proposal["repository_mutation_proposal"]["artifact_hash"] = replay_hash(
        {k: v for k, v in proposal["repository_mutation_proposal"].items() if k != "artifact_hash"}
    )
    proposal["artifact_hash"] = replay_hash({k: v for k, v in proposal.items() if k != "artifact_hash"})
    approval = _approval(proposal)

    capture = _execute(repo, tmp_path / "replay", proposal, approval)

    assert capture["execution_status"] == FAILED_CLOSED
    assert "FAIL_CLOSED_GOVERNED_REPOSITORY_MUTATION_FAILED" in capture["failure_reason"]
    assert (repo / proposal["governance_artifact_proposal"]["target_path"]).exists()


def test_corrupted_governed_development_replay_fails_closed(tmp_path) -> None:
    repo = _repo(tmp_path)
    proposal = _proposal()
    approval = _approval(proposal)
    _execute(repo, tmp_path / "replay", proposal, approval)
    replay_file = tmp_path / "replay" / "008_governed_development_outcome_recorded.json"
    payload = json.loads(replay_file.read_text(encoding="utf-8"))
    payload["artifact"]["execution_status"] = "CORRUPTED"
    replay_file.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError):
        reconstruct_governed_development_workflow_replay(tmp_path / "replay")
