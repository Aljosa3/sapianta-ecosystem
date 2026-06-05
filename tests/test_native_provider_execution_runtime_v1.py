"""Tests for AIGOL_NATIVE_PROVIDER_EXECUTION_RUNTIME_V1."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.native_provider_execution_runtime import (
    FINAL_CLASSIFICATION,
    MILESTONE_ID,
    STATUS_COMPLETED,
    STATUS_FAILED_CLOSED,
    normalize_provider_response,
    reconstruct_native_provider_execution_replay,
    run_native_provider_execution,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-05T00:00:00Z"


def _transport(raw_text: str = "Native provider result"):
    def call(payload: dict, metadata: dict) -> dict:
        assert payload["stream"] is False
        assert metadata["api_key"] == "test-openai-key"
        assert metadata["provider_id"] == "openai"
        return {"id": "resp-001", "output_text": raw_text}

    return call


def _invoke(tmp_path: Path, **overrides):
    args = {
        "execution_id": "NATIVE-PROVIDER-EXECUTION-1",
        "human_request": "Summarize governed provider continuity.",
        "provider_id": "openai",
        "model": "gpt-5.1",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "native_provider_execution",
        "human_approved": True,
        "approved_by": "human.operator",
        "credential_env": "AIGOL_OPENAI_API_KEY",
        "timeout_seconds": 20,
        "transport": _transport(),
    }
    args.update(overrides)
    return run_native_provider_execution(**args)


def test_native_provider_invocation_records_request_response_identity_metadata_and_lineage(tmp_path, monkeypatch):
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-openai-key")

    result = _invoke(tmp_path)
    replay = reconstruct_native_provider_execution_replay(tmp_path / "native_provider_execution")

    assert result["milestone_id"] == MILESTONE_ID
    assert result["final_classification"] == FINAL_CLASSIFICATION
    assert result["final_status"] == STATUS_COMPLETED
    assert result["provider_invoked"] is True
    assert result["provider_request"]["request"]["input_hash"].startswith("sha256:")
    assert result["provider_response"]["raw_response_hash"].startswith("sha256:")
    assert result["replay_binding"]["provider_identity"]["provider_id"] == "openai"
    assert result["replay_binding"]["provider_metadata"]["model"] == "gpt-5.1"
    assert result["replay_binding"]["lineage_refs"]["provider_request_hash"] == result["provider_request"]["artifact_hash"]
    assert replay["provider_invoked"] is True
    assert replay["human_request_to_provider_result_to_replay"] is True


def test_credential_policy_loads_without_persisting_secret(tmp_path, monkeypatch):
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-openai-key")

    _invoke(tmp_path)
    credential_wrapper = json.loads(
        (tmp_path / "native_provider_execution" / "000_credential_policy.json").read_text(encoding="utf-8")
    )

    assert credential_wrapper["artifact"]["credential_loaded"] is True
    assert credential_wrapper["artifact"]["credential_captured"] is False
    assert "_credential_secret" not in credential_wrapper["artifact"]
    assert "test-openai-key" not in json.dumps(credential_wrapper, sort_keys=True)


def test_schema_registry_normalizes_openai_output_list_shape(tmp_path, monkeypatch):
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-openai-key")

    result = _invoke(
        tmp_path,
        transport=lambda _payload, _metadata: {
            "id": "resp-002",
            "output": [{"content": [{"text": "Replay "}, {"text": "bound"}]}],
        },
    )

    assert result["normalized_provider_response"]["provider_schema_id"] == "openai.responses.v1"
    assert result["normalized_provider_response"]["normalized_response"]["response_text"] == "Replay bound"
    assert "openai.responses.v1" in result["normalized_provider_response"]["schema_registry"]["registered_schema_ids"]


def test_missing_human_approval_fails_closed_before_provider_invocation(tmp_path, monkeypatch):
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-openai-key")
    called = False

    def transport(_payload, _metadata):
        nonlocal called
        called = True
        return {"output_text": "should not run"}

    result = _invoke(tmp_path, human_approved=False, transport=transport)

    assert called is False
    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["provider_invoked"] is False
    assert "explicit human approval is required" in result["failure_reason"]


def test_missing_credential_fails_closed_before_provider_invocation(tmp_path, monkeypatch):
    monkeypatch.delenv("AIGOL_OPENAI_API_KEY", raising=False)
    called = False

    def transport(_payload, _metadata):
        nonlocal called
        called = True
        return {"output_text": "should not run"}

    result = _invoke(tmp_path, transport=transport)

    assert called is False
    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["provider_invoked"] is False
    assert "AIGOL_OPENAI_API_KEY is required" in result["failure_reason"]


def test_unregistered_response_schema_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-openai-key")
    result = _invoke(tmp_path)
    request = dict(result["provider_request"])
    response = dict(result["provider_response"])
    request["provider_schema_id"] = "unknown.schema"
    response["provider_schema_id"] = "unknown.schema"
    request.pop("artifact_hash")
    response.pop("artifact_hash")
    request["artifact_hash"] = replay_hash(request)
    response["artifact_hash"] = replay_hash(response)

    with pytest.raises(FailClosedRuntimeError, match="provider response schema is not registered"):
        normalize_provider_response(provider_response=response, provider_request=request)


def test_replay_tampering_is_detected(tmp_path, monkeypatch):
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-openai-key")
    _invoke(tmp_path)
    path = tmp_path / "native_provider_execution" / "002_provider_response.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["raw_response"] = {"output_text": "tampered"}
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_native_provider_execution_replay(tmp_path / "native_provider_execution")


def test_append_only_replay_violation_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setenv("AIGOL_OPENAI_API_KEY", "test-openai-key")
    _invoke(tmp_path)
    result = _invoke(tmp_path)

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "already exists" in result["failure_reason"]


def test_cli_provider_invoke_command_fails_closed_without_approval_or_credential(tmp_path, monkeypatch):
    monkeypatch.delenv("AIGOL_OPENAI_API_KEY", raising=False)
    parser = build_parser()
    args = parser.parse_args(
        [
            "provider",
            "invoke",
            "--request",
            "Human request without approval.",
            "--runtime-root",
            str(tmp_path),
        ]
    )
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol provider invoke"
    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert result["provider_invoked"] is False
    assert "AIGOL NATIVE PROVIDER EXECUTION" in rendered
    assert FINAL_CLASSIFICATION in rendered
