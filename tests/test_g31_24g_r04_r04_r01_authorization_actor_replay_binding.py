from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from test_g31_24g_r04_r02_mutation_authorization_binding import (  # noqa: E402
    _authorize,
    _evidence as _r02_evidence,
)

from aigol.authorization import authorization_runtime
from aigol.runtime import platform_core_existing_file_governance as governance
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


def _evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    common, calls, target = _r02_evidence(tmp_path, monkeypatch)
    common["activation_binding"]["activation_approval_artifact"] = {
        "approval_id": "G31-R04-R01-ACTIVATION",
        "artifact_hash": "activation-approval-hash",
    }
    return common, calls, target


def _bind(common: dict, authorization: dict) -> dict:
    return governance.bind_g31_mutation_authorization_actor_and_replay(
        authorization_capture=authorization, **common)


def _reconstruct(common: dict, authorization: dict, capture: dict) -> dict:
    return governance.reconstruct_g31_mutation_authorization_actor_and_replay(
        actor_replay_capture=capture, authorization_capture=authorization, **common)


def test_exact_r02_authorization_binds_canonical_actor_and_standalone_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    common, _, target = _evidence(tmp_path, monkeypatch)
    authorization = _authorize(common)
    record_before = deepcopy(authorization["authorization_record"])
    files_before = sorted(common["session_root"].rglob("*.json"))

    def forbidden_authorization(*_args, **_kwargs):
        raise AssertionError("a second authorization must not be created")

    monkeypatch.setattr(governance, "create_authorization_record", forbidden_authorization)
    capture = _bind(common, authorization)
    reconstructed = _reconstruct(common, authorization, capture)
    files_after = sorted(common["session_root"].rglob("*.json"))
    assert _reconstruct(common, authorization, capture) == reconstructed

    assert authorization["authorization_record"] == record_before
    assert reconstructed["authorization_record"] == record_before
    assert reconstructed["authorization_hash"] == record_before["authorization_hash"]
    assert reconstructed["worker_id"] == record_before["worker_id"]
    assert reconstructed["canonical_authorization_actor"] == authorization_runtime.CANONICAL_AUTHORIZATION_ACTOR
    assert reconstructed["canonical_authorization_actor"] != "HUMAN_OPERATOR"
    assert reconstructed["activation_replay_hash"] == common["activation_binding"]["activation_replay_hash"]
    assert reconstructed["activation_id"] == common["activation_binding"]["activation_approval_artifact"]["approval_id"]
    assert reconstructed["activation_hash"] == common["activation_binding"]["activation_approval_artifact"]["artifact_hash"]
    assert reconstructed["candidate_replay_hash"] == common["candidate_reconstruction"]["replay_hash"]
    assert reconstructed["mutation_decision_scope"] == "EXISTING_FILE_REPLACE_ONLY"
    assert reconstructed["mutation_decision_actor"] == "HUMAN_OPERATOR"
    assert reconstructed["target_path"] == "aigol/runtime/human_interface.py"
    assert reconstructed["authorization_actor_bound"] is True
    assert reconstructed["authorization_replay_recorded"] is True
    assert reconstructed["authorization_consumed"] is False
    assert reconstructed["replace_request_created"] is False
    assert reconstructed["worker_invoked"] is False
    assert reconstructed["repository_mutated"] is False
    assert target.read_bytes() == b"original bytes\n"
    assert subprocess.run(
        ["git", "status", "--short"], cwd=common["workspace"], check=True,
        capture_output=True, text=True,
    ).stdout == ""
    assert len(files_after) == len(files_before) + 3
    assert files_after == sorted(common["session_root"].rglob("*.json"))


def test_caller_actor_and_v3_actor_cannot_substitute_for_authorizer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    common, _, _ = _evidence(tmp_path, monkeypatch)
    authorization = _authorize(common)
    with pytest.raises(TypeError):
        governance.bind_g31_mutation_authorization_actor_and_replay(
            authorization_capture=authorization, authorization_actor="HUMAN_OPERATOR", **common)
    capture = _bind(common, authorization)
    changed = deepcopy(capture)
    artifact = changed["authorization_binding_artifact"]
    artifact["canonical_authorization_actor"] = artifact["mutation_decision_actor"]
    artifact["artifact_hash"] = replay_hash({key: value for key, value in artifact.items() if key != "artifact_hash"})
    changed["actor_replay_binding_hash"] = replay_hash(
        {key: value for key, value in changed.items() if key != "actor_replay_binding_hash"})
    with pytest.raises(FailClosedRuntimeError):
        _reconstruct(common, authorization, changed)


@pytest.mark.parametrize("field", [
    "authorization_hash", "authorization_status", "authorization_scope",
    "worker_id", "proposal_id", "replay_visible",
])
def test_changed_authorization_record_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str,
) -> None:
    common, _, _ = _evidence(tmp_path, monkeypatch)
    authorization = _authorize(common)
    changed = deepcopy(authorization)
    changed["authorization_record"][field] = "SUBSTITUTED"
    with pytest.raises(FailClosedRuntimeError):
        _bind(common, changed)


@pytest.mark.parametrize("field", [
    "candidate_capture", "mutation_decision_capture", "activation_binding", "repository_grounding_artifact",
])
def test_candidate_decision_and_activation_substitution_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str,
) -> None:
    common, _, _ = _evidence(tmp_path, monkeypatch)
    authorization = _authorize(common)
    changed = dict(common)
    changed[field] = deepcopy(common[field])
    if field == "candidate_capture":
        changed[field]["existing_file_mutation_candidate_artifact"]["artifact_hash"] = "substituted"
    elif field == "mutation_decision_capture":
        changed[field]["human_mutation_decision_artifact"]["artifact_hash"] = "substituted"
    elif field == "activation_binding":
        changed[field]["activation_replay_hash"] = "substituted"
    else:
        changed[field]["grounding_evidence_hash"] = "substituted"
    with pytest.raises(FailClosedRuntimeError):
        _bind(changed, authorization)


def test_target_preimage_and_r02_binding_tamper_fail_reconstruction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    common, _, _ = _evidence(tmp_path, monkeypatch)
    authorization = _authorize(common)
    capture = _bind(common, authorization)
    for field in ("target_path", "expected_source_sha256", "r02_authorization_binding_hash"):
        changed = deepcopy(capture)
        artifact = changed["authorization_binding_artifact"]
        artifact[field] = "substituted"
        artifact["artifact_hash"] = replay_hash({key: value for key, value in artifact.items() if key != "artifact_hash"})
        changed["actor_replay_binding_hash"] = replay_hash(
            {key: value for key, value in changed.items() if key != "actor_replay_binding_hash"})
        with pytest.raises(FailClosedRuntimeError):
            _reconstruct(common, authorization, changed)


def test_duplicate_destination_and_repeated_binding_fail_without_new_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    common, _, _ = _evidence(tmp_path, monkeypatch)
    authorization = _authorize(common)
    _bind(common, authorization)
    files = sorted(common["session_root"].rglob("*.json"))
    with pytest.raises(FailClosedRuntimeError, match="destination already exists"):
        _bind(common, authorization)
    assert files == sorted(common["session_root"].rglob("*.json"))


def test_prior_consumption_or_downstream_state_fails_before_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    common, _, _ = _evidence(tmp_path, monkeypatch)
    authorization = _authorize(common)
    for field in ("authorization_consumed", "replace_request_created", "rollback_performed"):
        changed = deepcopy(authorization)
        changed[field] = True
        changed["authorization_binding_hash"] = replay_hash(
            {key: value for key, value in changed.items() if key != "authorization_binding_hash"})
        with pytest.raises(FailClosedRuntimeError, match="unconsumed stop state"):
            _bind(common, changed)
    capture = _bind(common, authorization)
    changed_binding = deepcopy(capture["authorization_binding_artifact"])
    rejected_replay = common["session_root"] / "REJECTED-AUTHORIZATION-REPLAY"
    changed_binding["authorization_replay_reference"] = str(rejected_replay)
    changed_binding["main_repository_mutated"] = True
    changed_binding["artifact_hash"] = replay_hash(
        {key: value for key, value in changed_binding.items() if key != "artifact_hash"})
    with pytest.raises(FailClosedRuntimeError, match="identity is invalid"):
        authorization_runtime.persist_existing_authorization_binding_replay(
            binding=changed_binding, replay_dir=rejected_replay,
            session_root=common["session_root"],
        )
    assert not rejected_replay.exists()


def test_missing_reordered_tampered_and_cross_session_replay_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    common, _, _ = _evidence(tmp_path, monkeypatch)
    authorization = _authorize(common)
    capture = _bind(common, authorization)
    replay = Path(capture["authorization_replay_reference"])
    missing = replay / "002_authorization_returned.json"
    saved = missing.read_bytes()
    missing.unlink()
    with pytest.raises(FailClosedRuntimeError):
        _reconstruct(common, authorization, capture)
    missing.write_bytes(saved)
    duplicate = replay / "duplicate_authorization_returned.json"
    duplicate.write_bytes(saved)
    with pytest.raises(FailClosedRuntimeError, match="file set mismatch"):
        _reconstruct(common, authorization, capture)
    duplicate.unlink()
    first = replay / "000_authorization_owner_resolved.json"
    text = first.read_text(encoding="utf-8").replace('"replay_index":0', '"replay_index":2')
    first.write_text(text, encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError):
        _reconstruct(common, authorization, capture)
    with pytest.raises(FailClosedRuntimeError, match="cross-session"):
        authorization_runtime.reconstruct_existing_authorization_binding_replay(
            replay, session_root=tmp_path / "OTHER-SESSION")


def test_validly_rehashed_reordered_replay_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    common, _, _ = _evidence(tmp_path, monkeypatch)
    authorization = _authorize(common)
    capture = _bind(common, authorization)
    path = Path(capture["authorization_replay_reference"]) / "001_authorization_binding_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_index"] = 2
    wrapper["replay_hash"] = replay_hash({key: value for key, value in wrapper.items() if key != "replay_hash"})
    path.write_text(json.dumps(wrapper), encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        _reconstruct(common, authorization, capture)
