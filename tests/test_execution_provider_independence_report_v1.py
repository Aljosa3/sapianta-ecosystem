"""Checks for EXECUTION_PROVIDER_INDEPENDENCE_REPORT_V1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / ".github/governance/review/EXECUTION_PROVIDER_INDEPENDENCE_REPORT_V1.json"


def _load() -> dict:
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_provider_independence_report_reclassifies_all_codex_required_capabilities() -> None:
    report = _load()
    totals = report["reclassification_totals"]

    assert report["artifact_type"] == "EXECUTION_PROVIDER_INDEPENDENCE_REPORT_V1"
    assert totals["analyzed_codex_required_capabilities"] == 4
    assert totals["generic_cognition_provider_capabilities"] == 3
    assert totals["generic_execution_worker_capabilities"] == 3
    assert totals["codex_specific_capabilities"] == 0
    assert totals["human_authority_required_capabilities"] == 3
    assert totals["provider_replaceable_capabilities"] == 4


def test_provider_independence_report_marks_no_capability_as_codex_specific() -> None:
    report = _load()
    capabilities = report["reclassified_capabilities"]

    assert len(capabilities) == 4
    assert all(item["codex_specific"] is False for item in capabilities)
    assert {item["primary_reclassification"] for item in capabilities} == {
        "GENERIC_EXECUTION_WORKER",
        "GENERIC_COGNITION_PROVIDER",
        "HUMAN_AUTHORITY_REQUIRED",
    }


def test_provider_replacement_matrix_quantifies_openai_and_local_model_readiness() -> None:
    report = _load()
    matrix = {item["provider"]: item for item in report["provider_replacement_matrix"]}

    assert matrix["OpenAI API"]["replaceable_capabilities"] == 4
    assert matrix["OpenAI API"]["readiness_score"] == 75
    assert matrix["OpenAI API"]["replacement_readiness"] == "HIGH_WITH_GOVERNED_EXECUTION_WORKER"
    assert matrix["Local Mistral + Worker"]["replaceable_capabilities"] == 4
    assert matrix["Local Mistral + Worker"]["readiness_score"] == 70
    assert matrix["Claude Code"]["readiness_score"] == 90


def test_provider_independence_report_quantifies_independence_scores() -> None:
    report = _load()
    scores = report["quantified_independence"]

    assert scores["provider_independence_score"] == 100.0
    assert scores["execution_independence_score"] == 75.0
    assert scores["local_model_feasibility_score"] == 70.0
    assert scores["openai_replacement_readiness_score"] == 75.0
    assert scores["codex_specific_dependency_percent"] == 0.0


def test_provider_independence_report_preserves_governance_non_goals() -> None:
    report = _load()
    non_goals = " ".join(report["non_goals"])
    interpretation = report["interpretation"]

    assert "Do not claim provider substitution authorizes autonomous repository mutation." in non_goals
    assert "Do not remove human approval gates." in non_goals
    assert "task-specific certification" in non_goals
    assert "certified generic execution worker" in interpretation["blocking_condition"]


def test_provider_independence_report_final_outputs() -> None:
    report = _load()
    outputs = report["final_outputs"]

    assert outputs["GENERIC_PROVIDER_CAPABILITIES"] == "3_OF_4"
    assert outputs["CODEX_SPECIFIC_CAPABILITIES"] == "0_OF_4"
    assert outputs["LOCAL_MISTRAL_FEASIBLE_CAPABILITIES"] == (
        "4_OF_4_WITH_GOVERNED_WORKER_AND_CERTIFICATION"
    )
    assert outputs["OPENAI_REPLACEMENT_READINESS"] == "75.0_HIGH_WITH_GOVERNED_EXECUTION_WORKER"
    assert outputs["PROVIDER_INDEPENDENCE_SCORE"] == "100.0"
