"""Tests for AIGOL_FIRST_REAL_PROVIDER_RUNTIME_IMPLEMENTATION_V1."""

from __future__ import annotations

import inspect
from pathlib import Path

from aigol.runtime.external_resource_registry_runtime import (
    ACTIVE,
    COGNITION_PROVIDER,
    INACTIVE,
    OPENAI_PROVIDER_ID,
    create_err_v0_registry,
    register_resource,
)
from aigol.runtime.first_real_provider_runtime import (
    CANONICAL_COGNITION_PROVIDER_CONTRACT_V1,
    CANONICAL_COGNITION_PROVIDER_INPUT_V1,
    CANONICAL_COGNITION_PROVIDER_OUTPUT_V1,
    MILESTONE_ID,
    STATUS_COMPLETED,
    STATUS_FAILED_CLOSED,
    run_first_real_provider_runtime_validation,
)
from aigol.runtime.llm_cognition_provider_runtime import reconstruct_llm_cognition_provider_replay
from aigol.runtime.transport.serialization import load_json, replay_hash


CREATED_AT = "2026-06-16T00:00:00+00:00"


def _source_context() -> dict:
    artifact = {
        "artifact_type": "HUMAN_REQUEST_ARTIFACT_V1",
        "artifact_id": "FIRST-REAL-PROVIDER-HUMAN-REQUEST-000001",
        "status": "REPLAY_VISIBLE",
        "summary": "Human asks for first real provider runtime validation.",
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return {"conversation_context": [artifact]}


def _run(tmp_path: Path, monkeypatch, **overrides):
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "deterministic-validation-secret")
    args = {
        "validation_id": "FIRST-REAL-PROVIDER-RUNTIME-000001",
        "human_request": "Validate one governed OpenAI cognition provider path.",
        "source_context": _source_context(),
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "first_real_provider",
    }
    args.update(overrides)
    return run_first_real_provider_runtime_validation(**args)


def test_first_real_provider_runtime_validates_err_to_cognition_artifact_path(tmp_path, monkeypatch) -> None:
    result = _run(tmp_path, monkeypatch)
    validation = result["first_real_provider_runtime_validation_artifact"]
    canonical_contract = result["canonical_provider_contract"]
    canonical_input = result["canonical_provider_input"]
    canonical_output = result["canonical_provider_output"]
    cognition = result["llm_cognition_artifact_capture"]["llm_cognition_artifact"]
    llm_replay = reconstruct_llm_cognition_provider_replay(
        tmp_path / "first_real_provider" / "llm_cognition_provider",
    )

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_status"] == STATUS_COMPLETED
    assert result["selected_provider_id"] == OPENAI_PROVIDER_ID
    assert result["err_selection_capture"]["selected_resource_id"] == OPENAI_PROVIDER_ID
    assert result["err_selection_capture"]["provider_invoked"] is False
    assert canonical_contract["artifact_type"] == CANONICAL_COGNITION_PROVIDER_CONTRACT_V1
    assert canonical_contract["provider_id"] == OPENAI_PROVIDER_ID
    assert canonical_contract["provider_schema_id"] == "openai.responses.v1"
    assert canonical_contract["capabilities"] == [
        "reasoning",
        "planning",
        "summarization",
        "analysis",
        "generation",
    ]
    assert canonical_input["artifact_type"] == CANONICAL_COGNITION_PROVIDER_INPUT_V1
    assert canonical_input["provider_invoked"] is False
    assert canonical_input["source_input_artifact_hash"] == validation["llm_provider_request_hash"]
    assert canonical_output["artifact_type"] == CANONICAL_COGNITION_PROVIDER_OUTPUT_V1
    assert canonical_output["provider_invoked"] is True
    assert canonical_output["source_output_artifact_hash"] == validation["llm_provider_response_hash"]
    assert cognition["artifact_type"] == "LLM_COGNITION_ARTIFACT_V1"
    assert cognition["provider_identity"]["provider_id"] == OPENAI_PROVIDER_ID
    assert cognition["confidence"] == "HIGH"
    assert validation["llm_cognition_artifact_hash"] == cognition["artifact_hash"]
    assert result["deterministic_mock_provider_response"] is True
    assert result["real_openai_called"] is False
    assert llm_replay["provider_id"] == OPENAI_PROVIDER_ID
    assert llm_replay["provider_invoked"] is True


def test_first_real_provider_runtime_persists_replay_visible_validation_evidence(tmp_path, monkeypatch) -> None:
    result = _run(tmp_path, monkeypatch)
    replay_root = tmp_path / "first_real_provider"
    wrapper = load_json(replay_root / "000_first_real_provider_runtime_validation.json")
    artifact = wrapper["artifact"]

    assert artifact["artifact_type"] == "FIRST_REAL_PROVIDER_RUNTIME_VALIDATION_ARTIFACT_V1"
    assert artifact["selected_provider_id"] == OPENAI_PROVIDER_ID
    assert artifact["err_selection_hash"] == result["err_selection_capture"]["err_selection_evidence_artifact"]["artifact_hash"]
    assert artifact["canonical_contract_hash"] == result["canonical_provider_contract"]["artifact_hash"]
    assert artifact["canonical_input_hash"] == result["canonical_provider_input"]["artifact_hash"]
    assert artifact["canonical_output_hash"] == result["canonical_provider_output"]["artifact_hash"]
    assert artifact["replay_visible"] is True
    assert wrapper["replay_step"] == "first_real_provider_runtime_validation"
    assert (replay_root / "err_openai_selection" / "000_err_resource_selection_evidence_recorded.json").exists()
    assert (replay_root / "llm_cognition_provider" / "001_llm_cognition_provider_response.json").exists()
    assert (replay_root / "llm_cognition_artifact" / "000_llm_cognition_artifact.json").exists()


def test_first_real_provider_runtime_preserves_governance_boundaries(tmp_path, monkeypatch) -> None:
    result = _run(tmp_path, monkeypatch)

    for artifact in (
        result["first_real_provider_runtime_validation_artifact"],
        result["canonical_provider_contract"],
        result["canonical_provider_input"],
        result["canonical_provider_output"],
    ):
        if "authority_flags" in artifact:
            assert all(value is False for value in artifact["authority_flags"].values())
        assert artifact.get("worker_invoked", False) is False
        assert artifact.get("execution_requested", False) is False
        assert artifact.get("dispatch_requested", False) is False
        assert artifact.get("governance_modified", False) is False
        assert artifact.get("replay_modified", False) is False

    response = result["llm_cognition_provider_capture"]["llm_cognition_provider_response_artifact"]
    assert response["untrusted_provider_output"] is True
    assert response["non_authoritative"] is True
    assert response["raw_response"]["real_openai_called"] is False


def test_first_real_provider_runtime_fails_closed_when_err_does_not_select_openai(tmp_path, monkeypatch) -> None:
    registry = create_err_v0_registry()
    register_resource(
        registry,
        {
            "resource_id": OPENAI_PROVIDER_ID,
            "resource_type": COGNITION_PROVIDER,
            "capabilities": ["reasoning"],
            "status": INACTIVE,
        },
    )
    register_resource(
        registry,
        {
            "resource_id": "claude",
            "resource_type": COGNITION_PROVIDER,
            "capabilities": ["reasoning"],
            "status": ACTIVE,
        },
    )

    result = _run(tmp_path, monkeypatch, err_registry=registry)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["provider_invoked"] is False
    assert result["real_openai_called"] is False
    assert "requires ERR-selected openai" in result["failure_reason"]


def test_first_real_provider_runtime_authority_bearing_stub_response_fails_closed(tmp_path, monkeypatch) -> None:
    result = _run(
        tmp_path,
        monkeypatch,
        deterministic_response_text="I approve this and execution authorized.",
    )

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["worker_invoked"] is False
    assert result["execution_requested"] is False
    assert result["governance_modified"] is False
    assert result["real_openai_called"] is False
    assert "exceeds authority boundary" in result["failure_reason"]


def test_first_real_provider_runtime_has_no_transport_or_authentication_implementation() -> None:
    import aigol.runtime.first_real_provider_runtime as runtime

    source = inspect.getsource(runtime)

    assert "urlopen" not in source
    assert "requests" not in source
    assert "httpx" not in source
    assert "Authorization" not in source
    assert "api_key" not in source
    assert "_openai_http_transport" not in source
