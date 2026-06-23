"""Tests for AIGOL_REPLAY_DERIVED_IMPROVEMENT_OPERATIONALIZATION_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.replay_derived_improvement_operationalization_certification_v1 import (
    MILESTONE_ID,
    run_replay_derived_improvement_operationalization_certification_v1,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def test_operationalization_certification_produces_expected_packages(tmp_path) -> None:
    result = run_replay_derived_improvement_operationalization_certification_v1(
        replay_base=tmp_path / "rdi_operationalization"
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "REPLAY_DERIVED_IMPROVEMENT_OPERATIONALIZATION_CERTIFIED"
    assert all(result["assertions"].values())
    for key in (
        "coverage_report_path",
        "evidence_package_path",
        "replay_package_path",
        "operationalization_package_path",
        "certification_report_path",
    ):
        assert load_json(Path(result[key]))["runtime_version"] == MILESTONE_ID


def test_operationalization_certification_tracks_multi_generation_lineage(tmp_path) -> None:
    result = run_replay_derived_improvement_operationalization_certification_v1(
        replay_base=tmp_path / "rdi_operationalization"
    )
    replay = load_json(Path(result["replay_package_path"]))
    evidence = load_json(Path(result["evidence_package_path"]))

    assert replay["replay_reconstructed"] is True
    assert len(replay["generation_chain"]) == 2
    assert replay["generation_chain"][1]["predecessor_improvement_reference"]
    assert evidence["lineage"]["status"] == "APPROVED_PROPOSAL_PENDING_CERTIFICATION"


def test_operationalization_certification_records_duplicate_priority_and_supersession(tmp_path) -> None:
    result = run_replay_derived_improvement_operationalization_certification_v1(
        replay_base=tmp_path / "rdi_operationalization"
    )
    evidence = load_json(Path(result["evidence_package_path"]))
    operationalization = load_json(Path(result["operationalization_package_path"]))

    assert evidence["duplicate_detection"]["status"] == "DUPLICATE_OF_EXISTING"
    assert evidence["priority"]["status"] is None
    assert operationalization["priority_level"] == "P2"
    assert operationalization["superseded_proposal"] == "PROPOSAL-RDI-OP-ORIGINAL-000001"
    assert operationalization["superseding_proposal"] == "PROPOSAL-RDI-OP-COMPETING-000001"


def test_operationalization_certification_preserves_proposal_only_behavior(tmp_path) -> None:
    result = run_replay_derived_improvement_operationalization_certification_v1(
        replay_base=tmp_path / "rdi_operationalization"
    )
    operationalization = load_json(Path(result["operationalization_package_path"]))

    assert operationalization["proposal_only_behavior_preserved"] is True
    assert operationalization["human_approval_required"] is True
    assert operationalization["code_modified"] is False
    assert operationalization["governance_modified"] is False
    assert operationalization["worker_invoked"] is False
    assert operationalization["provider_invoked"] is False
    assert operationalization["authority_transferred"] is False


def test_operationalization_certification_evidence_is_secret_free(tmp_path) -> None:
    result = run_replay_derived_improvement_operationalization_certification_v1(
        replay_base=tmp_path / "rdi_operationalization"
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "OPENAI_API_KEY=" not in serialized
    assert "ANTHROPIC_API_KEY=" not in serialized
