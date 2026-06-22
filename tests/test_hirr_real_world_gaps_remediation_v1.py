"""Tests for HIRR_REAL_WORLD_GAPS_REMEDIATION_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.hirr_real_world_gaps_remediation_v1 import (
    execute_hirr_real_world_gaps_remediation_v1,
    reconstruct_hirr_real_world_gaps_remediation_v1,
)
from aigol.runtime.transport.serialization import write_json_immutable


def _write_hirr_root(root: Path, *, verdict: str, score: str, certified: int, gaps: int, failed: int) -> None:
    report = {
        "artifact_type": "HIRR_REAL_WORLD_DOGFOOD_V2_CERTIFICATION_REPORT",
        "final_verdict": verdict,
        "aggregate_score": score,
        "case_count": 30,
        "certified_cases": certified,
        "gaps_found_cases": gaps,
        "failed_cases": failed,
        "workflow_selection_accuracy": 1.0 if verdict == "HIRR_REAL_WORLD_READY" else 0.5333,
        "clarification_quality_score": 1.0,
        "escalation_quality_score": 1.0 if verdict == "HIRR_REAL_WORLD_READY" else 0.5333,
        "live_cognition_success_rate": 1.0 if verdict == "HIRR_REAL_WORLD_READY" else 0.0,
        "replay_reconstruction_rate": 1.0,
    }
    evidence = {
        "artifact_type": "HIRR_REAL_WORLD_DOGFOOD_V2_EVIDENCE_PACKAGE",
        "failed_cases": ["HRD2-013"] if failed else [],
        "gaps_found_cases": ["HRD2-005"] if gaps else [],
        "false_negative_routing_cases": [{"case_id": "HRD2-013"}] if failed else [],
        "false_positive_routing_cases": [],
        "remaining_hirr_gaps": ["false_negative_routing"] if failed else [],
    }
    coverage = {
        "artifact_type": "HIRR_REAL_WORLD_DOGFOOD_V2_COVERAGE_REPORT",
        "case_count": 30,
    }
    write_json_immutable(root / "certification_report" / "000_hirr_real_world_dogfood_v2_certification_report.json", report)
    write_json_immutable(root / "evidence_package" / "000_hirr_real_world_dogfood_v2_evidence_package.json", evidence)
    write_json_immutable(root / "coverage_report" / "000_hirr_real_world_dogfood_v2_coverage_report.json", coverage)


def test_hirr_real_world_gaps_remediation_packages_before_after(tmp_path):
    before_root = tmp_path / "hirr_v2" / "CERT-000001"
    after_root = tmp_path / "hirr_v2" / "CERT-000002"
    _write_hirr_root(
        before_root,
        verdict="HIRR_REAL_WORLD_GAPS_FOUND",
        score="319/360",
        certified=15,
        gaps=4,
        failed=11,
    )
    _write_hirr_root(
        after_root,
        verdict="HIRR_REAL_WORLD_READY",
        score="360/360",
        certified=30,
        gaps=0,
        failed=0,
    )

    result = execute_hirr_real_world_gaps_remediation_v1(
        runtime_root=tmp_path / "remediation",
        before_cert_root=before_root,
        after_cert_root=after_root,
    )
    replay = reconstruct_hirr_real_world_gaps_remediation_v1(result["cert_root"])

    assert result["final_verdict"] == "HIRR_REAL_WORLD_READY"
    assert replay["replay_reconstructed"] is True
    assert replay["certification_report"]["before_after_comparison"]["before"]["aggregate_score"] == "319/360"
    assert replay["certification_report"]["before_after_comparison"]["after"]["aggregate_score"] == "360/360"
    assert Path(result["evidence_package_path"]).exists()
