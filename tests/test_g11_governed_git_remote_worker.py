"""Tests for G11-08 governed Git remote Worker."""

from __future__ import annotations

import subprocess

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_git_remote_governance import create_governed_git_remote_authorization_record
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers.git_remote_worker import (
    AUTHORIZED_GIT_REMOTE_SCOPE,
    GIT_REMOTE_WORKER_ID,
    OPERATION_FETCH,
    OPERATION_PUSH,
    OPERATION_REMOTE_INSPECTION,
    create_authorized_git_remote_request,
    execute_git_remote_request,
    reconstruct_git_remote_worker_replay,
    validate_authorized_git_remote_request,
)


CREATED_AT = "2026-07-02T00:00:00Z"
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


def _run_git_root(cwd, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        shell=False,
        check=True,
        env=GIT_ENV,
    )
    return (completed.stdout or "").strip()


def _repo_with_remote(tmp_path):
    remote = tmp_path / "remote.git"
    _run_git_root(tmp_path, ["init", "--bare", str(remote)])
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, ["init"])
    _run_git(repo, ["remote", "add", "origin", str(remote)])
    tracked = repo / "tracked.txt"
    tracked.write_text("initial\n", encoding="utf-8")
    _run_git(repo, ["add", "--", "tracked.txt"])
    _run_git(repo, ["commit", "--no-gpg-sign", "-m", "Initial commit"])
    return repo, remote


def _branch(repo) -> str:
    return _run_git(repo, ["rev-parse", "--abbrev-ref", "HEAD"])


def _head(repo) -> str:
    return _run_git(repo, ["rev-parse", "HEAD"])


def _remote_head(repo, branch: str) -> str | None:
    output = _run_git(repo, ["ls-remote", "origin", f"refs/heads/{branch}"])
    return output.split()[0] if output else None


def _authorization() -> dict:
    return create_governed_git_remote_authorization_record(
        authorization_id="G11-08-GIT-REMOTE-AUTHORIZATION",
        proposal_id="G11-08-GIT-REMOTE-PROPOSAL",
        authorization_timestamp=CREATED_AT,
    )


def _request(repo, remote, *, operation: str, protected=False, protected_authorized=False) -> dict:
    branch = _branch(repo)
    return create_authorized_git_remote_request(
        authorization_record=_authorization(),
        request_id=f"G11-08-REQUEST-{operation}",
        operation=operation,
        repository_id="TEMP-GIT-REMOTE-REPOSITORY",
        remote_name="origin",
        remote_url=str(remote),
        local_branch=branch,
        remote_branch=branch,
        expected_local_head=_head(repo),
        expected_remote_head=_remote_head(repo, branch),
        protected_branch=protected,
        protected_branch_authorized=protected_authorized,
        credential_reference="credential://git/local-test",
        validation_artifact_hash="validation-artifact-hash",
        rollback_reference="rollback:git-remote:none",
        request_timestamp=CREATED_AT,
        proposal_reference={"proposal_id": "G11-08-GIT-REMOTE-PROPOSAL"},
        replay_reference="replay:g11-08:git-remote",
    )


def test_git_remote_push_executes_exact_authorized_operation_with_replay(tmp_path):
    repo, remote = _repo_with_remote(tmp_path)
    request = _request(repo, remote, operation=OPERATION_PUSH)

    capture = execute_git_remote_request(
        authorized_request=request,
        repository_root=repo,
        replay_dir=tmp_path / "replay",
    )
    reconstructed = reconstruct_git_remote_worker_replay(tmp_path / "replay")

    assert capture["execution_status"] == "GIT_REMOTE_OPERATION_COMPLETED"
    assert capture["git_remote_performed"] is True
    assert capture["remote_state_changed"] is True
    assert reconstructed["worker_invoked"] is True
    assert reconstructed["operation"] == OPERATION_PUSH
    assert reconstructed["remote_state_changed"] is True
    assert _remote_head(repo, _branch(repo)) == _head(repo)


def test_git_remote_inspection_does_not_change_remote_state(tmp_path):
    repo, remote = _repo_with_remote(tmp_path)
    _run_git(repo, ["push", "origin", f"{_branch(repo)}:{_branch(repo)}"])
    before = _remote_head(repo, _branch(repo))
    request = _request(repo, remote, operation=OPERATION_REMOTE_INSPECTION)

    capture = execute_git_remote_request(
        authorized_request=request,
        repository_root=repo,
        replay_dir=tmp_path / "inspect-replay",
    )

    assert capture["execution_status"] == "GIT_REMOTE_OPERATION_COMPLETED"
    assert capture["remote_state_changed"] is False
    assert _remote_head(repo, _branch(repo)) == before


def test_git_remote_fetch_executes_without_remote_mutation(tmp_path):
    repo, remote = _repo_with_remote(tmp_path)
    _run_git(repo, ["push", "origin", f"{_branch(repo)}:{_branch(repo)}"])
    request = _request(repo, remote, operation=OPERATION_FETCH)

    capture = execute_git_remote_request(
        authorized_request=request,
        repository_root=repo,
        replay_dir=tmp_path / "fetch-replay",
    )

    assert capture["execution_status"] == "GIT_REMOTE_OPERATION_COMPLETED"
    assert capture["remote_state_changed"] is False


def test_git_remote_protected_branch_requires_explicit_authorization(tmp_path):
    repo, remote = _repo_with_remote(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="protected branch authorization required"):
        _request(repo, remote, operation=OPERATION_PUSH, protected=True, protected_authorized=False)


def test_git_remote_request_rejects_forbidden_surfaces(tmp_path):
    repo, remote = _repo_with_remote(tmp_path)
    request = _request(repo, remote, operation=OPERATION_PUSH)
    request["force_push_request"] = True

    with pytest.raises(FailClosedRuntimeError, match="forbidden field"):
        validate_authorized_git_remote_request(request)


def test_git_remote_worker_uses_governance_authorization_scope():
    authorization = _authorization()

    assert authorization["worker_id"] == GIT_REMOTE_WORKER_ID
    assert authorization["authorization_scope"] == AUTHORIZED_GIT_REMOTE_SCOPE
    assert authorization["provider_can_authorize"] is False
    assert authorization["worker_can_self_authorize"] is False
