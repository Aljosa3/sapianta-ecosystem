"""Checks for GOVERNANCE_COST_REDUCTION_REPORT_V1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / ".github/governance/review/GOVERNANCE_COST_REDUCTION_REPORT_V1.json"


def _load() -> dict:
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_cost_reduction_report_quantifies_reducible_overhead() -> None:
    report = _load()
    baseline = report["baseline_overhead"]
    opportunities = report["quantified_opportunities"]

    assert report["artifact_type"] == "GOVERNANCE_COST_REDUCTION_REPORT_V1"
    assert baseline["total_overhead_actions"] == 12
    assert baseline["overhead_estimated_tokens"] == 561
    assert opportunities["reducible_actions"] == 3
    assert opportunities["overhead_action_reduction_percent"] == 25.0
    assert opportunities["scaled_overhead_token_reduction_estimate"] == 132
    assert opportunities["scaled_overhead_token_reduction_percent"] == 23.5
    assert opportunities["operator_action_reduction"] == 1
    assert opportunities["operator_action_reduction_percent"] == 12.5


def test_cost_reduction_report_classifies_mandatory_and_reducible_actions() -> None:
    report = _load()
    summary = report["classification_summary"]
    classifications = {item["classification"] for item in report["classified_actions"]}

    assert summary["mandatory_governance"] == 8
    assert summary["optional_governance"] == 1
    assert summary["duplicated_governance"] == 1
    assert summary["redundant_governance"] == 1
    assert "MANDATORY_GOVERNANCE" in classifications
    assert "OPTIONAL_GOVERNANCE" in classifications
    assert "DUPLICATED_GOVERNANCE" in classifications
    assert "REDUNDANT_GOVERNANCE" in classifications


def test_cost_reduction_report_preserves_governance_non_goals() -> None:
    report = _load()
    non_goals = " ".join(report["non_goals"])
    guidance = report["implementation_guidance"]

    assert "Do not remove replay certification." in non_goals
    assert "Do not remove regression certification." in non_goals
    assert "Do not remove human approval" in non_goals
    assert guidance["requires_governance_change"] is False
    assert guidance["requires_human_approval"] is True
    assert guidance["recommended_mode"] == "CONSOLIDATE_AND_RECLASSIFY_ONLY"


def test_cost_reduction_report_final_outputs_are_actionable() -> None:
    report = _load()
    outputs = report["final_outputs"]

    assert outputs["REDUNDANT_ACTIONS_IDENTIFIED"] == "YES"
    assert outputs["TOKEN_REDUCTION_OPPORTUNITY"].startswith("132_ESTIMATED_PROXY_TOKENS")
    assert outputs["OPERATOR_EFFORT_REDUCTION_OPPORTUNITY"] == "1_OPERATOR_ACTION_OR_12.5_PERCENT"
    assert outputs["RECOMMENDED_OPTIMIZATIONS"] == [
        "CERTIFICATION_LEDGER_REVIEW_CONSOLIDATION",
        "PROMPT_AS_APPROVAL_MEASUREMENT_AUTHORIZATION",
        "REPLAY_ARTIFACT_SCOPE_SEPARATION",
    ]
