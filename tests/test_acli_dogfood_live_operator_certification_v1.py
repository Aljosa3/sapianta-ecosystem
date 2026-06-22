"""Tests for AIGOL_ACLI_DOGFOOD_LIVE_OPERATOR_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.acli_dogfood_live_operator_certification_v1 import (
    MILESTONE_ID,
    reconstruct_acli_dogfood_live_operator_replay,
    run_acli_dogfood_live_operator_certification,
)
from aigol.runtime.transport.serialization import canonical_serialize, load_json


def test_acli_dogfood_live_operator_certification_runs_real_sessions(tmp_path):
    result = run_acli_dogfood_live_operator_certification(
        replay_base=tmp_path / "acli_dogfood_live_operator",
        workspace=tmp_path,
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] in {"ACLI_LIVE_OPERATOR_READY", "ACLI_LIVE_OPERATOR_GAPS_FOUND"}
    assert len(result["scenario_results"]) == 8
    assert all(Path(item["runtime_root"]).exists() for item in result["scenario_results"])

    root = Path(result["cert_root"])
    assert (root / "coverage_report" / "000_acli_dogfood_live_operator_coverage_report.json").exists()
    assert (root / "evidence_package" / "000_acli_dogfood_live_operator_evidence_package.json").exists()
    assert (root / "replay_package" / "000_acli_dogfood_live_operator_replay_package.json").exists()
    assert (root / "operator_experience_report" / "000_acli_dogfood_live_operator_experience_report.json").exists()
    assert (root / "certification_report" / "000_acli_dogfood_live_operator_certification_report.json").exists()


def test_acli_dogfood_live_operator_measures_required_rates(tmp_path):
    result = run_acli_dogfood_live_operator_certification(
        replay_base=tmp_path / "acli_dogfood_live_operator",
        workspace=tmp_path,
    )
    rates = result["rates"]

    assert set(rates) == {
        "first_pass_resolution_rate",
        "clarification_rate",
        "semantic_escalation_rate",
        "approval_rate",
        "replay_reconstruction_rate",
        "workflow_selection_accuracy",
        "certified_session_rate",
    }
    assert rates["replay_reconstruction_rate"] == 1.0


def test_acli_dogfood_live_operator_records_provider_participation_when_semantic(tmp_path):
    result = run_acli_dogfood_live_operator_certification(
        replay_base=tmp_path / "acli_dogfood_live_operator",
        workspace=tmp_path,
    )
    root = Path(result["cert_root"])
    usage = list((root / "provider_governance_replay").rglob("000_provider_usage_metric.json"))
    participation = list((root / "provider_governance_replay").rglob("000_cognition_participation.json"))

    assert usage
    assert participation
    assert all(load_json(path)["provider_authority"] is False for path in participation)


def test_acli_dogfood_live_operator_replay_reconstructs(tmp_path):
    result = run_acli_dogfood_live_operator_certification(
        replay_base=tmp_path / "acli_dogfood_live_operator",
        workspace=tmp_path,
    )
    replay = reconstruct_acli_dogfood_live_operator_replay(result["cert_root"])

    assert replay["replay_reconstructed"] is True
    assert replay["scenario_count"] == 8


def test_acli_dogfood_live_operator_preserves_governance_boundaries(tmp_path):
    result = run_acli_dogfood_live_operator_certification(
        replay_base=tmp_path / "acli_dogfood_live_operator",
        workspace=tmp_path,
    )

    assert all(item["no_unauthorized_execution"] for item in result["scenario_results"])
    assert all(item["no_authority_transfer"] for item in result["scenario_results"])


def test_acli_dogfood_live_operator_evidence_is_secret_free(tmp_path):
    result = run_acli_dogfood_live_operator_certification(
        replay_base=tmp_path / "acli_dogfood_live_operator",
        workspace=tmp_path,
    )
    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "operator-dogfood-test-key" not in serialized
    assert "sk-" not in serialized
    assert "Bearer " not in serialized
