"""Tests for AIGOL_COGNITION_ARTIFACT_RUNTIME_V1."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aigol.runtime.cognition_artifact_runtime import (
    CERTIFIED_CLASSIFICATION,
    FINAL_CLASSIFICATION,
    LLM_COGNITION_ARTIFACT_V1,
    STATUS_COMPLETED,
    STATUS_FAILED_CLOSED,
    reconstruct_cognition_artifact_replay,
    run_cognition_artifact_runtime,
)
from aigol.runtime.llm_cognition_provider_runtime import (
    create_default_openai_cognition_provider_contract,
    run_llm_cognition_provider_runtime,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-05T00:00:00Z"


def _conversation_source() -> dict:
    artifact = {
        "artifact_type": "HUMAN_REQUEST_ARTIFACT_V1",
        "artifact_id": "HUMAN-REQUEST-COGNITION-ARTIFACT-001",
        "status": "REPLAY_VISIBLE",
        "summary": "Human asks for provider-assisted cognition normalization.",
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _context(tmp_path: Path) -> dict:
    capture = assemble_ocs_context(
        context_assembly_id="OCS-CONTEXT-COGNITION-ARTIFACT-001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ocs_context",
        source_context={"conversation_context": [_conversation_source()]},
        source_chain_id="CHAIN-COGNITION-ARTIFACT-001",
        source_request_reference="HUMAN-REQUEST-COGNITION-ARTIFACT-001",
    )
    assert capture["fail_closed"] is False
    return capture["ocs_context_assembly_artifact"]


def _provider_text(**overrides) -> str:
    payload = {
        "findings": ["OCS context is sufficient for provider-assisted cognition normalization."],
        "assumptions": ["Provider output is advisory and untrusted."],
        "alternatives": ["Request additional human context before downstream use."],
        "risks": ["Provider output may omit governance constraints."],
        "uncertainties": ["No multi-provider agreement is available in this milestone."],
        "confidence": "MEDIUM",
    }
    payload.update(overrides)
    return json.dumps(payload, sort_keys=True)


def _provider_capture(tmp_path: Path, monkeypatch, *, provider_text: str | None = None) -> tuple[dict, dict, dict]:
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-openai-key")
    context = _context(tmp_path)

    def transport(_payload: dict, metadata: dict) -> dict:
        assert metadata["provider_role"] == "COGNITION_PROVIDER"
        return {"id": "resp-cognition-artifact-001", "output_text": provider_text or _provider_text()}

    capture = run_llm_cognition_provider_runtime(
        cognition_provider_request_id="LLM-COGNITION-PROVIDER-REQUEST-ARTIFACT-001",
        human_request="Normalize provider-assisted cognition.",
        ocs_context_artifact=context,
        provider_contract=create_default_openai_cognition_provider_contract(created_at=CREATED_AT),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "llm_cognition_provider",
        human_approved=True,
        transport=transport,
    )
    assert capture["fail_closed"] is False
    return (
        context,
        capture["llm_cognition_provider_request_artifact"],
        capture["llm_cognition_provider_response_artifact"],
    )


def _run_artifact(tmp_path: Path, monkeypatch, *, provider_text: str | None = None, **overrides) -> dict:
    context, request_artifact, response_artifact = _provider_capture(
        tmp_path / "provider_flow", monkeypatch, provider_text=provider_text
    )
    args = {
        "cognition_artifact_id": "LLM-COGNITION-ARTIFACT-001",
        "ocs_context_artifact": context,
        "provider_request_artifact": request_artifact,
        "provider_response_artifact": response_artifact,
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "cognition_artifact",
    }
    args.update(overrides)
    return run_cognition_artifact_runtime(**args)


def test_provider_response_normalizes_into_canonical_llm_cognition_artifact(tmp_path, monkeypatch):
    result = _run_artifact(tmp_path, monkeypatch)
    artifact = result["llm_cognition_artifact"]
    replay = reconstruct_cognition_artifact_replay(tmp_path / "cognition_artifact")

    assert result["final_classification"] == FINAL_CLASSIFICATION
    assert result["classification"] == CERTIFIED_CLASSIFICATION
    assert result["final_status"] == STATUS_COMPLETED
    assert artifact["artifact_type"] == LLM_COGNITION_ARTIFACT_V1
    assert artifact["canonical_provider_assisted_cognition_output"] is True
    assert artifact["findings"] == ["OCS context is sufficient for provider-assisted cognition normalization."]
    assert artifact["assumptions"] == ["Provider output is advisory and untrusted."]
    assert artifact["alternatives"] == ["Request additional human context before downstream use."]
    assert artifact["risks"] == ["Provider output may omit governance constraints."]
    assert artifact["uncertainties"] == ["No multi-provider agreement is available in this milestone."]
    assert artifact["confidence"] == "MEDIUM"
    assert artifact["context_hash"].startswith("sha256:")
    assert artifact["request_hash"].startswith("sha256:")
    assert artifact["response_hash"].startswith("sha256:")
    assert replay["canonical_provider_assisted_cognition_output"] is True


def test_nested_cognition_json_in_findings_is_merged_into_canonical_fields(tmp_path, monkeypatch):
    nested = {
        "findings": ["Nested finding is recovered."],
        "assumptions": ["Nested assumption is recovered."],
        "risks": ["Nested risk is recovered."],
        "uncertainties": ["Nested uncertainty is recovered."],
        "clarification_questions": ["Which buyer segment should be prioritized?"],
        "recommended_next_milestone": "Human review of recovered nested cognition.",
    }
    provider_text = _provider_text(
        findings=[json.dumps(nested, sort_keys=True)],
        assumptions=[],
        risks=[],
        uncertainties=[],
    )
    result = _run_artifact(tmp_path, monkeypatch, provider_text=provider_text)
    artifact = result["llm_cognition_artifact"]

    assert artifact["findings"] == ["Nested finding is recovered."]
    assert artifact["assumptions"] == ["Nested assumption is recovered."]
    assert artifact["risks"] == ["Nested risk is recovered."]
    assert artifact["uncertainties"] == ["Nested uncertainty is recovered."]
    assert artifact["clarification_questions"] == ["Which buyer segment should be prioritized?"]
    assert artifact["recommended_next_milestone"] == "Human review of recovered nested cognition."


def test_normal_findings_list_is_preserved_without_nested_json(tmp_path, monkeypatch):
    provider_text = _provider_text(findings=["Normal finding remains plain text."])
    result = _run_artifact(tmp_path, monkeypatch, provider_text=provider_text)
    artifact = result["llm_cognition_artifact"]

    assert artifact["findings"] == ["Normal finding remains plain text."]
    assert artifact["assumptions"] == ["Provider output is advisory and untrusted."]
    assert artifact["risks"] == ["Provider output may omit governance constraints."]


def test_mixed_findings_list_merges_nested_json_and_preserves_plain_findings(tmp_path, monkeypatch):
    nested = {
        "findings": ["Nested mixed finding is recovered."],
        "assumptions": ["Nested mixed assumption is recovered."],
        "risks": ["Nested mixed risk is recovered."],
        "uncertainties": ["Nested mixed uncertainty is recovered."],
    }
    provider_text = _provider_text(findings=["Plain mixed finding remains.", json.dumps(nested, sort_keys=True)])
    result = _run_artifact(tmp_path, monkeypatch, provider_text=provider_text)
    artifact = result["llm_cognition_artifact"]

    assert artifact["findings"] == ["Plain mixed finding remains.", "Nested mixed finding is recovered."]
    assert artifact["assumptions"] == [
        "Provider output is advisory and untrusted.",
        "Nested mixed assumption is recovered.",
    ]
    assert artifact["risks"] == [
        "Provider output may omit governance constraints.",
        "Nested mixed risk is recovered.",
    ]
    assert artifact["uncertainties"] == [
        "No multi-provider agreement is available in this milestone.",
        "Nested mixed uncertainty is recovered.",
    ]


def test_invalid_json_string_in_findings_remains_plain_finding(tmp_path, monkeypatch):
    invalid_json = '{"findings": ["not closed"]'
    provider_text = _provider_text(findings=[invalid_json])
    result = _run_artifact(tmp_path, monkeypatch, provider_text=provider_text)
    artifact = result["llm_cognition_artifact"]

    assert artifact["findings"] == [invalid_json]
    assert artifact["assumptions"] == ["Provider output is advisory and untrusted."]
    assert artifact["risks"] == ["Provider output may omit governance constraints."]


def test_multiline_section_labeled_cognition_text_populates_canonical_fields(tmp_path, monkeypatch):
    provider_text = "\n".join(
        [
            "Findings:",
            "- Section finding is recovered.",
            "Assumptions:",
            "- Section assumption is recovered.",
            "Risks:",
            "- Section risk is recovered.",
            "Uncertainties:",
            "- Section uncertainty is recovered.",
            "Clarification Questions:",
            "- Which buyer should be prioritized?",
            "Recommended Next Milestone:",
            "- Human review of section-labeled cognition.",
        ]
    )
    result = _run_artifact(tmp_path, monkeypatch, provider_text=provider_text)
    artifact = result["llm_cognition_artifact"]

    assert artifact["findings"] == ["Section finding is recovered."]
    assert artifact["assumptions"] == ["Section assumption is recovered."]
    assert artifact["risks"] == ["Section risk is recovered."]
    assert artifact["uncertainties"] == ["Section uncertainty is recovered."]
    assert artifact["clarification_questions"] == ["Which buyer should be prioritized?"]
    assert artifact["recommended_next_milestone"] == "Human review of section-labeled cognition."
    assert artifact["normalization"]["source_format"] == "plain_text"


def test_flattened_section_labeled_cognition_text_populates_canonical_fields(tmp_path, monkeypatch):
    provider_text = (
        "findings: - Flattened finding is recovered. "
        "assumptions: - Flattened assumption is recovered. "
        "risks: - Flattened risk is recovered. "
        "uncertainties: - Flattened uncertainty is recovered. "
        "clarification questions: 1. What evidence should be attached next? "
        "recommended next milestone: - Review recovered flattened cognition."
    )
    result = _run_artifact(tmp_path, monkeypatch, provider_text=provider_text)
    artifact = result["llm_cognition_artifact"]

    assert artifact["findings"] == ["Flattened finding is recovered."]
    assert artifact["assumptions"] == ["Flattened assumption is recovered."]
    assert artifact["risks"] == ["Flattened risk is recovered."]
    assert artifact["uncertainties"] == ["Flattened uncertainty is recovered."]
    assert artifact["clarification_questions"] == ["What evidence should be attached next?"]
    assert artifact["recommended_next_milestone"] == "Review recovered flattened cognition."


def test_dash_labeled_cognition_text_populates_canonical_fields(tmp_path, monkeypatch):
    provider_text = (
        "Findings - Dash finding is recovered. "
        "Assumptions - Dash assumption is recovered. "
        "Risks - Dash risk is recovered. "
        "Uncertainties - Dash uncertainty is recovered. "
        "Clarification Questions - What dash-labeled evidence should be reviewed? "
        "Recommended Next Milestone - Review recovered dash-labeled cognition."
    )
    result = _run_artifact(tmp_path, monkeypatch, provider_text=provider_text)
    artifact = result["llm_cognition_artifact"]

    assert artifact["findings"] == ["Dash finding is recovered."]
    assert artifact["assumptions"] == ["Dash assumption is recovered."]
    assert artifact["risks"] == ["Dash risk is recovered."]
    assert artifact["uncertainties"] == ["Dash uncertainty is recovered."]
    assert artifact["clarification_questions"] == ["What dash-labeled evidence should be reviewed?"]
    assert artifact["recommended_next_milestone"] == "Review recovered dash-labeled cognition."


def test_mixed_findings_merges_section_labeled_text_and_preserves_plain_findings(tmp_path, monkeypatch):
    provider_text = _provider_text(
        findings=[
            "Plain finding remains.",
            (
                "Findings: - Section mixed finding is recovered. "
                "Assumptions: - Section mixed assumption is recovered. "
                "Risks: - Section mixed risk is recovered. "
                "Uncertainties: - Section mixed uncertainty is recovered."
            ),
        ],
        assumptions=[],
        risks=[],
        uncertainties=[],
    )
    result = _run_artifact(tmp_path, monkeypatch, provider_text=provider_text)
    artifact = result["llm_cognition_artifact"]

    assert artifact["findings"] == ["Plain finding remains.", "Section mixed finding is recovered."]
    assert artifact["assumptions"] == ["Section mixed assumption is recovered."]
    assert artifact["risks"] == ["Section mixed risk is recovered."]
    assert artifact["uncertainties"] == ["Section mixed uncertainty is recovered."]
    assert artifact["normalization"]["source_format"] == "json"


def test_single_section_label_without_cognition_document_remains_plain_finding(tmp_path, monkeypatch):
    provider_text = "Finding: OCS context is adequate, but provider output remains advisory."
    result = _run_artifact(tmp_path, monkeypatch, provider_text=provider_text)
    artifact = result["llm_cognition_artifact"]

    assert artifact["findings"] == [provider_text]
    assert artifact["assumptions"] == []
    assert artifact["risks"] == []


def test_plain_text_provider_response_becomes_bounded_finding_with_unknown_confidence(tmp_path, monkeypatch):
    result = _run_artifact(
        tmp_path,
        monkeypatch,
        provider_text="Finding: OCS context is adequate, but provider output remains advisory.",
    )
    artifact = result["llm_cognition_artifact"]

    assert artifact["findings"] == ["Finding: OCS context is adequate, but provider output remains advisory."]
    assert artifact["assumptions"] == []
    assert artifact["confidence"] == "UNKNOWN"
    assert artifact["normalization"]["source_format"] == "plain_text"


def test_authority_bearing_provider_response_fails_closed(tmp_path, monkeypatch):
    context, request_artifact, response_artifact = _provider_capture(tmp_path / "provider_flow", monkeypatch)
    response_artifact["response_text"] = json.dumps({"findings": ["Execution authorized."], "confidence": "HIGH"})
    response_artifact["response_text_hash"] = replay_hash(response_artifact["response_text"])
    response_artifact["response_hash"] = replay_hash(
        {
            "cognition_provider_request_id": response_artifact["cognition_provider_request_id"],
            "provider_id": response_artifact["provider_id"],
            "provider_role": response_artifact["provider_role"],
            "provider_schema_id": response_artifact["provider_schema_id"],
            "provider_identity": response_artifact["provider_identity"],
            "provider_metadata": response_artifact["provider_metadata"],
            "provider_request_hash": response_artifact["provider_request_hash"],
            "request_hash": response_artifact["request_hash"],
            "ocs_context_hash": response_artifact["ocs_context_hash"],
            "raw_response_hash": response_artifact["raw_response_hash"],
            "response_text_hash": response_artifact["response_text_hash"],
            "response_status": response_artifact["response_status"],
            "untrusted_provider_output": response_artifact["untrusted_provider_output"],
            "non_authoritative": response_artifact["non_authoritative"],
            "authority_flags": response_artifact["authority_flags"],
            "lineage_refs": response_artifact["lineage_refs"],
        }
    )
    response_artifact.pop("artifact_hash")
    response_artifact["artifact_hash"] = replay_hash(response_artifact)

    result = run_cognition_artifact_runtime(
        cognition_artifact_id="LLM-COGNITION-ARTIFACT-002",
        ocs_context_artifact=context,
        provider_request_artifact=request_artifact,
        provider_response_artifact=response_artifact,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "cognition_artifact",
    )

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "authority boundary" in result["failure_reason"]
    assert result["worker_invoked"] is False
    assert result["execution_requested"] is False


def test_lineage_mismatch_fails_closed(tmp_path, monkeypatch):
    context, request_artifact, response_artifact = _provider_capture(tmp_path / "provider_flow", monkeypatch)
    response_artifact["ocs_context_hash"] = "sha256:bad"
    response_artifact.pop("artifact_hash")
    response_artifact["artifact_hash"] = replay_hash(response_artifact)

    result = run_cognition_artifact_runtime(
        cognition_artifact_id="LLM-COGNITION-ARTIFACT-003",
        ocs_context_artifact=context,
        provider_request_artifact=request_artifact,
        provider_response_artifact=response_artifact,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "cognition_artifact",
    )

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "context hash mismatch" in result["failure_reason"]


def test_no_downstream_authority_is_created(tmp_path, monkeypatch):
    result = _run_artifact(tmp_path, monkeypatch)
    artifact = result["llm_cognition_artifact"]

    assert artifact["non_authoritative"] is True
    assert artifact["human_review_required"] is True
    assert artifact["provider_invoked"] is True
    assert artifact["worker_invoked"] is False
    assert artifact["approval_created"] is False
    assert artifact["execution_requested"] is False
    assert artifact["governance_modified"] is False
    assert artifact["replay_modified"] is False
    assert all(value is False for value in artifact["authority_flags"].values())


def test_replay_tampering_is_detected(tmp_path, monkeypatch):
    _run_artifact(tmp_path, monkeypatch)
    path = tmp_path / "cognition_artifact" / "000_llm_cognition_artifact.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["confidence"] = "HIGH"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_cognition_artifact_replay(tmp_path / "cognition_artifact")


def test_append_only_replay_collision_fails_closed(tmp_path, monkeypatch):
    _run_artifact(tmp_path, monkeypatch)
    context, request_artifact, response_artifact = _provider_capture(tmp_path / "provider_flow_2", monkeypatch)
    result = run_cognition_artifact_runtime(
        cognition_artifact_id="LLM-COGNITION-ARTIFACT-004",
        ocs_context_artifact=context,
        provider_request_artifact=request_artifact,
        provider_response_artifact=response_artifact,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "cognition_artifact",
    )

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "already exists" in result["failure_reason"]
