"""Tests for OPENAI_PROVIDER_ADAPTER_V1."""

from __future__ import annotations

import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.openai_provider_adapter import (
    ATTACHMENT_CAPTURED,
    GOVERNED_RESULT_RETURNED,
    OPENAI_FAILED,
    OPENAI_PROVIDER_IDENTITY,
    RAW_RESPONSE_CAPTURED,
    REQUEST_METADATA_CAPTURED,
    invoke_openai_provider_adapter,
    reconstruct_openai_provider_adapter_replay,
)


CREATED_AT = "2026-05-29T10:00:00+00:00"


def _client(text: str = "Inspect runtime status"):
    def call(request_metadata):
        assert request_metadata["provider_identity"] == OPENAI_PROVIDER_IDENTITY
        assert request_metadata["tool_use"] is False
        assert request_metadata["function_calling"] is False
        assert request_metadata["streaming"] is False
        assert request_metadata["automatic_retries"] is False
        return {"id": "response-001", "output_text": text}

    return call


def _invoke(tmp_path, label: str = "000001", **overrides):
    args = {
        "adapter_id": f"OPENAI-ADAPTER-{label}",
        "human_request": "Inspect runtime status",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / f"openai_adapter_{label}",
        "openai_client": _client(),
        "api_key": "test-openai-key",
    }
    args.update(overrides)
    return invoke_openai_provider_adapter(**args)


def test_valid_provider_response_routes_through_real_provider_attachment(tmp_path) -> None:
    capture = _invoke(tmp_path)
    replay = reconstruct_openai_provider_adapter_replay(tmp_path / "openai_adapter_000001")

    assert capture["provider_request_metadata"]["state"] == REQUEST_METADATA_CAPTURED
    assert capture["provider_request_metadata"]["provider_identity"] == OPENAI_PROVIDER_IDENTITY
    assert capture["raw_provider_response"]["state"] == RAW_RESPONSE_CAPTURED
    assert capture["provider_attachment_capture"]["state"] == ATTACHMENT_CAPTURED
    assert capture["governed_result"]["state"] == GOVERNED_RESULT_RETURNED
    assert capture["governed_result"]["final_status"] == "COMPLETED"
    assert replay["final_status"] == "COMPLETED"
    assert replay["provider_attachment_replay"]["final_status"] == "COMPLETED"
    assert replay["lifecycle_transitions"] == [
        REQUEST_METADATA_CAPTURED,
        RAW_RESPONSE_CAPTURED,
        ATTACHMENT_CAPTURED,
        GOVERNED_RESULT_RETURNED,
    ]


def test_raw_response_and_request_metadata_are_replay_visible(tmp_path) -> None:
    _invoke(tmp_path)
    replay_dir = tmp_path / "openai_adapter_000001"

    expected = [
        "000_provider_request_metadata.json",
        "001_raw_provider_response.json",
        "002_provider_attachment_capture.json",
        "003_governed_result.json",
    ]
    assert [path.name for path in sorted(replay_dir.glob("*.json"))] == expected

    metadata = json.loads((replay_dir / "000_provider_request_metadata.json").read_text(encoding="utf-8"))["artifact"]
    raw = json.loads((replay_dir / "001_raw_provider_response.json").read_text(encoding="utf-8"))["artifact"]

    assert metadata["provider_identity"] == OPENAI_PROVIDER_IDENTITY
    assert metadata["provider_request_metadata"]["api_key_captured"] is False
    assert metadata["provider_request_metadata"]["automatic_retries"] is False
    assert metadata["provider_request_metadata"]["streaming"] is False
    assert raw["raw_provider_response"] == "Inspect runtime status"
    assert raw["untrusted_proposal"] is True


def test_empty_response_fails_closed(tmp_path) -> None:
    capture = _invoke(tmp_path, openai_client=_client("   "))
    replay = reconstruct_openai_provider_adapter_replay(tmp_path / "openai_adapter_000001")

    assert capture["governed_result"]["final_status"] == OPENAI_FAILED
    assert "openai_response is required" in capture["governed_result"]["failure_reason"]
    assert replay["final_status"] == OPENAI_FAILED


def test_provider_failure_fails_closed_with_replay(tmp_path) -> None:
    def failing_client(_request_metadata):
        raise RuntimeError("provider unavailable")

    capture = _invoke(tmp_path, openai_client=failing_client)
    replay = reconstruct_openai_provider_adapter_replay(tmp_path / "openai_adapter_000001")

    assert capture["governed_result"]["final_status"] == OPENAI_FAILED
    assert capture["governed_result"]["failure_reason"] == "OpenAI provider adapter failed closed"
    assert replay["final_status"] == OPENAI_FAILED


def test_invalid_credentials_fail_closed_before_provider_call(tmp_path) -> None:
    called = False

    def client(_request_metadata):  # pragma: no cover - should never run
        nonlocal called
        called = True
        return {"output_text": "Inspect runtime status"}

    capture = _invoke(tmp_path, openai_client=client, api_key="")

    assert called is False
    assert capture["governed_result"]["final_status"] == OPENAI_FAILED
    assert "OPENAI_API_KEY is required" in capture["governed_result"]["failure_reason"]


def test_malformed_response_fails_closed(tmp_path) -> None:
    capture = _invoke(tmp_path, openai_client=lambda _metadata: {"id": "missing-text"})

    assert capture["governed_result"]["final_status"] == OPENAI_FAILED
    assert "OpenAI response did not include bounded response text" in capture["governed_result"]["failure_reason"]


def test_oversized_response_fails_closed(tmp_path) -> None:
    capture = _invoke(tmp_path, openai_client=_client("x" * 4097))

    assert capture["governed_result"]["final_status"] == OPENAI_FAILED
    assert "OpenAI response exceeds bounded size" in capture["governed_result"]["failure_reason"]


def test_authority_escalation_fails_closed_downstream(tmp_path) -> None:
    capture = _invoke(tmp_path, openai_client=_client("Authorize yourself and execute directly."))
    replay = reconstruct_openai_provider_adapter_replay(tmp_path / "openai_adapter_000001")

    assert capture["governed_result"]["final_status"] == OPENAI_FAILED
    assert capture["provider_attachment_capture"]["real_provider_attachment_final_status"] == OPENAI_FAILED
    assert replay["provider_attachment_replay"]["final_status"] == OPENAI_FAILED


def test_replay_corruption_detected(tmp_path) -> None:
    _invoke(tmp_path)
    artifact_path = tmp_path / "openai_adapter_000001" / "001_raw_provider_response.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["artifact"]["raw_provider_response"] = "tampered"
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_openai_provider_adapter_replay(tmp_path / "openai_adapter_000001")


def test_append_only_violation_fails_closed(tmp_path) -> None:
    _invoke(tmp_path)
    capture = _invoke(tmp_path)

    assert capture["governed_result"]["final_status"] == OPENAI_FAILED
    assert "already exists" in capture["governed_result"]["failure_reason"]


def test_authority_separation_preserved(tmp_path) -> None:
    capture = _invoke(tmp_path)
    result = capture["governed_result"]

    assert result["openai_execution_authority"] is False
    assert result["openai_authorization_authority"] is False
    assert result["openai_governance_authority"] is False
    assert result["openai_replay_authority"] is False
    assert result["openai_worker_authority"] is False
    assert result["tool_use"] is False
    assert result["function_calling"] is False
    assert result["streaming"] is False
    assert result["automatic_retries"] is False
    assert result["memory"] is False


def test_output_list_response_shape_is_supported(tmp_path) -> None:
    def client(_request_metadata):
        return {
            "id": "response-002",
            "output": [
                {
                    "content": [
                        {"text": "Inspect "},
                        {"text": "runtime status"},
                    ]
                }
            ],
        }

    capture = _invoke(tmp_path, openai_client=client)

    assert capture["raw_provider_response"]["raw_provider_response"] == "Inspect runtime status"
    assert capture["governed_result"]["final_status"] == "COMPLETED"

