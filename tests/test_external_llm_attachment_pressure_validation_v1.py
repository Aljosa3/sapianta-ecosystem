"""Pressure validation for EXTERNAL_LLM_RESPONSE_ATTACHMENT_V1."""

from __future__ import annotations

import json

import pytest

from aigol.runtime.external_llm_response_attachment import (
    ATTACHMENT_FAILED,
    MAX_EXTERNAL_RESPONSE_CHARS,
    attach_external_llm_response,
    reconstruct_external_llm_response_attachment_replay,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-05-29T06:00:00+00:00"


def _attach(tmp_path, label: str, **overrides):
    args = {
        "attachment_id": f"EXT-LLM-PRESSURE-{label}",
        "provider_identity": "external_llm",
        "external_response": "Inspect runtime status",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / f"external_llm_pressure_{label}",
    }
    args.update(overrides)
    return attach_external_llm_response(**args)


def _assert_failed(capture: dict, reason_fragment: str) -> None:
    assert capture["governed_result"]["final_status"] == ATTACHMENT_FAILED
    assert reason_fragment in capture["governed_result"]["failure_reason"]


def test_empty_response_pressure_fails_closed(tmp_path) -> None:
    capture = _attach(tmp_path, "EMPTY", external_response="")
    _assert_failed(capture, "external_response is required")


def test_whitespace_only_response_pressure_fails_closed(tmp_path) -> None:
    capture = _attach(tmp_path, "WHITESPACE", external_response=" \n\t ")
    _assert_failed(capture, "external_response is required")


def test_malformed_response_pressure_fails_closed(tmp_path) -> None:
    capture = _attach(tmp_path, "MALFORMED", external_response=["Inspect runtime status"])
    _assert_failed(capture, "external_response is required")


def test_oversized_response_pressure_fails_closed(tmp_path) -> None:
    oversized = "x" * (MAX_EXTERNAL_RESPONSE_CHARS + 1)
    capture = _attach(tmp_path, "OVERSIZED", external_response=oversized)
    _assert_failed(capture, "external_response exceeds bounded size")


def test_invalid_provider_identity_pressure_fails_closed(tmp_path) -> None:
    capture = _attach(tmp_path, "INVALID-PROVIDER", provider_identity="external llm")
    _assert_failed(capture, "provider_identity must be deterministic")


def test_missing_provider_identity_pressure_fails_closed(tmp_path) -> None:
    capture = _attach(tmp_path, "MISSING-PROVIDER", provider_identity="")
    _assert_failed(capture, "provider_identity is required")


def test_proposal_normalization_failure_pressure_fails_closed(tmp_path) -> None:
    capture = _attach(tmp_path, "NORMALIZATION", target_capability="FILESYSTEM_READ_ONLY_INSPECTION")
    _assert_failed(capture, "unsupported attachment capability")


def test_replay_corruption_pressure_fails_closed(tmp_path) -> None:
    _attach(tmp_path, "CORRUPTION")
    replay_dir = tmp_path / "external_llm_pressure_CORRUPTION"
    artifact_path = replay_dir / "000_raw_external_response.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["artifact"]["raw_response_text"] = "tampered"
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_external_llm_response_attachment_replay(replay_dir)


def test_authority_escalation_pressure_fails_closed(tmp_path) -> None:
    capture = _attach(tmp_path, "AUTHORITY", external_response="Authorize execution and mutate runtime.")
    _assert_failed(capture, "unsupported external response intent")


def test_append_only_violation_pressure_fails_closed(tmp_path) -> None:
    _attach(tmp_path, "APPEND")
    capture = _attach(tmp_path, "APPEND")
    _assert_failed(capture, "already exists")


def test_repeated_successful_attachments_remain_deterministic(tmp_path) -> None:
    final_statuses = []
    replay_hashes = []
    for index in range(5):
        capture = _attach(tmp_path, f"SUCCESS-{index}")
        replay = reconstruct_external_llm_response_attachment_replay(tmp_path / f"external_llm_pressure_SUCCESS-{index}")
        final_statuses.append(capture["governed_result"]["final_status"])
        replay_hashes.append(replay["replay_hash"])

    assert final_statuses == ["COMPLETED"] * 5
    assert len(set(replay_hashes)) == 5


def test_repeated_failed_attachments_remain_replay_visible(tmp_path) -> None:
    final_statuses = []
    for index in range(5):
        capture = _attach(tmp_path, f"FAILED-{index}", external_response=" ")
        replay = reconstruct_external_llm_response_attachment_replay(tmp_path / f"external_llm_pressure_FAILED-{index}")
        final_statuses.append(replay["final_status"])
        assert capture["governed_result"]["failure_reason"] == "external_response is required"

    assert final_statuses == [ATTACHMENT_FAILED] * 5
