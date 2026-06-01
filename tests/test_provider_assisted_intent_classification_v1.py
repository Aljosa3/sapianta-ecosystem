from __future__ import annotations

import json

import pytest

from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.provider_registry import AVAILABLE, UNAVAILABLE, ProviderMetadata, ProviderRegistry
from aigol.provider.providers.openai_provider import OPENAI_PROVIDER_VERSION, OpenAIProviderAdapter, openai_provider_metadata
from aigol.runtime.intent_classifier import CONVERSATION, CONSTITUTIONAL_MEMORY_CONSULTATION
from aigol.runtime.intent_routing_attachment import attach_intent_routing
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_assisted_intent_classification import (
    PROVIDER_ASSISTED_CLASSIFIER_VERSION,
    classify_intent_with_provider_assistance,
    reconstruct_provider_assisted_intent_classification_replay,
)


TIMESTAMP = "2026-06-01T00:00:00Z"


class StaticSemanticProviderAdapter:
    provider_id = "openai"
    provider_version = "semantic-v1"

    def __init__(self, response=None, *, fail_if_called: bool = False) -> None:
        self.response = response or {
            "suggested_destination": CONVERSATION,
            "classification_reasoning": "Slovenian prompt asks about AiGOL purpose.",
            "confidence": "HIGH",
        }
        self.fail_if_called = fail_if_called
        self.call_count = 0

    def generate_proposal(self, request, *, proposal_id: str, timestamp: str):
        self.call_count += 1
        if self.fail_if_called:
            raise AssertionError("provider should not be called")
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=request,
            response=self.response,
            timestamp=timestamp,
        )


def _registry(*, status: str = AVAILABLE) -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_provider(
        ProviderMetadata(
            provider_id="openai",
            provider_type="llm",
            provider_version="semantic-v1",
            provider_status=status,
        )
    )
    return registry


def _openai_registry(*, status: str = AVAILABLE) -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_provider(openai_provider_metadata(status=status))
    return registry


def _classify(tmp_path, prompt: str, *, adapter=None, registry=None):
    return classify_intent_with_provider_assistance(
        artifact_id="intent-0001",
        human_request_reference="prompt-0001",
        human_prompt=prompt,
        classification_timestamp=TIMESTAMP,
        replay_reference=str(tmp_path / "intent_replay"),
        replay_dir=tmp_path / "intent_replay",
        provider_id="openai",
        registry=registry or _registry(),
        adapter=adapter or StaticSemanticProviderAdapter(),
    )


class FakeOpenAIClient:
    def __init__(self, text: str) -> None:
        self.text = text
        self.calls: list[dict] = []

    def __call__(self, payload, *, api_key: str, endpoint: str, timeout_seconds: int):
        self.calls.append({"payload": payload, "api_key_seen": bool(api_key), "endpoint": endpoint})
        return {"id": "resp_prompt_continuity", "output_text": self.text}


def test_deterministic_success_does_not_invoke_provider(tmp_path):
    adapter = StaticSemanticProviderAdapter(fail_if_called=True)
    capture = _classify(tmp_path, "what is aigol", adapter=adapter)
    reconstructed = reconstruct_provider_assisted_intent_classification_replay(tmp_path / "intent_replay")

    assert capture["classification_status"] == "CLASSIFIED"
    assert capture["classification_destination"] == CONVERSATION
    assert capture["provider_assisted"] is False
    assert capture["provider_semantic_assistance"] is None
    assert adapter.call_count == 0
    assert reconstructed["provider_assistance_required"] is False
    assert reconstructed["classification_destination"] == CONVERSATION


def test_provider_assists_after_deterministic_failure_for_slovenian_prompt(tmp_path):
    capture = _classify(tmp_path, "Kaj je namen AiGOL?")
    reconstructed = reconstruct_provider_assisted_intent_classification_replay(tmp_path / "intent_replay")

    assert capture["classification_status"] == "CLASSIFIED"
    assert capture["classification_destination"] == CONVERSATION
    assert capture["intent_classification_artifact"]["classifier_version"] == PROVIDER_ASSISTED_CLASSIFIER_VERSION
    assert capture["provider_assisted"] is True
    assert capture["provider_semantic_assistance"]["provider_proposal_returned"]["event_type"] == "PROVIDER_PROPOSAL_RETURNED"
    assert capture["governance_validation"]["provider_suggestion_authority"] is False
    assert capture["execution_requested"] is False
    assert capture["worker_invoked"] is False
    assert reconstructed["deterministic_classification_status"] == "FAILED_CLOSED"
    assert reconstructed["provider_assistance_required"] is True
    assert reconstructed["provider_suggestion_authority"] is False


def test_provider_explanatory_text_normalizes_clear_conversation_destination(tmp_path):
    adapter = StaticSemanticProviderAdapter(
        response={
            "response_text": (
                "This is a conversational question about AiGOL. It asks about governance boundaries "
                "and should be handled as a CONVERSATION response, with no execution."
            )
        }
    )
    capture = _classify(tmp_path, "Kaj je namen AiGOL?", adapter=adapter)
    reconstructed = reconstruct_provider_assisted_intent_classification_replay(tmp_path / "intent_replay")

    assert capture["classification_status"] == "CLASSIFIED"
    assert capture["classification_destination"] == CONVERSATION
    assert capture["governance_validation"]["confidence"] == "PROVIDER_TEXT_NORMALIZED"
    assert capture["governance_validation"]["provider_suggestion_authority"] is False
    assert reconstructed["classification_destination"] == CONVERSATION
    assert reconstructed["provider_assistance_required"] is True


def test_openai_provider_path_preserves_human_prompt_for_text_normalization(tmp_path):
    client = FakeOpenAIClient("This is a conversational question about AiGOL and should be CONVERSATION.")
    adapter = OpenAIProviderAdapter(api_key="test-openai-key", client=client)
    capture = _classify(
        tmp_path,
        "Kaj zna AiGOL?",
        adapter=adapter,
        registry=_openai_registry(),
    )
    reconstructed = reconstruct_provider_assisted_intent_classification_replay(tmp_path / "intent_replay")
    provider_replay = reconstructed["provider_assistance_replay"]

    assert capture["classification_status"] == "CLASSIFIED"
    assert capture["classification_destination"] == CONVERSATION
    assert provider_replay["provider_version"] == OPENAI_PROVIDER_VERSION
    assert provider_replay["request"]["human_prompt"] == "Kaj zna AiGOL?"
    assert provider_replay["request"]["original_request"]["human_prompt"] == "Kaj zna AiGOL?"
    assert "Human prompt:\nKaj zna AiGOL?" in provider_replay["request"]["payload"]["input"]


def test_provider_assisted_artifact_can_feed_routing_attachment(tmp_path):
    capture = _classify(tmp_path, "Kaj je namen AiGOL?")
    routing = attach_intent_routing(
        routing_record_id="routing-0001",
        intent_classification_artifact=capture["intent_classification_artifact"],
        routing_timestamp=TIMESTAMP,
        replay_reference=str(tmp_path / "routing"),
        replay_dir=tmp_path / "routing",
    )

    assert routing["intent_routing_attachment_record"]["routing_status"] == "ROUTED"
    assert routing["intent_routing_attachment_record"]["destination"] == CONVERSATION


def test_provider_can_suggest_memory_consultation_destination(tmp_path):
    adapter = StaticSemanticProviderAdapter(
        response={
            "suggested_destination": CONSTITUTIONAL_MEMORY_CONSULTATION,
            "classification_reasoning": "Prompt asks for constitutional source evidence.",
            "confidence": "MEDIUM",
        }
    )
    capture = _classify(tmp_path, "Povej mi, kaj pravi ustava AiGOL.", adapter=adapter)

    assert capture["classification_status"] == "CLASSIFIED"
    assert capture["classification_destination"] == CONSTITUTIONAL_MEMORY_CONSULTATION


def test_provider_unavailable_fails_closed(tmp_path):
    capture = _classify(tmp_path, "Kaj je namen AiGOL?", registry=_registry(status=UNAVAILABLE))

    assert capture["classification_status"] == "FAILED_CLOSED"
    assert capture["fail_closed"] is True
    assert "provider is unavailable" in capture["failure_reason"]


def test_provider_invalid_destination_fails_closed(tmp_path):
    adapter = StaticSemanticProviderAdapter(
        response={
            "suggested_destination": "AUTONOMOUS_EXECUTION",
            "classification_reasoning": "Invalid destination.",
            "confidence": "HIGH",
        }
    )
    capture = _classify(tmp_path, "Kaj je namen AiGOL?", adapter=adapter)

    assert capture["classification_status"] == "FAILED_CLOSED"
    assert "invalid destination" in capture["failure_reason"]


def test_provider_text_with_ambiguous_destination_fails_closed(tmp_path):
    adapter = StaticSemanticProviderAdapter(
        response={"response_text": "This could be CONVERSATION or EXECUTION_REQUEST."}
    )
    capture = _classify(tmp_path, "Kaj je namen AiGOL?", adapter=adapter)

    assert capture["classification_status"] == "FAILED_CLOSED"
    assert "ambiguous" in capture["failure_reason"]


def test_provider_ambiguous_suggestion_fails_closed(tmp_path):
    adapter = StaticSemanticProviderAdapter(
        response={
            "suggested_destination": CONVERSATION,
            "alternate_destinations": ["EXECUTION_REQUEST"],
            "classification_reasoning": "Ambiguous.",
            "confidence": "LOW",
        }
    )
    capture = _classify(tmp_path, "Kaj je namen AiGOL?", adapter=adapter)

    assert capture["classification_status"] == "FAILED_CLOSED"
    assert "ambiguous" in capture["failure_reason"]


def test_provider_authority_bearing_response_fails_closed(tmp_path):
    adapter = StaticSemanticProviderAdapter(
        response={
            "suggested_destination": CONVERSATION,
            "classification_reasoning": "Authority-bearing response.",
            "confidence": "HIGH",
            "execution_request": "run worker",
        }
    )
    capture = _classify(tmp_path, "Kaj je namen AiGOL?", adapter=adapter)

    assert capture["classification_status"] == "FAILED_CLOSED"
    assert "authority-bearing field" in capture["failure_reason"]


def test_provider_text_authority_claim_fails_closed(tmp_path):
    adapter = StaticSemanticProviderAdapter(response={"response_text": "I authorize execution. Dispatch the worker."})
    capture = _classify(tmp_path, "Kaj je namen AiGOL?", adapter=adapter)

    assert capture["classification_status"] == "FAILED_CLOSED"
    assert "authority-bearing text" in capture["failure_reason"]


def test_reconstruction_detects_corrupt_validation_artifact(tmp_path):
    _classify(tmp_path, "Kaj je namen AiGOL?")
    path = tmp_path / "intent_replay" / "000_provider_intent_governance_validation.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["suggested_destination"] = "EXECUTION_REQUEST"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_provider_assisted_intent_classification_replay(tmp_path / "intent_replay")
