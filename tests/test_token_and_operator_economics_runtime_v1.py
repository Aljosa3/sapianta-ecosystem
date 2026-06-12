"""Tests for AIGOL_TOKEN_AND_OPERATOR_ECONOMICS_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.token_and_operator_economics_runtime import (
    ECONOMICS_MEASUREMENT_COMPLETED,
    ECONOMICS_REPORT_V1,
    generate_token_and_operator_economics_report,
    reconstruct_token_and_operator_economics_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize


GENERATED_AT = "2026-06-12T00:00:00Z"


def _economics_capture(tmp_path):
    return generate_token_and_operator_economics_report(
        report_id="AIGOL_TOKEN_AND_OPERATOR_ECONOMICS_RUNTIME_V1",
        generated_at=GENERATED_AT,
        human_prompts=[
            "AIGOL_PRODUCTION_GOVERNANCE_READINESS_V1",
            "AIGOL_SUPERVISED_PRODUCTION_ADOPTION_V1",
        ],
        aigol_governance_actions=[
            "Review certified runtimes",
            "Review ACLI regression certification",
            "Run governance conformance evidence",
            "Generate supervised adoption report",
        ],
        codex_requests=[
            "Create production governance readiness report and guard tests",
            "Create supervised production adoption report and guard tests",
        ],
        replay_artifacts=[
            ".github/governance/review/PRODUCTION_GOVERNANCE_READINESS_REPORT_V1.json",
            ".github/governance/review/SUPERVISED_PRODUCTION_ADOPTION_REPORT_V1.json",
        ],
        certification_artifacts=[
            "REGRESSION_CERTIFICATION_ARTIFACT_V1",
            "REPLAY_CERTIFICATION_ARTIFACT_V1",
        ],
        approval_actions=[
            "Human approved supervised production adoption milestone",
        ],
        baseline_chatgpt_actions=[
            "Discuss readiness and adoption scope with ChatGPT",
        ],
        replay_dir=tmp_path / "economics",
    )


def test_economics_runtime_generates_report_with_measurable_proxy_evidence(tmp_path) -> None:
    capture = _economics_capture(tmp_path)
    report = capture["economics_report"]
    reconstructed = reconstruct_token_and_operator_economics_replay(tmp_path / "economics")

    assert capture["measurement_status"] == ECONOMICS_MEASUREMENT_COMPLETED
    assert capture["token_impact_measured"] is True
    assert capture["operator_effort_measured"] is True
    assert capture["governance_overhead_measured"] is True
    assert capture["roi_estimate_available"] is True
    assert capture["billable_roi_available"] is False
    assert report["artifact_type"] == ECONOMICS_REPORT_V1
    assert report["estimated_token_consumption"]["baseline_estimated_tokens"] > 0
    assert report["estimated_token_consumption"]["aigol_estimated_tokens"] > 0
    assert isinstance(report["estimated_token_consumption"]["delta_estimated_tokens"], int)
    assert report["operator_effort"]["approval_actions"] == 1
    assert report["governance_overhead"]["overhead_actions"] == 9
    assert report["governance_overhead"]["overhead_classification"] == "MODERATE"
    assert report["roi_estimate"]["roi_estimate_type"] == "DETERMINISTIC_PROXY_ESTIMATE"
    assert report["replay_lineage_preserved"] is True
    assert report["fail_closed_preserved"] is True
    assert report["provider_invoked"] is False
    assert report["worker_invoked"] is False
    assert report["code_modified"] is False
    assert report["governance_modified"] is False
    assert reconstructed["measurement_status"] == ECONOMICS_MEASUREMENT_COMPLETED
    assert reconstructed["token_impact_measured"] is True
    assert reconstructed["operator_effort_measured"] is True
    assert reconstructed["governance_overhead_measured"] is True
    assert reconstructed["roi_estimate_available"] is True


def test_economics_runtime_supports_cost_reduction_optimized_accounting(tmp_path) -> None:
    capture = generate_token_and_operator_economics_report(
        report_id="AIGOL_GOVERNANCE_COST_REDUCTION_IMPLEMENTATION_V1",
        generated_at=GENERATED_AT,
        human_prompts=[
            "AIGOL_PRODUCTION_GOVERNANCE_READINESS_V1",
            "AIGOL_SUPERVISED_PRODUCTION_ADOPTION_V1",
            "AIGOL_TOKEN_AND_OPERATOR_ECONOMICS_RUNTIME_V1",
        ],
        aigol_governance_actions=[
            "Review certified runtime and certification ledger",
            "Review ACLI regression certification",
            "Record economics measurement inputs",
            "Generate deterministic economics report",
        ],
        codex_requests=[
            "Create production governance readiness report and guard tests",
            "Create supervised production adoption report and guard tests",
            "Create token and operator economics runtime and tests",
        ],
        replay_artifacts=[
            ".github/governance/review/PRODUCTION_GOVERNANCE_READINESS_REPORT_V1.json",
            ".github/governance/review/SUPERVISED_PRODUCTION_ADOPTION_REPORT_V1.json",
        ],
        certification_artifacts=[
            "REGRESSION_CERTIFICATION_ARTIFACT_V1",
            "REPLAY_CERTIFICATION_ARTIFACT_V1",
        ],
        approval_actions=[
            "Human approved supervised production adoption milestone",
        ],
        baseline_chatgpt_actions=[
            "Discuss readiness and adoption scope with ChatGPT",
            "Request Codex implementation guidance through ChatGPT",
        ],
        replay_dir=tmp_path / "optimized",
        validation_artifacts=[
            "tests/test_token_and_operator_economics_runtime_v1.py",
        ],
        measurement_prompt_authorized=True,
    )
    report = capture["economics_report"]

    assert report["governance_overhead"]["aigol_governance_actions"] == 4
    assert report["governance_overhead"]["approval_actions"] == 1
    assert report["governance_overhead"]["replay_artifacts"] == 2
    assert report["governance_overhead"]["certification_artifacts"] == 2
    assert report["governance_overhead"]["overhead_actions"] == 9
    assert report["governance_overhead"]["validation_artifacts_recorded_outside_replay_overhead"] == 1
    assert report["governance_overhead"]["measurement_prompt_authorized"] is True
    assert report["operator_effort"]["aigol_operator_actions"] == 7
    assert report["final_outputs"]["TOKEN_IMPACT_MEASURED"] is True
    assert report["replay_lineage_preserved"] is True
    assert report["fail_closed_preserved"] is True


def test_economics_runtime_fails_closed_without_human_prompts(tmp_path) -> None:
    capture = generate_token_and_operator_economics_report(
        report_id="AIGOL_TOKEN_AND_OPERATOR_ECONOMICS_RUNTIME_EMPTY",
        generated_at=GENERATED_AT,
        human_prompts=[],
        aigol_governance_actions=["Review certified runtimes"],
        codex_requests=["Create report"],
        replay_artifacts=["SUPERVISED_PRODUCTION_ADOPTION_REPORT_V1.json"],
        certification_artifacts=["REPLAY_CERTIFICATION_ARTIFACT_V1"],
        approval_actions=["Human approved scope"],
        baseline_chatgpt_actions=["Discuss scope with ChatGPT"],
        replay_dir=tmp_path / "failed",
    )

    assert capture["measurement_status"] == "FAILED_CLOSED"
    assert capture["token_impact_measured"] is False
    assert capture["operator_effort_measured"] is False
    assert capture["governance_overhead_measured"] is False
    assert capture["roi_estimate_available"] is False
    assert capture["fail_closed_preserved"] is True
    assert "human_prompts requires at least one item" in capture["failure_reason"]


def test_economics_reconstruction_detects_corrupt_replay(tmp_path) -> None:
    _economics_capture(tmp_path)
    path = tmp_path / "economics" / "001_economics_report_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["provider_invoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_token_and_operator_economics_replay(tmp_path / "economics")


def test_economics_runtime_has_no_provider_worker_or_mutation_surfaces() -> None:
    import aigol.runtime.token_and_operator_economics_runtime as runtime

    source = inspect.getsource(runtime)

    assert "invoke_worker(" not in source
    assert "execute_worker(" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "modify_governance(" not in source
    assert "modify_code(" not in source
    assert "subprocess." not in source
    assert "os.system" not in source
