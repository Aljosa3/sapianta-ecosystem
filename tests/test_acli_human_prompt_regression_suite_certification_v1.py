"""Tests for AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_CERTIFICATION_V1."""

from __future__ import annotations

from aigol.runtime.acli_human_prompt_regression_suite_certification_runtime import (
    AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_CERTIFICATION_VERSION,
    REQUIRED_COVERAGE,
    reconstruct_acli_lifecycle_regression_certification,
    run_acli_lifecycle_regression_certification,
)
from aigol.runtime.acli_human_prompt_regression_suite_runtime import (
    REGRESSION_CERTIFICATION_ARTIFACT_V1,
    REGRESSION_RUN_ARTIFACT_V1,
)
from aigol.runtime.transport.serialization import load_json


CREATED_AT = "2026-06-12T00:00:00Z"


def test_acli_human_prompt_regression_suite_certifies_complete_lifecycle(tmp_path) -> None:
    result = run_acli_lifecycle_regression_certification(
        run_id="ACLI-LIFECYCLE-REGRESSION-CERTIFICATION-000001",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "regression_certification",
        workspace=tmp_path,
        domains=("FreshDomain", "PilotDomain"),
        auto_continue=True,
    )
    run_artifact = result["regression_run_artifact"]
    certification = result["regression_certification_artifact"]
    reconstructed = reconstruct_acli_lifecycle_regression_certification(
        tmp_path
        / "regression_certification"
        / "ACLI-LIFECYCLE-REGRESSION-CERTIFICATION-000001"
    )

    assert result["runtime_version"] == AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_CERTIFICATION_VERSION
    assert run_artifact["artifact_type"] == REGRESSION_RUN_ARTIFACT_V1
    assert certification["artifact_type"] == REGRESSION_CERTIFICATION_ARTIFACT_V1
    assert run_artifact["total_tests"] == 2
    assert run_artifact["total_prompts"] == 28
    assert run_artifact["passed_tests"] == 2
    assert run_artifact["failed_tests"] == 0
    assert run_artifact["termination_rate"] == 1.0
    assert run_artifact["fail_closed_rate"] == 0.0
    assert run_artifact["replay_lineage_integrity"] is True
    assert run_artifact["gap_distribution"] == {"NO_GAPS": 2}
    assert all(run_artifact["coverage"][item] is True for item in REQUIRED_COVERAGE)
    assert certification["certification_status"] == "CERTIFIED"
    assert certification["minimum_prompt_requirement_met"] is True
    assert certification["replay_lineage_preserved"] is True
    assert certification["no_lifecycle_regressions"] is True
    assert certification["production_readiness_score"] == 100.0
    assert certification["execution_statistics"]["termination_rate"] == 1.0
    assert certification["execution_statistics"]["fail_closed_rate"] == 0.0
    assert result["regression_suite_certified"] is True
    assert result["production_readiness_score"] == 100.0
    assert result["termination_rate"] == 1.0
    assert result["fail_closed_rate"] == 0.0
    assert reconstructed["run_artifact"]["artifact_hash"] == run_artifact["artifact_hash"]
    assert reconstructed["certification_artifact"]["artifact_hash"] == certification["artifact_hash"]


def test_acli_human_prompt_regression_suite_certification_artifacts_persist(tmp_path) -> None:
    run_acli_lifecycle_regression_certification(
        run_id="ACLI-LIFECYCLE-REGRESSION-CERTIFICATION-PERSISTED",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "regression_certification",
        workspace=tmp_path,
    )
    run_root = (
        tmp_path
        / "regression_certification"
        / "ACLI-LIFECYCLE-REGRESSION-CERTIFICATION-PERSISTED"
    )
    run_artifact = load_json(run_root / "REGRESSION_RUN_ARTIFACT_V1.json")
    certification = load_json(run_root / "REGRESSION_CERTIFICATION_ARTIFACT_V1.json")

    assert run_artifact["artifact_type"] == REGRESSION_RUN_ARTIFACT_V1
    assert certification["artifact_type"] == REGRESSION_CERTIFICATION_ARTIFACT_V1
    assert certification["regression_run_hash"] == run_artifact["artifact_hash"]
