from __future__ import annotations

import json

import pytest

from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, UNAVAILABLE, ProviderMetadata, ProviderRegistry
from aigol.provider.providers.openai_provider import OPENAI_PROVIDER_VERSION, OpenAIProviderAdapter
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


class FakeOpenAIClient:
    def __init__(self, response=None) -> None:
        self.response = response if response is not None else {
            "id": "resp_contract_alignment",
            "output_text": "Provider boundaries keep providers proposal-only and non-authoritative.",
        }
        self.calls: list[dict] = []

    def __call__(self, payload, *, api_key: str, endpoint: str, timeout_seconds: int):
        self.calls.append(
            {
                "payload": payload,
                "api_key_seen": bool(api_key),
                "endpoint": endpoint,
                "timeout_seconds": timeout_seconds,
            }
        )
        return self.response


class ContextSensitiveOpenAIClient:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def __call__(self, payload, *, api_key: str, endpoint: str, timeout_seconds: int):
        self.calls.append(
            {
                "payload": payload,
                "api_key_seen": bool(api_key),
                "endpoint": endpoint,
                "timeout_seconds": timeout_seconds,
            }
        )
        prompt = payload["input"]
        if "AiGOL context:" in prompt and "LLM providers are proposal-only sources" in prompt:
            return {
                "id": "resp_context_capsule",
                "output_text": "AiGOL provider boundaries keep LLM providers proposal-only and non-authoritative while replay records evidence.",
            }
        return {
            "id": "resp_raw_prompt",
            "output_text": "Professional provider boundaries define appropriate relationships with patients and clients.",
        }


class ContextSensitiveConversationProviderAdapter:
    provider_id = "openai"
    provider_version = "conversation-v1"

    def __init__(self) -> None:
        self.requests: list[dict] = []

    def classify_raw_prompt_quality(self, prompt: str) -> str:
        return "AIGOL_SPECIFIC" if "AiGOL context:" in prompt else "GENERIC"

    def generate_proposal(self, request, *, proposal_id: str, timestamp: str):
        self.requests.append(request)
        if request.get("semantic_task") == "intent_classification_suggestion":
            response = {
                "suggested_destination": "CONVERSATION",
                "classification_reasoning": "The capsule frames the prompt as an AiGOL conversational question.",
                "confidence": "HIGH",
            }
        elif self.classify_raw_prompt_quality(request["prompt"]) == "AIGOL_SPECIFIC":
            response = {
                "suggested_response_text": (
                    "AiGOL provider boundaries keep LLM providers proposal-only while AiGOL validates suggestions, "
                    "workers act only after governed approval, and replay records evidence."
                ),
                "response_reasoning": "The minimal context capsule disambiguates provider boundaries as AiGOL boundaries.",
                "confidence": "HIGH",
            }
        else:
            response = {
                "suggested_response_text": "Professional provider boundaries describe relationships with patients and clients.",
                "response_reasoning": "The raw prompt does not identify AiGOL as the domain.",
                "confidence": "MEDIUM",
            }
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


def _openai_registry(*, status: str = AVAILABLE) -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_provider(
        ProviderMetadata(
            provider_id="openai",
            provider_type="llm",
            provider_version=OPENAI_PROVIDER_VERSION,
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


def test_provider_requests_include_minimal_context_capsule(tmp_path):
    adapter = SemanticConversationProviderAdapter()
    _run(tmp_path, "Kaj je namen AiGOL?", adapter=adapter)

    assert [request["semantic_task"] for request in adapter.requests] == [
        "intent_classification_suggestion",
        "conversation_response_suggestion",
    ]
    for request in adapter.requests:
        capsule = request["context_capsule"]
        assert capsule["context_capsule_version"] == "MINIMAL_PROVIDER_CONTEXT_CAPSULE_V1"
        assert capsule["provider_neutral"] is True
        assert capsule["authority_transfer"] is False
        assert "AiGOL context:" in request["prompt"]
        assert "LLM providers are proposal-only sources" in request["prompt"]
        assert f"Human prompt:\n{request['human_prompt']}" in request["prompt"]
        assert request["provider_authority"] is False
        assert request["execution_authority"] is False


def test_openai_response_text_is_aligned_to_conversation_contract(tmp_path):
    client = FakeOpenAIClient()
    adapter = OpenAIProviderAdapter(api_key="test-openai-key", client=client)
    capture = _run(
        tmp_path,
        "Explain provider boundaries.",
        adapter=adapter,
        registry=_openai_registry(),
    )
    reconstructed = reconstruct_provider_assisted_conversation_replay(tmp_path / "conversation")

    assert capture["conversation_status"] == "PROVIDER_ASSISTED_CONVERSATION_RESPONSE_CREATED"
    assert capture["provider_assistance_required"] is True
    assert "proposal-only" in capture["response_text"]
    assert capture["provider_conversation_response_validation"]["response_reasoning"] == (
        "deterministically aligned from provider response_text"
    )
    assert capture["provider_conversation_response_validation"]["confidence"] == "PROVIDER_TEXT_NORMALIZED"
    assert reconstructed["response_text"] == capture["response_text"]
    assert reconstructed["provider_response_replay"]["response"]["response_text"] == capture["response_text"]
    assert len(client.calls) == 1


def test_minimal_context_capsule_improves_ambiguous_provider_boundary_prompt(tmp_path):
    client = ContextSensitiveOpenAIClient()
    raw_response = client(
        {"input": "Explain provider boundaries."},
        api_key="test-openai-key",
        endpoint="https://api.openai.com/v1/responses",
        timeout_seconds=20,
    )
    adapter = OpenAIProviderAdapter(api_key="test-openai-key", client=client)
    capture = _run(
        tmp_path,
        "Explain provider boundaries.",
        adapter=adapter,
        registry=_openai_registry(),
    )
    reconstructed = reconstruct_provider_assisted_conversation_replay(tmp_path / "conversation")
    provider_payload = client.calls[1]["payload"]

    assert raw_response["output_text"].startswith("Professional provider boundaries")
    assert capture["conversation_status"] == "PROVIDER_ASSISTED_CONVERSATION_RESPONSE_CREATED"
    assert "AiGOL provider boundaries" in capture["response_text"]
    assert "professional" not in capture["response_text"].lower()
    assert "AiGOL context:" in provider_payload["input"]
    assert "LLM providers are proposal-only sources" in provider_payload["input"]
    assert "Human prompt:\nExplain provider boundaries." in provider_payload["input"]
    assert reconstructed["provider_response_replay"]["request"]["payload"]["input"] == provider_payload["input"]


def test_minimal_context_capsule_improves_same_prompt_set(tmp_path):
    prompts = [
        "Explain provider boundaries.",
        "Explain worker execution.",
        "Explain authorization.",
        "Explain fail closed behavior.",
        "Summarize operation history.",
        "Explain AiGOL in Slovenian.",
    ]
    without_context_quality = []
    with_context_successes = 0

    for index, prompt in enumerate(prompts):
        adapter = ContextSensitiveConversationProviderAdapter()
        without_context_quality.append(adapter.classify_raw_prompt_quality(prompt))
        capture = run_provider_assisted_conversation(
            conversation_id=f"conversation-{index}",
            prompt_id=f"prompt-{index}",
            human_prompt=prompt,
            created_at=TIMESTAMP,
            provider_id="openai",
            registry=_registry(),
            adapter=adapter,
            replay_dir=tmp_path / f"conversation-{index}",
        )

        assert capture["conversation_status"] == "PROVIDER_ASSISTED_CONVERSATION_RESPONSE_CREATED"
        assert capture["provider_assistance_required"] is True
        assert "AiGOL provider boundaries" in capture["response_text"]
        assert "professional" not in capture["response_text"].lower()
        assert adapter.requests[-1]["context_capsule"]["context_capsule_version"] == "MINIMAL_PROVIDER_CONTEXT_CAPSULE_V1"
        with_context_successes += 1

    assert without_context_quality == ["GENERIC"] * len(prompts)
    assert with_context_successes == len(prompts)


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


def test_invalid_provider_confidence_fails_closed(tmp_path):
    adapter = SemanticConversationProviderAdapter(
        conversation_response={
            "suggested_response_text": "AiGOL preserves replay evidence.",
            "response_reasoning": "Prompt asks about AiGOL.",
            "confidence": "CERTAIN",
        }
    )
    capture = _run(tmp_path, "Kaj je namen AiGOL?", adapter=adapter)

    assert capture["conversation_status"] == "FAILED_CLOSED"
    assert "confidence is invalid" in capture["failure_reason"]


def test_malformed_provider_response_shape_fails_closed(tmp_path):
    adapter = SemanticConversationProviderAdapter(conversation_response=["not", "an", "object"])
    capture = _run(tmp_path, "Kaj je namen AiGOL?", adapter=adapter)

    assert capture["conversation_status"] == "FAILED_CLOSED"
    assert "must be a JSON object" in capture["failure_reason"]


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


def test_explanatory_authority_vocabulary_is_accepted(tmp_path):
    adapter = SemanticConversationProviderAdapter(
        conversation_response={
            "suggested_response_text": (
                "Providers do not have authority to execute. AiGOL makes the governance decision, "
                "and workers execute only after governed authorization."
            ),
            "response_reasoning": "Explains authority boundaries without claiming authority.",
            "confidence": "HIGH",
        }
    )
    capture = _run(tmp_path, "Kaj je namen AiGOL?", adapter=adapter)
    reconstructed = reconstruct_provider_assisted_conversation_replay(tmp_path / "conversation")

    assert capture["conversation_status"] == "PROVIDER_ASSISTED_CONVERSATION_RESPONSE_CREATED"
    assert "Providers do not have authority to execute" in capture["response_text"]
    assert capture["provider_response_authority"] is False
    assert capture["execution_requested"] is False
    assert capture["worker_invoked"] is False
    assert reconstructed["response_text"] == capture["response_text"]


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
