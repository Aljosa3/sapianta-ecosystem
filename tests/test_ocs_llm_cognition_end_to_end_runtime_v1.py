"""Tests for AIGOL_OCS_LLM_COGNITION_END_TO_END_V1."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.multi_provider_cognition_runtime import create_default_cognition_provider_contract
from aigol.runtime.ocs_llm_cognition_end_to_end_runtime import (
    CERTIFIED_CLASSIFICATION,
    FINAL_CLASSIFICATION,
    OCS_LLM_COGNITION_END_TO_END_ARTIFACT_V1,
    STATUS_COMPLETED,
    STATUS_FAILED_CLOSED,
    reconstruct_ocs_llm_cognition_end_to_end_replay,
    render_operator_visible_ocs_llm_cognition,
    render_ocs_llm_cognition_end_to_end_summary,
    run_ocs_llm_cognition_end_to_end,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-05T00:00:00Z"


def _conversation_source(source_id: str) -> dict:
    artifact = {
        "artifact_type": "HUMAN_REQUEST_ARTIFACT_V1",
        "artifact_id": source_id,
        "status": "REPLAY_VISIBLE",
        "summary": "Human asks for full OCS LLM cognition.",
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _source_context(suffix: str = "001") -> dict:
    return {
        "conversation_context": [_conversation_source(f"HUMAN-REQUEST-E2E-{suffix}")],
        "domain_context": [_conversation_source(f"DOMAIN-CONTEXT-E2E-{suffix}")],
    }


def _contracts(provider_ids: tuple[str, ...] = ("provider-a", "provider-b", "provider-c")) -> list[dict]:
    return [
        create_default_cognition_provider_contract(provider_id=provider_id, created_at=CREATED_AT)
        for provider_id in provider_ids
    ]


def _provider_text(provider_id: str) -> str:
    return json.dumps(
        {
            "findings": [
                "Shared finding: the question requires bounded human review.",
                f"{provider_id} finding differs.",
            ],
            "assumptions": [f"{provider_id} assumption differs."],
            "alternatives": [f"{provider_id} alternative differs."],
            "risks": [f"{provider_id} risk differs."],
            "uncertainties": ["Shared uncertainty: exact operating scope remains underspecified."],
            "confidence": "MEDIUM",
        },
        sort_keys=True,
    )


def _transports(failing: set[str] | None = None):
    failing = failing or set()
    transports = {}
    for provider_id in ("provider-a", "provider-b", "provider-c"):
        def call(_payload: dict, metadata: dict, provider_id: str = provider_id) -> dict:
            assert metadata["provider_role"] == "COGNITION_PROVIDER"
            if provider_id in failing:
                raise RuntimeError("provider unavailable")
            return {"output_text": _provider_text(provider_id)}

        transports[provider_id] = call
    return transports


def _single_provider_transport(response_text: str):
    def call(_payload: dict, metadata: dict) -> dict:
        assert metadata["provider_role"] == "COGNITION_PROVIDER"
        return {"output_text": response_text}

    return {"provider-a": call}


def _run(tmp_path: Path, **overrides):
    args = {
        "end_to_end_id": "OCS-LLM-COGNITION-E2E-001",
        "human_question": "What should OCS recommend for a bounded product cognition path?",
        "source_context": _source_context(),
        "provider_contracts": _contracts(),
        "transport_registry": _transports(),
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "e2e",
        "source_chain_id": "CHAIN-E2E-001",
        "source_request_reference": "HUMAN-REQUEST-E2E-001",
    }
    args.update(overrides)
    return run_ocs_llm_cognition_end_to_end(**args)


def test_end_to_end_runtime_creates_human_facing_cognition_result(tmp_path):
    result = _run(tmp_path)
    artifact = result["ocs_llm_cognition_end_to_end_artifact"]
    replay = reconstruct_ocs_llm_cognition_end_to_end_replay(tmp_path / "e2e")

    assert result["final_classification"] == FINAL_CLASSIFICATION
    assert result["classification"] == CERTIFIED_CLASSIFICATION
    assert result["final_status"] == STATUS_COMPLETED
    assert artifact["artifact_type"] == OCS_LLM_COGNITION_END_TO_END_ARTIFACT_V1
    assert artifact["provider_count"] == 3
    assert artifact["successful_provider_count"] == 3
    assert len(artifact["cognition_artifact_hashes"]) == 3
    assert artifact["human_facing_cognition_result"]["clarification_required"] is True
    assert artifact["human_facing_cognition_result"]["allowed_next_step"] == "HUMAN_REVIEW"
    assert artifact["human_facing_cognition_result"]["findings"]
    assert artifact["human_facing_cognition_result"]["assumptions"]
    assert artifact["human_facing_cognition_result"]["risks"]
    assert artifact["human_facing_cognition_result"]["uncertainties"]
    assert artifact["human_facing_cognition_result"]["clarification_questions"]
    assert artifact["human_facing_cognition_result"]["recommended_next_milestone"]
    assert replay["final_status"] == STATUS_COMPLETED
    assert replay["provider_count"] == 3
    assert replay["cognition_artifact_count"] == 3
    assert replay["clarification_required"] is True


def test_operator_visible_cognition_rendering_precedes_technical_summary(tmp_path):
    result = _run(tmp_path)
    operator_section = render_operator_visible_ocs_llm_cognition(result)
    technical_summary = render_ocs_llm_cognition_end_to_end_summary(result)
    combined = operator_section + "\n" + technical_summary

    assert combined.index("AIGOL OCS COGNITION") < combined.index("AIGOL OCS LLM COGNITION END-TO-END")
    for heading in (
        "Findings:",
        "Assumptions:",
        "Risks:",
        "Uncertainties:",
        "Clarification Questions:",
        "Recommended Next Milestone:",
    ):
        assert heading in operator_section
    assert "Shared finding: the question requires bounded human review." in operator_section
    assert "Shared uncertainty: exact operating scope remains underspecified." in operator_section
    assert "Human review of normalized cognition output." in operator_section
    assert "replay_reference:" in technical_summary
    assert "provider_count:" in technical_summary
    assert "non_authoritative:" not in operator_section
    assert "allowed_next_step:" not in operator_section


@pytest.mark.parametrize(
    ("case_id", "response_payload", "expected_lines"),
    [
        (
            "structured",
            {
                "findings": [
                    "Structured finding is operator readable.",
                    json.dumps({"findings": ["Nested JSON finding is extracted cleanly."]}, sort_keys=True),
                ],
                "assumptions": ["Structured assumption is operator readable."],
                "risks": ["Structured risk is operator readable."],
                "uncertainties": ["Structured uncertainty is operator readable."],
                "confidence": "MEDIUM",
            },
            [
                "Structured finding is operator readable.",
                "Nested JSON finding is extracted cleanly.",
                "Structured assumption is operator readable.",
                "Structured risk is operator readable.",
                "Structured uncertainty is operator readable.",
            ],
        ),
        (
            "partial",
            {
                "findings": ["Partial finding is still rendered."],
                "assumptions": ["Partial assumption is still rendered."],
                "confidence": "LOW",
            },
            [
                "Partial finding is still rendered.",
                "Partial assumption is still rendered.",
                "- (none recorded)",
            ],
        ),
        (
            "missing_optional",
            {
                "findings": ["Required finding survives missing optional fields."],
                "confidence": "UNKNOWN",
            },
            [
                "Required finding survives missing optional fields.",
                "- (none recorded)",
            ],
        ),
        (
            "large",
            {
                "findings": [f"Large clean finding {index:02d}." for index in range(40)],
                "assumptions": ["Large payload assumption remains readable."],
                "risks": ["Large payload risk remains readable."],
                "uncertainties": ["Large payload uncertainty remains readable."],
                "confidence": "MEDIUM",
            },
            [
                "Large clean finding 00.",
                "Large clean finding 39.",
                "Large payload assumption remains readable.",
                "Large payload risk remains readable.",
                "Large payload uncertainty remains readable.",
            ],
        ),
    ],
)
def test_operator_cognition_renderer_outputs_clean_human_text(tmp_path, case_id, response_payload, expected_lines):
    result = _run(
        tmp_path,
        end_to_end_id=f"OCS-LLM-COGNITION-CLEANUP-{case_id.upper()}",
        provider_contracts=_contracts(("provider-a",)),
        transport_registry=_single_provider_transport(json.dumps(response_payload, sort_keys=True)),
        single_provider_primary_mode=True,
    )
    operator_section = render_operator_visible_ocs_llm_cognition(result)
    technical_summary = render_ocs_llm_cognition_end_to_end_summary(result)
    replay = reconstruct_ocs_llm_cognition_end_to_end_replay(tmp_path / "e2e")

    for line in expected_lines:
        assert line in operator_section
    forbidden_fragments = (
        '{"findings"',
        '"assumptions"',
        "artifact_type",
        "runtime_version",
        "provider_metadata",
        "raw_response",
        "response_hash",
        "replay_reference:",
        "non_authoritative:",
        "allowed_next_step:",
    )
    for fragment in forbidden_fragments:
        assert fragment not in operator_section
    assert "AIGOL OCS LLM COGNITION END-TO-END" in technical_summary
    assert "replay_reference:" in technical_summary
    assert replay["final_status"] == STATUS_COMPLETED


def test_end_to_end_reconstructs_each_stage_replay(tmp_path):
    _run(tmp_path)
    replay = reconstruct_ocs_llm_cognition_end_to_end_replay(tmp_path / "e2e")
    stage_replay = replay["stage_replay"]

    assert stage_replay["context"]["context_status"] == "OCS_CONTEXT_ASSEMBLED"
    assert stage_replay["multi_provider_cognition"]["successful_provider_count"] == 3
    assert stage_replay["cognition_comparison"]["source_cognition_artifact_count"] == 3
    assert stage_replay["continuity_and_clarification"]["clarification_candidate_count"] >= 3


def test_provider_failure_is_isolated_when_two_providers_succeed(tmp_path):
    result = _run(
        tmp_path,
        transport_registry=_transports(failing={"provider-c"}),
    )
    artifact = result["ocs_llm_cognition_end_to_end_artifact"]
    replay = reconstruct_ocs_llm_cognition_end_to_end_replay(tmp_path / "e2e")

    assert result["final_status"] == STATUS_COMPLETED
    assert artifact["successful_provider_count"] == 2
    assert artifact["failed_provider_count"] == 1
    assert len(artifact["provider_failure_hashes"]) == 1
    assert replay["successful_provider_count"] == 2
    assert replay["failed_provider_count"] == 1


def test_single_provider_primary_mode_completes_without_comparison_requirement(tmp_path):
    result = _run(
        tmp_path,
        provider_contracts=_contracts(("provider-a",)),
        transport_registry=_transports(),
        single_provider_primary_mode=True,
    )
    artifact = result["ocs_llm_cognition_end_to_end_artifact"]
    replay = reconstruct_ocs_llm_cognition_end_to_end_replay(tmp_path / "e2e")

    assert result["final_status"] == STATUS_COMPLETED
    assert artifact["provider_count"] == 1
    assert artifact["successful_provider_count"] == 1
    assert artifact["cognition_artifact_hashes"]
    assert artifact["single_provider_primary_mode"] is True
    assert artifact["comparison_required"] is False
    assert artifact["comparison_performed"] is False
    assert replay["final_status"] == STATUS_COMPLETED
    assert replay["provider_count"] == 1
    assert replay["cognition_artifact_count"] == 1
    assert replay["stage_replay"]["cognition_comparison"]["source_cognition_artifact_count"] == 1


def test_end_to_end_fails_closed_when_comparison_lacks_two_cognition_artifacts(tmp_path):
    result = _run(
        tmp_path,
        transport_registry=_transports(failing={"provider-b", "provider-c"}),
    )
    artifact = result["ocs_llm_cognition_end_to_end_artifact"]

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["fail_closed"] is True
    assert artifact["workflow_status"] == STATUS_FAILED_CLOSED
    assert "at least two cognition artifacts are required for comparison" in result["failure_reason"]
    replay = reconstruct_ocs_llm_cognition_end_to_end_replay(tmp_path / "e2e")
    assert replay["final_status"] == STATUS_FAILED_CLOSED


def test_prior_history_is_reused_by_end_to_end_continuity(tmp_path):
    first = _run(tmp_path / "first")
    first_stage = first["stage_captures"]
    prior_cognition = [
        item["llm_cognition_artifact"]
        for item in first_stage["multi_provider_cognition"]["provider_results"]
    ]
    prior_comparison = first_stage["cognition_comparison"]["cognition_comparison_artifact"]
    prior_clarification = first_stage["continuity_and_clarification"]["cognition_clarification_artifact"]

    second = _run(
        tmp_path / "second",
        end_to_end_id="OCS-LLM-COGNITION-E2E-002",
        source_context=_source_context("002"),
        replay_dir=tmp_path / "second" / "e2e",
        prior_cognition_artifacts=prior_cognition[:1],
        prior_comparison_artifacts=[prior_comparison],
        prior_clarification_artifacts=[prior_clarification],
    )
    continuity = second["stage_captures"]["continuity_and_clarification"]["cognition_continuity_artifact"]

    assert second["final_status"] == STATUS_COMPLETED
    assert continuity["continuity_summary"]["prior_cognition_reused"] == 1
    assert continuity["continuity_summary"]["prior_comparisons_reused"] == 1
    assert continuity["continuity_summary"]["prior_clarifications_reused"] == 1


def test_boundary_preservation_no_execution_or_approval_created(tmp_path):
    result = _run(tmp_path)
    artifact = result["ocs_llm_cognition_end_to_end_artifact"]
    human_result = artifact["human_facing_cognition_result"]

    for item in (result, artifact):
        assert item["approval_created"] is False
        assert item["worker_invoked"] is False
        assert item["execution_requested"] is False
        assert item["governance_modified"] is False
        assert item["replay_modified"] is False
        assert all(value is False for value in item["authority_flags"].values())
    assert human_result["approval_created"] is False
    assert human_result["execution_requested"] is False
    assert human_result["worker_invoked"] is False


def test_replay_tampering_is_detected(tmp_path):
    _run(tmp_path)
    path = tmp_path / "e2e" / "000_ocs_llm_cognition_end_to_end_artifact.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["successful_provider_count"] = 99
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_ocs_llm_cognition_end_to_end_replay(tmp_path / "e2e")


def test_append_only_replay_collision_fails_closed(tmp_path):
    _run(tmp_path)
    result = _run(tmp_path)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "already exists" in result["failure_reason"]
