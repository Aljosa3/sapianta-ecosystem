"""Tests for COGNITION_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.cognition_runtime import (
    COMPLETED,
    FAILED,
    FAILED_CLOSED,
    STARTED,
    STATE,
    reconstruct_cognition_replay,
    run_cognition,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-05-30T07:00:00+00:00"


def _run(tmp_path, **overrides) -> dict:
    args = {
        "cognition_session_id": "COGNITION-SESSION-000001",
        "prompt_id": "HUMAN-PROMPT-COGNITION-000001",
        "human_prompt": "Explain how AiGOL preserves replay.",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "cognition",
    }
    args.update(overrides)
    return run_cognition(**args)


def test_cognition_session_starts_and_completes(tmp_path) -> None:
    capture = _run(tmp_path)
    started = capture["cognition_session_started"]
    state = capture["cognition_runtime_state"]
    terminal = capture["cognition_session_terminal"]

    assert started["event_type"] == STARTED
    assert started["cognition_session_id"] == "COGNITION-SESSION-000001"
    assert started["prompt_text"] == "Explain how AiGOL preserves replay."
    assert state["event_type"] == STATE
    assert state["cognition_status"] == COMPLETED
    assert state["authority"] is False
    assert state["provider_invoked"] is False
    assert state["worker_invoked"] is False
    assert state["execution_requested"] is False
    assert terminal["event_type"] == COMPLETED
    assert terminal["cognition_status"] == COMPLETED


def test_replay_reconstruction_succeeds(tmp_path) -> None:
    _run(tmp_path)
    reconstructed = reconstruct_cognition_replay(tmp_path / "cognition")

    assert reconstructed["cognition_session_id"] == "COGNITION-SESSION-000001"
    assert reconstructed["prompt_id"] == "HUMAN-PROMPT-COGNITION-000001"
    assert reconstructed["prompt"] == "Explain how AiGOL preserves replay."
    assert reconstructed["cognition_status"] == COMPLETED
    assert reconstructed["terminal_event"] == COMPLETED
    assert reconstructed["replay_visible"] is True
    assert reconstructed["authority"] is False
    assert reconstructed["provider_invoked"] is False
    assert reconstructed["worker_invoked"] is False
    assert reconstructed["execution_requested"] is False
    assert reconstructed["intent_id"]
    assert reconstructed["memory_consultation_id"]
    assert reconstructed["response_id"]
    assert reconstructed["conversation_response_id"]


def test_nested_conversation_replay_is_recorded(tmp_path) -> None:
    _run(tmp_path)

    conversation_dir = tmp_path / "cognition" / "conversation_runtime"
    assert (conversation_dir / "000_conversation_started.json").exists()
    assert (conversation_dir / "001_conversation_response_created.json").exists()
    assert (conversation_dir / "002_conversation_response_returned.json").exists()


def test_dependency_failure_fails_cognition_runtime(tmp_path) -> None:
    capture = _run(tmp_path, human_prompt="Inspect runtime status.")
    state = capture["cognition_runtime_state"]
    terminal = capture["cognition_session_terminal"]

    assert state["cognition_status"] == FAILED_CLOSED
    assert "conversation dependency failed" in state["failure_reason"]
    assert terminal["event_type"] == FAILED
    assert terminal["cognition_status"] == FAILED_CLOSED
    assert terminal["reconstruction_metadata"]["response_reconstructable"] is False


def test_memory_dependency_failure_fails_cognition_runtime(tmp_path) -> None:
    capture = _run(tmp_path, artifact_query="MISSING_MEMORY_ARTIFACT")
    state = capture["cognition_runtime_state"]

    assert state["cognition_status"] == FAILED_CLOSED
    assert "conversation dependency failed" in state["failure_reason"]


def test_no_provider_worker_execution_or_authority_introduced(tmp_path) -> None:
    capture = _run(tmp_path)
    state = capture["cognition_runtime_state"]
    terminal = capture["cognition_session_terminal"]
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

    assert forbidden.isdisjoint(state)
    assert state["authority"] is False
    assert terminal["authority"] is False
    assert terminal["reconstruction_metadata"]["authority_introduced"] is False
    assert terminal["reconstruction_metadata"]["provider_invoked"] is False
    assert terminal["reconstruction_metadata"]["worker_invoked"] is False
    assert terminal["reconstruction_metadata"]["execution_requested"] is False


def test_replay_artifacts_are_created(tmp_path) -> None:
    _run(tmp_path)

    started = tmp_path / "cognition" / "000_cognition_session_started.json"
    state = tmp_path / "cognition" / "001_cognition_runtime_state.json"
    completed = tmp_path / "cognition" / "002_cognition_session_completed.json"
    assert started.exists()
    assert state.exists()
    assert completed.exists()
    assert json.loads(started.read_text(encoding="utf-8"))["artifact"]["event_type"] == STARTED
    assert json.loads(state.read_text(encoding="utf-8"))["artifact"]["event_type"] == STATE
    assert json.loads(completed.read_text(encoding="utf-8"))["artifact"]["event_type"] == COMPLETED


def test_append_only_replay_violation_fails_closed(tmp_path) -> None:
    first = _run(tmp_path)
    second = _run(tmp_path)
    reconstructed = reconstruct_cognition_replay(tmp_path / "cognition")

    assert first["cognition_runtime_state"]["cognition_status"] == COMPLETED
    assert second["cognition_runtime_state"]["cognition_status"] == FAILED_CLOSED
    assert "already exists" in second["cognition_runtime_state"]["failure_reason"]
    assert reconstructed["cognition_status"] == COMPLETED


def test_replay_reconstruction_detects_state_corruption(tmp_path) -> None:
    _run(tmp_path)
    path = tmp_path / "cognition" / "001_cognition_runtime_state.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["provider_invoked"] = True
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_cognition_replay(tmp_path / "cognition")


def test_replay_reconstruction_detects_terminal_corruption(tmp_path) -> None:
    _run(tmp_path)
    path = tmp_path / "cognition" / "002_cognition_session_completed.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["state_hash"] = "sha256:bad"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_cognition_replay(tmp_path / "cognition")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _run(tmp_path)
    path = tmp_path / "cognition" / "002_cognition_session_completed.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "cognition_session_started"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_cognition_replay(tmp_path / "cognition")


def test_no_expanded_runtime_surface_imports() -> None:
    import aigol.runtime.cognition_runtime as cognition

    source = inspect.getsource(cognition)

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
