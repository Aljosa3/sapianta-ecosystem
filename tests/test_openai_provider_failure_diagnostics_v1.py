from __future__ import annotations

import json
from urllib import error

from aigol.provider.provider_registry import AVAILABLE, ProviderRegistry
from aigol.provider.provider_runtime import (
    reconstruct_provider_attachment_replay,
    run_provider_attachment,
)
from aigol.provider.providers import openai_provider
from aigol.provider.providers.openai_provider import (
    OPENAI_PROVIDER_ID,
    OpenAIProviderAdapter,
    openai_provider_metadata,
)


TIMESTAMP = "2026-06-06T00:00:00Z"
REQUEST = {"prompt": "Explain OpenAI provider failure diagnostics."}


class FailingOpenAIClient:
    def __init__(self, exc: Exception) -> None:
        self.exc = exc

    def __call__(self, payload, *, api_key: str, endpoint: str, timeout_seconds: int):
        raise self.exc


def _registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_provider(openai_provider_metadata(status=AVAILABLE))
    return registry


def _run_failure(tmp_path, exc: Exception):
    return run_provider_attachment(
        provider_id=OPENAI_PROVIDER_ID,
        request=REQUEST,
        proposal_id="openai-diagnostics-proposal-0001",
        timestamp=TIMESTAMP,
        registry=_registry(),
        adapter=OpenAIProviderAdapter(api_key="test-openai-key", client=FailingOpenAIClient(exc)),
        replay_dir=tmp_path,
    )


def test_dns_failure_records_sanitized_url_error_diagnostics(tmp_path):
    capture = _run_failure(tmp_path, error.URLError(OSError("dns lookup failed")))

    diagnostics = capture["provider_proposal_created"]["failure_diagnostics"]

    assert capture["provider_proposal_created"]["failure_reason"] == "OpenAI provider unavailable"
    assert diagnostics == {
        "failure_stage": "openai_http_request",
        "exception_type": "URLError",
        "transport_failure_category": "URL_ERROR",
        "http_status": None,
    }


def test_timeout_failure_records_sanitized_timeout_diagnostics(tmp_path):
    capture = _run_failure(tmp_path, TimeoutError("request timed out"))

    diagnostics = capture["provider_proposal_created"]["failure_diagnostics"]

    assert capture["provider_proposal_created"]["failure_reason"] == "OpenAI provider unavailable"
    assert diagnostics["failure_stage"] == "openai_http_request"
    assert diagnostics["exception_type"] == "TimeoutError"
    assert diagnostics["transport_failure_category"] == "TIMEOUT"
    assert diagnostics["http_status"] is None


def test_http_error_records_sanitized_status_diagnostics(tmp_path, monkeypatch):
    http_error = error.HTTPError(
        url="https://api.openai.com/v1/responses",
        code=429,
        msg="Too Many Requests",
        hdrs={},
        fp=None,
    )

    def fail_urlopen(http_request, *, timeout: int):
        raise http_error

    monkeypatch.setattr(openai_provider.request, "urlopen", fail_urlopen)
    capture = run_provider_attachment(
        provider_id=OPENAI_PROVIDER_ID,
        request=REQUEST,
        proposal_id="openai-diagnostics-proposal-0001",
        timestamp=TIMESTAMP,
        registry=_registry(),
        adapter=OpenAIProviderAdapter(api_key="test-openai-key"),
        replay_dir=tmp_path,
    )

    diagnostics = capture["provider_proposal_created"]["failure_diagnostics"]

    assert capture["provider_proposal_created"]["failure_reason"] == "OpenAI provider HTTP failure"
    assert diagnostics["failure_stage"] == "openai_http_request"
    assert diagnostics["exception_type"] == "HTTPError"
    assert diagnostics["transport_failure_category"] == "HTTP_ERROR"
    assert diagnostics["http_status"] == 429


def test_replay_contains_failure_diagnostics(tmp_path):
    _run_failure(tmp_path, TimeoutError("request timed out"))

    created = json.loads((tmp_path / "000_provider_proposal_created.json").read_text())["artifact"]
    returned = json.loads((tmp_path / "001_provider_proposal_returned.json").read_text())["artifact"]
    reconstructed = reconstruct_provider_attachment_replay(tmp_path)

    assert created["failure_diagnostics"]["transport_failure_category"] == "TIMEOUT"
    assert returned["failure_diagnostics"] == created["failure_diagnostics"]
    assert reconstructed["failure_diagnostics"] == created["failure_diagnostics"]
    assert reconstructed["provider_status"] == "FAILED_CLOSED"
    assert reconstructed["provider_invoked"] is False


def test_failure_diagnostics_exclude_sensitive_data(tmp_path):
    capture = _run_failure(tmp_path, error.URLError(OSError("dns lookup failed")))

    serialized = json.dumps(capture, sort_keys=True)
    diagnostics = capture["provider_proposal_created"]["failure_diagnostics"]

    assert set(diagnostics) == {
        "exception_type",
        "transport_failure_category",
        "http_status",
        "failure_stage",
    }
    assert "test-openai-key" not in serialized
    assert "Authorization" not in serialized
    assert "Bearer" not in serialized
    assert "Traceback" not in serialized
    assert "dns lookup failed" not in serialized
