"""Checks for GOVERNANCE_COST_REDUCTION_IMPLEMENTATION_REPORT_V1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / ".github/governance/review/GOVERNANCE_COST_REDUCTION_IMPLEMENTATION_REPORT_V1.json"


def _load() -> dict:
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_implementation_report_records_all_three_optimizations() -> None:
    report = _load()
    optimizations = {item["optimization_id"] for item in report["implemented_optimizations"]}

    assert report["artifact_type"] == "GOVERNANCE_COST_REDUCTION_IMPLEMENTATION_REPORT_V1"
    assert optimizations == {"GOV-COST-OPT-001", "GOV-COST-OPT-002", "GOV-COST-OPT-003"}
    assert all(item["governance_guarantee_preserved"] is True for item in report["implemented_optimizations"])


def test_implementation_report_measures_reduced_overhead() -> None:
    report = _load()
    measurement = report["before_after_measurement"]

    assert measurement["governance_action_count"] == {"before": 5, "after": 4, "delta": -1}
    assert measurement["approval_action_count"] == {"before": 2, "after": 1, "delta": -1}
    assert measurement["replay_artifact_count"] == {"before": 3, "after": 2, "delta": -1}
    assert measurement["total_overhead_actions"]["before"] == 12
    assert measurement["total_overhead_actions"]["after"] == 9
    assert measurement["total_overhead_actions"]["reduction_percent"] == 25.0
    assert measurement["operator_actions"]["delta"] == -1
    assert measurement["aigol_estimated_proxy_tokens"]["delta"] == -73
    assert measurement["overhead_estimated_proxy_tokens"]["delta"] == -73
    assert measurement["overhead_classification"] == {"before": "HIGH", "after": "MODERATE"}


def test_implementation_report_preserves_governance_guarantees() -> None:
    report = _load()
    guarantees = report["governance_guarantee_preservation"]
    acceptance = report["acceptance"]

    assert guarantees["replay_lineage_preserved"] is True
    assert guarantees["fail_closed_behavior_preserved"] is True
    assert guarantees["certification_guarantees_preserved"] is True
    assert guarantees["human_authority_preserved"] is True
    assert guarantees["regression_certification_preserved"] is True
    assert guarantees["replay_certification_preserved"] is True
    assert guarantees["governance_modified"] is False
    assert acceptance["governance_guarantees_remain_unchanged"] is True
    assert acceptance["measured_governance_overhead_decreases"] is True


def test_implementation_report_final_outputs() -> None:
    report = _load()
    outputs = report["final_outputs"]

    assert outputs["TOKEN_REDUCTION_REALIZED"] == (
        "73_ESTIMATED_PROXY_TOKENS_OR_8.6_PERCENT_OF_AIGOL_PROXY_TOKENS"
    )
    assert outputs["OPERATOR_ACTION_REDUCTION_REALIZED"] == "1_OPERATOR_ACTION_OR_12.5_PERCENT"
    assert outputs["APPROVAL_REDUCTION_REALIZED"] == "1_APPROVAL_ACTION_OR_50.0_PERCENT"
    assert outputs["GOVERNANCE_GUARANTEES_PRESERVED"] == "YES"
