"""Tests for G9-11 governed multi-file mutation runtime."""

from __future__ import annotations

import pytest

from aigol.runtime.multi_file_mutation_runtime import (
    FAILED_CLOSED,
    MULTI_FILE_MUTATION_COMPLETED,
    create_governed_multi_file_mutation_approval,
    create_governed_multi_file_mutation_candidate,
    execute_governed_multi_file_mutation,
    reconstruct_multi_file_mutation_replay,
)
from aigol.runtime.platform_core_ocs_mutation_candidate import DEFAULT_ALLOWLISTED_WORKSPACE
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-02T00:00:00Z"


def _workspace(repo):
    workspace = repo / DEFAULT_ALLOWLISTED_WORKSPACE
    workspace.mkdir(parents=True)
    return workspace


def _operations(replace_before: str = "replace before\n") -> list[dict]:
    return [
        {
            "operation_id": "CREATE-001",
            "operation_type": "create",
            "target_path": "created.txt",
            "content": "created content\n",
        },
        {
            "operation_id": "REPLACE-001",
            "operation_type": "replace",
            "target_path": "replace.txt",
            "expected_content_hash": replay_hash(replace_before),
            "replacement_content": "replace after\n",
        },
        {
            "operation_id": "PATCH-001",
            "operation_type": "patch",
            "target_path": "patch.txt",
            "current_content": "alpha\nbeta\ngamma\n",
            "old_text": "beta\n",
            "new_text": "delta\n",
        },
    ]


def _candidate(replace_before: str = "replace before\n") -> dict:
    return create_governed_multi_file_mutation_candidate(
        candidate_id="G9-11-CANDIDATE-001",
        session_id="G9-11-SESSION-001",
        operations=_operations(replace_before=replace_before),
        created_by="OCS",
        created_at=CREATED_AT,
    )


def _approval(candidate: dict) -> dict:
    return create_governed_multi_file_mutation_approval(
        approval_id="G9-11-APPROVAL-001",
        candidate_artifact=candidate,
        confirmation_text=f"confirm multi-file mutation {candidate['candidate_id']} {candidate['artifact_hash']}",
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
    )


def test_multi_file_mutation_composes_create_replace_and_patch_with_transaction_replay(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    workspace = _workspace(repo)
    (workspace / "replace.txt").write_text("replace before\n", encoding="utf-8")
    (workspace / "patch.txt").write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
    candidate = _candidate()
    approval = _approval(candidate)

    capture = execute_governed_multi_file_mutation(
        execution_id="G9-11-EXECUTION-001",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )
    reconstructed = reconstruct_multi_file_mutation_replay(tmp_path / "replay")

    assert capture["execution_status"] == MULTI_FILE_MUTATION_COMPLETED
    assert capture["repository_mutated"] is True
    assert capture["mutated_file_count"] == 3
    assert capture["rollback_metadata_present"] is True
    assert capture["automatic_rollback_performed"] is False
    assert capture["git_performed"] is False
    assert capture["deployment_performed"] is False
    assert capture["provider_invoked"] is False
    assert capture["dependency_installation_performed"] is False
    assert (workspace / "created.txt").read_text(encoding="utf-8") == "created content\n"
    assert (workspace / "replace.txt").read_text(encoding="utf-8") == "replace after\n"
    assert (workspace / "patch.txt").read_text(encoding="utf-8") == "alpha\ndelta\ngamma\n"
    assert capture["validation_artifact"]["all_operations_valid"] is True
    assert len(capture["rollback_artifact"]["rollback_records"]) == 3
    assert reconstructed["execution_status"] == MULTI_FILE_MUTATION_COMPLETED
    assert reconstructed["operation_count"] == 3
    assert reconstructed["worker_invoked_count"] == 3
    assert reconstructed["replay_artifact_count"] == 8


def test_multi_file_mutation_requires_hash_bound_human_approval(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    workspace = _workspace(repo)
    (workspace / "replace.txt").write_text("replace before\n", encoding="utf-8")
    (workspace / "patch.txt").write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
    candidate = _candidate()

    capture = execute_governed_multi_file_mutation(
        execution_id="G9-11-EXECUTION-NO-APPROVAL",
        candidate_artifact=candidate,
        approval_artifact=None,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )

    assert capture["execution_status"] == FAILED_CLOSED
    assert capture["repository_mutated"] is False
    assert "approval required" in capture["failure_reason"]
    assert not (workspace / "created.txt").exists()


def test_multi_file_mutation_fails_closed_before_execution_on_hash_conflict(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    workspace = _workspace(repo)
    (workspace / "replace.txt").write_text("unexpected replace content\n", encoding="utf-8")
    (workspace / "patch.txt").write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
    candidate = _candidate(replace_before="replace before\n")
    approval = _approval(candidate)

    capture = execute_governed_multi_file_mutation(
        execution_id="G9-11-EXECUTION-CONFLICT",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )

    assert capture["execution_status"] == FAILED_CLOSED
    assert capture["repository_mutated"] is False
    assert "pre-transaction validation conflict" in capture["failure_reason"]
    assert not (workspace / "created.txt").exists()
    assert (workspace / "replace.txt").read_text(encoding="utf-8") == "unexpected replace content\n"


def test_multi_file_mutation_rejects_duplicate_transaction_targets() -> None:
    operations = _operations()
    operations[1]["target_path"] = "created.txt"

    with pytest.raises(Exception, match="duplicate target path"):
        create_governed_multi_file_mutation_candidate(
            candidate_id="G9-11-CANDIDATE-DUPLICATE",
            session_id="G9-11-SESSION-001",
            operations=operations,
            created_by="OCS",
            created_at=CREATED_AT,
        )


def test_multi_file_mutation_rejects_unbound_confirmation() -> None:
    candidate = _candidate()

    with pytest.raises(Exception, match="confirmation does not bind candidate hash"):
        create_governed_multi_file_mutation_approval(
            approval_id="G9-11-BAD-APPROVAL",
            candidate_artifact=candidate,
            confirmation_text="confirm multi-file mutation please",
            approved_by="HUMAN_OPERATOR",
            approved_at=CREATED_AT,
        )
