"""Checks for PRODUCTION_GOVERNANCE_READINESS_REPORT_V1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / ".github/governance/review/PRODUCTION_GOVERNANCE_READINESS_REPORT_V1.json"


def _load() -> dict:
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_production_governance_readiness_report_declares_conditional_readiness() -> None:
    report = _load()
    outputs = report["final_outputs"]

    assert report["artifact_type"] == "PRODUCTION_GOVERNANCE_READINESS_REPORT_V1"
    assert report["readiness_decision"] == "CONDITIONALLY_READY_FOR_SUPERVISED_PRIMARY_GOVERNANCE"
    assert report["readiness_score"] == 86.0
    assert outputs["PRODUCTION_GOVERNANCE_READY"] == "YES_CONDITIONAL"
    assert outputs["CODEX_DEPENDENCY_LEVEL"] == "HIGH"
    assert outputs["RECOMMENDED_ADOPTION_MODE"] == "SUPERVISED_PRIMARY_GOVERNANCE_WITH_CODEX_IMPLEMENTATION"


def test_production_governance_readiness_report_keeps_remaining_blockers_visible() -> None:
    report = _load()
    blockers = report["final_outputs"]["REMAINING_BLOCKERS"]
    conformance_gap = report["remaining_gaps"][0]

    assert blockers["supervised_primary_governance"] == 0
    assert blockers["full_unsupervised_or_autonomous_governance"] == 2
    assert conformance_gap["severity"] == "HIGH"
    assert conformance_gap["blocks_unsupervised_production"] is True
    assert report["readiness_score_basis"]["governance_conformance_status"] == "PARTIALLY_CONFORMANT"
    assert report["remaining_codex_dependencies"]["dependency_level"] == "HIGH"


def test_production_governance_readiness_report_references_acli_certification_evidence() -> None:
    report = _load()
    acli = report["review_scope"]["acli_regression_certification"]

    assert acli["prompts_executed"] == 28
    assert acli["termination_rate"] == 1.0
    assert acli["fail_closed_rate"] == 0.0
    assert acli["replay_lineage_integrity"] is True
    assert acli["no_lifecycle_regressions"] is True
