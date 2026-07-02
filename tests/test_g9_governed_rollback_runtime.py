"""Tests for G9-09 governed rollback execution runtime."""

from __future__ import annotations

import pytest

from aigol.runtime.first_mutating_worker_runtime import (
    FIRST_MUTATING_WORKER_COMPLETED,
    create_first_mutating_worker_approval,
    create_first_mutating_worker_candidate,
    execute_first_mutating_worker,
)
from aigol.runtime.existing_file_mutation_runtime import (
    EXISTING_FILE_MUTATION_COMPLETED,
    create_existing_file_mutation_approval,
    create_existing_file_mutation_candidate,
    execute_existing_file_mutation,
)
from aigol.runtime.governed_rollback_runtime import (
    FAILED_CLOSED,
    GOVERNED_ROLLBACK_EXECUTION_COMPLETED,
    create_governed_rollback_candidate,
    create_governed_rollback_human_approval,
    execute_governed_rollback,
    reconstruct_governed_rollback_replay,
)
from aigol.runtime.platform_core_ocs_mutation_candidate import DEFAULT_ALLOWLISTED_WORKSPACE
from aigol.runtime.platform_core_rollback_candidate import (
    PRIOR_EXISTING_FILE_MUTATION,
    PRIOR_FIRST_MUTATING_WORKER,
    PRIOR_PATCH_MUTATION,
)
from aigol.runtime.single_file_patch_mutation_runtime import (
    PATCH_MUTATION_COMPLETED,
    create_single_file_patch_mutation_approval,
    create_single_file_patch_mutation_candidate,
    execute_single_file_patch_mutation,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-02T00:00:00Z"


def _workspace(repo):
    workspace = repo / DEFAULT_ALLOWLISTED_WORKSPACE
    workspace.mkdir(parents=True)
    return workspace


def _rollback_approval(candidate: dict) -> dict:
    return create_governed_rollback_human_approval(
        approval_id=f"{candidate['candidate_id']}:APPROVAL",
        candidate_artifact=candidate,
        confirmation_text=f"confirm governed rollback execution {candidate['candidate_id']} {candidate['artifact_hash']}",
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
    )


def _execute_prior_patch(repo, replay_dir, *, target_path: str = "patch-target.txt") -> dict:
    workspace = repo / DEFAULT_ALLOWLISTED_WORKSPACE
    target = workspace / target_path
    target.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
    candidate = create_single_file_patch_mutation_candidate(
        candidate_id="G9-09-PRIOR-PATCH-CANDIDATE",
        session_id="G9-09-SESSION",
        target_path=target_path,
        current_content="alpha\nbeta\ngamma\n",
        old_text="beta\n",
        new_text="delta\n",
        created_by="OCS",
        created_at=CREATED_AT,
    )
    approval = create_single_file_patch_mutation_approval(
        approval_id="G9-09-PRIOR-PATCH-APPROVAL",
        candidate_artifact=candidate,
        confirmation_text=f"confirm single-file patch mutation {candidate['candidate_id']} {candidate['artifact_hash']}",
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
    )
    capture = execute_single_file_patch_mutation(
        execution_id="G9-09-PRIOR-PATCH-EXECUTION",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=replay_dir,
    )
    assert capture["execution_status"] == PATCH_MUTATION_COMPLETED
    return capture


def _execute_prior_create(repo, replay_dir, *, target_path: str = "created-target.txt") -> dict:
    candidate = create_first_mutating_worker_candidate(
        candidate_id="G9-09-PRIOR-CREATE-CANDIDATE",
        session_id="G9-09-SESSION",
        target_filename=target_path,
        content="created content\n",
        created_by="OCS",
        created_at=CREATED_AT,
    )
    approval = create_first_mutating_worker_approval(
        approval_id="G9-09-PRIOR-CREATE-APPROVAL",
        candidate_artifact=candidate,
        confirmation_text=f"confirm mutation {candidate['candidate_id']} {candidate['artifact_hash']}",
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
    )
    capture = execute_first_mutating_worker(
        execution_id="G9-09-PRIOR-CREATE-EXECUTION",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=replay_dir,
    )
    assert capture["execution_status"] == FIRST_MUTATING_WORKER_COMPLETED
    return capture


def _execute_prior_existing_file_replacement(repo, replay_dir, *, target_path: str = "existing-target.txt") -> dict:
    workspace = repo / DEFAULT_ALLOWLISTED_WORKSPACE
    target = workspace / target_path
    target.write_text("before\n", encoding="utf-8")
    candidate = create_existing_file_mutation_candidate(
        candidate_id="G9-09-PRIOR-EXISTING-CANDIDATE",
        session_id="G9-09-SESSION",
        target_path=target_path,
        expected_content_hash=replay_hash("before\n"),
        replacement_content="after\n",
        created_by="OCS",
        created_at=CREATED_AT,
    )
    approval = create_existing_file_mutation_approval(
        approval_id="G9-09-PRIOR-EXISTING-APPROVAL",
        candidate_artifact=candidate,
        confirmation_text=f"confirm existing-file mutation {candidate['candidate_id']} {candidate['artifact_hash']}",
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
    )
    capture = execute_existing_file_mutation(
        execution_id="G9-09-PRIOR-EXISTING-EXECUTION",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=replay_dir,
    )
    assert capture["execution_status"] == EXISTING_FILE_MUTATION_COMPLETED
    return capture


def test_governed_rollback_restores_prior_patch_mutation(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    workspace = _workspace(repo)
    prior_replay = tmp_path / "prior_patch_replay"
    _execute_prior_patch(repo, prior_replay)
    target = workspace / "patch-target.txt"
    assert target.read_text(encoding="utf-8") == "alpha\ndelta\ngamma\n"
    candidate = create_governed_rollback_candidate(
        candidate_id="G9-09-ROLLBACK-PATCH-CANDIDATE",
        session_id="G9-09-SESSION",
        prior_mutation_type=PRIOR_PATCH_MUTATION,
        prior_replay_dir=prior_replay,
        target_path="patch-target.txt",
        created_by="OCS",
        created_at=CREATED_AT,
    )
    approval = _rollback_approval(candidate)

    capture = execute_governed_rollback(
        execution_id="G9-09-ROLLBACK-PATCH-EXECUTION",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "rollback_replay",
    )
    reconstructed = reconstruct_governed_rollback_replay(tmp_path / "rollback_replay")

    assert capture["execution_status"] == GOVERNED_ROLLBACK_EXECUTION_COMPLETED
    assert capture["rollback_executed"] is True
    assert capture["repository_mutated"] is True
    assert capture["mutated_file_count"] == 1
    assert capture["git_performed"] is False
    assert capture["branch_manipulation_performed"] is False
    assert capture["deployment_performed"] is False
    assert capture["provider_invoked"] is False
    assert capture["dependency_rollback_performed"] is False
    assert capture["automatic_rollback_performed"] is False
    assert target.read_text(encoding="utf-8") == "alpha\nbeta\ngamma\n"
    assert capture["validation_artifact"]["post_rollback_hash"] == replay_hash("alpha\nbeta\ngamma\n")
    assert reconstructed["execution_status"] == GOVERNED_ROLLBACK_EXECUTION_COMPLETED
    assert reconstructed["prior_mutation_type"] == PRIOR_PATCH_MUTATION
    assert reconstructed["replay_artifact_count"] == 8


def test_governed_rollback_deletes_prior_created_file(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    workspace = _workspace(repo)
    prior_replay = tmp_path / "prior_create_replay"
    _execute_prior_create(repo, prior_replay)
    target = workspace / "created-target.txt"
    assert target.exists()
    candidate = create_governed_rollback_candidate(
        candidate_id="G9-09-ROLLBACK-CREATE-CANDIDATE",
        session_id="G9-09-SESSION",
        prior_mutation_type=PRIOR_FIRST_MUTATING_WORKER,
        prior_replay_dir=prior_replay,
        target_path="created-target.txt",
        created_by="OCS",
        created_at=CREATED_AT,
    )
    approval = _rollback_approval(candidate)

    capture = execute_governed_rollback(
        execution_id="G9-09-ROLLBACK-CREATE-EXECUTION",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "rollback_replay",
    )

    assert capture["execution_status"] == GOVERNED_ROLLBACK_EXECUTION_COMPLETED
    assert capture["rollback_executed"] is True
    assert target.exists() is False
    assert capture["validation_artifact"]["target_exists_after"] is False


def test_governed_rollback_requires_hash_bound_human_approval(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _workspace(repo)
    prior_replay = tmp_path / "prior_patch_replay"
    _execute_prior_patch(repo, prior_replay)
    candidate = create_governed_rollback_candidate(
        candidate_id="G9-09-ROLLBACK-NO-APPROVAL-CANDIDATE",
        session_id="G9-09-SESSION",
        prior_mutation_type=PRIOR_PATCH_MUTATION,
        prior_replay_dir=prior_replay,
        target_path="patch-target.txt",
        created_by="OCS",
        created_at=CREATED_AT,
    )

    capture = execute_governed_rollback(
        execution_id="G9-09-ROLLBACK-NO-APPROVAL-EXECUTION",
        candidate_artifact=candidate,
        approval_artifact=None,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "rollback_replay",
    )

    assert capture["execution_status"] == FAILED_CLOSED
    assert capture["rollback_executed"] is False
    assert capture["repository_mutated"] is False
    assert "approval required" in capture["failure_reason"]


def test_governed_rollback_fails_closed_on_current_hash_conflict(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    workspace = _workspace(repo)
    prior_replay = tmp_path / "prior_patch_replay"
    _execute_prior_patch(repo, prior_replay)
    target = workspace / "patch-target.txt"
    target.write_text("operator changed after mutation\n", encoding="utf-8")
    candidate = create_governed_rollback_candidate(
        candidate_id="G9-09-ROLLBACK-CONFLICT-CANDIDATE",
        session_id="G9-09-SESSION",
        prior_mutation_type=PRIOR_PATCH_MUTATION,
        prior_replay_dir=prior_replay,
        target_path="patch-target.txt",
        created_by="OCS",
        created_at=CREATED_AT,
    )
    approval = _rollback_approval(candidate)

    capture = execute_governed_rollback(
        execution_id="G9-09-ROLLBACK-CONFLICT-EXECUTION",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "rollback_replay",
    )

    assert capture["execution_status"] == FAILED_CLOSED
    assert capture["rollback_executed"] is False
    assert capture["repository_mutated"] is False
    assert "current hash conflict" in capture["failure_reason"]
    assert target.read_text(encoding="utf-8") == "operator changed after mutation\n"


def test_governed_rollback_rejects_unbound_confirmation(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _workspace(repo)
    prior_replay = tmp_path / "prior_patch_replay"
    _execute_prior_patch(repo, prior_replay)
    candidate = create_governed_rollback_candidate(
        candidate_id="G9-09-ROLLBACK-BAD-APPROVAL-CANDIDATE",
        session_id="G9-09-SESSION",
        prior_mutation_type=PRIOR_PATCH_MUTATION,
        prior_replay_dir=prior_replay,
        target_path="patch-target.txt",
        created_by="OCS",
        created_at=CREATED_AT,
    )

    with pytest.raises(Exception, match="confirmation does not bind candidate hash"):
        create_governed_rollback_human_approval(
            approval_id="G9-09-BAD-APPROVAL",
            candidate_artifact=candidate,
            confirmation_text="confirm governed rollback execution",
            approved_by="HUMAN_OPERATOR",
            approved_at=CREATED_AT,
        )


def test_existing_file_rollback_without_complete_original_content_fails_closed(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _workspace(repo)
    prior_replay = tmp_path / "existing_file_replay"
    _execute_prior_existing_file_replacement(repo, prior_replay)

    with pytest.raises(Exception, match="complete original content evidence"):
        create_governed_rollback_candidate(
            candidate_id="G9-09-EXISTING-FILE-ROLLBACK-CANDIDATE",
            session_id="G9-09-SESSION",
            prior_mutation_type=PRIOR_EXISTING_FILE_MUTATION,
            prior_replay_dir=prior_replay,
            target_path="existing-target.txt",
            created_by="OCS",
            created_at=CREATED_AT,
        )
