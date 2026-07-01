"""Tests for G8-12 governed existing-file mutation runtime."""

from __future__ import annotations

import inspect

import pytest

from aigol.runtime.existing_file_mutation_runtime import (
    EXISTING_FILE_MUTATION_COMPLETED,
    FAILED_CLOSED,
    create_existing_file_mutation_approval,
    create_existing_file_mutation_candidate,
    execute_existing_file_mutation,
    reconstruct_existing_file_mutation_replay,
)
from aigol.runtime.platform_core_ocs_mutation_candidate import DEFAULT_ALLOWLISTED_WORKSPACE
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-01T00:00:00Z"


def _workspace(repo):
    workspace = repo / DEFAULT_ALLOWLISTED_WORKSPACE
    workspace.mkdir(parents=True)
    return workspace


def _candidate(current_content: str = "before\n") -> dict:
    return create_existing_file_mutation_candidate(
        candidate_id="G8-12-CANDIDATE-001",
        session_id="G8-12-SESSION-001",
        target_path="existing-file.txt",
        expected_content_hash=replay_hash(current_content),
        replacement_content="after\n",
        created_by="OCS",
        created_at=CREATED_AT,
    )


def _approval(candidate: dict) -> dict:
    return create_existing_file_mutation_approval(
        approval_id="G8-12-APPROVAL-001",
        candidate_artifact=candidate,
        confirmation_text=f"confirm existing-file mutation {candidate['candidate_id']} {candidate['artifact_hash']}",
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
    )


def test_existing_file_mutation_replaces_one_file_with_replay_validation_and_rollback(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    workspace = _workspace(repo)
    target = workspace / "existing-file.txt"
    target.write_text("before\n", encoding="utf-8")
    candidate = _candidate()
    approval = _approval(candidate)

    capture = execute_existing_file_mutation(
        execution_id="G8-12-EXECUTION-001",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )
    reconstructed = reconstruct_existing_file_mutation_replay(tmp_path / "replay")

    assert capture["execution_status"] == EXISTING_FILE_MUTATION_COMPLETED
    assert capture["repository_mutated"] is True
    assert capture["file_replaced"] is True
    assert capture["git_performed"] is False
    assert capture["commit_created"] is False
    assert capture["deployment_performed"] is False
    assert capture["provider_invoked"] is False
    assert target.read_text(encoding="utf-8") == "after\n"
    assert capture["rollback_artifact"]["rollback_operation"] == (
        "RESTORE_ORIGINAL_CONTENT_IF_CURRENT_HASH_MATCHES_AUTHORIZED_POST_HASH"
    )
    assert capture["rollback_artifact"]["automatic_rollback_allowed"] is False
    assert reconstructed["execution_status"] == EXISTING_FILE_MUTATION_COMPLETED
    assert reconstructed["worker_invoked"] is True
    assert reconstructed["repository_mutated"] is True
    assert reconstructed["rollback_metadata_present"] is True
    assert reconstructed["replay_artifact_count"] == 9


def test_existing_file_mutation_requires_hash_bound_human_approval(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    workspace = _workspace(repo)
    target = workspace / "existing-file.txt"
    target.write_text("before\n", encoding="utf-8")
    candidate = _candidate()

    capture = execute_existing_file_mutation(
        execution_id="G8-12-EXECUTION-NO-APPROVAL",
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
    assert target.read_text(encoding="utf-8") == "before\n"


def test_existing_file_mutation_fails_closed_on_hash_conflict(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    workspace = _workspace(repo)
    target = workspace / "existing-file.txt"
    target.write_text("changed\n", encoding="utf-8")
    candidate = _candidate(current_content="before\n")
    approval = _approval(candidate)

    capture = execute_existing_file_mutation(
        execution_id="G8-12-EXECUTION-CONFLICT",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )

    assert capture["execution_status"] == FAILED_CLOSED
    assert capture["repository_mutated"] is False
    assert "target hash conflict" in capture["failure_reason"]
    assert target.read_text(encoding="utf-8") == "changed\n"


def test_existing_file_mutation_fails_closed_when_target_is_missing(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _workspace(repo)
    candidate = _candidate()
    approval = _approval(candidate)

    capture = execute_existing_file_mutation(
        execution_id="G8-12-EXECUTION-MISSING",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )

    assert capture["execution_status"] == FAILED_CLOSED
    assert capture["repository_mutated"] is False
    assert "target must be existing regular file" in capture["failure_reason"]


def test_existing_file_mutation_rejects_path_traversal_candidate() -> None:
    with pytest.raises(Exception, match="target path must not contain traversal"):
        create_existing_file_mutation_candidate(
            candidate_id="G8-12-CANDIDATE-ESCAPE",
            session_id="G8-12-SESSION-001",
            target_path="../escape.txt",
            expected_content_hash=replay_hash("before\n"),
            replacement_content="after\n",
            created_by="OCS",
            created_at=CREATED_AT,
        )


def test_existing_file_mutation_rejects_unbound_confirmation() -> None:
    candidate = _candidate()

    with pytest.raises(Exception, match="confirmation does not bind candidate hash"):
        create_existing_file_mutation_approval(
            approval_id="G8-12-APPROVAL-BAD",
            candidate_artifact=candidate,
            confirmation_text="confirm existing-file mutation please",
            approved_by="HUMAN_OPERATOR",
            approved_at=CREATED_AT,
        )


def test_existing_file_mutation_has_no_provider_git_or_deployment_surface() -> None:
    import aigol.runtime.existing_file_mutation_runtime as runtime
    import aigol.workers.filesystem_replace_worker as worker

    source = inspect.getsource(runtime) + inspect.getsource(worker)

    assert "subprocess." not in source
    assert "os.system" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "git " not in source.lower()
    assert "commit(" not in source
    deployment_flag_source = source.replace('"deployment_allowed"', "")
    deployment_flag_source = deployment_flag_source.replace('"deployment_performed"', "")
    deployment_flag_source = deployment_flag_source.replace('"deployment_request"', "")
    assert "deploy" not in deployment_flag_source
