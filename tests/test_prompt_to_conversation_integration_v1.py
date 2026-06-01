from __future__ import annotations

import json

import pytest

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, UNAVAILABLE, ProviderMetadata, ProviderRegistry
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.prompt_to_conversation_integration import (
    reconstruct_prompt_to_conversation_replay,
    submit_prompt_to_conversation,
)


TIMESTAMP = "2026-06-01T00:00:00Z"


class StaticConversationAdapter:
    provider_id = "openai"
    provider_version = "conversation-v1"

    def __init__(self, *, intent_response=None, conversation_response=None) -> None:
        self.intent_response = intent_response if intent_response is not None else {
            "suggested_destination": "CONVERSATION",
            "classification_reasoning": "Prompt asks about AiGOL purpose.",
            "confidence": "HIGH",
        }
        self.conversation_response = conversation_response if conversation_response is not None else {
            "suggested_response_text": "AiGOL exists to govern AI operations with replay-visible evidence.",
            "response_reasoning": "Prompt asks for AiGOL's purpose.",
            "confidence": "HIGH",
        }
        self.requests: list[dict] = []

    def generate_proposal(self, request, *, proposal_id: str, timestamp: str):
        self.requests.append(request)
        response = self.conversation_response
        if request.get("semantic_task") == "intent_classification_suggestion":
            response = self.intent_response
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=request,
            response=response,
            timestamp=timestamp,
        )


def _registry(*, status: str = AVAILABLE) -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_provider(
        ProviderMetadata(
            provider_id="openai",
            provider_type="llm",
            provider_version="conversation-v1",
            provider_status=status,
        )
    )
    return registry


def test_prompt_submit_returns_deterministic_conversation_response(tmp_path):
    adapter = StaticConversationAdapter()
    result = submit_prompt_to_conversation(
        human_prompt="What is AiGOL?",
        created_at=TIMESTAMP,
        replay_dir=tmp_path / "prompt_runtime",
        registry=_registry(),
        adapter=adapter,
    )
    reconstructed = reconstruct_prompt_to_conversation_replay(tmp_path / "prompt_runtime", prompt_id=result["prompt_id"])

    assert result["prompt_status"] == "HUMAN_PROMPT_ACCEPTED"
    assert result["routing_destination"] == "CONVERSATION"
    assert result["response_status"] == "PROVIDER_ASSISTED_CONVERSATION_RESPONSE_CREATED"
    assert result["response_source"] == "SELF_RESOLUTION"
    assert "governed AI operation path" in result["response_text"]
    assert result["provider_used"] is False
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["execution_requested"] is False
    assert adapter.requests == []
    assert reconstructed["response_status"] == result["response_status"]


def test_prompt_submit_uses_provider_assisted_conversation_when_needed(tmp_path):
    adapter = StaticConversationAdapter()
    result = submit_prompt_to_conversation(
        human_prompt="Kaj je namen AiGOL?",
        created_at=TIMESTAMP,
        replay_dir=tmp_path / "prompt_runtime",
        registry=_registry(),
        adapter=adapter,
    )

    assert result["prompt_status"] == "HUMAN_PROMPT_ACCEPTED"
    assert result["response_status"] == "PROVIDER_ASSISTED_CONVERSATION_RESPONSE_CREATED"
    assert result["response_source"] == "PROVIDER_ASSISTED"
    assert result["provider_used"] is True
    assert "replay-visible evidence" in result["response_text"]
    assert [request["semantic_task"] for request in adapter.requests] == [
        "intent_classification_suggestion",
        "conversation_response_suggestion",
    ]


def test_cli_prompt_submit_returns_response_for_deterministic_conversation(tmp_path):
    parser = build_parser()
    args = parser.parse_args(
        [
            "prompt",
            "submit",
            "--prompt",
            "What is AiGOL?",
            "--runtime-root",
            str(tmp_path / "prompt_runtime"),
        ]
    )

    result = run_command(args)
    rendered = render_command_result(result)

    assert result["response_status"] == "PROVIDER_ASSISTED_CONVERSATION_RESPONSE_CREATED"
    assert result["response_source"] == "SELF_RESOLUTION"
    assert "response_text:" in rendered
    assert "provider_used: False" in rendered


def test_missing_routing_fails_closed_without_execution(tmp_path):
    result = submit_prompt_to_conversation(
        human_prompt="Book me a flight to Tokyo tomorrow.",
        created_at=TIMESTAMP,
        replay_dir=tmp_path / "prompt_runtime",
        registry=_registry(status=UNAVAILABLE),
        adapter=StaticConversationAdapter(),
    )

    assert result["response_status"] == "FAILED_CLOSED"
    assert result["fail_closed"] is True
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["execution_requested"] is False


def test_invalid_provider_response_fails_closed(tmp_path):
    result = submit_prompt_to_conversation(
        human_prompt="Kaj je namen AiGOL?",
        created_at=TIMESTAMP,
        replay_dir=tmp_path / "prompt_runtime",
        registry=_registry(),
        adapter=StaticConversationAdapter(conversation_response={}),
    )

    assert result["response_status"] == "FAILED_CLOSED"
    assert result["fail_closed"] is True
    assert "response is required" in result["failure_reason"]


def test_reconstruct_detects_corrupt_conversation_response(tmp_path):
    result = submit_prompt_to_conversation(
        human_prompt="What is AiGOL?",
        created_at=TIMESTAMP,
        replay_dir=tmp_path / "prompt_runtime",
        registry=_registry(),
        adapter=StaticConversationAdapter(),
    )
    path = (
        tmp_path
        / "prompt_runtime"
        / result["prompt_id"]
        / "conversation_response"
        / "003_provider_assisted_conversation_response_created.json"
    )
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["response_text"] = "tampered"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_prompt_to_conversation_replay(tmp_path / "prompt_runtime", prompt_id=result["prompt_id"])
