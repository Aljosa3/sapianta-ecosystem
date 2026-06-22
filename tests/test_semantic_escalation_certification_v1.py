"""Tests for AIGOL_SEMANTIC_ESCALATION_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.semantic_escalation_certification_v1 import (
    MILESTONE_ID,
    reconstruct_semantic_escalation_replay,
    run_semantic_escalation_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def test_semantic_escalation_certification_produces_required_artifacts(tmp_path):
    result = run_semantic_escalation_certification(replay_base=tmp_path / "semantic_escalation")

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == "SEMANTIC_ESCALATION_CERTIFIED"
    assert all(result["assertions"].values())

    root = Path(result["cert_root"])
    assert (root / "coverage_report" / "000_semantic_escalation_coverage_report.json").exists()
    assert (root / "evidence_package" / "000_semantic_escalation_evidence_package.json").exists()
    assert (root / "replay_package" / "000_semantic_escalation_replay_package.json").exists()
    assert (root / "certification_report" / "000_semantic_escalation_certification_report.json").exists()


def test_semantic_escalation_covers_required_prompt_classes(tmp_path):
    result = run_semantic_escalation_certification(replay_base=tmp_path / "semantic_escalation")
    evidence = load_json(
        Path(result["cert_root"]) / "evidence_package" / "000_semantic_escalation_evidence_package.json"
    )
    categories = {item["category"] for item in evidence["scenario_results"]}

    assert {
        "ambiguous_request",
        "incomplete_request",
        "overloaded_terminology",
        "multiple_plausible_interpretations",
        "domain_ambiguity",
        "slovenian_natural_language",
        "mixed_language_prompt",
    }.issubset(categories)


def test_semantic_escalation_requires_confirmation_before_workflow_selection(tmp_path):
    result = run_semantic_escalation_certification(replay_base=tmp_path / "semantic_escalation")
    evidence = load_json(
        Path(result["cert_root"]) / "evidence_package" / "000_semantic_escalation_evidence_package.json"
    )

    assert all(item["deterministic_resolution_attempted"] for item in evidence["scenario_results"])
    assert all(item["deterministic_confidence"] == "LOW" for item in evidence["scenario_results"])
    assert all(item["escalated_to_cognition_provider"] for item in evidence["scenario_results"])
    assert all(item["semantic_proposal_received"] for item in evidence["scenario_results"])
    assert all(item["human_confirmation_recorded"] for item in evidence["scenario_results"])
    assert all(item["workflow_selected_after_confirmation"] for item in evidence["scenario_results"])
    assert not any(item["execution_before_confirmation"] for item in evidence["scenario_results"])


def test_semantic_escalation_records_provider_usage_and_participation(tmp_path):
    result = run_semantic_escalation_certification(replay_base=tmp_path / "semantic_escalation")
    root = Path(result["cert_root"])

    usage_files = list((root / "provider_governance_replay").rglob("000_provider_usage_metric.json"))
    participation_files = list((root / "provider_governance_replay").rglob("000_cognition_participation.json"))

    assert len(usage_files) == 7
    assert len(participation_files) == 7
    assert all(load_json(path)["provider_authority"] is False for path in participation_files)
    assert all(load_json(path)["human_confirmation_required"] is True for path in participation_files)


def test_semantic_escalation_replay_reconstructs(tmp_path):
    result = run_semantic_escalation_certification(replay_base=tmp_path / "semantic_escalation")
    reconstruction = reconstruct_semantic_escalation_replay(result["cert_root"])

    assert reconstruction["replay_reconstructed"] is True
    assert reconstruction["deterministic_attempts_visible"] is True
    assert reconstruction["provider_proposals_visible"] is True
    assert reconstruction["human_confirmations_visible"] is True
    assert reconstruction["workflow_selection_after_confirmation_visible"] is True


def test_semantic_escalation_evidence_is_secret_free(tmp_path):
    result = run_semantic_escalation_certification(replay_base=tmp_path / "semantic_escalation")
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "OPENAI_API_KEY=" not in serialized
