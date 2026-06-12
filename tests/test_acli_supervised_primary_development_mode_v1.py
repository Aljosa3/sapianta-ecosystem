"""Checks for AIGOL_SUPERVISED_PRIMARY_DEVELOPMENT_MODE_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.runtime.acli_human_prompt_regression_suite_runtime import (
    reconstruct_acli_human_prompt_regression_suite,
    run_acli_human_prompt_regression_suite,
)
from aigol.runtime.transport.serialization import load_json


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / ".github/governance/review/ACLI_SUPERVISED_PRIMARY_DEVELOPMENT_MODE_REPORT_V1.json"
CREATED_AT = "2026-06-12T00:00:00Z"


SELECTED_MILESTONE_PROMPTS = [
    "Create a new governed domain called ValidationCommandRunner.",
    "Create a new governed domain called RepositoryMutationWorker.",
    "Create a new governed domain called AutonomousDevelopmentFlow.",
    "Create a new governed domain called ACLIPrimaryDevelopmentMode.",
]


def test_acli_primary_mode_executes_selected_milestone_prompts(tmp_path) -> None:
    result = run_acli_human_prompt_regression_suite(
        prompts=SELECTED_MILESTONE_PROMPTS,
        run_id="ACLI-SUPERVISED-PRIMARY-DEVELOPMENT-MODE-000001",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "acli_primary_mode",
        workspace=tmp_path,
        auto_continue=True,
        max_lifecycle_depth=32,
    )
    run_artifact = result["regression_run_artifact"]
    certification = result["regression_certification_artifact"]
    reconstructed = reconstruct_acli_human_prompt_regression_suite(
        tmp_path
        / "acli_primary_mode"
        / "ACLI-SUPERVISED-PRIMARY-DEVELOPMENT-MODE-000001"
    )

    assert run_artifact["total_tests"] == 4
    assert len(result["test_evidence"]) == 4
    assert certification["certification_status"] == "CERTIFIED"
    assert certification["replay_lineage_preserved"] is True
    assert certification["determinism_preserved"] is True
    assert certification["fail_closed_preserved"] is True
    assert reconstructed["replay_lineage_preserved"] is True
    assert all(item["replay_lineage_preserved"] is True for item in result["test_evidence"])
    assert all(item["governance_constraints"]["code_modified"] is False for item in result["test_evidence"])
    assert all(item["governance_constraints"]["repair_invoked"] is False for item in result["test_evidence"])
    assert all(item["governance_constraints"]["provider_fix_invoked"] is False for item in result["test_evidence"])
    assert all(item["governance_constraints"]["worker_remediation_invoked"] is False for item in result["test_evidence"])


def test_acli_primary_mode_report_selects_four_real_milestones() -> None:
    report = load_json(REPORT)
    milestones = report["selected_real_sapianta_milestones"]

    assert report["artifact_type"] == "ACLI_SUPERVISED_PRIMARY_DEVELOPMENT_MODE_REPORT_V1"
    assert report["adoption_mode"] == "ACLI_FIRST_SUPERVISED_PRIMARY_DEVELOPMENT"
    assert len(milestones) == 4
    assert [item["milestone_id"] for item in milestones] == [
        "AIGOL_VALIDATION_COMMAND_RUNNER_RUNTIME_V1",
        "AIGOL_REPOSITORY_MUTATION_WORKER_RUNTIME_V1",
        "AIGOL_GOVERNED_AUTONOMOUS_DEVELOPMENT_FLOW_V1",
        "AIGOL_SUPERVISED_PRIMARY_DEVELOPMENT_MODE_V1",
    ]
    assert report["acli_first_execution"]["entrypoint"] == "AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_V1"
    assert report["acli_first_execution"]["prompt_count"] == 4
    assert report["acli_first_execution"]["new_governance_primitives_introduced"] is False


def test_acli_primary_mode_report_records_measured_benefits() -> None:
    report = load_json(REPORT)
    comparison = report["measured_operational_comparison"]
    outputs = report["final_outputs"]

    assert comparison["operator_actions"]["historical_copy_paste_actions"] == 28
    assert comparison["operator_actions"]["acli_first_actions"] == 20
    assert comparison["operator_actions"]["actions_reduced"] == 8
    assert comparison["operator_actions"]["operator_effort_reduction_measured"] is True
    assert comparison["token_consumption_proxy"]["historical_copy_paste_proxy_tokens"] == 4200
    assert comparison["token_consumption_proxy"]["acli_first_proxy_tokens"] == 3100
    assert comparison["token_consumption_proxy"]["token_reduction_measured"] is True
    assert comparison["token_consumption_proxy"]["billable_token_claim"] is False
    assert comparison["development_cycle_time"]["development_speed_improvement"] is True
    assert report["integrity_results"]["replay_integrity"] is True
    assert report["integrity_results"]["governance_integrity"] is True
    assert report["integrity_results"]["validation_success"] is True
    assert report["integrity_results"]["repository_mutation_success"] is True
    assert outputs["ACLI_PRIMARY_MODE_PASSED"] == "YES"
    assert outputs["TOKEN_REDUCTION_MEASURED"] == "YES_PROXY_26.2_PERCENT"
    assert outputs["OPERATOR_EFFORT_REDUCTION_MEASURED"] == "YES_8_ACTIONS_OR_28.6_PERCENT"
    assert outputs["DEVELOPMENT_SPEED_IMPROVEMENT"] == "YES_33.3_PERCENT_PROXY"
    assert outputs["READY_FOR_ACLI_FIRST_DEVELOPMENT"] == "YES_SUPERVISED_SELECTED_MILESTONES"


def test_acli_primary_mode_keeps_baseline_limits_visible() -> None:
    report = load_json(REPORT)
    method = report["measurement_method"]
    limits = " ".join(report["historical_baseline_limits"])

    assert method["billable_provider_telemetry_available"] is False
    assert method["wall_clock_telemetry_available"] is False
    assert "not provider billable telemetry" in limits
    assert "not wall-clock telemetry" in limits
    assert "supervised" in report["adoption_decision"]["mode"].lower()
