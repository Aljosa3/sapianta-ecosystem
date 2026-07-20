from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import subprocess

import pytest

from aigol.runtime import codex_worker_activation_binding_runtime as activation
from aigol.runtime import human_decision_runtime as decision
from aigol.runtime import platform_core_existing_file_governance as governance
from aigol.runtime import platform_core_existing_file_mutation_candidate as candidate
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


def _evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, outcome: str = decision.MUTATION_APPROVED):
    root = tmp_path / "G31-24G-R04-R02"
    workspace = tmp_path / "repo"
    target = workspace / "aigol/runtime/human_interface.py"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"original bytes\n")
    subprocess.run(["git", "init"], cwd=workspace, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "G31"], cwd=workspace, check=True)
    subprocess.run(["git", "config", "user.email", "g31@example.invalid"], cwd=workspace, check=True)
    subprocess.run(["git", "add", "aigol/runtime/human_interface.py"], cwd=workspace, check=True)
    subprocess.run(["git", "commit", "-m", "baseline"], cwd=workspace, check=True, capture_output=True)
    grounding = {"grounding_evidence_hash": "grounding-hash", "workspace_root": str(workspace.resolve())}
    activation_binding = {
        "lineage": {"grounding": grounding}, "activation_replay_reference": str(root / "ACTIVATION"),
        "activation_replay_hash": "activation-replay-hash",
    }
    raw_activation = {"activation_replay_reference": str(root / "ACTIVATION"), "worker_invoked": True}
    calls = {"activation_reconstruction": 0, "candidate_reconstruction": 0}

    def reconstruct_activation(**_kwargs):
        calls["activation_reconstruction"] += 1
        return deepcopy(activation_binding)

    def reconstruct_candidate(*, candidate_capture, **_kwargs):
        calls["candidate_reconstruction"] += 1
        artifact = candidate_capture["existing_file_mutation_candidate_artifact"]
        return {
            "candidate_id": artifact["candidate_id"], "candidate_hash": artifact["artifact_hash"],
            "candidate_provenance_binding_hash": artifact["candidate_provenance_binding_hash"],
            "replay_artifact_count": 3, "replay_hash": candidate_capture["candidate_replay_hash"],
            "result_accepted": True, "human_mutation_decision_recorded": False,
            "mutation_authorized": False, "main_repository_mutated": False,
        }

    monkeypatch.setattr(activation, "reconstruct_codex_worker_activation_binding", reconstruct_activation)
    monkeypatch.setattr(candidate, "reconstruct_g31_accepted_existing_file_mutation_candidate_replay", reconstruct_candidate)
    provenance = {
        "session_id": root.name, "repository_identity": "repo-identity",
        "repository_root": str(workspace.resolve()), "repository_grounding_hash": "grounding-hash",
        "accepted_result_hash": "accepted-hash", "acceptance_hash": "acceptance-hash",
        "content_decision_hash": "content-decision-hash", "prerequisite_hash": "prerequisite-hash",
        "manifest_hash": "manifest-hash", "target_path": "aigol/runtime/human_interface.py",
        "preimage_sha256": "sha256:" + sha256(target.read_bytes()).hexdigest(),
        "postimage_sha256": "sha256:" + sha256(b"replacement bytes\n").hexdigest(),
        "source_mode": "0o100644", "replacement_mode": "0o100644",
        "content_validation_hash": "content-validation-hash", "test_validation_hash": "test-validation-hash",
        "disposable_validation_hash": "disposable-validation-hash", "operation": "REPLACE_CONTENT",
    }
    provenance["binding_hash"] = replay_hash(provenance)
    artifact = {
        "artifact_type": candidate.EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V2,
        "runtime_version": candidate.G31_EXISTING_FILE_MUTATION_CANDIDATE_VERSION,
        "candidate_id": "G31-R04-R02-CANDIDATE", "session_id": root.name,
        "operation": "REPLACE_CONTENT", "target_path": provenance["target_path"], "file_count": 1,
        "candidate_provenance": provenance, "candidate_provenance_binding_hash": provenance["binding_hash"],
        "created_by": "HUMAN_OPERATOR", "created_at": "2026-07-20T00:00:00Z",
        "human_mutation_decision_recorded": False, "mutation_authorized": False,
        "main_repository_mutated": False, "provider_invoked": False, "worker_invoked": False,
        "command_executed": False, "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    candidate_capture = {
        "existing_file_mutation_candidate_artifact": artifact,
        "candidate_replay_reference": str(root / "CANDIDATE"), "candidate_replay_hash": "candidate-replay-hash",
        "existing_file_mutation_candidate_created": True, "result_accepted": True,
        "human_mutation_decision_recorded": False, "mutation_authorized": False,
        "main_repository_mutated": False,
    }
    candidate_reconstruction = reconstruct_candidate(candidate_capture=candidate_capture)
    context = decision.prepare_existing_file_mutation_decision_context(
        context_id="G31-R04-R02-DECISION", candidate_capture=candidate_capture,
        acceptance_capture={}, content_decision_capture={}, binding_capture={},
        repository_grounding_artifact=grounding, human_actor_id="HUMAN_OPERATOR",
        presented_at="2026-07-20T00:00:00Z", session_root=root, replay_dir=root / "DECISION",
    )
    mutation_decision = decision.record_existing_file_mutation_decision(
        context_capture=context, candidate_capture=candidate_capture, acceptance_capture={},
        content_decision_capture={}, binding_capture={}, repository_grounding_artifact=grounding,
        decision_outcome=outcome, decided_by="HUMAN_OPERATOR", decided_at="2026-07-20T00:00:00Z",
        session_root=root,
    )
    mutation_decision_reconstruction = decision.reconstruct_existing_file_mutation_decision_replay(
        decision_capture=mutation_decision, candidate_capture=candidate_capture, acceptance_capture={},
        content_decision_capture={}, binding_capture={}, repository_grounding_artifact=grounding,
        session_root=root,
    )
    common = dict(
        candidate_capture=candidate_capture, candidate_reconstruction=candidate_reconstruction,
        mutation_decision_capture=mutation_decision,
        mutation_decision_reconstruction=mutation_decision_reconstruction,
        acceptance_capture={}, content_decision_capture={}, binding_capture={},
        repository_grounding_artifact=grounding, activation_capture=raw_activation,
        activation_binding=activation_binding, governed_execution_capture={},
        execution_candidate_capture={}, session_root=root, workspace=workspace,
    )
    return common, calls, target


def _authorize(common: dict) -> dict:
    return governance.authorize_g31_approved_existing_file_mutation(
        authorization_id="G31-R04-R02-AUTHORIZATION",
        authorization_timestamp="2026-07-20T00:00:00Z", **common,
    )


def test_exact_reconstructed_candidate_and_approved_decision_reach_canonical_authorization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    common, calls, target = _evidence(tmp_path, monkeypatch)
    before, status = target.read_bytes(), subprocess.run(
        ["git", "status", "--short"], cwd=common["workspace"], check=True, capture_output=True, text=True).stdout
    capture = _authorize(common)
    reconstructed = governance.reconstruct_g31_existing_file_mutation_authorization_binding(
        authorization_capture=capture, **common)
    assert capture["authorization_record"]["proposal_id"] == reconstructed["candidate_id"]
    assert capture["authorization_evidence"]["mutation_decision_hash"] == reconstructed["mutation_decision_hash"]
    assert reconstructed["mutation_authorized"] is True
    assert reconstructed["patch_created"] is False
    assert reconstructed["repository_mutated"] is False
    assert reconstructed["worker_invoked"] is False
    assert calls["activation_reconstruction"] == 2
    assert target.read_bytes() == before
    assert subprocess.run(["git", "status", "--short"], cwd=common["workspace"], check=True, capture_output=True, text=True).stdout == status == ""


def test_non_approved_decision_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    common, _, _ = _evidence(tmp_path, monkeypatch, outcome=decision.REJECTED)
    with pytest.raises(FailClosedRuntimeError, match="decision or candidate lineage mismatch"):
        _authorize(common)


def test_decision_for_different_candidate_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    common, _, _ = _evidence(tmp_path, monkeypatch)
    changed = deepcopy(common["candidate_capture"])
    changed["existing_file_mutation_candidate_artifact"]["candidate_id"] = "DIFFERENT-CANDIDATE"
    value = changed["existing_file_mutation_candidate_artifact"]
    value["artifact_hash"] = replay_hash({key: item for key, item in value.items() if key != "artifact_hash"})
    common["candidate_capture"] = changed
    common["candidate_reconstruction"] = {
        **common["candidate_reconstruction"], "candidate_id": value["candidate_id"],
        "candidate_hash": value["artifact_hash"],
    }
    with pytest.raises(FailClosedRuntimeError):
        _authorize(common)


@pytest.mark.parametrize("field", ["candidate_capture", "mutation_decision_capture"])
def test_candidate_or_decision_hash_tamper_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str,
) -> None:
    common, _, _ = _evidence(tmp_path, monkeypatch)
    changed = deepcopy(common[field])
    artifact_key = ("existing_file_mutation_candidate_artifact" if field == "candidate_capture"
                    else "human_mutation_decision_artifact")
    changed[artifact_key]["artifact_hash"] = "sha256:" + "0" * 64
    common[field] = changed
    with pytest.raises(FailClosedRuntimeError):
        _authorize(common)


def test_replay_session_and_raw_activation_substitution_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    common, _, _ = _evidence(tmp_path, monkeypatch)
    changed = dict(common)
    changed["candidate_reconstruction"] = {**common["candidate_reconstruction"], "replay_hash": "substituted"}
    with pytest.raises(FailClosedRuntimeError, match="reconstructed V2 candidate"):
        _authorize(changed)
    changed = dict(common)
    changed["mutation_decision_reconstruction"] = {
        **common["mutation_decision_reconstruction"], "replay_hash": "substituted"}
    with pytest.raises(FailClosedRuntimeError, match="reconstructed V3 decision"):
        _authorize(changed)
    changed = dict(common)
    changed["mutation_decision_capture"] = {}
    with pytest.raises(FailClosedRuntimeError):
        _authorize(changed)
    changed = dict(common)
    changed["candidate_reconstruction"] = common["candidate_capture"]
    with pytest.raises(FailClosedRuntimeError, match="reconstructed V2 candidate"):
        _authorize(changed)
    changed = dict(common)
    changed["mutation_decision_reconstruction"] = common["mutation_decision_capture"]
    with pytest.raises(FailClosedRuntimeError, match="reconstructed V3 decision"):
        _authorize(changed)
    changed = dict(common)
    changed["activation_binding"] = common["activation_capture"]
    with pytest.raises(FailClosedRuntimeError, match="reconstructed activation lineage"):
        _authorize(changed)
    changed = dict(common)
    changed["session_root"] = tmp_path / "OTHER-SESSION"
    with pytest.raises(FailClosedRuntimeError):
        _authorize(changed)


@pytest.mark.parametrize("field", ["target_path", "preimage_sha256"])
def test_candidate_path_or_expected_source_hash_substitution_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str,
) -> None:
    common, _, _ = _evidence(tmp_path, monkeypatch)
    changed = deepcopy(common["candidate_capture"])
    artifact = changed["existing_file_mutation_candidate_artifact"]
    artifact["candidate_provenance"][field] = "substituted"
    artifact["candidate_provenance"]["binding_hash"] = replay_hash({
        key: value for key, value in artifact["candidate_provenance"].items() if key != "binding_hash"
    })
    artifact["candidate_provenance_binding_hash"] = artifact["candidate_provenance"]["binding_hash"]
    artifact["artifact_hash"] = replay_hash({key: value for key, value in artifact.items() if key != "artifact_hash"})
    common["candidate_capture"] = changed
    common["candidate_reconstruction"] = {
        **common["candidate_reconstruction"], "candidate_hash": artifact["artifact_hash"],
        "candidate_provenance_binding_hash": artifact["candidate_provenance_binding_hash"],
    }
    with pytest.raises(FailClosedRuntimeError):
        _authorize(common)


def test_repeated_reconstruction_creates_no_new_generation_or_side_effect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    common, calls, target = _evidence(tmp_path, monkeypatch)
    capture = _authorize(common)
    files_before = sorted(path.relative_to(common["session_root"]) for path in common["session_root"].rglob("*.json"))
    first = governance.reconstruct_g31_existing_file_mutation_authorization_binding(
        authorization_capture=capture, **common)
    second = governance.reconstruct_g31_existing_file_mutation_authorization_binding(
        authorization_capture=capture, **common)
    assert first == second
    assert calls["activation_reconstruction"] == 3
    assert files_before == sorted(path.relative_to(common["session_root"]) for path in common["session_root"].rglob("*.json"))
    assert target.read_bytes() == b"original bytes\n"
    assert first["worker_invoked"] is False and first["provider_invoked"] is False
