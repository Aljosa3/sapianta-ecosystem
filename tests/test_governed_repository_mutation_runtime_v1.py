"""Tests for AIGOL_GOVERNED_REPOSITORY_MUTATION_RUNTIME_V1."""

from __future__ import annotations

import json
import subprocess

import pytest

from aigol.runtime.governed_repository_mutation_runtime import (
    APPROVED,
    FAILED_CLOSED,
    GOVERNED_REPOSITORY_MUTATION_APPROVAL_ARTIFACT_V1,
    GOVERNED_REPOSITORY_MUTATION_COMPLETED,
    GOVERNED_REPOSITORY_MUTATION_PROPOSAL_ARTIFACT_V1,
    create_governed_repository_mutation_approval,
    create_governed_repository_mutation_proposal,
    execute_governed_repository_mutation,
    reconstruct_governed_repository_mutation_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-23T00:00:00Z"


def _repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    return repo


def _file_mutation(target_path: str = "aigol/runtime/generated_repo_mutation.py", content: str = "VALUE = 1\n"):
    return {
        "target_path": target_path,
        "operation": "CREATE_OR_REPLACE",
        "new_content": content,
        "new_content_hash": replay_hash(content),
        "approved": True,
    }


def _proposal(file_mutations=None, validation_command=None):
    return create_governed_repository_mutation_proposal(
        proposal_id="GOVERNED-REPOSITORY-MUTATION-PROPOSAL-000001",
        original_request_reference="REQUEST-000001",
        resolved_intent_reference="INTENT-000001",
        file_mutations=file_mutations or [_file_mutation()],
        validation_command=validation_command,
        replay_references=["replay/request.json"],
        replay_hashes=[replay_hash({"request": "repository mutation"})],
        created_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
    )


def _approval(proposal, decision: str = APPROVED):
    return create_governed_repository_mutation_approval(
        approval_id="GOVERNED-REPOSITORY-MUTATION-APPROVAL-000001",
        proposal_artifact=proposal,
        decision=decision,
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
        replay_references=["replay/proposal.json"],
        replay_hashes=[proposal["artifact_hash"]],
    )


def _execute(repo, replay_dir, proposal, approval):
    return execute_governed_repository_mutation(
        execution_id="GOVERNED-REPOSITORY-MUTATION-000001",
        request_artifact={"request_id": "REQUEST-000001", "artifact_hash": replay_hash({"request_id": "REQUEST-000001"})},
        intent_artifact={"intent_id": "INTENT-000001", "artifact_hash": replay_hash({"intent_id": "INTENT-000001"})},
        workflow_artifact={"workflow_id": "GOVERNED_REPOSITORY_MUTATION"},
        repository_context_artifact={
            "context_id": "CONTEXT-000001",
            "target_paths": proposal["target_paths"],
            "context_fresh": True,
        },
        proposal_artifact=proposal,
        approval_artifact=approval,
        repository_root=repo,
        executed_by="AIGOL_GOVERNED_REPOSITORY_MUTATION_RUNTIME",
        executed_at=CREATED_AT,
        replay_dir=replay_dir,
    )


def test_proposal_creation_records_worker_and_approval_controls() -> None:
    proposal = _proposal()

    assert proposal["artifact_type"] == GOVERNED_REPOSITORY_MUTATION_PROPOSAL_ARTIFACT_V1
    assert proposal["workflow_id"] == "GOVERNED_REPOSITORY_MUTATION"
    assert proposal["human_approval_required"] is True
    assert proposal["mutation_allowed_before_approval"] is False
    assert proposal["repository_mutation_worker_required"] is True
    assert proposal["validation_plan"]["required_command"] == ["git", "diff", "--check"]


def test_proposal_rejects_governance_artifact_scope() -> None:
    with pytest.raises(FailClosedRuntimeError):
        _proposal([_file_mutation("docs/governance/NOT_ALLOWED.md", "# Nope\n")])


def test_proposal_rejects_path_escape() -> None:
    with pytest.raises(FailClosedRuntimeError):
        _proposal([_file_mutation("../escape.py", "VALUE = 1\n")])


def test_approval_binds_to_proposal_hash() -> None:
    proposal = _proposal()
    approval = _approval(proposal)

    assert approval["artifact_type"] == GOVERNED_REPOSITORY_MUTATION_APPROVAL_ARTIFACT_V1
    assert approval["proposal_id"] == proposal["proposal_id"]
    assert approval["proposal_hash"] == proposal["artifact_hash"]
    assert approval["decision"] == APPROVED
    assert approval["approval_bypassed"] is False


def test_approved_repository_mutation_uses_worker_validates_and_reconstructs(tmp_path) -> None:
    repo = _repo(tmp_path)
    proposal = _proposal()
    approval = _approval(proposal)

    capture = _execute(repo, tmp_path / "replay", proposal, approval)
    reconstructed = reconstruct_governed_repository_mutation_replay(tmp_path / "replay")

    target = repo / proposal["target_paths"][0]
    assert capture["execution_status"] == GOVERNED_REPOSITORY_MUTATION_COMPLETED
    assert capture["repository_mutation_worker_used"] is True
    assert capture["repository_mutation_performed"] is True
    assert capture["approval_bypassed"] is False
    assert target.read_text(encoding="utf-8") == proposal["file_mutations"][0]["new_content"]
    assert capture["worker_capture"]["mutation_status"] == "REPOSITORY_MUTATION_COMPLETED"
    assert capture["validation_capture"]["validation_command_result_artifact"]["exit_code"] == 0
    assert reconstructed["execution_status"] == GOVERNED_REPOSITORY_MUTATION_COMPLETED
    assert reconstructed["repository_mutation_worker_used"] is True
    assert reconstructed["replay_artifact_count"] == 9


def test_missing_approval_fails_closed_without_mutating(tmp_path) -> None:
    repo = _repo(tmp_path)
    proposal = _proposal()

    capture = _execute(repo, tmp_path / "replay", proposal, None)

    assert capture["execution_status"] == FAILED_CLOSED
    assert capture["repository_mutation_performed"] is False
    assert capture["repository_mutation_worker_used"] is False
    assert not (repo / proposal["target_paths"][0]).exists()
    assert "FAIL_CLOSED_NO_APPROVAL" in capture["failure_reason"]


def test_rejected_approval_fails_closed_without_mutating(tmp_path) -> None:
    repo = _repo(tmp_path)
    proposal = _proposal()
    approval = _approval(proposal, "REJECTED")

    capture = _execute(repo, tmp_path / "replay", proposal, approval)

    assert capture["execution_status"] == FAILED_CLOSED
    assert capture["repository_mutation_performed"] is False
    assert not (repo / proposal["target_paths"][0]).exists()


def test_validation_failure_fails_closed_after_worker_evidence(tmp_path) -> None:
    repo = _repo(tmp_path)
    proposal = _proposal(
        [_file_mutation("aigol/runtime/bad_python.py", "def nope(:\n")],
        validation_command=["python", "-m", "py_compile", "aigol/runtime/bad_python.py"],
    )
    approval = _approval(proposal)

    capture = _execute(repo=repo, replay_dir=tmp_path / "replay", proposal=proposal, approval=approval)

    assert capture["execution_status"] == FAILED_CLOSED
    assert "FAIL_CLOSED_VALIDATION_FAILED" in capture["failure_reason"]


def test_corrupted_replay_fails_closed(tmp_path) -> None:
    repo = _repo(tmp_path)
    proposal = _proposal()
    approval = _approval(proposal)
    _execute(repo, tmp_path / "replay", proposal, approval)
    replay_file = tmp_path / "replay" / "008_governed_repository_mutation_outcome_recorded.json"
    payload = json.loads(replay_file.read_text(encoding="utf-8"))
    payload["artifact"]["execution_status"] = "CORRUPTED"
    replay_file.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError):
        reconstruct_governed_repository_mutation_replay(tmp_path / "replay")
