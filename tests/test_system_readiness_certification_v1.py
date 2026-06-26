"""Tests for AIGOL_SYSTEM_READINESS_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.system_readiness_certification_v1 import (
    MILESTONE_ID,
    run_system_readiness_certification_v1,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def test_system_readiness_certification_produces_expected_packages(tmp_path) -> None:
    result = run_system_readiness_certification_v1(replay_base=tmp_path / "system_readiness")

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "AIGOL_SYSTEM_GAPS_FOUND"
    assert result["assertions"]["cognition_governance_verified"] is False
    assert all(
        value is True
        for key, value in result["assertions"].items()
        if key != "cognition_governance_verified"
    )
    for key in (
        "readiness_coverage_report_path",
        "evidence_package_path",
        "replay_package_path",
        "readiness_report_path",
        "certification_report_path",
    ):
        assert load_json(Path(result[key]))["runtime_version"] == MILESTONE_ID


def test_system_readiness_certifies_major_architectural_chains(tmp_path) -> None:
    result = run_system_readiness_certification_v1(replay_base=tmp_path / "system_readiness")
    readiness = load_json(Path(result["readiness_report_path"]))

    chains = readiness["major_chains_verified"]
    assert chains["human_intent_resolution"] is True
    assert chains["cognition_governance"] is False
    assert chains["provider_governance"] is True
    assert chains["worker_governance"] is True
    assert chains["worker_selection"] is True
    assert chains["replay_reconstruction"] is True
    assert chains["audit_review"] is True
    assert chains["executive_review"] is True
    assert chains["replay_derived_improvement"] is True
    assert chains["all_major_chains_verified"] is False
    assert readiness["remaining_blockers"] == ["cognition_governance_verified"]


def test_system_readiness_preserves_architectural_invariants(tmp_path) -> None:
    result = run_system_readiness_certification_v1(replay_base=tmp_path / "system_readiness")
    readiness = load_json(Path(result["readiness_report_path"]))

    invariants = readiness["architectural_invariants"]
    assert invariants["no_authority_transfer"] is True
    assert invariants["no_autonomous_modification"] is True
    assert invariants["replay_as_source_of_truth"] is True
    assert invariants["proposal_only_llm_participation"] is True
    assert invariants["executive_review_defined"] is True


def test_system_readiness_replay_package_links_sources(tmp_path) -> None:
    result = run_system_readiness_certification_v1(replay_base=tmp_path / "system_readiness")
    replay = load_json(Path(result["replay_package_path"]))

    assert replay["replay_reconstructed"] is True
    assert replay["replay_as_source_of_truth"] is True
    assert set(replay["source_replay_roots"]) == {
        "human_intent_resolution",
        "product1_end_to_end",
        "multi_provider_operational",
        "worker_selection",
        "replay_reproducibility",
        "product1_audit_review",
        "replay_derived_improvement",
        "provider_governance",
        "cognition_governance",
    }


def test_system_readiness_evidence_is_secret_free(tmp_path) -> None:
    result = run_system_readiness_certification_v1(replay_base=tmp_path / "system_readiness")
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "OPENAI_API_KEY=" not in serialized
    assert "ANTHROPIC_API_KEY=" not in serialized
