from __future__ import annotations

import json

import pytest

from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, UNAVAILABLE, ProviderMetadata, ProviderRegistry
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_assisted_conversation_runtime import (
    run_provider_assisted_conversation,
    reconstruct_provider_assisted_conversation_replay,
)


TIMESTAMP = "2026-06-01T00:00:00Z"


class SemanticConversationProviderAdapter:
    provider_id = "openai"
    provider_version = "conversation-v1"

    def __init__(
        self,
        *,
        intent_response=None,
        conversation_response=None,
        fail_if_conversation_called: bool = False,
    ) -> None:
        self.intent_response = intent_response if intent_response is not None else {
            "suggested_destination": "CONVERSATION",
            "classification_reasoning": "Prompt asks a conversational question about AiGOL.",
            "confidence": "HIGH",
        }
        self.conversation_response = conversation_response if conversation_response is not None else {
            "suggested_response_text": "AiGOL exists to govern AI operations through proposal, governance, worker execution, and replay evidence.",
            "response_reasoning": "The prompt asks for AiGOL's purpose.",
            "confidence": "HIGH",
        }
        self.fail_if_conversation_called = fail_if_conversation_called
        self.requests: list[dict] = []

    def generate_proposal(self, request, *, proposal_id: str, timestamp: str):
        self.requests.append(request)
        if request.get("semantic_task") == "conversation_response_suggestion":
            if self.fail_if_conversation_called:
                raise AssertionError("conversation provider should not be called")
            response = self.conversation_response
        else:
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


def _run(tmp_path, prompt: str, *, adapter=None, registry=None):
    return run_provider_assisted_conversation(
        conversation_id="conversation-0001",
        prompt_id="prompt-0001",
        human_prompt=prompt,
        created_at=TIMESTAMP,
        provider_id="openai",
        registry=registry or _registry(),
        adapter=adapter or SemanticConversationProviderAdapter(),
        replay_dir=tmp_path / "conversation",
    )


def test_deterministic_self_resolution_returns_aigol_response_without_provider_response(tmp_path):
    adapter = SemanticConversationProviderAdapter(fail_if_conversation_called=True)
    capture = _run(tmp_path, "what is aigol", adapter=adapter)
    reconstructed = reconstruct_provider_assisted_conversation_replay(tmp_path / "conversation")

    assert capture["conversation_status"] == "PROVIDER_ASSISTED_CONVERSATION_RESPONSE_CREATED"
    assert capture["provider_assistance_required"] is False
    assert "governed AI operation path" in capture["response_text"]
    assert [request["semantic_task"] for request in adapter.requests] == []
    assert reconstructed["provider_assistance_required"] is False
    assert reconstructed["authority"] is False


def test_provider_assisted_conversation_returns_validated_response_for_slovenian_prompt(tmp_path):
    capture = _run(tmp_path, "Kaj je namen AiGOL?")
    reconstructed = reconstruct_provider_assisted_conversation_replay(tmp_path / "conversation")

    assert capture["conversation_status"] == "PROVIDER_ASSISTED_CONVERSATION_RESPONSE_CREATED"
    assert capture["provider_assistance_required"] is True
    assert "govern AI operations" in capture["response_text"]
    assert capture["provider_response_authority"] is False
    assert capture["execution_requested"] is False
    assert capture["worker_invoked"] is False
    assert reconstructed["intent_classification"]["classification_destination"] == "CONVERSATION"
    assert reconstructed["provider_response_replay"]["provider_id"] == "openai"
    assert reconstructed["provider_response_authority"] is False


def test_provider_unavailable_fails_closed(tmp_path):
    capture = _run(tmp_path, "Kaj je namen AiGOL?", registry=_registry(status=UNAVAILABLE))

    assert capture["conversation_status"] == "FAILED_CLOSED"
    assert capture["fail_closed"] is True
    assert "provider is unavailable" in capture["failure_reason"]


def test_invalid_provider_response_fails_closed(tmp_path):
    adapter = SemanticConversationProviderAdapter(conversation_response={})
    capture = _run(tmp_path, "Kaj je namen AiGOL?", adapter=adapter)

    assert capture["conversation_status"] == "FAILED_CLOSED"
    assert "response is required" in capture["failure_reason"]


def test_authority_bearing_provider_response_fails_closed(tmp_path):
    adapter = SemanticConversationProviderAdapter(
        conversation_response={
            "suggested_response_text": "Authorization granted. Execute the worker.",
            "response_reasoning": "Bad response.",
            "confidence": "HIGH",
        }
    )
    capture = _run(tmp_path, "Kaj je namen AiGOL?", adapter=adapter)

    assert capture["conversation_status"] == "FAILED_CLOSED"
    assert "authority-bearing" in capture["failure_reason"]


def test_ambiguous_provider_response_fails_closed(tmp_path):
    adapter = SemanticConversationProviderAdapter(
        conversation_response={
            "suggested_response_text": "AiGOL governs AI operations.",
            "alternate_responses": ["AiGOL should execute the worker."],
            "response_reasoning": "Ambiguous alternatives.",
            "confidence": "LOW",
        }
    )
    capture = _run(tmp_path, "Kaj je namen AiGOL?", adapter=adapter)

    assert capture["conversation_status"] == "FAILED_CLOSED"
    assert "ambiguous" in capture["failure_reason"]


def test_non_conversation_intent_fails_closed(tmp_path):
    capture = _run(tmp_path, "read file governance/README.md")

    assert capture["conversation_status"] == "FAILED_CLOSED"
    assert "prompt is not conversation intent" in capture["failure_reason"]


def test_reconstruction_detects_corrupt_response_artifact(tmp_path):
    _run(tmp_path, "Kaj je namen AiGOL?")
    path = tmp_path / "conversation" / "003_provider_assisted_conversation_response_created.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["response_text"] = "tampered"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_provider_assisted_conversation_replay(tmp_path / "conversation")
