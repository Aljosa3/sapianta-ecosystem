"""Tests for AIGOL_LLM_COGNITION_PROVIDER_RUNTIME_V1."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aigol.runtime.llm_cognition_provider_runtime import (
    CERTIFIED_CLASSIFICATION,
    FINAL_CLASSIFICATION,
    LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1,
    LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1,
    MILESTONE_ID,
    STATUS_COMPLETED,
    STATUS_FAILED_CLOSED,
    create_default_openai_cognition_provider_contract,
    reconstruct_llm_cognition_provider_replay,
    run_llm_cognition_provider_runtime,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-05T00:00:00Z"


def _conversation_source() -> dict:
    artifact = {
        "artifact_type": "HUMAN_REQUEST_ARTIFACT_V1",
        "artifact_id": "HUMAN-REQUEST-001",
        "status": "REPLAY_VISIBLE",
        "summary": "Human asks for governed cognition-provider analysis.",
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
        context_assembly_id="OCS-CONTEXT-LLM-001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ocs_context",
        source_context={"conversation_context": [_conversation_source()]},
        source_chain_id="CHAIN-001",
        source_request_reference="HUMAN-REQUEST-001",
    )
    assert capture["fail_closed"] is False
    return capture["ocs_context_assembly_artifact"]


def _contract() -> dict:
    return create_default_openai_cognition_provider_contract(created_at=CREATED_AT)


def _transport(raw_text: str = "Findings: OCS context is sufficient. Confidence: medium."):
    def call(payload: dict, metadata: dict) -> dict:
        assert payload["stream"] is False
        assert metadata["api_key"] == "test-openai-key"
        assert metadata["provider_id"] == "openai"
        assert metadata["provider_role"] == "COGNITION_PROVIDER"
        assert "COGNITION_PROVIDER" in payload["input"]
        return {"id": "resp-cognition-001", "output_text": raw_text}

    return call


def _invoke(tmp_path: Path, monkeypatch, **overrides):
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-openai-key")
    args = {
        "cognition_provider_request_id": "LLM-COGNITION-PROVIDER-REQUEST-001",
        "human_request": "Analyze the OCS context and identify missing information.",
        "ocs_context_artifact": _context(tmp_path),
        "provider_contract": _contract(),
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "llm_cognition_provider",
        "human_approved": True,
        "approved_by": "human.operator",
        "provider_id": "openai",
        "model": "gpt-5.1",
        "credential_env": "AIGOL_OPENAI_API_KEY",
        "transport": _transport(),
    }
    args.update(overrides)
    return run_llm_cognition_provider_runtime(**args)


def test_single_approved_cognition_provider_records_request_response_and_replay(tmp_path, monkeypatch):
    result = _invoke(tmp_path, monkeypatch)
    replay = reconstruct_llm_cognition_provider_replay(tmp_path / "llm_cognition_provider")

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_classification"] == FINAL_CLASSIFICATION
    assert result["classification"] == CERTIFIED_CLASSIFICATION
    assert result["final_status"] == STATUS_COMPLETED
    assert result["provider_invoked"] is True
    assert result["llm_cognition_provider_request_artifact"]["artifact_type"] == LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1
    assert result["llm_cognition_provider_response_artifact"]["artifact_type"] == LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1
    assert result["llm_cognition_provider_request_artifact"]["ocs_context_reference"]["context_hash"].startswith("sha256:")
    assert result["llm_cognition_provider_request_artifact"]["request_hash"].startswith("sha256:")
    assert result["llm_cognition_provider_response_artifact"]["response_hash"].startswith("sha256:")
    assert result["replay_binding"]["lineage_refs"]["llm_cognition_provider_request_artifact_hash"] == (
        result["llm_cognition_provider_request_artifact"]["artifact_hash"]
    )
    assert replay["provider_invoked"] is True
    assert replay["human_request_to_ocs_context_to_cognition_provider_to_response_to_replay"] is True


def test_provider_remains_non_authoritative_and_no_downstream_authority_is_created(tmp_path, monkeypatch):
    result = _invoke(tmp_path, monkeypatch)
    request_artifact = result["llm_cognition_provider_request_artifact"]
    response_artifact = result["llm_cognition_provider_response_artifact"]
    binding = result["replay_binding"]

    for artifact in (request_artifact, response_artifact, binding, result):
        flags = artifact["authority_flags"]
        assert flags["provider_authority"] is False
        assert flags["approval_authority"] is False
        assert flags["execution_authority"] is False
        assert flags["worker_authority"] is False
        assert flags["governance_authority"] is False
        assert flags["replay_authority"] is False
        assert artifact["worker_invoked"] is False
        assert artifact["execution_requested"] is False
        assert artifact["governance_modified"] is False
        assert artifact["replay_modified"] is False


def test_missing_human_approval_fails_closed_before_provider_invocation(tmp_path, monkeypatch):
    called = False

    def transport(_payload, _metadata):
        nonlocal called
        called = True
        return {"output_text": "should not run"}

    result = _invoke(tmp_path, monkeypatch, human_approved=False, transport=transport)

    assert called is False
    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["provider_invoked"] is False
    assert "explicit human approval is required" in result["failure_reason"]


def test_unapproved_provider_contract_fails_closed(tmp_path, monkeypatch):
    contract = _contract()
    contract["provider_approved"] = False
    contract.pop("artifact_hash")
    contract["artifact_hash"] = replay_hash(contract)
    called = False

    def transport(_payload, _metadata):
        nonlocal called
        called = True
        return {"output_text": "should not run"}

    result = _invoke(tmp_path, monkeypatch, provider_contract=contract, transport=transport)

    assert called is False
    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["provider_invoked"] is False
    assert "provider is not approved" in result["failure_reason"]


def test_authority_bearing_provider_response_fails_closed(tmp_path, monkeypatch):
    result = _invoke(
        tmp_path,
        monkeypatch,
        transport=_transport("I approve this and execution authorized."),
    )

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "exceeds authority boundary" in result["failure_reason"]
    assert result["worker_invoked"] is False
    assert result["execution_requested"] is False


def test_replay_tampering_is_detected(tmp_path, monkeypatch):
    _invoke(tmp_path, monkeypatch)
    path = tmp_path / "llm_cognition_provider" / "001_llm_cognition_provider_response.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["response_text"] = "tampered"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_llm_cognition_provider_replay(tmp_path / "llm_cognition_provider")


def test_append_only_replay_violation_fails_closed(tmp_path, monkeypatch):
    _invoke(tmp_path, monkeypatch)
    result = run_llm_cognition_provider_runtime(
        cognition_provider_request_id="LLM-COGNITION-PROVIDER-REQUEST-002",
        human_request="Analyze again.",
        ocs_context_artifact=_context(tmp_path / "second_context"),
        provider_contract=_contract(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "llm_cognition_provider",
        human_approved=True,
        transport=_transport(),
    )

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "already exists" in result["failure_reason"]
