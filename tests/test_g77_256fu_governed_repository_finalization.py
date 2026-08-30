"""Focused proof for G77-256FU one-command governed finalization."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import os
import stat
import subprocess

import pytest

import aigol.runtime.governed_repository_finalization_runtime as finalization_runtime
from aigol.cli.aigol_cli import build_parser, main
from aigol.runtime.governed_repository_finalization_runtime import (
    FAILED_CLOSED,
    FINALIZATION_COMPLETED,
    create_governed_repository_finalization_contract,
    execute_governed_repository_finalization,
    reconstruct_governed_repository_finalization_replay,
)
from aigol.runtime.platform_core_git_commit_candidate import (
    ADD_TEXT_FILE,
    REPLACE_TEXT_FILE,
)
from aigol.runtime.transport.serialization import replay_hash


AUTHORIZED_AT = "2026-08-30T00:00:00Z"
GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "FU Test",
    "GIT_AUTHOR_EMAIL": "fu-test@example.invalid",
    "GIT_COMMITTER_NAME": "FU Test",
    "GIT_COMMITTER_EMAIL": "fu-test@example.invalid",
}


def _git(repo: Path, *args: str, check: bool = True) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        shell=False,
        check=check,
        env=GIT_ENV,
    )
    return (completed.stdout or "").strip()


def _write_executable(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _active_git_path(repo: Path, relative: str) -> Path:
    return Path(
        _git(
            repo,
            "rev-parse",
            "--path-format=absolute",
            "--git-path",
            relative,
        )
    )


def _install_passing_pre_commit(repo: Path) -> None:
    _write_executable(
        _active_git_path(repo, "hooks/pre-commit"),
        "#!/bin/sh\nset -eu\nmarker=$(git rev-parse --git-path g77-256fu-hook-ran)\n"
        "printf 'ran\\n' > \"$marker\"\n",
    )


def _repository(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "--quiet")
    (repo / ".gitignore").write_text("sapianta_system/\n", encoding="utf-8")
    (repo / "tracked.txt").write_text("before\n", encoding="utf-8")
    (repo / "other.txt").write_text("stable\n", encoding="utf-8")
    _git(repo, "add", "--", ".gitignore", "tracked.txt", "other.txt")
    _git(repo, "commit", "--quiet", "--no-gpg-sign", "-m", "Initial baseline")

    nested = repo / "sapianta_system"
    nested.mkdir()
    _git(nested, "init", "--quiet")
    (nested / "pinned.txt").write_text("pinned\n", encoding="utf-8")
    _git(nested, "add", "--", "pinned.txt")
    _git(nested, "commit", "--quiet", "--no-gpg-sign", "-m", "Pinned nested")
    _git(nested, "checkout", "--quiet", "--detach", "HEAD")

    remote = tmp_path / "remote.git"
    subprocess.run(
        ["git", "init", "--quiet", "--bare", str(remote)],
        capture_output=True,
        text=True,
        check=True,
        env=GIT_ENV,
    )
    _git(repo, "remote", "add", "origin", str(remote))
    _install_passing_pre_commit(repo)
    return repo, remote


def _mutation(path: str, change_type: str, content: str) -> dict[str, str]:
    return {
        "path": path,
        "change_type": change_type,
        "content_hash": replay_hash(content),
    }


def _contract(
    repo: Path,
    *,
    mutations: list[dict[str, str]] | None = None,
    contract_id: str = "G77-256FU-TEST",
) -> dict:
    nested = repo / "sapianta_system"
    return create_governed_repository_finalization_contract(
        contract_id=contract_id,
        repository_root=repo,
        repository_id="DISPOSABLE-FU-REPOSITORY",
        expected_branch=_git(repo, "symbolic-ref", "--short", "HEAD"),
        expected_parent_head=_git(repo, "rev-parse", "HEAD"),
        expected_parent_tree=_git(repo, "rev-parse", "HEAD^{tree}"),
        authorized_mutations=mutations
        or [_mutation("tracked.txt", REPLACE_TEXT_FILE, "after\n")],
        commit_message={"subject": "Governed FU finalization", "body": "Disposable proof."},
        author={"name": "FU Test", "email": "fu-test@example.invalid"},
        nested_authority={
            "path": "sapianta_system",
            "commit": _git(nested, "rev-parse", "HEAD"),
            "tree": _git(nested, "rev-parse", "HEAD^{tree}"),
            "required_status": "CLEAN__DETACHED_HEAD",
        },
        authorized_by="HUMAN_OPERATOR",
        authorized_at=AUTHORIZED_AT,
    )


def _rehash(contract: dict) -> dict:
    changed = deepcopy(contract)
    changed.pop("artifact_hash", None)
    changed["artifact_hash"] = replay_hash(changed)
    return changed


def _prepare_tracked_change(repo: Path) -> dict:
    (repo / "tracked.txt").write_text("after\n", encoding="utf-8")
    return _contract(repo)


def _commit_count(repo: Path) -> int:
    return int(_git(repo, "rev-list", "--count", "HEAD"))


@pytest.fixture(autouse=True)
def _conformant_repository_observer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        finalization_runtime,
        "run_conformance_check",
        lambda _root: {"status": "CONFORMANT", "report_hash": "c" * 64},
    )


def test_exact_authorized_envelope_creates_one_verified_local_commit(tmp_path: Path) -> None:
    repo, remote = _repository(tmp_path)
    parent = _git(repo, "rev-parse", "HEAD")
    nested_head = _git(repo / "sapianta_system", "rev-parse", "HEAD")
    before_count = _commit_count(repo)
    contract = _prepare_tracked_change(repo)

    result = execute_governed_repository_finalization(contract_artifact=contract)

    assert result["finalization_status"] == FINALIZATION_COMPLETED
    assert result["commit_effect_count"] == 1
    assert _commit_count(repo) == before_count + 1
    assert _git(repo, "rev-parse", "HEAD^") == parent
    assert result["committed_head"] == _git(repo, "rev-parse", "HEAD")
    assert result["committed_tree"] == _git(repo, "rev-parse", "HEAD^{tree}")
    assert result["commit_subject"] == "Governed FU finalization"
    assert result["committed_path_set"] == ["tracked.txt"]
    assert result["post_commit_status"] == "CLEAN__VERIFIED"
    assert result["existing_git_commit_worker_reused"] is True
    assert result["push_performed"] is False
    assert _git(repo, "status", "--porcelain", "--untracked-files=all") == ""
    assert _active_git_path(repo, "g77-256fu-hook-ran").read_text(encoding="utf-8") == "ran\n"
    assert _git(repo / "sapianta_system", "rev-parse", "HEAD") == nested_head
    assert _git(repo / "sapianta_system", "status", "--porcelain") == ""
    assert _git(remote, "for-each-ref") == ""
    reconstructed = reconstruct_governed_repository_finalization_replay(
        result["replay_reference"]
    )
    assert reconstructed["finalization_status"] == FINALIZATION_COMPLETED
    assert reconstructed["committed_head"] == result["committed_head"]
    assert reconstructed["committed_path_set"] == ["tracked.txt"]
    assert reconstructed["replay_artifact_count"] == 2


def test_one_cli_invocation_executes_the_explicit_contract(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo, _remote = _repository(tmp_path)
    contract = _prepare_tracked_change(repo)
    contract_path = tmp_path / "finalization-contract.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")

    exit_code = main(["finalize", "--contract", str(contract_path), "--json"])
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["command"] == "aigol finalize"
    assert output["finalization_status"] == FINALIZATION_COMPLETED
    assert output["committed_head"] == _git(repo, "rev-parse", "HEAD")


def test_unrelated_tracked_mutation_fails_closed(tmp_path: Path) -> None:
    repo, _remote = _repository(tmp_path)
    parent = _git(repo, "rev-parse", "HEAD")
    contract = _prepare_tracked_change(repo)
    (repo / "other.txt").write_text("unexpected\n", encoding="utf-8")

    result = execute_governed_repository_finalization(contract_artifact=contract)

    assert result["finalization_status"] == FAILED_CLOSED
    assert "mutation envelope mismatch" in result["failure_reason"]
    assert _git(repo, "rev-parse", "HEAD") == parent


def test_unrelated_untracked_mutation_fails_closed(tmp_path: Path) -> None:
    repo, _remote = _repository(tmp_path)
    parent = _git(repo, "rev-parse", "HEAD")
    contract = _prepare_tracked_change(repo)
    (repo / "unexpected.txt").write_text("unexpected\n", encoding="utf-8")

    result = execute_governed_repository_finalization(contract_artifact=contract)

    assert result["finalization_status"] == FAILED_CLOSED
    assert "mutation envelope mismatch" in result["failure_reason"]
    assert _git(repo, "rev-parse", "HEAD") == parent


def test_missing_authorized_path_fails_closed(tmp_path: Path) -> None:
    repo, _remote = _repository(tmp_path)
    (repo / "tracked.txt").write_text("after\n", encoding="utf-8")
    contract = _contract(
        repo,
        mutations=[
            _mutation("missing.txt", ADD_TEXT_FILE, "missing\n"),
            _mutation("tracked.txt", REPLACE_TEXT_FILE, "after\n"),
        ],
    )

    result = execute_governed_repository_finalization(contract_artifact=contract)

    assert result["finalization_status"] == FAILED_CLOSED
    assert "mutation envelope mismatch" in result["failure_reason"]


def test_wrong_expected_parent_head_fails_closed(tmp_path: Path) -> None:
    repo, _remote = _repository(tmp_path)
    parent = _git(repo, "rev-parse", "HEAD")
    contract = _prepare_tracked_change(repo)
    contract["expected_parent_head"] = "0" * 40
    contract = _rehash(contract)

    result = execute_governed_repository_finalization(contract_artifact=contract)

    assert result["finalization_status"] == FAILED_CLOSED
    assert "parent HEAD mismatch" in result["failure_reason"]
    assert _git(repo, "rev-parse", "HEAD") == parent


def test_non_empty_index_fails_before_commit(tmp_path: Path) -> None:
    repo, _remote = _repository(tmp_path)
    parent = _git(repo, "rev-parse", "HEAD")
    contract = _prepare_tracked_change(repo)
    _git(repo, "add", "--", "tracked.txt")

    result = execute_governed_repository_finalization(contract_artifact=contract)

    assert result["finalization_status"] == FAILED_CLOSED
    assert "NON_EMPTY_INDEX" in result["failure_reason"]
    assert _git(repo, "rev-parse", "HEAD") == parent


def test_validation_failure_prevents_commit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo, _remote = _repository(tmp_path)
    parent = _git(repo, "rev-parse", "HEAD")
    contract = _prepare_tracked_change(repo)
    monkeypatch.setattr(
        finalization_runtime,
        "run_conformance_check",
        lambda _root: {"status": "PARTIALLY_CONFORMANT", "report_hash": "f" * 64},
    )

    result = execute_governed_repository_finalization(contract_artifact=contract)

    assert result["finalization_status"] == FAILED_CLOSED
    assert "governance conformance" in result["failure_reason"]
    assert _git(repo, "rev-parse", "HEAD") == parent


def test_pre_commit_governance_failure_prevents_commit(tmp_path: Path) -> None:
    repo, _remote = _repository(tmp_path)
    parent = _git(repo, "rev-parse", "HEAD")
    contract = _prepare_tracked_change(repo)
    _write_executable(
        _active_git_path(repo, "hooks/pre-commit"),
        "#!/bin/sh\nexit 1\n",
    )

    result = execute_governed_repository_finalization(contract_artifact=contract)

    assert result["finalization_status"] == FAILED_CLOSED
    assert result["commit_effect_count"] == 0
    assert _git(repo, "rev-parse", "HEAD") == parent


def test_post_commit_dirty_state_is_detected_without_repair(tmp_path: Path) -> None:
    repo, _remote = _repository(tmp_path)
    before_count = _commit_count(repo)
    contract = _prepare_tracked_change(repo)
    _write_executable(
        _active_git_path(repo, "hooks/pre-commit"),
        "#!/bin/sh\ntouch dirty-after-staging.txt\n",
    )

    result = execute_governed_repository_finalization(contract_artifact=contract)

    assert result["finalization_status"] == FAILED_CLOSED
    assert result["commit_effect_count"] == 1
    assert "post-commit worktree is not clean" in result["failure_reason"]
    assert _commit_count(repo) == before_count + 1
    assert (repo / "dirty-after-staging.txt").exists()


def test_wrong_commit_subject_is_detected_without_amend(tmp_path: Path) -> None:
    repo, _remote = _repository(tmp_path)
    before_count = _commit_count(repo)
    contract = _prepare_tracked_change(repo)
    _write_executable(
        _active_git_path(repo, "hooks/commit-msg"),
        "#!/bin/sh\nprintf 'Wrong subject\\n' > \"$1\"\n",
    )

    result = execute_governed_repository_finalization(contract_artifact=contract)

    assert result["finalization_status"] == FAILED_CLOSED
    assert result["commit_effect_count"] == 1
    assert "commit subject mismatch" in result["failure_reason"]
    assert _commit_count(repo) == before_count + 1
    assert _git(repo, "show", "-s", "--format=%s", "HEAD") == "Wrong subject"


def test_explicit_human_authorization_is_required(tmp_path: Path) -> None:
    repo, _remote = _repository(tmp_path)
    parent = _git(repo, "rev-parse", "HEAD")
    contract = _prepare_tracked_change(repo)
    contract["human_authorization"]["decision"] = "REJECTED"
    contract = _rehash(contract)

    result = execute_governed_repository_finalization(contract_artifact=contract)

    assert result["finalization_status"] == FAILED_CLOSED
    assert "explicit Human authorization required" in result["failure_reason"]
    assert _git(repo, "rev-parse", "HEAD") == parent


def test_authorized_untracked_addition_commits_exact_blob(tmp_path: Path) -> None:
    repo, _remote = _repository(tmp_path)
    (repo / "new.txt").write_text("new governed content\n", encoding="utf-8")
    contract = _contract(
        repo,
        mutations=[_mutation("new.txt", ADD_TEXT_FILE, "new governed content\n")],
        contract_id="G77-256FU-ADD-TEST",
    )

    result = execute_governed_repository_finalization(contract_artifact=contract)

    assert result["finalization_status"] == FINALIZATION_COMPLETED
    assert result["committed_path_set"] == ["new.txt"]
    blob = result["finalization_result_artifact"]["committed_blobs"][0]
    assert blob["path"] == "new.txt"
    assert blob["content_hash"] == replay_hash("new governed content\n")


def test_nested_authority_mismatch_fails_before_commit(tmp_path: Path) -> None:
    repo, _remote = _repository(tmp_path)
    parent = _git(repo, "rev-parse", "HEAD")
    contract = _prepare_tracked_change(repo)
    contract["nested_authority"]["commit"] = "0" * 40
    contract = _rehash(contract)

    result = execute_governed_repository_finalization(contract_artifact=contract)

    assert result["finalization_status"] == FAILED_CLOSED
    assert "nested pinned identity mismatch" in result["failure_reason"]
    assert _git(repo, "rev-parse", "HEAD") == parent


def test_cli_exposes_one_explicit_finalization_invocation() -> None:
    args = build_parser().parse_args(
        ["finalize", "--contract", "/tmp/finalization-contract.json", "--json"]
    )

    assert args.command == "finalize"
    assert args.contract == "/tmp/finalization-contract.json"
    assert args.json is True


def test_contract_has_no_push_or_implicit_authority_surface(tmp_path: Path) -> None:
    repo, _remote = _repository(tmp_path)
    contract = _prepare_tracked_change(repo)

    assert contract["push_allowed"] is False
    assert contract["remote_interaction_allowed"] is False
    assert contract["hook_bypass_allowed"] is False
    assert contract["human_invocation_required"] is True
    assert contract["new_authority_truth_created"] is False
    assert contract["human_authorization"]["candidate_readiness_is_not_authority"] is True
