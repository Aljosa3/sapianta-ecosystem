"""Tests for CONVERSATION_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.conversation_runtime import (
    CONVERSATION_RESPONSE,
    CONVERSATION_RESPONSE_ARTIFACT_V1,
    CREATED,
    FAILED_CLOSED,
    RETURNED,
    STARTED,
    reconstruct_conversation_replay,
    run_conversation,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-05-30T06:00:00+00:00"


def _run(tmp_path, **overrides) -> dict:
    args = {
        "conversation_id": "CONVERSATION-000001",
        "prompt_id": "HUMAN-PROMPT-CONVERSATION-000001",
        "human_prompt": "Explain how AiGOL preserves replay.",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "conversation",
    }
    args.update(overrides)
    return run_conversation(**args)


def test_conversation_starts_successfully(tmp_path) -> None:
    capture = _run(tmp_path)
    started = capture["conversation_started"]

    assert started["event_type"] == STARTED
    assert started["conversation_id"] == "CONVERSATION-000001"
    assert started["prompt_id"] == "HUMAN-PROMPT-CONVERSATION-000001"
    assert started["prompt_text"] == "Explain how AiGOL preserves replay."
    assert started["authority"] is False
    assert started["replay_visible"] is True


def test_response_returned_successfully(tmp_path) -> None:
    capture = _run(tmp_path)
    response = capture["conversation_response_artifact"]
    returned = capture["conversation_response_replay"]

    assert response["artifact_type"] == CONVERSATION_RESPONSE_ARTIFACT_V1
    assert response["response_type"] == CONVERSATION_RESPONSE
    assert response["conversation_status"] == CREATED
    assert response["authority"] is False
    assert response["replay_visible"] is True
    assert "Constitutional Memory evidence references" in response["response_text"]
    assert returned["event_type"] == RETURNED
    assert returned["conversation_status"] == RETURNED
    assert returned["reconstruction_metadata"]["provider_invoked"] is False
    assert returned["reconstruction_metadata"]["worker_invoked"] is False


def test_replay_reconstruction_succeeds(tmp_path) -> None:
    _run(tmp_path)
    reconstructed = reconstruct_conversation_replay(tmp_path / "conversation")

    assert reconstructed["conversation_id"] == "CONVERSATION-000001"
    assert reconstructed["prompt_id"] == "HUMAN-PROMPT-CONVERSATION-000001"
    assert reconstructed["prompt"] == "Explain how AiGOL preserves replay."
    assert reconstructed["response_type"] == CONVERSATION_RESPONSE
    assert reconstructed["conversation_status"] == CREATED
    assert reconstructed["replay_visible"] is True
    assert reconstructed["authority"] is False
    assert reconstructed["provider_invoked"] is False
    assert reconstructed["worker_invoked"] is False
    assert reconstructed["execution_requested"] is False
    assert reconstructed["citation_bundle_id"] == "CONVERSATION-000001:MEMORY_CONSULTATION:MEMORY_RETRIEVAL"


def test_fail_closed_when_prompt_is_not_conversation_intent(tmp_path) -> None:
    capture = _run(tmp_path, human_prompt="Inspect runtime status.")
    response = capture["conversation_response_artifact"]
    returned = capture["conversation_response_replay"]

    assert response["conversation_status"] == FAILED_CLOSED
    assert response["response_text"] == ""
    assert "not conversation intent" in response["failure_reason"]
    assert returned["event_type"] == FAILED_CLOSED
    assert returned["conversation_status"] == FAILED_CLOSED


def test_fail_closed_when_memory_consultation_dependency_fails(tmp_path) -> None:
    capture = _run(tmp_path, artifact_query="MISSING_MEMORY_ARTIFACT")
    response = capture["conversation_response_artifact"]

    assert response["conversation_status"] == FAILED_CLOSED
    assert response["response_text"] == ""
    assert "memory consultation failed" in response["failure_reason"]


def test_no_provider_worker_or_authority_introduced(tmp_path) -> None:
    capture = _run(tmp_path)
    response = capture["conversation_response_artifact"]
    returned = capture["conversation_response_replay"]
    forbidden = {
        "authorization_decision",
        "governance_decision",
        "execution_request",
        "provider_request",
        "worker_request",
        "worker_instruction",
        "provider_command",
        "worker_command",
    }

    assert forbidden.isdisjoint(response)
    assert response["authority"] is False
    assert returned["authority"] is False
    assert returned["reconstruction_metadata"]["authority_introduced"] is False
    assert returned["reconstruction_metadata"]["execution_requested"] is False
    assert returned["reconstruction_metadata"]["provider_invoked"] is False
    assert returned["reconstruction_metadata"]["worker_invoked"] is False


def test_replay_artifacts_are_created(tmp_path) -> None:
    _run(tmp_path)

    started = tmp_path / "conversation" / "000_conversation_started.json"
    created = tmp_path / "conversation" / "001_conversation_response_created.json"
    returned = tmp_path / "conversation" / "002_conversation_response_returned.json"
    assert started.exists()
    assert created.exists()
    assert returned.exists()
    assert json.loads(started.read_text(encoding="utf-8"))["artifact"]["event_type"] == STARTED
    assert json.loads(created.read_text(encoding="utf-8"))["artifact"]["conversation_status"] == CREATED
    assert json.loads(returned.read_text(encoding="utf-8"))["artifact"]["event_type"] == RETURNED


def test_append_only_replay_violation_fails_closed(tmp_path) -> None:
    first = _run(tmp_path)
    second = _run(tmp_path)
    reconstructed = reconstruct_conversation_replay(tmp_path / "conversation")

    assert first["conversation_response_artifact"]["conversation_status"] == CREATED
    assert second["conversation_response_artifact"]["conversation_status"] == FAILED_CLOSED
    assert "already exists" in second["conversation_response_artifact"]["failure_reason"]
    assert reconstructed["conversation_status"] == CREATED


def test_replay_reconstruction_detects_response_corruption(tmp_path) -> None:
    _run(tmp_path)
    path = tmp_path / "conversation" / "001_conversation_response_created.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["response_text"] = "tampered"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_conversation_replay(tmp_path / "conversation")


def test_replay_reconstruction_detects_returned_corruption(tmp_path) -> None:
    _run(tmp_path)
    path = tmp_path / "conversation" / "002_conversation_response_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["response_artifact_hash"] = "sha256:bad"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_conversation_replay(tmp_path / "conversation")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _run(tmp_path)
    path = tmp_path / "conversation" / "002_conversation_response_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "conversation_started"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_conversation_replay(tmp_path / "conversation")


def test_no_expanded_runtime_surface_imports() -> None:
    import aigol.runtime.conversation_runtime as conversation

    source = inspect.getsource(conversation)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "openai" not in source.lower()
    assert "anthropic" not in source.lower()
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
