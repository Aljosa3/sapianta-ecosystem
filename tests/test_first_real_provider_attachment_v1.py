from __future__ import annotations

import json

import pytest

from aigol.provider.provider_registry import AVAILABLE, ProviderRegistry
from aigol.provider.provider_runtime import (
    reconstruct_provider_attachment_replay,
    run_provider_attachment,
)
from aigol.provider.providers.openai_provider import (
    OPENAI_PROVIDER_ID,
    OPENAI_PROVIDER_VERSION,
    OpenAIProviderAdapter,
    openai_provider_metadata,
)
from aigol.runtime.models import FailClosedRuntimeError


TIMESTAMP = "2026-05-30T12:00:00Z"
REQUEST = {"prompt": "Explain provider attachment boundaries."}


class FakeOpenAIClient:
    def __init__(self, response=None, *, fail: bool = False) -> None:
        self.response = response or {"id": "resp_001", "output_text": "Provider is proposal-only evidence."}
        self.fail = fail
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
        if self.fail:
            raise TimeoutError("provider unavailable")
        return self.response


def _registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_provider(openai_provider_metadata(status=AVAILABLE))
    return registry


def _adapter(client: FakeOpenAIClient, *, api_key: str | None = "test-openai-key") -> OpenAIProviderAdapter:
    return OpenAIProviderAdapter(api_key=api_key, client=client)


def _run(tmp_path, *, adapter=None, registry=None, provider_id: str = OPENAI_PROVIDER_ID, request=REQUEST):
    return run_provider_attachment(
        provider_id=provider_id,
        request=request,
        proposal_id="openai-proposal-0001",
        timestamp=TIMESTAMP,
        registry=registry or _registry(),
        adapter=adapter or _adapter(FakeOpenAIClient()),
        replay_dir=tmp_path,
    )


def test_openai_provider_attaches_through_existing_provider_runtime(tmp_path):
    client = FakeOpenAIClient()
    capture = _run(tmp_path, adapter=_adapter(client))
    replay = reconstruct_provider_attachment_replay(tmp_path)

    envelope = capture["provider_proposal_envelope"]
    assert envelope["provider_id"] == OPENAI_PROVIDER_ID
    assert envelope["provider_version"] == OPENAI_PROVIDER_VERSION
    assert envelope["response"]["response_text"] == "Provider is proposal-only evidence."
    assert envelope["response"]["raw_response"]["id"] == "resp_001"
    assert envelope["request"]["payload"] == {
        "model": "gpt-5.1",
        "input": "Explain provider attachment boundaries.",
        "stream": False,
    }
    assert envelope["request"]["human_prompt"] == "Explain provider attachment boundaries."
    assert envelope["request"]["original_request"] == REQUEST
    assert envelope["request"]["api_key_captured"] is False
    assert len(client.calls) == 1

    assert replay["provider_id"] == OPENAI_PROVIDER_ID
    assert replay["provider_version"] == OPENAI_PROVIDER_VERSION
    assert replay["request"]["human_prompt"] == "Explain provider attachment boundaries."
    assert replay["response"] == envelope["response"]
    assert replay["proposal_hash"] == envelope["proposal_hash"]


def test_openai_provider_preserves_structured_prompt_evidence(tmp_path):
    structured_request = {
        "semantic_task": "intent_classification_suggestion",
        "human_prompt": "Kaj zna AiGOL?",
        "prompt": "AiGOL context:\nHuman prompt:\nKaj zna AiGOL?",
        "allowed_destinations": ["CONVERSATION"],
        "context_capsule": {"provider_neutral": True, "authority_transfer": False},
    }
    capture = _run(tmp_path, request=structured_request)
    replay = reconstruct_provider_attachment_replay(tmp_path)
    request = capture["provider_proposal_envelope"]["request"]

    assert request["human_prompt"] == "Kaj zna AiGOL?"
    assert request["original_request"] == structured_request
    assert request["payload"]["input"] == structured_request["prompt"]
    assert replay["request"]["human_prompt"] == "Kaj zna AiGOL?"
    assert replay["request"]["original_request"]["semantic_task"] == "intent_classification_suggestion"


def test_openai_provider_redacts_secret_fields_from_original_request(tmp_path):
    capture = _run(
        tmp_path,
        request={
            "human_prompt": "Explain AiGOL.",
            "prompt": "Explain AiGOL.",
            "api_key": "must-not-persist",
            "nested": {"token": "must-not-persist"},
        },
    )
    original = capture["provider_proposal_envelope"]["request"]["original_request"]

    assert original["api_key"] == "REDACTED"
    assert original["nested"]["token"] == "REDACTED"
    assert "must-not-persist" not in json.dumps(capture)


def test_openai_output_list_shape_is_supported(tmp_path):
    client = FakeOpenAIClient(
        {
            "id": "resp_002",
            "output": [
                {"content": [{"text": "Provider "}, {"text": "proposal evidence."}]},
            ],
        }
    )
    capture = _run(tmp_path, adapter=_adapter(client))

    assert capture["provider_proposal_envelope"]["response"]["response_text"] == "Provider proposal evidence."


def test_missing_api_key_fails_closed_before_provider_call(tmp_path):
    client = FakeOpenAIClient()
    capture = _run(tmp_path, adapter=_adapter(client, api_key=""))

    assert client.calls == []
    assert capture["provider_proposal_created"]["event_type"] == "FAILED_CLOSED"
    assert "OPENAI_API_KEY is required" in capture["provider_proposal_created"]["failure_reason"]


def test_provider_unavailable_fails_closed(tmp_path):
    capture = _run(tmp_path, adapter=_adapter(FakeOpenAIClient(fail=True)))

    assert capture["provider_proposal_created"]["event_type"] == "FAILED_CLOSED"
    assert "OpenAI provider unavailable" in capture["provider_proposal_created"]["failure_reason"]


def test_malformed_response_fails_closed(tmp_path):
    capture = _run(tmp_path, adapter=_adapter(FakeOpenAIClient({"id": "missing-output"})))

    assert capture["provider_proposal_created"]["event_type"] == "FAILED_CLOSED"
    assert "OpenAI provider response is malformed" in capture["provider_proposal_created"]["failure_reason"]


def test_empty_response_fails_closed(tmp_path):
    capture = _run(tmp_path, adapter=_adapter(FakeOpenAIClient({"output_text": "   "})))

    assert capture["provider_proposal_created"]["event_type"] == "FAILED_CLOSED"
    assert "openai_response is required" in capture["provider_proposal_created"]["failure_reason"]


def test_authority_bearing_provider_response_fails_closed(tmp_path):
    capture = _run(
        tmp_path,
        adapter=_adapter(
            FakeOpenAIClient(
                {
                    "output_text": "I propose evidence only.",
                    "execution_request": {"command": "run"},
                }
            )
        ),
    )

    assert capture["provider_proposal_created"]["event_type"] == "FAILED_CLOSED"
    assert "authority-bearing field" in capture["provider_proposal_created"]["failure_reason"]


def test_unknown_provider_fails_closed(tmp_path):
    capture = _run(tmp_path, provider_id="claude")

    assert capture["provider_proposal_created"]["event_type"] == "FAILED_CLOSED"
    assert "provider is unknown" in capture["provider_proposal_created"]["failure_reason"]


def test_provider_remains_non_authoritative(tmp_path):
    capture = _run(tmp_path)
    envelope = capture["provider_proposal_envelope"]
    created = capture["provider_proposal_created"]

    forbidden = {
        "authority",
        "execution_capable",
        "authorization_decision",
        "governance_decision",
        "execution_request",
        "worker_command",
        "dispatch_request",
        "memory_mutation",
        "replay_mutation",
    }
    assert forbidden.isdisjoint(envelope)
    assert created["authority"] is False
    assert created["execution_capable"] is False
    assert created["worker_invoked"] is False


def test_replay_corruption_detection(tmp_path):
    _run(tmp_path)
    replay_file = tmp_path / "000_provider_proposal_created.json"
    replay = json.loads(replay_file.read_text(encoding="utf-8"))
    replay["artifact"]["response"]["response_text"] = "tampered"
    replay_file.write_text(json.dumps(replay, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError):
        reconstruct_provider_attachment_replay(tmp_path)
