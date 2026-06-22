"""Tests for AIGOL_PRODUCT1_END_TO_END_CERTIFICATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.product1_end_to_end_certification_v1 import (
    FINAL_VERDICT_CERTIFIED,
    MILESTONE_ID,
    reconstruct_product1_end_to_end_certification_v1,
    run_product1_end_to_end_certification_v1,
)
from aigol.runtime.transport.serialization import canonical_serialize, write_json_immutable, load_json


def _component_reports(root: Path) -> dict[str, Path]:
    hirr = root / "hirr_report.json"
    live = root / "live_cognition_report.json"
    governance = root / "provider_governance_report.json"
    vault = root / "provider_vault_acli_report.json"
    write_json_immutable(
        hirr,
        {
            "artifact_type": "TEST_HIRR_REPORT",
            "final_verdict": "HIRR_REAL_WORLD_READY",
            "aggregate_score": "360/360",
        },
    )
    write_json_immutable(
        live,
        {
            "artifact_type": "TEST_LIVE_COGNITION_REPORT",
            "final_verdict": "FIRST_LIVE_COGNITION_PROVIDER_CERTIFIED",
            "observed": {
                "provider_selected": "openai",
                "provider_invoked": True,
                "provider_response_received": True,
                "human_confirmation_recorded": True,
                "replay_reconstructed": True,
                "worker_invoked": False,
                "failure_reason": "",
            },
        },
    )
    write_json_immutable(
        governance,
        {
            "artifact_type": "TEST_PROVIDER_GOVERNANCE_REPORT",
            "final_verdict": "PROVIDER_GOVERNANCE_CERTIFIED",
        },
    )
    write_json_immutable(
        vault,
        {
            "artifact_type": "TEST_PROVIDER_VAULT_ACLI_REPORT",
            "final_verdict": "PROVIDER_VAULT_ACLI_INTEGRATION_CERTIFIED",
        },
    )
    return {
        "hirr_ready_report_path": hirr,
        "live_cognition_report_path": live,
        "provider_governance_report_path": governance,
        "provider_vault_acli_report_path": vault,
    }


def test_product1_end_to_end_certification_runs_and_reconstructs(tmp_path):
    reports = _component_reports(tmp_path / "component_reports")
    result = run_product1_end_to_end_certification_v1(
        runtime_root=tmp_path / "product1_e2e",
        **reports,
    )
    replay = reconstruct_product1_end_to_end_certification_v1(result["cert_root"])

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_verdict"] == FINAL_VERDICT_CERTIFIED
    assert len(result["scenario_results"]) == 6
    assert all(result["assertions"].values())
    assert replay["replay_reconstructed"] is True
    assert replay["final_verdict"] == FINAL_VERDICT_CERTIFIED

    for key in ("coverage_report_path", "evidence_package_path", "replay_package_path", "certification_report_path"):
        assert Path(result[key]).exists()


def test_product1_end_to_end_certification_covers_required_paths(tmp_path):
    reports = _component_reports(tmp_path / "component_reports")
    result = run_product1_end_to_end_certification_v1(
        runtime_root=tmp_path / "product1_e2e",
        **reports,
    )
    report = load_json(Path(result["certification_report_path"]))
    coverage = {item["coverage"] for item in report["scenario_results"]}

    assert {
        "direct_execution",
        "clarification_path",
        "cognition_path",
        "approval_path",
        "rejection_path",
        "fail_closed_path",
    } <= coverage
    assert report["product1_question_answer"].startswith("YES")


def test_product1_end_to_end_evidence_is_secret_free(tmp_path):
    reports = _component_reports(tmp_path / "component_reports")
    result = run_product1_end_to_end_certification_v1(
        runtime_root=tmp_path / "product1_e2e",
        **reports,
    )

    serialized = ""
    for path in sorted(Path(result["cert_root"]).rglob("*.json")):
        serialized += canonical_serialize(load_json(path))

    assert "sk-" not in serialized
    assert "Bearer " not in serialized
    assert "api_key" not in serialized.lower()
