"""Governed live Claude HTTPS executor for AIGOL_LIVE_CLAUDE_EXECUTOR_V1."""

from __future__ import annotations

import json
import os
import socket
from typing import Any, Callable
from urllib import error, request

from aigol.runtime.models import FailClosedRuntimeError


MILESTONE_ID = "AIGOL_LIVE_CLAUDE_EXECUTOR_V1"
ANTHROPIC_MESSAGES_ENDPOINT = "https://api.anthropic.com/v1/messages"
DEFAULT_ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_CLAUDE_MODEL = "claude-sonnet-4-5"

OpenUrl = Callable[..., Any]


class GovernedLiveClaudeExecutor:
    """Execute exactly one governed Claude HTTPS request without replaying secrets."""

    aigol_governed_live_claude_executor_v1 = True

    def __init__(self, *, opener: OpenUrl | None = None) -> None:
        self._opener = opener or request.urlopen

    def __call__(self, payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
        _validate_metadata(metadata)
        safe_payload = _validate_payload(payload)
        credential = _require_secret(metadata.get("_credential_secret"))
        timeout_seconds = _normalize_timeout(metadata.get("timeout_seconds", 20))
        http_request = request.Request(
            ANTHROPIC_MESSAGES_ENDPOINT,
            data=json.dumps(safe_payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
            headers={
                "x-api-key": credential,
                "anthropic-version": _anthropic_version(),
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with self._opener(http_request, timeout=timeout_seconds) as response:
                status_code = int(getattr(response, "status", 200))
                body = response.read()
        except TimeoutError as exc:
            raise FailClosedRuntimeError("live Claude executor failed closed: timeout") from exc
        except socket.timeout as exc:
            raise FailClosedRuntimeError("live Claude executor failed closed: timeout") from exc
        except error.HTTPError as exc:
            if exc.code == 429:
                raise FailClosedRuntimeError("live Claude executor failed closed: rate limit") from exc
            if exc.code in {401, 403}:
                raise FailClosedRuntimeError("live Claude executor failed closed: authorization failure") from exc
            raise FailClosedRuntimeError("live Claude executor failed closed: transport unavailable") from exc
        except error.URLError as exc:
            reason = str(getattr(exc, "reason", exc)).lower()
            if "timed out" in reason or "timeout" in reason:
                raise FailClosedRuntimeError("live Claude executor failed closed: timeout") from exc
            raise FailClosedRuntimeError("live Claude executor failed closed: transport unavailable") from exc
        except Exception as exc:
            raise FailClosedRuntimeError("live Claude executor failed closed: transport unavailable") from exc
        parsed = _parse_response_body(body)
        response_text = _extract_response_text(parsed)
        return {
            "status_code": status_code,
            "response_json": parsed,
            "output_text": response_text,
            "claude_response_id": parsed.get("id"),
            "provider_id": "claude",
            "model": parsed.get("model") or safe_payload["model"],
            "real_claude_called": True,
            "live_provider_call_performed": True,
            "credential_secret_replayed": False,
            "authorization_header_replayed": False,
            "request_count": 1,
        }


def create_governed_live_claude_executor(*, opener: OpenUrl | None = None) -> GovernedLiveClaudeExecutor:
    return GovernedLiveClaudeExecutor(opener=opener)


def _validate_metadata(metadata: dict[str, Any]) -> None:
    if not isinstance(metadata, dict):
        raise FailClosedRuntimeError("live Claude executor failed closed: metadata is required")
    if metadata.get("provider_id") != "claude":
        raise FailClosedRuntimeError("live Claude executor failed closed: unauthorized provider")
    if metadata.get("credential_secret_replayed") is not False:
        raise FailClosedRuntimeError("live Claude executor failed closed: credential replay violation")


def _validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise FailClosedRuntimeError("live Claude executor failed closed: malformed request")
    prompt = payload.get("prompt") or payload.get("input")
    if not isinstance(prompt, str) or not prompt.strip():
        raise FailClosedRuntimeError("live Claude executor failed closed: malformed request")
    if payload.get("stream") is not False:
        raise FailClosedRuntimeError("live Claude executor failed closed: streaming is not allowed")
    model = payload.get("model")
    if not isinstance(model, str) or not model.strip():
        model = _claude_model()
    max_tokens = payload.get("max_tokens", 256)
    if isinstance(max_tokens, bool) or not isinstance(max_tokens, int) or max_tokens <= 0 or max_tokens > 4096:
        raise FailClosedRuntimeError("live Claude executor failed closed: malformed request")
    return {
        "model": model.strip(),
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt.strip()}],
        "stream": False,
    }


def _require_secret(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError("live Claude executor failed closed: credential unavailable")
    return value.strip()


def _normalize_timeout(value: Any) -> int:
    if not isinstance(value, int) or value <= 0 or value > 60:
        raise FailClosedRuntimeError("live Claude executor failed closed: invalid timeout")
    return value


def _parse_response_body(body: bytes) -> dict[str, Any]:
    if not isinstance(body, bytes) or not body:
        raise FailClosedRuntimeError("live Claude executor failed closed: malformed response")
    try:
        parsed = json.loads(body.decode("utf-8"))
    except Exception as exc:
        raise FailClosedRuntimeError("live Claude executor failed closed: malformed response") from exc
    if not isinstance(parsed, dict):
        raise FailClosedRuntimeError("live Claude executor failed closed: malformed response")
    return parsed


def _extract_response_text(parsed: dict[str, Any]) -> str:
    for key in ("output_text", "text", "response_text"):
        value = parsed.get(key)
        if isinstance(value, str) and value.strip():
            return _bounded_text(value)
    content = parsed.get("content")
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str):
                parts.append(item["text"])
        if parts:
            return _bounded_text("".join(parts))
    raise FailClosedRuntimeError("live Claude executor failed closed: malformed response")


def _bounded_text(value: str) -> str:
    text = value.strip()
    if not text or len(text) > 8192:
        raise FailClosedRuntimeError("live Claude executor failed closed: malformed response")
    return text


def _anthropic_version() -> str:
    value = os.environ.get("AIGOL_ANTHROPIC_VERSION", DEFAULT_ANTHROPIC_VERSION)
    return value.strip() if isinstance(value, str) and value.strip() else DEFAULT_ANTHROPIC_VERSION


def _claude_model() -> str:
    value = os.environ.get("AIGOL_CLAUDE_MODEL", DEFAULT_CLAUDE_MODEL)
    return value.strip() if isinstance(value, str) and value.strip() else DEFAULT_CLAUDE_MODEL
