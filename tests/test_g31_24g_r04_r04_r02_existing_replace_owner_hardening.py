from __future__ import annotations

from base64 import b64encode
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from hashlib import sha256
import os
from pathlib import Path
import stat
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import test_g31_24g_r04_r04_r01_authorization_actor_replay_binding as r01  # noqa: E402

from aigol.authorization.authorization_record import create_authorization_record
from aigol.authorization.authorization_runtime import CANONICAL_AUTHORIZATION_ACTOR
from aigol.runtime import platform_core_existing_file_governance as governance
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from aigol.workers import filesystem_replace_worker as worker


STAMP = "2026-07-20T00:00:00Z"


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _manual_request(tmp_path: Path, target_path: str = "src/target.txt") -> tuple[dict, Path, Path]:
    repo = (tmp_path / "repo").resolve()
    target = repo / target_path
    target.parent.mkdir(parents=True)
    target.write_bytes(b"before\n")
    _git(repo, "init"); _git(repo, "config", "user.name", "G31"); _git(repo, "config", "user.email", "g31@example.invalid")
    _git(repo, "add", "."); _git(repo, "commit", "-m", "baseline")
    session = (tmp_path / "SESSION-R02").resolve(); session.mkdir()
    record = create_authorization_record(
        authorization_id="G31-R02-AUTH", proposal_id="G31-R02-CANDIDATE",
        worker_id=worker.FILESYSTEM_REPLACE_WORKER_ID,
        authorization_scope=worker.AUTHORIZED_REPLACE_SCOPE,
        authorization_timestamp=STAMP,
    ).to_dict()
    source, replacement = b"before\n", b"after\n"
    destinations = worker.g31_replace_destinations(session, record["authorization_hash"], repo, target_path)
    request = {
        "request_type": worker.AUTHENTICATED_REPLACE_REQUEST_TYPE_V2,
        "runtime_version": worker.HARDENED_REPLACE_VERSION,
        "request_id": "G31-R02-AUTH:HARDENED-REPLACE-V2",
        "canonical_authorization_actor": CANONICAL_AUTHORIZATION_ACTOR,
        "authorization_record": record, "authorization_id": record["authorization_id"],
        "authorization_hash": record["authorization_hash"], "authorization_status": "AUTHORIZED",
        "authorization_scope": record["authorization_scope"], "worker_id": record["worker_id"],
        "authorization_replay_reference": str(session / "AUTHORIZATION"),
        "authorization_replay_hash": "authorization-replay-hash",
        "actor_replay_binding_hash": "actor-replay-binding-hash",
        "r02_authorization_binding_hash": "r02-binding-hash",
        "candidate_id": record["proposal_id"], "candidate_hash": "candidate-hash",
        "candidate_replay_hash": "candidate-replay-hash",
        "candidate_provenance_binding_hash": "candidate-provenance-hash",
        "mutation_decision_id": "decision-id", "mutation_decision_hash": "decision-hash",
        "mutation_decision_outcome": "APPROVED", "mutation_decision_scope": "EXISTING_FILE_REPLACE_ONLY",
        "mutation_decision_actor": "HUMAN_OPERATOR", "mutation_decision_replay_hash": "decision-replay-hash",
        "session_id": session.name, "session_root": str(session), "repository_identity": "repo-identity",
        "repository_root": str(repo), "repository_grounding_hash": "grounding-hash", "manifest_hash": "manifest-hash",
        "operation": "REPLACE_CONTENT", "worker_operation": worker.OPERATION_REPLACE_EXISTING_TEXT_FILE,
        "target_path": target_path, "preimage_sha256": "sha256:" + sha256(source).hexdigest(),
        "postimage_sha256": "sha256:" + sha256(replacement).hexdigest(),
        "source_content_hash": replay_hash(source.decode()), "replacement_content_hash": replay_hash(replacement.decode()),
        "preimage_bytes_b64": b64encode(source).decode(), "replacement_bytes_b64": b64encode(replacement).decode(),
        "source_mode": str(target.stat().st_mode), "replacement_mode": str(target.stat().st_mode),
        "destinations": destinations, "authorization_consumed": False, "replace_request_created": True,
        "worker_invoked": False, "provider_invoked": False, "command_executed": False,
        "repository_mutated": False, "main_repository_mutated": False, "replay_visible": True,
    }
    request["request_hash"] = replay_hash(request)
    return worker.validate_authenticated_replace_request_v2(request), target, repo


def _rehash(request: dict) -> dict:
    request["request_hash"] = replay_hash({key: value for key, value in request.items() if key != "request_hash"})
    return request


def _public_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    common, _, target = r01._evidence(tmp_path, monkeypatch)
    target.chmod(0o644)
    authorization = r01._authorize(common)
    actor = r01._bind(common, authorization)
    provenance = common["candidate_capture"]["existing_file_mutation_candidate_artifact"]["candidate_provenance"]
    source, replacement = target.read_text(encoding="utf-8"), "replacement bytes\n"
    entry = {"operation": "REPLACE_CONTENT", "target_path": provenance["target_path"],
             "preimage_content": source, "postimage_content": replacement,
             "preimage_sha256": provenance["preimage_sha256"], "postimage_sha256": provenance["postimage_sha256"],
             "file_mode": provenance["source_mode"], "postimage_file_mode": provenance["replacement_mode"]}
    common["binding_capture"] = {"implementation_manifest_capture": {
        "implementation_manifest_artifact": {"artifact_hash": provenance["manifest_hash"], "file_entries": [entry]}}}
    return common, authorization, actor, target


def test_public_reconstruction_builds_and_executes_exact_authenticated_request(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    common, authorization, actor, target = _public_evidence(tmp_path, monkeypatch)
    request = governance.create_g31_authenticated_replace_request(
        actor_replay_capture=actor, authorization_capture=authorization, **common)
    assert request["canonical_authorization_actor"] == CANONICAL_AUTHORIZATION_ACTOR
    assert request["authorization_replay_hash"] == actor["authorization_replay_hash"]
    assert request["repository_root"] == str(common["workspace"].resolve())
    capture = governance.execute_g31_authenticated_replace(
        actor_replay_capture=actor, authorization_capture=authorization, **common)
    assert capture["execution_status"] == "COMPLETED"
    assert capture["authorization_consumed"] is True
    assert capture["repository_mutated"] is True
    assert capture["recovery_required"] is False
    assert target.read_bytes() == b"replacement bytes\n"


def test_public_request_rejects_manifest_and_actor_substitution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    common, authorization, actor, _ = _public_evidence(tmp_path, monkeypatch)
    changed = deepcopy(common)
    changed["binding_capture"]["implementation_manifest_capture"]["implementation_manifest_artifact"]["file_entries"][0]["postimage_content"] = "substituted\n"
    with pytest.raises(FailClosedRuntimeError):
        governance.create_g31_authenticated_replace_request(
            actor_replay_capture=actor, authorization_capture=authorization, **changed)
    changed_actor = deepcopy(actor); changed_actor["authorization_replay_hash"] = "substituted"
    with pytest.raises(FailClosedRuntimeError):
        governance.create_g31_authenticated_replace_request(
            actor_replay_capture=changed_actor, authorization_capture=authorization, **common)
    with pytest.raises(TypeError):
        governance.execute_g31_authenticated_replace(authorized_request={}, **common)


def test_success_is_atomic_durable_replayed_and_one_shot(tmp_path: Path) -> None:
    request, target, repo = _manual_request(tmp_path)
    capture = worker._execute_authenticated_replace_v2(request)
    replay = worker.reconstruct_authenticated_replace_replay_v2(request)
    assert capture["execution_status"] == "COMPLETED"
    assert capture["repository_mutated"] is True
    assert target.read_bytes() == b"after\n"
    assert stat.S_IMODE(target.stat().st_mode) == stat.S_IMODE(int(request["replacement_mode"]))
    assert replay["event_keys"] == ["request", "consumption", "journal", "started", "atomic", "result", "completion"]
    assert not Path(request["destinations"]["temporary_file"]).exists()
    assert _git(repo, "status", "--porcelain").stdout.strip() == "M src/target.txt"
    with pytest.raises(FailClosedRuntimeError, match="already consumed"):
        worker._execute_authenticated_replace_v2(request)


@pytest.mark.parametrize("field,value", [
    ("candidate_id", "substituted"), ("mutation_decision_outcome", "REJECTED"),
    ("mutation_decision_scope", "CONTENT_ACCEPTANCE_ONLY"), ("session_id", "OTHER-SESSION"),
    ("authorization_status", "REJECTED"), ("target_path", "../escape"),
])
def test_request_identity_tampering_fails_before_consumption(
    tmp_path: Path, field: str, value: str,
) -> None:
    request, target, _ = _manual_request(tmp_path)
    request[field] = value
    _rehash(request)
    with pytest.raises(FailClosedRuntimeError):
        worker._execute_authenticated_replace_v2(request)
    assert target.read_bytes() == b"before\n"
    assert not Path(request["destinations"]["consumption"]).exists()


@pytest.mark.parametrize("case", ["dirty", "nested", "symlink", "symlink_component", "hardlink", "mode", "preimage"])
def test_repository_path_link_mode_and_drift_guards(tmp_path: Path, case: str) -> None:
    request, target, repo = _manual_request(tmp_path)
    if case == "dirty":
        (repo / "untracked.txt").write_text("dirty\n")
    elif case == "nested":
        _git(target.parent, "init")
    elif case == "symlink":
        other = repo / "other.txt"; other.write_bytes(b"before\n")
        target.unlink(); target.symlink_to(other); _git(repo, "add", "-A"); _git(repo, "commit", "-m", "symlink")
    elif case == "symlink_component":
        external = repo.parent / "external"; external.mkdir(); (external / "target.txt").write_bytes(b"before\n")
        target.unlink(); target.parent.rmdir(); target.parent.symlink_to(external)
        _git(repo, "add", "-A"); _git(repo, "commit", "-m", "symlink-component")
    elif case == "hardlink":
        other = repo / "other.txt"; other.write_bytes(b"before\n")
        target.unlink(); os.link(other, target); _git(repo, "add", "-A"); _git(repo, "commit", "-m", "hardlink")
    elif case == "mode":
        target.chmod(0o755); _git(repo, "add", target.relative_to(repo).as_posix()); _git(repo, "commit", "-m", "mode")
    else:
        target.write_bytes(b"drifted\n"); _git(repo, "add", target.relative_to(repo).as_posix()); _git(repo, "commit", "-m", "drift")
    with pytest.raises((FailClosedRuntimeError, OSError)):
        worker._execute_authenticated_replace_v2(request)
    assert not Path(request["destinations"]["consumption"]).exists()


@pytest.mark.parametrize("stage", [
    "temporary_created", "temporary_written", "temporary_fsynced", "before_replace",
    "directory_fsync", "post_write_verification", "replay_journal", "replay_atomic",
])
def test_deterministic_failure_points_restore_or_preserve_preimage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stage: str,
) -> None:
    request, target, _ = _manual_request(tmp_path)
    original = worker._checkpoint

    def failpoint(name: str) -> None:
        if name == stage:
            raise OSError(f"injected {stage}")
        original(name)

    monkeypatch.setattr(worker, "_checkpoint", failpoint)
    capture = worker._execute_authenticated_replace_v2(request)
    assert capture["execution_status"] == "TERMINATED"
    assert capture["repository_mutated"] is False
    assert capture["recovery_required"] is False
    assert target.read_bytes() == b"before\n"
    assert "termination" in worker.reconstruct_authenticated_replace_replay_v2(request)["event_keys"]


def test_replace_failure_preserves_preimage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    request, target, _ = _manual_request(tmp_path)

    def failed_replace(*_args, **_kwargs):
        raise OSError("replace failed")

    monkeypatch.setattr(worker.os, "replace", failed_replace)
    capture = worker._execute_authenticated_replace_v2(request)
    assert capture["repository_mutated"] is False
    assert capture["recovery_required"] is False
    assert target.read_bytes() == b"before\n"


def test_drift_immediately_before_replace_is_detected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    request, target, _ = _manual_request(tmp_path)

    def drift(name: str) -> None:
        if name == "before_replace":
            target.write_bytes(b"drifted-before-replace\n")

    monkeypatch.setattr(worker, "_checkpoint", drift)
    capture = worker._execute_authenticated_replace_v2(request)
    assert capture["repository_mutated"] is False
    assert capture["recovery_required"] is False
    assert target.read_bytes() == b"drifted-before-replace\n"


def test_post_write_verifier_failure_restores_original(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    request, target, _ = _manual_request(tmp_path)
    original = worker._verify_v2_named; calls = {"count": 0}

    def fail_once(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise FailClosedRuntimeError("injected byte and mode verification failure")
        return original(*args, **kwargs)

    monkeypatch.setattr(worker, "_verify_v2_named", fail_once)
    capture = worker._execute_authenticated_replace_v2(request)
    assert capture["restoration_performed"] is True
    assert capture["repository_mutated"] is False
    assert target.read_bytes() == b"before\n"


def test_failed_restoration_is_truthful_and_explicit_recovery_succeeds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    request, target, _ = _manual_request(tmp_path)
    original_restore = worker._atomic_restore_v2

    def fail_after_replace(name: str) -> None:
        if name == "after_replace":
            raise OSError("post-replace failure")

    monkeypatch.setattr(worker, "_checkpoint", fail_after_replace)
    monkeypatch.setattr(worker, "_atomic_restore_v2", lambda *_args, **_kwargs: False)
    capture = worker._execute_authenticated_replace_v2(request)
    assert capture["repository_mutated"] is True
    assert capture["recovery_required"] is True
    assert target.read_bytes() == b"after\n"
    with pytest.raises(FailClosedRuntimeError, match="already consumed"):
        worker._execute_authenticated_replace_v2(request)
    monkeypatch.setattr(worker, "_checkpoint", lambda _name: None)
    monkeypatch.setattr(worker, "_atomic_restore_v2", original_restore)
    recovered = worker._recover_authenticated_replace_v2(request)
    assert recovered["execution_status"] == "RECOVERED"
    assert recovered["repository_mutated"] is False
    assert target.read_bytes() == b"before\n"


def test_process_interruption_is_recovered_from_durable_journal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    request, target, _ = _manual_request(tmp_path)

    def interrupt(name: str) -> None:
        if name == "after_replace":
            raise KeyboardInterrupt("simulated interruption")

    monkeypatch.setattr(worker, "_checkpoint", interrupt)
    with pytest.raises(KeyboardInterrupt):
        worker._execute_authenticated_replace_v2(request)
    assert target.read_bytes() == b"after\n"
    assert Path(request["destinations"]["journal"]).exists()
    monkeypatch.setattr(worker, "_checkpoint", lambda _name: None)
    recovered = worker._recover_authenticated_replace_v2(request)
    assert recovered["execution_status"] == "RECOVERED"
    assert target.read_bytes() == b"before\n"


def test_concurrent_consumption_has_one_exclusive_winner(tmp_path: Path) -> None:
    request, target, _ = _manual_request(tmp_path)
    previous = worker._persist_v2_event(request, "request", "REQUEST_VALIDATED", {}, None)

    def claim() -> str:
        return worker._persist_v2_event(
            request, "consumption", "AUTHORIZATION_CONSUMPTION_CLAIMED",
            {"consumption_identity": request["authorization_hash"]}, previous)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(claim) for _ in range(2)]
    successes = [future for future in futures if future.exception() is None]
    failures = [future for future in futures if future.exception() is not None]
    assert len(successes) == len(failures) == 1
    assert isinstance(failures[0].exception(), FileExistsError)
    assert target.read_bytes() == b"before\n"


def test_replay_tamper_fails_reconstruction(tmp_path: Path) -> None:
    request, _, _ = _manual_request(tmp_path)
    worker._execute_authenticated_replace_v2(request)
    result = Path(request["destinations"]["result"])
    result.write_text(result.read_text().replace("POST_WRITE_VALIDATION_SUCCEEDED", "SUBSTITUTED"))
    with pytest.raises(FailClosedRuntimeError):
        worker.reconstruct_authenticated_replace_replay_v2(request)
