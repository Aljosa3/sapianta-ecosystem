"""Tests for G8-09 first governed mutating Worker runtime."""

from __future__ import annotations

import inspect

import pytest

from aigol.runtime.first_mutating_worker_runtime import (
    DEFAULT_ALLOWLISTED_WORKSPACE,
    FAILED_CLOSED,
    FIRST_MUTATING_WORKER_COMPLETED,
    create_first_mutating_worker_approval,
    create_first_mutating_worker_candidate,
    execute_first_mutating_worker,
    reconstruct_first_mutating_worker_replay,
)


CREATED_AT = "2026-07-01T00:00:00Z"


def _workspace(repo):
    workspace = repo / DEFAULT_ALLOWLISTED_WORKSPACE
    workspace.mkdir(parents=True)
    return workspace


def _candidate() -> dict:
    return create_first_mutating_worker_candidate(
        candidate_id="G8-09-CANDIDATE-001",
        session_id="G8-09-SESSION-001",
        target_filename="first-governed-mutation.txt",
        content="first governed mutation\n",
        created_by="OCS",
        created_at=CREATED_AT,
    )


def _approval(candidate: dict) -> dict:
    return create_first_mutating_worker_approval(
        approval_id="G8-09-APPROVAL-001",
        candidate_artifact=candidate,
        confirmation_text=f"confirm mutation {candidate['candidate_id']} {candidate['artifact_hash']}",
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
    )


def test_first_mutating_worker_creates_one_file_with_replay_validation_and_rollback(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    workspace = _workspace(repo)
    candidate = _candidate()
    approval = _approval(candidate)

    capture = execute_first_mutating_worker(
        execution_id="G8-09-EXECUTION-001",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )
    reconstructed = reconstruct_first_mutating_worker_replay(tmp_path / "replay")

    target = workspace / "first-governed-mutation.txt"
    assert capture["execution_status"] == FIRST_MUTATING_WORKER_COMPLETED
    assert capture["repository_mutated"] is True
    assert capture["file_created"] is True
    assert capture["git_performed"] is False
    assert capture["commit_created"] is False
    assert capture["deployment_performed"] is False
    assert capture["provider_invoked"] is False
    assert target.read_text(encoding="utf-8") == "first governed mutation\n"
    assert capture["rollback_artifact"]["rollback_operation"] == "DELETE_CREATED_FILE_IF_HASH_MATCHES"
    assert capture["rollback_artifact"]["automatic_rollback_allowed"] is False
    assert reconstructed["execution_status"] == FIRST_MUTATING_WORKER_COMPLETED
    assert reconstructed["worker_invoked"] is True
    assert reconstructed["repository_mutated"] is True
    assert reconstructed["rollback_metadata_present"] is True
    assert reconstructed["replay_artifact_count"] == 9


def test_first_mutating_worker_requires_hash_bound_human_approval(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _workspace(repo)
    candidate = _candidate()

    capture = execute_first_mutating_worker(
        execution_id="G8-09-EXECUTION-NO-APPROVAL",
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
    assert not (repo / DEFAULT_ALLOWLISTED_WORKSPACE / "first-governed-mutation.txt").exists()


def test_first_mutating_worker_rejects_unbound_confirmation() -> None:
    candidate = _candidate()

    with pytest.raises(Exception, match="confirmation does not bind candidate hash"):
        create_first_mutating_worker_approval(
            approval_id="G8-09-APPROVAL-BAD",
            candidate_artifact=candidate,
            confirmation_text="confirm mutation please",
            approved_by="HUMAN_OPERATOR",
            approved_at=CREATED_AT,
        )


def test_first_mutating_worker_fails_closed_on_existing_target(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    workspace = _workspace(repo)
    (workspace / "first-governed-mutation.txt").write_text("preexisting\n", encoding="utf-8")
    candidate = _candidate()
    approval = _approval(candidate)

    capture = execute_first_mutating_worker(
        execution_id="G8-09-EXECUTION-COLLISION",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )

    assert capture["execution_status"] == FAILED_CLOSED
    assert capture["repository_mutated"] is False
    assert "target file already exists" in capture["failure_reason"]
    assert (workspace / "first-governed-mutation.txt").read_text(encoding="utf-8") == "preexisting\n"


def test_first_mutating_worker_rejects_path_traversal_candidate() -> None:
    with pytest.raises(Exception, match="one relative filename"):
        create_first_mutating_worker_candidate(
            candidate_id="G8-09-CANDIDATE-ESCAPE",
            session_id="G8-09-SESSION-001",
            target_filename="../escape.txt",
            content="escape\n",
            created_by="OCS",
            created_at=CREATED_AT,
        )


def test_first_mutating_worker_has_no_provider_git_or_deployment_surface() -> None:
    import aigol.runtime.first_mutating_worker_runtime as runtime

    source = inspect.getsource(runtime)

    assert "subprocess." not in source
    assert "os.system" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "git " not in source.lower()
    assert "commit(" not in source
    assert "deploy" not in source.replace('"deployment_allowed"', "").replace('"deployment_performed"', "")


def test_first_mutating_worker_runtime_delegates_platform_core_responsibilities() -> None:
    import aigol.runtime.first_mutating_worker_runtime as runtime

    source = inspect.getsource(runtime)

    assert "def create_first_mutating_worker_candidate" not in source
    assert "def create_first_mutating_worker_approval" not in source
    assert "def reconstruct_first_mutating_worker_replay" not in source
    assert "create_authorization_record" not in source
    assert "validate_authorization_record" not in source
    assert "write_json_immutable" not in source
    assert "load_json" not in source
    assert "def _validation_artifact" not in source
    assert "def _rollback_artifact" not in source
    assert "validate_mutation_candidate" in source
    assert "validate_mutation_approval" in source
    assert "create_mutation_authorization_record" in source
    assert "persist_mutation_replay_step" in source
    assert "post_mutation_validation_artifact" in source
    assert "mutation_rollback_metadata_artifact" in source
