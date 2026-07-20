from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from aigol.runtime import human_decision_runtime as decision
from aigol.runtime import platform_core_existing_file_mutation_candidate as candidate
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


@pytest.fixture
def accepted_candidate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = tmp_path / "G31-24G-R02"
    provenance = {
        "session_id": root.name, "repository_identity": "repo-identity", "repository_root": "/isolated/repo",
        "repository_grounding_hash": "grounding-hash", "accepted_result_hash": "accepted-hash",
        "acceptance_hash": "acceptance-hash", "content_decision_hash": "content-decision-hash",
        "prerequisite_hash": "prerequisite-hash", "manifest_hash": "manifest-hash",
        "target_path": "aigol/runtime/human_interface.py", "preimage_sha256": "preimage-hash",
        "postimage_sha256": "postimage-hash", "source_mode": "0o100644", "replacement_mode": "0o100644",
        "content_validation_hash": "content-validation-hash", "test_validation_hash": "test-validation-hash",
        "disposable_validation_hash": "disposable-validation-hash", "operation": "REPLACE_CONTENT",
    }
    provenance["binding_hash"] = replay_hash(provenance)
    artifact = {
        "artifact_type": candidate.EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V2,
        "runtime_version": candidate.G31_EXISTING_FILE_MUTATION_CANDIDATE_VERSION,
        "candidate_id": "G31-24G-R02-CANDIDATE", "session_id": root.name, "operation": "REPLACE_CONTENT",
        "target_path": provenance["target_path"], "file_count": 1, "candidate_provenance": provenance,
        "candidate_provenance_binding_hash": provenance["binding_hash"], "created_by": "HUMAN_OPERATOR",
        "created_at": "2026-07-20T00:00:00Z", "human_mutation_decision_recorded": False,
        "mutation_authorized": False, "main_repository_mutated": False, "provider_invoked": False,
        "worker_invoked": False, "command_executed": False, "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    capture = {
        "existing_file_mutation_candidate_artifact": artifact, "candidate_replay_reference": str(root / "CANDIDATE"),
        "candidate_replay_hash": "candidate-replay-hash", "existing_file_mutation_candidate_created": True,
        "result_accepted": True, "human_mutation_decision_recorded": False, "mutation_authorized": False,
        "main_repository_mutated": False,
    }

    def reconstruct(**_kwargs):
        return {"candidate_id": artifact["candidate_id"], "candidate_hash": artifact["artifact_hash"],
                "candidate_provenance_binding_hash": provenance["binding_hash"], "replay_artifact_count": 3,
                "replay_hash": "candidate-replay-hash", "result_accepted": True,
                "human_mutation_decision_recorded": False, "mutation_authorized": False,
                "main_repository_mutated": False}

    monkeypatch.setattr(candidate, "reconstruct_g31_accepted_existing_file_mutation_candidate_replay", reconstruct)
    return root, capture


def _context(root: Path, capture: dict, name: str = "MUTATION-DECISION") -> dict:
    return decision.prepare_existing_file_mutation_decision_context(
        context_id=f"G31-24G-R02-{name}", candidate_capture=capture, acceptance_capture={},
        content_decision_capture={}, binding_capture={}, repository_grounding_artifact={},
        human_actor_id="HUMAN_OPERATOR_VIA_AICLI", presented_at="2026-07-20T00:00:00Z",
        session_root=root, replay_dir=root / name,
    )


@pytest.mark.parametrize("outcome, approved", [(decision.MUTATION_APPROVED, True), (decision.REJECTED, False)])
def test_exact_v2_candidate_records_and_reconstructs_distinct_mutation_decision(
    accepted_candidate: tuple[Path, dict], outcome: str, approved: bool,
) -> None:
    root, capture = accepted_candidate
    context = _context(root, capture, f"MUTATION-{outcome}")
    recorded = decision.record_existing_file_mutation_decision(
        context_capture=context, candidate_capture=capture, acceptance_capture={}, content_decision_capture={},
        binding_capture={}, repository_grounding_artifact={}, decision_outcome=outcome,
        decided_by="HUMAN_OPERATOR_VIA_AICLI", decided_at="2026-07-20T00:00:00Z", session_root=root,
    )
    reconstructed = decision.reconstruct_existing_file_mutation_decision_replay(
        decision_capture=recorded, candidate_capture=capture, acceptance_capture={}, content_decision_capture={},
        binding_capture={}, repository_grounding_artifact={}, session_root=root,
    )
    assert reconstructed["replay_artifact_count"] == 4
    assert reconstructed["mutation_decision_approved"] is approved
    assert recorded["mutation_authorized"] is False
    assert recorded["main_repository_mutated"] is False
    assert "distinct from content acceptance" in decision.render_existing_file_mutation_decision_context(context)
    assert "No repository file will be changed" in decision.render_existing_file_mutation_decision_context(context)
    assert "Mutation Authorized: False" in decision.render_existing_file_mutation_decision(recorded)


def test_v3_rejects_generic_vocabulary_tampered_candidate_actor_replay_and_reuse(
    accepted_candidate: tuple[Path, dict], monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, capture = accepted_candidate
    context = _context(root, capture)
    common = dict(context_capture=context, candidate_capture=capture, acceptance_capture={}, content_decision_capture={},
                  binding_capture={}, repository_grounding_artifact={}, decided_by="HUMAN_OPERATOR_VIA_AICLI",
                  decided_at="2026-07-20T00:00:00Z", session_root=root)
    for value in ("APPROVE", "YES", "SATISFIED", "ACCEPTED", True, decision.CONTENT_ACCEPTANCE):
        with pytest.raises(FailClosedRuntimeError):
            decision.record_existing_file_mutation_decision(decision_outcome=value, **common)
    altered = deepcopy(capture)
    altered["existing_file_mutation_candidate_artifact"]["artifact_type"] = candidate.EXISTING_FILE_MUTATION_CANDIDATE_ARTIFACT_V1
    with pytest.raises(FailClosedRuntimeError):
        _context(root, altered, "ALTERED")
    with pytest.raises(FailClosedRuntimeError):
        decision.record_existing_file_mutation_decision(decision_outcome=decision.MUTATION_APPROVED,
                                                        decided_by="SUBSTITUTED_ACTOR", **{k: v for k, v in common.items() if k != "decided_by"})
    recorded = decision.record_existing_file_mutation_decision(decision_outcome=decision.MUTATION_APPROVED, **common)
    with pytest.raises(FailClosedRuntimeError, match="destination already exists"):
        decision.record_existing_file_mutation_decision(decision_outcome=decision.MUTATION_APPROVED, **common)
    with pytest.raises(FailClosedRuntimeError, match="already decided"):
        decision.record_existing_file_mutation_decision(
            context_capture=_context(root, capture, "SECOND"), candidate_capture=capture, acceptance_capture={},
            content_decision_capture={}, binding_capture={}, repository_grounding_artifact={}, decision_outcome=decision.REJECTED,
            decided_by="HUMAN_OPERATOR_VIA_AICLI", decided_at="2026-07-20T00:00:00Z", session_root=root,
        )
    original_load = decision.load_json

    def reordered_load(path):
        value = original_load(path)
        if Path(path).name.startswith("000_"):
            value["replay_step"] = "mutation_decision_recorded"
        return value

    monkeypatch.setattr(decision, "load_json", reordered_load)
    with pytest.raises(FailClosedRuntimeError):
        decision.reconstruct_existing_file_mutation_decision_replay(
            decision_capture=recorded, candidate_capture=capture, acceptance_capture={}, content_decision_capture={},
            binding_capture={}, repository_grounding_artifact={}, session_root=root,
        )
