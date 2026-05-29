"""Tests for REAL_PROVIDER_ATTACHMENT_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_attachment import (
    PROVIDER_ATTACHMENT_RECORDED,
    PROVIDER_CAPTURED,
    PROVIDER_FAILED,
    PROVIDER_GOVERNED_RESULT_RETURNED,
    RAW_PROVIDER_RESPONSE_CAPTURED,
    attach_real_provider_response,
    reconstruct_provider_attachment_replay,
)


CREATED_AT = "2026-05-29T07:00:00+00:00"


def _attach(tmp_path, label: str = "000001", **overrides):
    args = {
        "provider_attachment_id": f"PROVIDER-ATTACHMENT-{label}",
        "provider_identity": "openai",
        "provider_response": "Inspect runtime status",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / f"provider_attachment_{label}",
    }
    args.update(overrides)
    return attach_real_provider_response(**args)


def test_valid_provider_response_reaches_external_attachment_path(tmp_path) -> None:
    capture = _attach(tmp_path)
    replay = reconstruct_provider_attachment_replay(tmp_path / "provider_attachment_000001")

    assert capture["provider_identity"]["state"] == PROVIDER_CAPTURED
    assert capture["raw_provider_response"]["state"] == RAW_PROVIDER_RESPONSE_CAPTURED
    assert capture["provider_attachment_record"]["state"] == PROVIDER_ATTACHMENT_RECORDED
    assert capture["governed_result"]["state"] == PROVIDER_GOVERNED_RESULT_RETURNED
    assert capture["governed_result"]["final_status"] == "COMPLETED"
    assert replay["final_status"] == "COMPLETED"
    assert replay["external_attachment_replay"]["final_status"] == "COMPLETED"
    assert replay["lifecycle_transitions"] == [
        PROVIDER_CAPTURED,
        RAW_PROVIDER_RESPONSE_CAPTURED,
        PROVIDER_ATTACHMENT_RECORDED,
        PROVIDER_GOVERNED_RESULT_RETURNED,
    ]


def test_provider_identity_preserved_across_boundary(tmp_path) -> None:
    capture = _attach(tmp_path, provider_identity="Claude_Provider")

    assert capture["provider_identity"]["provider_identity"] == "claude_provider"
    assert capture["raw_provider_response"]["provider_identity"] == "claude_provider"
    assert capture["provider_attachment_record"]["provider_identity"] == "claude_provider"
    assert capture["governed_result"]["provider_identity"] == "claude_provider"


def test_invalid_provider_identity_fails_closed(tmp_path) -> None:
    capture = _attach(tmp_path, provider_identity="open ai")

    assert capture["governed_result"]["final_status"] == PROVIDER_FAILED
    assert "provider_identity must be deterministic" in capture["governed_result"]["failure_reason"]


def test_missing_provider_identity_fails_closed(tmp_path) -> None:
    capture = _attach(tmp_path, provider_identity="")

    assert capture["governed_result"]["final_status"] == PROVIDER_FAILED
    assert "provider_identity is required" in capture["governed_result"]["failure_reason"]


def test_empty_provider_response_fails_closed(tmp_path) -> None:
    capture = _attach(tmp_path, provider_response="")
    replay = reconstruct_provider_attachment_replay(tmp_path / "provider_attachment_000001")

    assert capture["governed_result"]["final_status"] == PROVIDER_FAILED
    assert "provider_response is required" in capture["governed_result"]["failure_reason"]
    assert replay["final_status"] == PROVIDER_FAILED


def test_malformed_provider_response_fails_closed(tmp_path) -> None:
    capture = _attach(tmp_path, provider_response={"text": "Inspect runtime status"})

    assert capture["governed_result"]["final_status"] == PROVIDER_FAILED
    assert "provider_response is required" in capture["governed_result"]["failure_reason"]


def test_replay_visibility_and_ordering(tmp_path) -> None:
    _attach(tmp_path)
    replay_dir = tmp_path / "provider_attachment_000001"

    expected = [
        "000_provider_identity.json",
        "001_raw_provider_response.json",
        "002_provider_attachment_record.json",
        "003_governed_result.json",
    ]
    assert [path.name for path in sorted(replay_dir.glob("*.json"))] == expected


def test_replay_determinism_for_same_inputs_in_distinct_runs(tmp_path) -> None:
    replay_hashes = []
    for index in range(3):
        _attach(tmp_path, label=f"DETERMINISM-{index}")
        replay = reconstruct_provider_attachment_replay(tmp_path / f"provider_attachment_DETERMINISM-{index}")
        replay_hashes.append(replay["replay_hash"])

    assert len(set(replay_hashes)) == 3


def test_repeated_successful_runs_complete(tmp_path) -> None:
    statuses = []
    for index in range(5):
        capture = _attach(tmp_path, label=f"SUCCESS-{index}")
        statuses.append(capture["governed_result"]["final_status"])

    assert statuses == ["COMPLETED"] * 5


def test_repeated_failed_runs_are_replay_visible(tmp_path) -> None:
    statuses = []
    for index in range(5):
        capture = _attach(tmp_path, label=f"FAILED-{index}", provider_response=" ")
        replay = reconstruct_provider_attachment_replay(tmp_path / f"provider_attachment_FAILED-{index}")
        statuses.append(replay["final_status"])
        assert capture["governed_result"]["failure_reason"] == "provider_response is required"

    assert statuses == [PROVIDER_FAILED] * 5


def test_append_only_violation_fails_closed(tmp_path) -> None:
    _attach(tmp_path)
    capture = _attach(tmp_path)

    assert capture["governed_result"]["final_status"] == PROVIDER_FAILED
    assert "already exists" in capture["governed_result"]["failure_reason"]


def test_replay_corruption_detected(tmp_path) -> None:
    _attach(tmp_path)
    artifact_path = tmp_path / "provider_attachment_000001" / "001_raw_provider_response.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["artifact"]["raw_provider_response"] = "tampered"
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_provider_attachment_replay(tmp_path / "provider_attachment_000001")


def test_authority_separation_preserved(tmp_path) -> None:
    capture = _attach(tmp_path)
    result = capture["governed_result"]

    assert result["provider_execution_authority"] is False
    assert result["provider_authorization_authority"] is False
    assert result["provider_governance_authority"] is False
    assert result["provider_replay_authority"] is False


def test_no_provider_sdk_or_network_imports() -> None:
    import aigol.runtime.provider_attachment as provider_attachment

    source = inspect.getsource(provider_attachment)

    assert "openai" not in source.lower()
    assert "anthropic" not in source.lower()
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "subprocess" not in source
    assert "async " not in source
    assert "await " not in source
