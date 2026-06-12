"""Checks for SUPERVISED_PRODUCTION_ADOPTION_REPORT_V1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / ".github/governance/review/SUPERVISED_PRODUCTION_ADOPTION_REPORT_V1.json"


def _load() -> dict:
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_supervised_production_adoption_report_records_selected_real_milestone() -> None:
    report = _load()
    milestone = report["selected_real_development_milestone"]

    assert report["artifact_type"] == "SUPERVISED_PRODUCTION_ADOPTION_REPORT_V1"
    assert milestone["milestone_id"] == "AIGOL_PRODUCTION_GOVERNANCE_READINESS_V1"
    assert milestone["primary_artifact"] == ".github/governance/review/PRODUCTION_GOVERNANCE_READINESS_REPORT_V1.json"
    assert report["supervised_route"]["codex"]["codex_remains_required_for_repository_mutation"] is True


def test_supervised_production_adoption_report_keeps_measurement_limits_visible() -> None:
    report = _load()
    token = report["captured_evidence"]["token_consumption"]

    assert token["codex_session_token_telemetry_available"] is False
    assert token["aigol_runtime_token_metering_available"] is False
    assert token["token_reduction"] == "NOT_MEASURED"
    assert report["adoption_metrics"]["token_reduction"]["classification"] == "NOT_MEASURED"


def test_supervised_production_adoption_report_final_outputs_are_bounded() -> None:
    report = _load()
    outputs = report["final_outputs"]
    decision = report["adoption_decision"]

    assert outputs["GOVERNANCE_OVERHEAD"] == "MODERATE"
    assert outputs["TOKEN_REDUCTION"] == "NOT_MEASURED"
    assert outputs["OPERATOR_EFFORT_CHANGE"] == "INCREASED_MODERATELY"
    assert outputs["RECOMMENDED_ADOPTION_EXPANSION"] == "YES_LIMITED_SUPERVISED_MILESTONES"
    assert decision["recommended"] is True
    assert decision["mode"] == "LIMITED_SUPERVISED_EXPANSION"
    assert "unsupervised" in report["adoption_metrics"]["recommended_adoption_expansion"]["excluded_scope"]
