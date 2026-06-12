"""Checks for CODEX_DEPENDENCY_REDUCTION_REPORT_V1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / ".github/governance/review/CODEX_DEPENDENCY_REDUCTION_REPORT_V1.json"


def _load() -> dict:
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_codex_dependency_report_quantifies_capability_breakdown() -> None:
    report = _load()
    breakdown = report["quantified_breakdown"]

    assert report["artifact_type"] == "CODEX_DEPENDENCY_REDUCTION_REPORT_V1"
    assert breakdown["total_capabilities_analyzed"] == 20
    assert breakdown["aigol_only_capabilities"] == 12
    assert breakdown["partial_autonomy_capabilities"] == 4
    assert breakdown["codex_required_capabilities"] == 4
    assert breakdown["aigol_only_percent"] == 60.0
    assert breakdown["partial_autonomy_percent"] == 20.0
    assert breakdown["codex_required_percent"] == 20.0


def test_codex_dependency_report_classifications_match_capabilities() -> None:
    report = _load()
    capabilities = report["capability_breakdown"]
    classifications = [item["classification"] for item in capabilities]

    assert len(capabilities) == 20
    assert classifications.count("AIGOL_ONLY") == 12
    assert classifications.count("AIGOL_PLUS_CODEX") == 4
    assert classifications.count("CODEX_REQUIRED") == 4


def test_codex_dependency_report_scores_activity_areas() -> None:
    report = _load()
    areas = report["activity_area_breakdown"]

    assert areas["implementation_requests"]["area_autonomy_score"] == 37.5
    assert areas["worker_requests"]["area_autonomy_score"] == 100.0
    assert areas["governance_decisions"]["area_autonomy_score"] == 58.3
    assert areas["validation_activities"]["area_autonomy_score"] == 80.0
    assert areas["replay_activities"]["area_autonomy_score"] == 100.0
    assert report["autonomy_estimates"]["autonomy_score"] == 70.0
    assert report["autonomy_estimates"]["implementation_autonomy_level"] == "LOW"
    assert report["autonomy_estimates"]["remaining_codex_dependency"] == "MEDIUM_HIGH"


def test_codex_dependency_report_preserves_non_goals() -> None:
    report = _load()
    non_goals = " ".join(report["non_goals"])

    assert "Do not claim AiGOL can autonomously mutate repository code." in non_goals
    assert "Do not remove Codex from implementation execution" in non_goals
    assert "Do not remove human approval gates." in non_goals
    assert "Do not hide partial governance conformance drift." in non_goals


def test_codex_dependency_report_final_outputs() -> None:
    report = _load()
    outputs = report["final_outputs"]

    assert outputs["AIGOL_ONLY_CAPABILITIES"] == "12_OF_20"
    assert outputs["PARTIAL_AUTONOMY_CAPABILITIES"] == "4_OF_20"
    assert outputs["CODEX_REQUIRED_CAPABILITIES"] == "4_OF_20"
    assert outputs["AUTONOMY_SCORE"] == "70.0"
