from __future__ import annotations

import json

import pytest

from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.provider.provider_registry import (
    AVAILABLE,
    UNAVAILABLE,
    ProviderMetadata,
    ProviderRegistry,
)
from aigol.provider.provider_runtime import (
    reconstruct_provider_attachment_replay,
    run_provider_attachment,
)
from aigol.runtime.models import FailClosedRuntimeError


TIMESTAMP = "2026-05-30T00:00:00Z"
REQUEST = {"prompt": "Summarize constitutional provider boundary."}
RESPONSE = {"proposal_text": "Provider may return proposal evidence only."}


class StaticProviderAdapter:
    provider_id = "openai"
    provider_version = "adapter-v1"

    def __init__(self, response=RESPONSE, *, provider_id: str = "openai", provider_version: str = "adapter-v1") -> None:
        self.provider_id = provider_id
        self.provider_version = provider_version
        self.response = response

    def generate_proposal(self, request, *, proposal_id: str, timestamp: str):
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=request,
            response=self.response,
            timestamp=timestamp,
        )


class CorruptHashAdapter(StaticProviderAdapter):
    def generate_proposal(self, request, *, proposal_id: str, timestamp: str):
        envelope = super().generate_proposal(request, proposal_id=proposal_id, timestamp=timestamp).to_dict()
        envelope["proposal_hash"] = "sha256:corrupt"
        return envelope


def _registry(*, status: str = AVAILABLE, provider_id: str = "openai", provider_version: str = "adapter-v1") -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_provider(
        ProviderMetadata(
            provider_id=provider_id,
            provider_type="llm",
            provider_version=provider_version,
            provider_status=status,
        )
    )
    return registry


def _run(tmp_path, *, registry=None, adapter=None, provider_id: str = "openai", request=REQUEST):
    return run_provider_attachment(
        provider_id=provider_id,
        request=request,
        proposal_id="proposal-0001",
        timestamp=TIMESTAMP,
        registry=registry or _registry(),
        adapter=adapter or StaticProviderAdapter(),
        replay_dir=tmp_path,
    )


def test_valid_provider_response_creates_replay_visible_proposal(tmp_path):
    capture = _run(tmp_path)

    envelope = capture["provider_proposal_envelope"]
    assert envelope["provider_id"] == "openai"
    assert envelope["provider_version"] == "adapter-v1"
    assert envelope["request"] == REQUEST
    assert envelope["response"] == RESPONSE
    assert envelope["replay_visible"] is True
    assert "proposal_hash" in envelope

    reconstructed = reconstruct_provider_attachment_replay(tmp_path)
    assert reconstructed["provider_id"] == "openai"
    assert reconstructed["provider_version"] == "adapter-v1"
    assert reconstructed["request"] == REQUEST
    assert reconstructed["response"] == RESPONSE
    assert reconstructed["proposal_hash"] == envelope["proposal_hash"]
    assert reconstructed["authority"] is False
    assert reconstructed["execution_capable"] is False
    assert reconstructed["worker_invoked"] is False


def test_registry_is_metadata_only_and_deterministic():
    registry = _registry()
    metadata = registry.lookup_provider("openai")

    assert metadata["provider_status"] == AVAILABLE
    assert metadata["authority"] is False
    assert metadata["execution_capable"] is False
    assert metadata["dispatch_capable"] is False
    assert registry.provider_metadata() == [metadata]


def test_provider_proposal_envelope_contains_no_authority_metadata(tmp_path):
    capture = _run(tmp_path)
    envelope = capture["provider_proposal_envelope"]

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


def test_unknown_provider_fails_closed_with_replay_visible_failure(tmp_path):
    capture = _run(tmp_path, provider_id="claude")

    assert capture["provider_proposal_created"]["event_type"] == "FAILED_CLOSED"
    assert capture["provider_proposal_created"]["provider_invoked"] is False
    assert capture["provider_proposal_created"]["authority"] is False
    assert "provider is unknown" in capture["provider_proposal_created"]["failure_reason"]


def test_unavailable_provider_fails_closed(tmp_path):
    capture = _run(tmp_path, registry=_registry(status=UNAVAILABLE))

    assert capture["provider_proposal_created"]["event_type"] == "FAILED_CLOSED"
    assert "provider is unavailable" in capture["provider_proposal_created"]["failure_reason"]


def test_missing_provider_metadata_fails_closed():
    registry = ProviderRegistry()
    with pytest.raises(FailClosedRuntimeError):
        registry.register_provider(
            {
                "provider_id": "openai",
                "provider_type": "llm",
                "provider_status": AVAILABLE,
            }
        )


def test_malformed_empty_response_fails_closed(tmp_path):
    capture = _run(tmp_path, adapter=StaticProviderAdapter(response={}))

    assert capture["provider_proposal_created"]["event_type"] == "FAILED_CLOSED"
    assert "response is required" in capture["provider_proposal_created"]["failure_reason"]


def test_invalid_proposal_envelope_fails_closed(tmp_path):
    capture = _run(tmp_path, adapter=CorruptHashAdapter())

    assert capture["provider_proposal_created"]["event_type"] == "FAILED_CLOSED"
    assert "hash mismatch" in capture["provider_proposal_created"]["failure_reason"]


def test_authority_bearing_request_fails_closed(tmp_path):
    capture = _run(tmp_path, request={"prompt": "run it", "execution_request": "delete files"})

    assert capture["provider_proposal_created"]["event_type"] == "FAILED_CLOSED"
    assert "forbidden field" in capture["provider_proposal_created"]["failure_reason"]


def test_replay_corruption_detection(tmp_path):
    _run(tmp_path)
    replay_file = tmp_path / "000_provider_proposal_created.json"
    replay = json.loads(replay_file.read_text(encoding="utf-8"))
    replay["artifact"]["response"] = {"proposal_text": "tampered"}
    replay_file.write_text(json.dumps(replay, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError):
        reconstruct_provider_attachment_replay(tmp_path)


def test_append_only_replay_violation_fails_closed(tmp_path):
    _run(tmp_path)
    second = _run(tmp_path)

    assert second["provider_proposal_created"]["event_type"] == "FAILED_CLOSED"
    assert "append-only runtime artifact already exists" in second["provider_proposal_created"]["failure_reason"]


def test_provider_substitutability_uses_same_contract(tmp_path):
    provider_specs = [
        ("openai", "openai-v1"),
        ("claude", "claude-v1"),
        ("codex", "codex-v1"),
        ("gemini", "gemini-v1"),
        ("local_llm", "local-v1"),
    ]

    for provider_id, provider_version in provider_specs:
        replay_dir = tmp_path / provider_id
        capture = _run(
            replay_dir,
            registry=_registry(provider_id=provider_id, provider_version=provider_version),
            adapter=StaticProviderAdapter(provider_id=provider_id, provider_version=provider_version),
            provider_id=provider_id,
        )
        assert capture["provider_proposal_envelope"]["provider_id"] == provider_id
        assert reconstruct_provider_attachment_replay(replay_dir)["provider_id"] == provider_id
