from __future__ import annotations

import json

from aigol.provider.provider_registry import AVAILABLE, UNAVAILABLE, ProviderRegistry
from aigol.provider.provider_runtime import (
    NOT_READY,
    READY,
    reconstruct_provider_attachment_replay,
    run_provider_attachment,
)
from aigol.provider.providers.openai_provider import (
    OPENAI_PROVIDER_ID,
    OPENAI_PROVIDER_VERSION,
    OpenAIProviderAdapter,
    openai_provider_metadata,
)


TIMESTAMP = "2026-06-06T00:00:00Z"
REQUEST = {"prompt": "Explain provider readiness."}


class RecordingOpenAIClient:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def __call__(self, payload, *, api_key: str, endpoint: str, timeout_seconds: int):
        self.calls.append({"payload": payload, "api_key_seen": bool(api_key)})
        return {"id": "resp_ready", "output_text": "Provider readiness passed."}


class NonCallableTransport:
    pass


def _registry(*, status: str = AVAILABLE, provider_version: str = OPENAI_PROVIDER_VERSION) -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_provider(openai_provider_metadata(provider_version=provider_version, status=status))
    return registry


def _run(tmp_path, *, adapter: OpenAIProviderAdapter, registry: ProviderRegistry | None = None):
    return run_provider_attachment(
        provider_id=OPENAI_PROVIDER_ID,
        request=REQUEST,
        proposal_id="openai-readiness-proposal-0001",
        timestamp=TIMESTAMP,
        registry=registry or _registry(),
        adapter=adapter,
        replay_dir=tmp_path,
    )


def _readiness_from_file(tmp_path) -> dict:
    return json.loads((tmp_path / "000_provider_readiness_recorded.json").read_text())["artifact"]


def test_ready_openai_provider_records_readiness_before_invocation(tmp_path):
    client = RecordingOpenAIClient()
    capture = _run(tmp_path, adapter=OpenAIProviderAdapter(api_key="test-openai-key", client=client))
    readiness = _readiness_from_file(tmp_path)
    replay = reconstruct_provider_attachment_replay(tmp_path)

    assert readiness["artifact_type"] == "PROVIDER_READINESS_ARTIFACT_V1"
    assert readiness["readiness_status"] == READY
    assert readiness["api_key_present"] is True
    assert readiness["provider_configuration_valid"] is True
    assert readiness["model_configuration_valid"] is True
    assert readiness["transport_available"] is True
    assert readiness["provider_activation_ready"] is True
    assert readiness["provider_invocation_allowed"] is True
    assert len(client.calls) == 1
    assert capture["provider_proposal_created"]["provider_invoked"] is True
    assert replay["provider_readiness_artifact"]["readiness_status"] == READY


def test_missing_api_key_records_not_ready_and_skips_invocation(tmp_path):
    client = RecordingOpenAIClient()
    capture = _run(tmp_path, adapter=OpenAIProviderAdapter(api_key="", client=client))
    readiness = _readiness_from_file(tmp_path)

    assert client.calls == []
    assert readiness["readiness_status"] == NOT_READY
    assert readiness["sanitized_diagnostics"] == {
        "readiness_stage": "api_key_presence",
        "failure_category": "MISSING_API_KEY",
        "exception_type": None,
        "http_status": None,
    }
    assert capture["provider_proposal_created"]["provider_invoked"] is False
    assert capture["provider_proposal_created"]["provider_readiness_artifact"] == readiness


def test_provider_configuration_invalid_records_not_ready(tmp_path):
    client = RecordingOpenAIClient()
    adapter = OpenAIProviderAdapter(
        api_key="test-openai-key",
        provider_version="openai-responses-other",
        client=client,
    )
    capture = _run(tmp_path, adapter=adapter)
    readiness = _readiness_from_file(tmp_path)

    assert client.calls == []
    assert readiness["readiness_status"] == NOT_READY
    assert readiness["provider_configuration_valid"] is False
    assert readiness["sanitized_diagnostics"]["readiness_stage"] == "provider_configuration_validity"
    assert readiness["sanitized_diagnostics"]["failure_category"] == "PROVIDER_CONFIGURATION_INVALID"
    assert capture["provider_proposal_created"]["event_type"] == "FAILED_CLOSED"


def test_model_configuration_invalid_records_not_ready(tmp_path):
    client = RecordingOpenAIClient()
    adapter = OpenAIProviderAdapter(api_key="test-openai-key", client=client)
    adapter.endpoint = "http://api.openai.invalid/v1/responses"

    capture = _run(tmp_path, adapter=adapter)
    readiness = _readiness_from_file(tmp_path)

    assert client.calls == []
    assert readiness["readiness_status"] == NOT_READY
    assert readiness["model_configuration_valid"] is False
    assert readiness["sanitized_diagnostics"]["readiness_stage"] == "model_configuration_validity"
    assert readiness["sanitized_diagnostics"]["failure_category"] == "MODEL_CONFIGURATION_INVALID"
    assert capture["provider_proposal_created"]["provider_invoked"] is False


def test_transport_unavailable_records_not_ready(tmp_path):
    adapter = OpenAIProviderAdapter(api_key="test-openai-key", client=NonCallableTransport())
    capture = _run(tmp_path, adapter=adapter)
    readiness = _readiness_from_file(tmp_path)

    assert readiness["readiness_status"] == NOT_READY
    assert readiness["transport_available"] is False
    assert readiness["sanitized_diagnostics"]["readiness_stage"] == "transport_availability"
    assert readiness["sanitized_diagnostics"]["failure_category"] == "TRANSPORT_UNAVAILABLE"
    assert capture["provider_proposal_created"]["provider_invoked"] is False


def test_provider_activation_not_ready_records_not_ready(tmp_path):
    client = RecordingOpenAIClient()
    capture = _run(
        tmp_path,
        adapter=OpenAIProviderAdapter(api_key="test-openai-key", client=client),
        registry=_registry(status=UNAVAILABLE),
    )
    readiness = _readiness_from_file(tmp_path)

    assert client.calls == []
    assert readiness["readiness_status"] == NOT_READY
    assert readiness["provider_activation_ready"] is False
    assert readiness["sanitized_diagnostics"]["readiness_stage"] == "provider_activation_readiness"
    assert readiness["sanitized_diagnostics"]["failure_category"] == "PROVIDER_NOT_AVAILABLE"
    assert capture["provider_proposal_created"]["event_type"] == "FAILED_CLOSED"


def test_readiness_replay_excludes_sensitive_data(tmp_path):
    _run(tmp_path, adapter=OpenAIProviderAdapter(api_key="test-openai-key", client=RecordingOpenAIClient()))

    serialized = (tmp_path / "000_provider_readiness_recorded.json").read_text()
    readiness = _readiness_from_file(tmp_path)

    assert set(readiness["sanitized_diagnostics"]) == {
        "readiness_stage",
        "failure_category",
        "exception_type",
        "http_status",
    }
    assert "test-openai-key" not in serialized
    assert "Authorization" not in serialized
    assert "Bearer" not in serialized
    assert "Traceback" not in serialized
    assert REQUEST["prompt"] not in serialized
