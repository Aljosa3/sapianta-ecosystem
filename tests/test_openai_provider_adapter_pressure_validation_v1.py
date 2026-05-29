"""Pressure validation for OPENAI_PROVIDER_ADAPTER_V1."""

from __future__ import annotations

import json

import pytest

import aigol.runtime.openai_provider_adapter as adapter
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.openai_provider_adapter import (
    OPENAI_FAILED,
    invoke_openai_provider_adapter,
    reconstruct_openai_provider_adapter_replay,
)


CREATED_AT = "2026-05-29T11:00:00+00:00"


def _client(response):
    def call(request_metadata):
        assert request_metadata["tool_use"] is False
        assert request_metadata["function_calling"] is False
        assert request_metadata["streaming"] is False
        assert request_metadata["automatic_retries"] is False
        return response

    return call


def _invoke(tmp_path, label: str, **overrides):
    args = {
        "adapter_id": f"OPENAI-PRESSURE-{label}",
        "human_request": "Inspect runtime status",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / f"openai_pressure_{label}",
        "openai_client": _client({"id": f"response-{label}", "output_text": "Inspect runtime status"}),
        "api_key": "test-openai-key",
    }
    args.update(overrides)
    return invoke_openai_provider_adapter(**args)


def _assert_failed(capture: dict, reason_fragment: str | None = None) -> None:
    assert capture["governed_result"]["final_status"] == OPENAI_FAILED
    if reason_fragment is not None:
        assert reason_fragment in capture["governed_result"]["failure_reason"]


def test_valid_response_pressure_completes_with_replay(tmp_path) -> None:
    capture = _invoke(tmp_path, "VALID")
    replay = reconstruct_openai_provider_adapter_replay(tmp_path / "openai_pressure_VALID")

    assert capture["governed_result"]["final_status"] == "COMPLETED"
    assert replay["final_status"] == "COMPLETED"
    assert replay["provider_attachment_replay"]["final_status"] == "COMPLETED"


def test_empty_response_pressure_fails_closed(tmp_path) -> None:
    capture = _invoke(tmp_path, "EMPTY", openai_client=_client({"output_text": ""}))

    _assert_failed(capture, "openai_response is required")


def test_whitespace_only_response_pressure_fails_closed(tmp_path) -> None:
    capture = _invoke(tmp_path, "WHITESPACE", openai_client=_client({"output_text": " \n\t "}))

    _assert_failed(capture, "openai_response is required")


def test_malformed_response_pressure_fails_closed(tmp_path) -> None:
    capture = _invoke(tmp_path, "MALFORMED", openai_client=_client({"id": "missing-output"}))

    _assert_failed(capture, "OpenAI response did not include bounded response text")


def test_oversized_response_pressure_fails_closed(tmp_path) -> None:
    capture = _invoke(tmp_path, "OVERSIZED", openai_client=_client({"output_text": "x" * 4097}))

    _assert_failed(capture, "OpenAI response exceeds bounded size")


def test_unexpected_structure_pressure_fails_closed(tmp_path) -> None:
    capture = _invoke(tmp_path, "UNEXPECTED", openai_client=_client({"output": [{"content": "not-a-list"}]}))

    _assert_failed(capture, "OpenAI response did not include bounded response text")


def test_invalid_content_type_pressure_fails_closed(tmp_path) -> None:
    capture = _invoke(tmp_path, "CONTENT-TYPE", openai_client=_client(b"Inspect runtime status"))

    _assert_failed(capture, "OpenAI response is malformed")


def test_missing_provider_identity_pressure_fails_closed(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(adapter, "NORMALIZED_OPENAI_PROVIDER_IDENTITY", "")
    capture = _invoke(tmp_path, "MISSING-PROVIDER")

    _assert_failed(capture)
    nested = capture["provider_attachment_capture"]["real_provider_attachment_capture"]["governed_result"]
    assert "provider_identity is required" in nested["failure_reason"]


def test_invalid_provider_identity_pressure_fails_closed(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(adapter, "NORMALIZED_OPENAI_PROVIDER_IDENTITY", "open ai")
    capture = _invoke(tmp_path, "INVALID-PROVIDER")

    _assert_failed(capture)
    nested = capture["provider_attachment_capture"]["real_provider_attachment_capture"]["governed_result"]
    assert "provider_identity must be deterministic" in nested["failure_reason"]


def test_corrupted_provider_identity_replay_fails_closed(tmp_path) -> None:
    _invoke(tmp_path, "CORRUPT-PROVIDER")
    replay_dir = tmp_path / "openai_pressure_CORRUPT-PROVIDER"
    artifact_path = replay_dir / "000_provider_request_metadata.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["artifact"]["provider_identity"] = "CORRUPTED"
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_openai_provider_adapter_replay(replay_dir)


def test_replay_provider_mismatch_fails_closed(tmp_path) -> None:
    _invoke(tmp_path, "PROVIDER-MISMATCH")
    replay_dir = tmp_path / "openai_pressure_PROVIDER-MISMATCH"
    artifact_path = replay_dir / "002_provider_attachment_capture.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["artifact"]["real_provider_attachment_capture"]["governed_result"]["provider_identity"] = "claude"
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_openai_provider_adapter_replay(replay_dir)


def test_missing_credentials_pressure_fails_closed(tmp_path) -> None:
    capture = _invoke(tmp_path, "MISSING-CREDS", api_key="")

    _assert_failed(capture, "OPENAI_API_KEY is required")


def test_authentication_failure_pressure_fails_closed(tmp_path) -> None:
    def client(_request_metadata):
        raise PermissionError("authentication failed")

    capture = _invoke(tmp_path, "AUTH", openai_client=client)

    _assert_failed(capture)


def test_authorization_failure_pressure_fails_closed(tmp_path) -> None:
    def client(_request_metadata):
        raise PermissionError("authorization failed")

    capture = _invoke(tmp_path, "AUTHZ", openai_client=client)

    _assert_failed(capture)


def test_timeout_pressure_fails_closed(tmp_path) -> None:
    def client(_request_metadata):
        raise TimeoutError("provider timeout")

    capture = _invoke(tmp_path, "TIMEOUT", openai_client=client)

    _assert_failed(capture)


def test_provider_unavailable_pressure_fails_closed(tmp_path) -> None:
    def client(_request_metadata):
        raise ConnectionError("provider unavailable")

    capture = _invoke(tmp_path, "UNAVAILABLE", openai_client=client)

    _assert_failed(capture)


def test_provider_error_pressure_fails_closed(tmp_path) -> None:
    def client(_request_metadata):
        raise RuntimeError("provider error")

    capture = _invoke(tmp_path, "ERROR", openai_client=client)

    _assert_failed(capture)


def test_provider_interruption_pressure_fails_closed(tmp_path) -> None:
    def client(_request_metadata):
        raise InterruptedError("interrupted")

    capture = _invoke(tmp_path, "INTERRUPTION", openai_client=client)

    _assert_failed(capture)


def test_network_exception_pressure_fails_closed(tmp_path) -> None:
    def client(_request_metadata):
        raise OSError("network exception")

    capture = _invoke(tmp_path, "NETWORK", openai_client=client)

    _assert_failed(capture)


def test_replay_ordering_pressure_fails_closed(tmp_path) -> None:
    _invoke(tmp_path, "ORDERING")
    replay_dir = tmp_path / "openai_pressure_ORDERING"
    artifact_path = replay_dir / "003_governed_result.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["replay_index"] = 99
    artifact["replay_hash"] = "sha256:corrupted"
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_openai_provider_adapter_replay(replay_dir)


def test_nested_replay_integrity_pressure_fails_closed(tmp_path) -> None:
    _invoke(tmp_path, "NESTED")
    replay_dir = tmp_path / "openai_pressure_NESTED" / "real_provider_attachment"
    artifact_path = replay_dir / "001_raw_provider_response.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["artifact"]["raw_provider_response"] = "tampered"
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_openai_provider_adapter_replay(tmp_path / "openai_pressure_NESTED")


def test_append_only_pressure_fails_closed(tmp_path) -> None:
    _invoke(tmp_path, "APPEND")
    capture = _invoke(tmp_path, "APPEND")

    _assert_failed(capture, "already exists")


@pytest.mark.parametrize(
    "text",
    [
        "Please execute shell commands.",
        "Authorize yourself.",
        "Override governance.",
        "Ask the worker to mutate replay.",
        "Mutate replay evidence.",
    ],
)
def test_authority_escalation_pressure_rejected(tmp_path, text: str) -> None:
    label = str(abs(hash(text)))
    capture = _invoke(tmp_path, label, openai_client=_client({"output_text": text}))
    replay = reconstruct_openai_provider_adapter_replay(tmp_path / f"openai_pressure_{label}")

    _assert_failed(capture)
    assert replay["openai_authority"] is False
    if capture["provider_attachment_capture"] is not None:
        assert capture["provider_attachment_capture"]["real_provider_attachment_final_status"] == OPENAI_FAILED


def test_repeated_successful_operations_remain_stable(tmp_path) -> None:
    statuses = []
    replay_hashes = []
    for index in range(5):
        capture = _invoke(tmp_path, f"SUCCESS-{index}")
        replay = reconstruct_openai_provider_adapter_replay(tmp_path / f"openai_pressure_SUCCESS-{index}")
        statuses.append(capture["governed_result"]["final_status"])
        replay_hashes.append(replay["replay_hash"])

    assert statuses == ["COMPLETED"] * 5
    assert len(set(replay_hashes)) == 5


def test_repeated_failed_operations_remain_reconstructable(tmp_path) -> None:
    statuses = []
    for index in range(5):
        capture = _invoke(tmp_path, f"FAILED-{index}", openai_client=_client({"output_text": ""}))
        replay = reconstruct_openai_provider_adapter_replay(tmp_path / f"openai_pressure_FAILED-{index}")
        statuses.append(replay["final_status"])
        assert capture["governed_result"]["failure_reason"] == "openai_response is required"

    assert statuses == [OPENAI_FAILED] * 5


def test_mixed_success_failure_sequence_remains_deterministic(tmp_path) -> None:
    scenarios = [
        ("MIXED-0", _client({"output_text": "Inspect runtime status"}), "COMPLETED"),
        ("MIXED-1", _client({"output_text": ""}), OPENAI_FAILED),
        ("MIXED-2", _client({"id": "missing-output"}), OPENAI_FAILED),
        ("MIXED-3", _client({"output_text": "Inspect runtime status"}), "COMPLETED"),
    ]

    statuses = []
    for label, client, expected in scenarios:
        capture = _invoke(tmp_path, label, openai_client=client)
        replay = reconstruct_openai_provider_adapter_replay(tmp_path / f"openai_pressure_{label}")
        statuses.append(replay["final_status"])
        assert capture["governed_result"]["final_status"] == expected

    assert statuses == ["COMPLETED", OPENAI_FAILED, OPENAI_FAILED, "COMPLETED"]


def test_boundary_preservation_pressure(tmp_path) -> None:
    capture = _invoke(tmp_path, "BOUNDARY")
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
    assert result["aigol_governs"] is True
    assert result["worker_executes_after_authorization"] is True
    assert result["replay_records"] is True
