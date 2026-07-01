"""Tests for G9-04 governed single-file patch-level mutation runtime."""

from __future__ import annotations

import inspect

import pytest

from aigol.runtime.platform_core_ocs_mutation_candidate import DEFAULT_ALLOWLISTED_WORKSPACE
from aigol.runtime.single_file_patch_mutation_runtime import (
    FAILED_CLOSED,
    PATCH_MUTATION_COMPLETED,
    create_single_file_patch_mutation_approval,
    create_single_file_patch_mutation_candidate,
    execute_single_file_patch_mutation,
    reconstruct_single_file_patch_mutation_replay,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-01T00:00:00Z"


def _workspace(repo):
    workspace = repo / DEFAULT_ALLOWLISTED_WORKSPACE
    workspace.mkdir(parents=True)
    return workspace


def _candidate(current_content: str = "alpha\nbeta\ngamma\n") -> dict:
    return create_single_file_patch_mutation_candidate(
        candidate_id="G9-04-CANDIDATE-001",
        session_id="G9-04-SESSION-001",
        target_path="patch-target.txt",
        current_content=current_content,
        old_text="beta\n",
        new_text="delta\n",
        created_by="OCS",
        created_at=CREATED_AT,
    )


def _approval(candidate: dict) -> dict:
    return create_single_file_patch_mutation_approval(
        approval_id="G9-04-APPROVAL-001",
        candidate_artifact=candidate,
        confirmation_text=f"confirm single-file patch mutation {candidate['candidate_id']} {candidate['artifact_hash']}",
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
    )


def test_single_file_patch_mutation_persists_complete_canonical_artifact(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    workspace = _workspace(repo)
    target = workspace / "patch-target.txt"
    target.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
    candidate = _candidate()
    approval = _approval(candidate)

    capture = execute_single_file_patch_mutation(
        execution_id="G9-04-EXECUTION-001",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )
    reconstructed = reconstruct_single_file_patch_mutation_replay(tmp_path / "replay")

    assert capture["execution_status"] == PATCH_MUTATION_COMPLETED
    assert capture["repository_mutated"] is True
    assert capture["file_patched"] is True
    assert capture["git_performed"] is False
    assert capture["commit_created"] is False
    assert capture["deployment_performed"] is False
    assert capture["provider_invoked"] is False
    assert target.read_text(encoding="utf-8") == "alpha\ndelta\ngamma\n"
    assert capture["canonical_execution_artifact"] == "complete_resulting_file"
    assert capture["patch_is_intent_only"] is True
    assert capture["patch_persisted_as_execution_artifact"] is False
    assert capture["complete_resulting_content_hash"] == replay_hash("alpha\ndelta\ngamma\n")
    assert capture["validation_artifact"]["complete_resulting_content"] == "alpha\ndelta\ngamma\n"
    assert capture["rollback_artifact"]["rollback_operation"] == (
        "RESTORE_ORIGINAL_CONTENT_IF_CURRENT_HASH_MATCHES_AUTHORIZED_POST_HASH"
    )
    assert reconstructed["execution_status"] == PATCH_MUTATION_COMPLETED
    assert reconstructed["worker_invoked"] is True
    assert reconstructed["repository_mutated"] is True
    assert reconstructed["rollback_metadata_present"] is True
    assert reconstructed["canonical_execution_artifact"] == "complete_resulting_file"
    assert reconstructed["patch_is_intent_only"] is True
    assert reconstructed["replay_artifact_count"] == 9


def test_single_file_patch_mutation_requires_hash_bound_human_approval(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    workspace = _workspace(repo)
    target = workspace / "patch-target.txt"
    target.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
    candidate = _candidate()

    capture = execute_single_file_patch_mutation(
        execution_id="G9-04-EXECUTION-NO-APPROVAL",
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
    assert target.read_text(encoding="utf-8") == "alpha\nbeta\ngamma\n"


def test_single_file_patch_mutation_fails_closed_on_hash_conflict(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    workspace = _workspace(repo)
    target = workspace / "patch-target.txt"
    target.write_text("alpha\nchanged\ngamma\n", encoding="utf-8")
    candidate = _candidate(current_content="alpha\nbeta\ngamma\n")
    approval = _approval(candidate)

    capture = execute_single_file_patch_mutation(
        execution_id="G9-04-EXECUTION-CONFLICT",
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
    assert target.read_text(encoding="utf-8") == "alpha\nchanged\ngamma\n"


def test_single_file_patch_mutation_rejects_ambiguous_old_text_candidate() -> None:
    with pytest.raises(Exception, match="old text ambiguous"):
        create_single_file_patch_mutation_candidate(
            candidate_id="G9-04-CANDIDATE-AMBIGUOUS",
            session_id="G9-04-SESSION-001",
            target_path="patch-target.txt",
            current_content="alpha\nbeta\nbeta\n",
            old_text="beta\n",
            new_text="delta\n",
            created_by="OCS",
            created_at=CREATED_AT,
        )


def test_single_file_patch_mutation_rejects_missing_old_text_candidate() -> None:
    with pytest.raises(Exception, match="old text missing"):
        create_single_file_patch_mutation_candidate(
            candidate_id="G9-04-CANDIDATE-MISSING",
            session_id="G9-04-SESSION-001",
            target_path="patch-target.txt",
            current_content="alpha\ngamma\n",
            old_text="beta\n",
            new_text="delta\n",
            created_by="OCS",
            created_at=CREATED_AT,
        )


def test_single_file_patch_mutation_rejects_unbound_confirmation() -> None:
    candidate = _candidate()

    with pytest.raises(Exception, match="confirmation does not bind candidate hash"):
        create_single_file_patch_mutation_approval(
            approval_id="G9-04-APPROVAL-BAD",
            candidate_artifact=candidate,
            confirmation_text="confirm single-file patch mutation please",
            approved_by="HUMAN_OPERATOR",
            approved_at=CREATED_AT,
        )


def test_single_file_patch_mutation_requires_validation_evidence_when_required(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    workspace = _workspace(repo)
    target = workspace / "patch-target.txt"
    target.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
    candidate = create_single_file_patch_mutation_candidate(
        candidate_id="G9-04-CANDIDATE-VALIDATION",
        session_id="G9-04-SESSION-001",
        target_path="patch-target.txt",
        current_content="alpha\nbeta\ngamma\n",
        old_text="beta\n",
        new_text="delta\n",
        created_by="OCS",
        created_at=CREATED_AT,
        validation_state="validation_required_before_completion",
    )
    approval = _approval(candidate)

    capture = execute_single_file_patch_mutation(
        execution_id="G9-04-EXECUTION-VALIDATION-MISSING",
        candidate_artifact=candidate,
        approval_artifact=approval,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )

    assert capture["execution_status"] == FAILED_CLOSED
    assert "validation evidence required" in capture["failure_reason"]


def test_single_file_patch_mutation_has_no_provider_git_or_deployment_surface() -> None:
    import aigol.runtime.single_file_patch_mutation_runtime as runtime
    import aigol.workers.filesystem_patch_worker as worker

    source = inspect.getsource(runtime) + inspect.getsource(worker)

    assert "subprocess." not in source
    assert "os.system" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "git " not in source.lower()
    assert "commit(" not in source
    deployment_flag_source = source.replace('"deployment_performed"', "")
    deployment_flag_source = deployment_flag_source.replace('"deployment_request"', "")
    assert "deploy" not in deployment_flag_source
