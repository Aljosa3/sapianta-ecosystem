"""Enforcement review tests for AIGOL_EXECUTION_SUMMARY_ENFORCEMENT_V1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "governance" / "AIGOL_EXECUTION_SUMMARY_ENFORCEMENT_V1.json"

REQUIRED_PATHS = {
    "DEVELOPMENT_EXECUTION_PATHS",
    "WORKER_EXECUTION_PATHS",
    "DOMAIN_OPERATION_PATHS",
    "CAPABILITY_OPERATION_PATHS",
    "REPLAY_DERIVED_IMPROVEMENT_EXECUTION_PATHS",
}

FINAL_FIELDS = {
    "SUMMARY_ENFORCEMENT_COMPLETE": "NO",
    "EXECUTION_WITHOUT_SUMMARY_POSSIBLE": "YES",
    "EXECUTION_WITHOUT_CONFIRMATION_POSSIBLE": "YES",
    "EXECUTION_WITHOUT_AUTHORIZATION_POSSIBLE": "YES",
    "ALL_EXECUTION_PATHS_PROTECTED": "NO",
}


def _report() -> dict:
    return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


def test_execution_path_inventory_covers_required_surfaces() -> None:
    report = _report()
    inventory = {path["path_id"]: path for path in report["execution_path_inventory"]}

    assert report["review_status"] == "ENFORCEMENT_GAP_IDENTIFIED"
    assert set(inventory) == REQUIRED_PATHS
    for path in inventory.values():
        assert path["execution_capable"] is True
        assert path["execution_summary_enforced"] is False
        assert path["human_confirmation_bound_to_execution_summary"] is False
        assert path["representative_runtimes"]
        assert path["gap"]


def test_enforcement_analysis_reports_summary_boundary_not_yet_wired() -> None:
    analysis = _report()["enforcement_analysis"]

    assert analysis["policy_defined"] is True
    assert analysis["artifact_standard_defined"] is True
    assert analysis["runtime_enforcement_defined"] is False
    assert analysis["execution_summary_artifact_runtime_references_found"] is False
    assert analysis["execution_authorization_requires_execution_summary"] is False
    assert analysis["summary_bound_human_confirmation_required"] is False
    assert analysis["missing_summary_fails_closed"] is False


def test_required_repairs_identify_central_gate_and_negative_tests() -> None:
    report = _report()
    repairs = {repair["repair_id"]: repair for repair in report["required_repairs"]}

    assert "EXECUTION_SUMMARY_RUNTIME_V1" in repairs
    assert "SUMMARY_BOUND_HUMAN_CONFIRMATION_V1" in repairs
    assert "EXECUTION_AUTHORIZATION_SUMMARY_GATE_V1" in repairs
    assert "DOWNSTREAM_SUMMARY_LINEAGE_COMPATIBILITY_V1" in repairs
    assert "MISSING_SUMMARY_FAIL_CLOSED_TESTS_V1" in repairs
    assert any("EXECUTION_AUTHORIZATION_ARTIFACT_V1" in item for item in report["missing_coverage"])
    assert any("FAIL_CLOSED" in item for item in report["missing_coverage"])


def test_final_fields_reflect_incomplete_enforcement() -> None:
    assert _report()["final_fields"] == FINAL_FIELDS
