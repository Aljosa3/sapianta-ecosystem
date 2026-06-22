"""Tests for AIGOL_LIVE_CLAUDE_EXECUTOR_V1."""

from __future__ import annotations

import json
import socket
from urllib import error, request

import pytest

from aigol.runtime.live_claude_executor import (
    ANTHROPIC_MESSAGES_ENDPOINT,
    MILESTONE_ID,
    create_governed_live_claude_executor,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


class _FakeHTTPResponse:
    status = 200

    def __init__(self, body: dict) -> None:
        self._body = json.dumps(body).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _traceback):
        return False

    def read(self) -> bytes:
        return self._body


def _metadata(secret: str = "test-live-claude-secret") -> dict:
    return {
        "provider_id": "claude",
        "timeout_seconds": 20,
        "credential_secret_replayed": False,
        "_credential_secret": secret,
    }


def _payload() -> dict:
    return {
        "provider_id": "claude",
        "prompt": "Produce a bounded cognition-only response.",
        "stream": False,
        "model": "claude-test-model",
    }


def test_live_claude_executor_constructs_https_request_and_returns_secret_free_response():
    captured: dict = {}

    def opener(http_request: request.Request, timeout: int):
        captured["url"] = http_request.full_url
        captured["timeout"] = timeout
        captured["x_api_key"] = http_request.get_header("X-api-key")
        captured["anthropic_version"] = http_request.get_header("Anthropic-version")
        captured["content_type"] = http_request.get_header("Content-type")
        captured["payload"] = json.loads(http_request.data.decode("utf-8"))
        return _FakeHTTPResponse(
            {
                "id": "msg_live_claude_1",
                "model": "claude-test-model",
                "content": [{"type": "text", "text": "Claude response captured. Confidence: HIGH"}],
            }
        )

    executor = create_governed_live_claude_executor(opener=opener)
    result = executor(_payload(), _metadata())

    assert MILESTONE_ID == "AIGOL_LIVE_CLAUDE_EXECUTOR_V1"
    assert executor.aigol_governed_live_claude_executor_v1 is True
    assert captured["url"] == ANTHROPIC_MESSAGES_ENDPOINT
    assert captured["timeout"] == 20
    assert captured["x_api_key"] == "test-live-claude-secret"
    assert captured["anthropic_version"] == "2023-06-01"
    assert captured["content_type"] == "application/json"
    assert captured["payload"]["model"] == "claude-test-model"
    assert captured["payload"]["stream"] is False
    assert captured["payload"]["messages"] == [
        {"role": "user", "content": "Produce a bounded cognition-only response."}
    ]
    assert result["status_code"] == 200
    assert result["output_text"] == "Claude response captured. Confidence: HIGH"
    assert result["claude_response_id"] == "msg_live_claude_1"
    assert result["real_claude_called"] is True
    assert result["live_provider_call_performed"] is True
    assert result["credential_secret_replayed"] is False
    assert result["authorization_header_replayed"] is False
    assert "test-live-claude-secret" not in canonical_serialize(result)
    assert "x-api-key" not in canonical_serialize(result).lower()


def test_live_claude_executor_passes_timeout_as_keyword_argument():
    captured: dict = {}

    def opener(http_request: request.Request, *, timeout: int):
        captured["url"] = http_request.full_url
        captured["timeout"] = timeout
        return _FakeHTTPResponse(
            {
                "id": "msg_keyword_timeout",
                "content": [{"type": "text", "text": "Keyword timeout response captured."}],
            }
        )

    result = create_governed_live_claude_executor(opener=opener)(_payload(), _metadata())

    assert captured["url"] == ANTHROPIC_MESSAGES_ENDPOINT
    assert captured["timeout"] == 20
    assert result["output_text"] == "Keyword timeout response captured."


def test_live_claude_executor_fails_closed_on_rate_limit():
    def opener(http_request: request.Request, *, timeout: int):
        assert timeout == 20
        raise error.HTTPError(http_request.full_url, 429, "Too Many Requests", hdrs=None, fp=None)

    with pytest.raises(FailClosedRuntimeError, match="rate limit"):
        create_governed_live_claude_executor(opener=opener)(_payload(), _metadata())


def test_live_claude_executor_fails_closed_on_timeout():
    def opener(_http_request: request.Request, *, timeout: int):
        assert timeout == 20
        raise socket.timeout("timed out")

    with pytest.raises(FailClosedRuntimeError, match="timeout"):
        create_governed_live_claude_executor(opener=opener)(_payload(), _metadata())


def test_live_claude_executor_fails_closed_on_malformed_response():
    class BadResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, _exc_type, _exc, _traceback):
            return False

        def read(self) -> bytes:
            return b"not-json"

    with pytest.raises(FailClosedRuntimeError, match="malformed response"):
        create_governed_live_claude_executor(opener=lambda _request, *, timeout: BadResponse())(
            _payload(), _metadata()
        )
