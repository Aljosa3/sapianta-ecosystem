"""Tests for G8-16 governed local Git commit runtime."""

from __future__ import annotations

import subprocess

import pytest

from aigol.runtime.governed_git_commit_runtime import (
    FAILED_CLOSED,
    GOVERNED_GIT_COMMIT_COMPLETED,
    create_governed_git_commit_approval,
    create_governed_git_commit_candidate,
    execute_governed_git_commit,
    reconstruct_governed_git_commit_replay,
)
from aigol.runtime.platform_core_git_commit_candidate import ADD_TEXT_FILE, REPLACE_TEXT_FILE
from aigol.runtime.platform_core_git_commit_governance import create_governed_git_commit_authorization_record
from aigol.runtime.platform_core_validation_result import VALIDATION_RESULT_ARTIFACT_V1
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.git_commit_worker import (
    create_authorized_git_commit_request,
    validate_authorized_git_commit_request,
)


CREATED_AT = "2026-07-01T00:00:00Z"
GIT_ENV = {
    "GIT_AUTHOR_NAME": "AiGOL Test",
    "GIT_AUTHOR_EMAIL": "aigol@example.invalid",
    "GIT_COMMITTER_NAME": "AiGOL Test",
    "GIT_COMMITTER_EMAIL": "aigol@example.invalid",
}


def _run_git(repo, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        shell=False,
        check=True,
        env=GIT_ENV,
    )
    return (completed.stdout or "").strip()


def _repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, ["init"])
    tracked = repo / "tracked.txt"
    tracked.write_text("before\n", encoding="utf-8")
    _run_git(repo, ["add", "--", "tracked.txt"])
    _run_git(repo, ["commit", "--no-gpg-sign", "-m", "Initial commit"])
    return repo


def _branch(repo) -> str:
    return _run_git(repo, ["rev-parse", "--abbrev-ref", "HEAD"])


def _head(repo) -> str:
    return _run_git(repo, ["rev-parse", "HEAD"])


def _validation_artifact(status: str = "VALIDATION_PASSED") -> dict:
    artifact = {
        "artifact_type": VALIDATION_RESULT_ARTIFACT_V1,
        "runtime_version": "G8_14_GOVERNED_VALIDATION_EXECUTION_IMPLEMENTATION_V1",
        "execution_id": "G8-16-VALIDATION-001",
        "validation_status": status,
        "validation_passed": status == "VALIDATION_PASSED",
        "exit_code": 0 if status == "VALIDATION_PASSED" else 1,
        "timed_out": False,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _candidate(repo, path: str = "new.txt", change_type: str = ADD_TEXT_FILE) -> tuple[dict, dict]:
    if change_type == ADD_TEXT_FILE:
        (repo / path).write_text("new governed content\n", encoding="utf-8")
    validation = _validation_artifact()
    candidate = create_governed_git_commit_candidate(
        candidate_id=f"G8-16-CANDIDATE-{path}",
        session_id="G8-16-SESSION-001",
        repository_id="TEMP-GIT-REPOSITORY",
        branch_name=_branch(repo),
        expected_head=_head(repo),
        file_set=[
            {
                "path": path,
                "change_type": change_type,
                "content_hash": replay_hash((repo / path).read_text(encoding="utf-8")),
            }
        ],
        commit_message={
            "subject": "Governed local commit",
            "body": "AiGOL governed commit test.",
        },
        author={"name": "AiGOL Test", "email": "aigol@example.invalid"},
        validation_artifact=validation,
        created_by="OCS",
        created_at=CREATED_AT,
    )
    return candidate, validation


def _approval(candidate: dict) -> dict:
    return create_governed_git_commit_approval(
        approval_id=f"{candidate['candidate_id']}:APPROVAL",
        candidate_artifact=candidate,
        confirmation_text=f"confirm governed git commit {candidate['candidate_id']} {candidate['artifact_hash']}",
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
    )


def test_governed_git_commit_creates_one_local_commit_with_replay(tmp_path) -> None:
    repo = _repo(tmp_path)
    parent = _head(repo)
    candidate, validation = _candidate(repo)
    approval = _approval(candidate)

    capture = execute_governed_git_commit(
        execution_id="G8-16-EXECUTION-001",
        candidate_artifact=candidate,
        approval_artifact=approval,
        validation_artifact=validation,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )
    reconstructed = reconstruct_governed_git_commit_replay(tmp_path / "replay")

    assert capture["execution_status"] == GOVERNED_GIT_COMMIT_COMPLETED
    assert capture["git_performed"] is True
    assert capture["commit_created"] is True
    assert capture["push_performed"] is False
    assert capture["remote_interaction_performed"] is False
    assert capture["branch_management_performed"] is False
    assert capture["deployment_performed"] is False
    assert capture["provider_invoked"] is False
    assert capture["parent_head"] == parent
    assert capture["commit_hash"] == _head(repo)
    assert capture["commit_hash"] != parent
    assert reconstructed["commit_hash"] == capture["commit_hash"]
    assert reconstructed["replay_artifact_count"] == 10
    assert "new.txt" in _run_git(repo, ["show", "--name-only", "--format=", capture["commit_hash"]])


def test_governed_git_commit_can_commit_authorized_existing_file_replacement(tmp_path) -> None:
    repo = _repo(tmp_path)
    (repo / "tracked.txt").write_text("after\n", encoding="utf-8")
    candidate, validation = _candidate(repo, path="tracked.txt", change_type=REPLACE_TEXT_FILE)
    approval = _approval(candidate)

    capture = execute_governed_git_commit(
        execution_id="G8-16-EXECUTION-REPLACE",
        candidate_artifact=candidate,
        approval_artifact=approval,
        validation_artifact=validation,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )

    assert capture["execution_status"] == GOVERNED_GIT_COMMIT_COMPLETED
    assert capture["commit_created"] is True
    assert "tracked.txt" in _run_git(repo, ["show", "--name-only", "--format=", capture["commit_hash"]])


def test_governed_git_commit_requires_hash_bound_human_approval(tmp_path) -> None:
    repo = _repo(tmp_path)
    parent = _head(repo)
    candidate, validation = _candidate(repo)

    capture = execute_governed_git_commit(
        execution_id="G8-16-EXECUTION-NO-APPROVAL",
        candidate_artifact=candidate,
        approval_artifact=None,
        validation_artifact=validation,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )

    assert capture["execution_status"] == FAILED_CLOSED
    assert capture["commit_created"] is False
    assert _head(repo) == parent
    assert "approval required" in capture["failure_reason"]


def test_governed_git_commit_fails_closed_on_head_conflict(tmp_path) -> None:
    repo = _repo(tmp_path)
    candidate, validation = _candidate(repo)
    approval = _approval(candidate)
    (repo / "other.txt").write_text("other\n", encoding="utf-8")
    _run_git(repo, ["add", "--", "other.txt"])
    _run_git(repo, ["commit", "--no-gpg-sign", "-m", "Intervening commit"])
    intervening = _head(repo)

    capture = execute_governed_git_commit(
        execution_id="G8-16-EXECUTION-HEAD-CONFLICT",
        candidate_artifact=candidate,
        approval_artifact=approval,
        validation_artifact=validation,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )

    assert capture["execution_status"] == FAILED_CLOSED
    assert capture["commit_created"] is False
    assert _head(repo) == intervening
    assert "HEAD mismatch" in capture["failure_reason"]


def test_governed_git_commit_fails_closed_on_unexpected_staged_content(tmp_path) -> None:
    repo = _repo(tmp_path)
    candidate, validation = _candidate(repo)
    approval = _approval(candidate)
    (repo / "unexpected.txt").write_text("unexpected\n", encoding="utf-8")
    _run_git(repo, ["add", "--", "unexpected.txt"])
    parent = _head(repo)

    capture = execute_governed_git_commit(
        execution_id="G8-16-EXECUTION-STAGED-CONFLICT",
        candidate_artifact=candidate,
        approval_artifact=approval,
        validation_artifact=validation,
        repository_root=repo,
        executed_by="PLATFORM_CORE",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )

    assert capture["execution_status"] == FAILED_CLOSED
    assert capture["commit_created"] is False
    assert _head(repo) == parent
    assert "unexpected staged content" in capture["failure_reason"]


def test_governed_git_commit_rejects_prohibited_worker_request_surface(tmp_path) -> None:
    repo = _repo(tmp_path)
    candidate, _validation = _candidate(repo)
    authorization = create_governed_git_commit_authorization_record(
        authorization_id="G8-16-AUTHORIZATION",
        candidate=candidate,
        authorization_timestamp=CREATED_AT,
    )
    request = create_authorized_git_commit_request(
        authorization_record=authorization,
        request_id="G8-16-WORKER-REQUEST",
        candidate=candidate,
        request_timestamp=CREATED_AT,
        proposal_reference={"candidate_id": candidate["candidate_id"], "candidate_hash": candidate["artifact_hash"]},
        replay_reference=str(tmp_path / "replay"),
    )
    request["push_request"] = {"remote": "origin"}

    with pytest.raises(Exception, match="forbidden field"):
        validate_authorized_git_commit_request(request)


def test_governed_git_commit_requires_successful_validation_before_candidate() -> None:
    failed_validation = _validation_artifact("VALIDATION_FAILED")

    with pytest.raises(Exception, match="successful governed validation"):
        create_governed_git_commit_candidate(
            candidate_id="G8-16-CANDIDATE-BAD-VALIDATION",
            session_id="G8-16-SESSION-001",
            repository_id="TEMP-GIT-REPOSITORY",
            branch_name="main",
            expected_head="sha",
            file_set=[{"path": "new.txt", "change_type": ADD_TEXT_FILE, "content_hash": replay_hash("new\n")}],
            commit_message={"subject": "Bad validation"},
            author={"name": "AiGOL Test", "email": "aigol@example.invalid"},
            validation_artifact=failed_validation,
            created_by="OCS",
            created_at=CREATED_AT,
        )
