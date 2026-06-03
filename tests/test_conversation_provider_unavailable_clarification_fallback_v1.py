"""Tests for AIGOL_CONVERSATION_PROVIDER_UNAVAILABLE_CLARIFICATION_FALLBACK_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.conversation_provider_unavailable_clarification_fallback import (
    FAILED_CLOSED,
    HUMAN_CLARIFICATION_REQUIRED,
    reconstruct_conversation_provider_unavailable_clarification_fallback_replay,
    run_conversation_provider_unavailable_clarification_fallback,
)
from aigol.runtime.intent_clarification_dialog_runtime import HUMAN_CLARIFICATION_REQUEST_ARTIFACT_V1
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


CREATED_AT = "2026-06-03T12:45:00+00:00"
CHAIN_ID = "CHAIN-PROVIDER-UNAVAILABLE-FALLBACK-000001"
PROMPT_ID = "SESSION-FALLBACK-000001:TURN-000001"


def _provider_failure(**overrides) -> dict:
    capture = {
        "prompt_id": PROMPT_ID,
        "response_status": "FAILED_CLOSED",
        "response_source": "UNAVAILABLE",
        "response_text": "",
        "conversation_replay_reference": "provider/conversation_response",
        "prompt_to_conversation_capture_hash": "sha256:provider-failure",
        "provider_used": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "fail_closed": True,
        "failure_reason": "provider-assisted conversation failed closed: OpenAI provider unavailable",
        "canonical_chain_id": CHAIN_ID,
        "current_chain_id": CHAIN_ID,
        "latest_chain_id": CHAIN_ID,
    }
    capture.update(overrides)
    return capture


def _fallback(tmp_path, *, human_prompt: str = "Create a workstation.", provider_failure: dict | None = None):
    return run_conversation_provider_unavailable_clarification_fallback(
        fallback_id="PROVIDER-UNAVAILABLE-FALLBACK-000001",
        prompt_id=PROMPT_ID,
        human_prompt=human_prompt,
        provider_failure_capture=provider_failure or _provider_failure(),
        canonical_chain_id=CHAIN_ID,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "fallback",
    )


def _args(tmp_path):
    parser = build_parser()
    return parser.parse_args(
        [
            "conversation",
            "--session-id",
            "SESSION-FALLBACK-000001",
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "interactive_runtime"),
        ]
    )


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def test_provider_unavailable_workstation_prompt_creates_clarification_request(tmp_path) -> None:
    capture = _fallback(tmp_path)
    reconstructed = reconstruct_conversation_provider_unavailable_clarification_fallback_replay(tmp_path / "fallback")
    request = capture["human_clarification_request_artifact"]

    assert capture["response_status"] == HUMAN_CLARIFICATION_REQUIRED
    assert capture["fail_closed"] is False
    assert capture["fallback_allowed"] is True
    assert capture["provider_failure_preserved"] is True
    assert request["artifact_type"] == HUMAN_CLARIFICATION_REQUEST_ARTIFACT_V1
    assert request["request_status"] == "CLARIFICATION_REQUESTED"
    assert "INTENT_AMBIGUITY" in request["ambiguity_categories"]
    assert "WORKER_AMBIGUITY" in request["ambiguity_categories"]
    assert "RESOURCE_AMBIGUITY" in request["ambiguity_categories"]
    assert request["candidate_interpretations"]
    assert "AiGOL will not guess" in capture["response_text"]
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["authorization_created"] is False
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert reconstructed["fallback_status"] == HUMAN_CLARIFICATION_REQUIRED
    assert reconstructed["provider_failure_preserved"] is True


def test_fallback_fails_closed_for_noneligible_prompt(tmp_path) -> None:
    capture = _fallback(tmp_path, human_prompt="What is AiGOL?")

    assert capture["response_status"] == FAILED_CLOSED
    assert capture["fallback_allowed"] is False
    assert "prompt is not clarification-eligible" in capture["failure_reason"]
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False


def test_fallback_fails_closed_without_provider_unavailable_evidence(tmp_path) -> None:
    capture = _fallback(tmp_path, provider_failure=_provider_failure(failure_reason="provider suggestion is ambiguous"))

    assert capture["response_status"] == FAILED_CLOSED
    assert "provider unavailable not detected" in capture["failure_reason"]


def test_interactive_conversation_uses_clarification_fallback_when_provider_unavailable(tmp_path, monkeypatch) -> None:
    args = _args(tmp_path)
    output: list[str] = []

    def provider_unavailable(**kwargs):
        prompt_id = kwargs["prompt_id"]
        return _provider_failure(
            prompt_id=prompt_id,
            canonical_chain_id=CHAIN_ID,
            current_chain_id=CHAIN_ID,
            latest_chain_id=CHAIN_ID,
        )

    monkeypatch.setattr(aigol_cli, "submit_prompt_to_conversation", provider_unavailable)

    result = run_interactive_conversation(
        args,
        input_func=_input_sequence(["Create a workstation.", "exit"]),
        output_func=output.append,
    )
    turn = result["turns"][0]
    session_root = tmp_path / "interactive_runtime" / "SESSION-FALLBACK-000001"

    assert result["turn_count"] == 1
    assert result["failed_turns"] == 0
    assert turn["response_status"] == HUMAN_CLARIFICATION_REQUIRED
    assert turn["response_source"] == "DETERMINISTIC_CLARIFICATION_FALLBACK"
    assert turn["fail_closed"] is False
    assert "HUMAN_CLARIFICATION_REQUIRED" in output[0]
    assert "EMPLOYEE_MANAGEMENT_DOMAIN" in output[0]
    assert (
        session_root
        / "TURN-000001"
        / "provider_unavailable_clarification_fallback"
        / "000_conversation_provider_unavailable_clarification_fallback_recorded.json"
    ).exists()


def test_reconstruction_detects_corrupt_fallback_replay(tmp_path) -> None:
    _fallback(tmp_path)
    path = tmp_path / "fallback" / "000_conversation_provider_unavailable_clarification_fallback_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["fallback_status"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_conversation_provider_unavailable_clarification_fallback_replay(tmp_path / "fallback")


def test_fallback_runtime_has_no_provider_worker_or_execution_invocations() -> None:
    import aigol.runtime.conversation_provider_unavailable_clarification_fallback as runtime

    source = inspect.getsource(runtime)

    assert "run_provider_attachment(" not in source
    assert "produce_provider_development_proposal(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
