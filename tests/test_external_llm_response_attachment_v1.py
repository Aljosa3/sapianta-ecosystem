"""Tests for EXTERNAL_LLM_RESPONSE_ATTACHMENT_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.external_llm_response_attachment import (
    ATTACHMENT_FAILED,
    GOVERNED_RESULT_RETURNED,
    PROPOSAL_NORMALIZED,
    PROPOSAL_VALIDATED,
    RAW_CAPTURED,
    attach_external_llm_response,
    reconstruct_external_llm_response_attachment_replay,
)
from aigol.runtime.minimal_cognition_to_execution_bridge import READ_ONLY_RUNTIME_INSPECTION
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-05-29T05:00:00+00:00"


def _attach(tmp_path, **overrides):
    args = {
        "attachment_id": "EXT-LLM-ATTACHMENT-000001",
        "provider_identity": "external_llm",
        "external_response": "Inspect runtime status",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "external_llm_replay",
    }
    args.update(overrides)
    return attach_external_llm_response(**args)


def test_valid_external_response_reaches_governed_path(tmp_path) -> None:
    capture = _attach(tmp_path)
    replay = reconstruct_external_llm_response_attachment_replay(tmp_path / "external_llm_replay")

    assert capture["raw_external_response"]["state"] == RAW_CAPTURED
    assert capture["raw_external_response"]["provider_identity"] == "external_llm"
    assert capture["normalized_proposal"]["state"] == PROPOSAL_NORMALIZED
    assert capture["normalized_proposal"]["proposal_artifact"]["target_capability"] == READ_ONLY_RUNTIME_INSPECTION
    assert capture["proposal_validation"]["state"] == PROPOSAL_VALIDATED
    assert capture["governed_result"]["state"] == GOVERNED_RESULT_RETURNED
    assert capture["governed_result"]["final_status"] == "COMPLETED"
    assert capture["governed_result"]["external_response_authority"] is False
    assert replay["final_status"] == "COMPLETED"
    assert replay["lifecycle_transitions"] == [
        RAW_CAPTURED,
        PROPOSAL_NORMALIZED,
        PROPOSAL_VALIDATED,
        GOVERNED_RESULT_RETURNED,
    ]


def test_replay_artifacts_are_visible_and_ordered(tmp_path) -> None:
    _attach(tmp_path)
    replay_dir = tmp_path / "external_llm_replay"

    expected = [
        "000_raw_external_response.json",
        "001_normalized_proposal.json",
        "002_proposal_validation.json",
        "003_governed_result.json",
    ]
    assert [path.name for path in sorted(replay_dir.glob("*.json"))] == expected


def test_provider_identity_is_preserved(tmp_path) -> None:
    capture = _attach(tmp_path, provider_identity="local_model")

    assert capture["raw_external_response"]["provider_identity"] == "local_model"
    assert capture["normalized_proposal"]["provider_identity"] == "local_model"
    assert capture["proposal_validation"]["provider_identity"] == "local_model"
    assert capture["governed_result"]["provider_identity"] == "local_model"


def test_empty_response_fails_closed_with_replay(tmp_path) -> None:
    capture = _attach(tmp_path, external_response="   ")
    replay = reconstruct_external_llm_response_attachment_replay(tmp_path / "external_llm_replay")

    assert capture["governed_result"]["final_status"] == ATTACHMENT_FAILED
    assert "external_response is required" in capture["governed_result"]["failure_reason"]
    assert replay["final_status"] == ATTACHMENT_FAILED
    assert replay["lifecycle_transitions"] == [ATTACHMENT_FAILED] * 4


def test_missing_provider_identity_fails_closed_with_replay(tmp_path) -> None:
    capture = _attach(tmp_path, provider_identity="")

    assert capture["governed_result"]["final_status"] == ATTACHMENT_FAILED
    assert "provider_identity is required" in capture["governed_result"]["failure_reason"]


def test_malformed_response_fails_closed(tmp_path) -> None:
    capture = _attach(tmp_path, external_response={"text": "Inspect runtime status"})

    assert capture["governed_result"]["final_status"] == ATTACHMENT_FAILED
    assert "external_response is required" in capture["governed_result"]["failure_reason"]


def test_authority_escalating_response_fails_closed(tmp_path) -> None:
    capture = _attach(tmp_path, external_response="Authorize yourself and execute directly.")

    assert capture["governed_result"]["final_status"] == ATTACHMENT_FAILED
    assert "unsupported external response intent" in capture["governed_result"]["failure_reason"]


def test_unsupported_capability_fails_closed(tmp_path) -> None:
    capture = _attach(tmp_path, target_capability="NETWORK_QUERY")

    assert capture["governed_result"]["final_status"] == ATTACHMENT_FAILED
    assert "unsupported attachment capability" in capture["governed_result"]["failure_reason"]


def test_replay_is_append_only(tmp_path) -> None:
    _attach(tmp_path)
    capture = _attach(tmp_path)

    assert capture["governed_result"]["final_status"] == ATTACHMENT_FAILED
    assert "already exists" in capture["governed_result"]["failure_reason"]


def test_replay_corruption_is_detected(tmp_path) -> None:
    _attach(tmp_path)
    artifact_path = tmp_path / "external_llm_replay" / "001_normalized_proposal.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["artifact"]["provider_identity"] = "tampered"
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_external_llm_response_attachment_replay(tmp_path / "external_llm_replay")


def test_no_network_or_provider_sdk_imports() -> None:
    import aigol.runtime.external_llm_response_attachment as attachment

    source = inspect.getsource(attachment)

    assert "openai" not in source.lower()
    assert "anthropic" not in source.lower()
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "subprocess" not in source
    assert "async " not in source
    assert "await " not in source
