"""Tests for AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_V1."""

from __future__ import annotations

from aigol.runtime.acli_human_prompt_regression_suite_runtime import (
    AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_VERSION,
    CLARIFICATION_STALL,
    REGRESSION_CERTIFICATION_ARTIFACT_V1,
    REGRESSION_RUN_ARTIFACT_V1,
    WAITING_FOR_OPERATOR,
    load_prompt_corpus,
    reconstruct_acli_human_prompt_regression_suite,
    run_acli_human_prompt_regression_suite,
)
from aigol.runtime.transport.serialization import load_json


CREATED_AT = "2026-06-11T00:00:00Z"
FRESHDOMAIN_PROMPT = "Create a new governed domain called FreshDomain."


def test_plain_text_prompt_corpus_loads_deterministically(tmp_path) -> None:
    corpus = tmp_path / "prompts.txt"
    corpus.write_text(
        "\n".join(
            [
                "",
                FRESHDOMAIN_PROMPT,
                "Show latest replay chain.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    cases = load_prompt_corpus(corpus)

    assert cases == [
        {"prompt_id": "PROMPT-000001", "prompt_text": FRESHDOMAIN_PROMPT},
        {"prompt_id": "PROMPT-000002", "prompt_text": "Show latest replay chain."},
    ]


def test_regression_suite_executes_prompt_corpus_and_generates_artifacts(tmp_path) -> None:
    result = run_acli_human_prompt_regression_suite(
        prompts=[FRESHDOMAIN_PROMPT],
        run_id="REGRESSION-RUN-000001",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "regression_runtime",
        workspace=tmp_path,
        auto_continue=True,
        max_lifecycle_depth=32,
    )
    run_artifact = result["regression_run_artifact"]
    certification = result["regression_certification_artifact"]
    evidence = result["test_evidence"][0]
    reconstructed = reconstruct_acli_human_prompt_regression_suite(
        tmp_path / "regression_runtime" / "REGRESSION-RUN-000001"
    )

    assert result["runtime_version"] == AIGOL_ACLI_HUMAN_PROMPT_REGRESSION_SUITE_VERSION
    assert evidence["session_id"] == "REGRESSION-RUN-000001-TEST-000001"
    assert evidence["prompt_id"] == "PROMPT-000001"
    assert evidence["prompt_text_hash"].startswith("sha256:")
    assert evidence["detected_workflow"] == "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION"
    assert evidence["final_lifecycle_stage"] == WAITING_FOR_OPERATOR
    assert evidence["failure_classification"] == CLARIFICATION_STALL
    assert evidence["replay_lineage_preserved"] is True
    assert evidence["governance_constraints"]["repair_invoked"] is False
    assert evidence["governance_constraints"]["ppp_invoked"] is False
    assert evidence["governance_constraints"]["provider_fix_invoked"] is False
    assert evidence["governance_constraints"]["worker_remediation_invoked"] is False
    assert evidence["governance_constraints"]["improvement_intent_created"] is False

    assert run_artifact["artifact_type"] == REGRESSION_RUN_ARTIFACT_V1
    assert run_artifact["total_tests"] == 1
    assert run_artifact["passed_tests"] == 0
    assert run_artifact["failed_tests"] == 0
    assert run_artifact["waiting_tests"] == 1
    assert run_artifact["termination_rate"] == 0.0
    assert run_artifact["fail_closed_rate"] == 0.0
    assert run_artifact["average_lifecycle_depth"] == 1.0
    assert run_artifact["workflow_distribution"] == {"CREATE_DOMAIN_COMPLIANCE_CLARIFICATION": 1}

    assert certification["artifact_type"] == REGRESSION_CERTIFICATION_ARTIFACT_V1
    assert certification["certification_status"] == "CERTIFIED"
    assert certification["execution_statistics"]["waiting_tests"] == 1
    assert certification["replay_lineage_preserved"] is True
    assert certification["determinism_preserved"] is True
    assert certification["fail_closed_preserved"] is True
    assert reconstructed["run_artifact"]["artifact_hash"] == run_artifact["artifact_hash"]
    assert reconstructed["certification_artifact"]["artifact_hash"] == certification["artifact_hash"]

    persisted_run = load_json(
        tmp_path
        / "regression_runtime"
        / "REGRESSION-RUN-000001"
        / "REGRESSION_RUN_ARTIFACT_V1.json"
    )
    persisted_certification = load_json(
        tmp_path
        / "regression_runtime"
        / "REGRESSION-RUN-000001"
        / "REGRESSION_CERTIFICATION_ARTIFACT_V1.json"
    )
    assert persisted_run["artifact_hash"] == run_artifact["artifact_hash"]
    assert persisted_certification["artifact_hash"] == certification["artifact_hash"]


def test_regression_suite_preserves_isolated_sessions_for_each_prompt(tmp_path) -> None:
    result = run_acli_human_prompt_regression_suite(
        prompts=[FRESHDOMAIN_PROMPT, "Create a new governed domain called FreshDomain."],
        run_id="REGRESSION-RUN-ISOLATION-000001",
        created_at=CREATED_AT,
        runtime_root=tmp_path / "regression_runtime",
        workspace=tmp_path,
    )
    evidence = result["test_evidence"]

    assert [item["session_id"] for item in evidence] == [
        "REGRESSION-RUN-ISOLATION-000001-TEST-000001",
        "REGRESSION-RUN-ISOLATION-000001-TEST-000002",
    ]
    assert evidence[0]["replay_references"] != evidence[1]["replay_references"]
    assert all(item["replay_lineage_preserved"] is True for item in evidence)
