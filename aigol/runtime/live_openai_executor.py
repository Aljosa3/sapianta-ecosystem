"""Governed live OpenAI HTTPS executor for AIGOL_LIVE_OPENAI_EXECUTOR_V1."""

from __future__ import annotations

import json
import socket
from typing import Any, Callable
from urllib import error, request

from aigol.runtime.llm_cognition_provider_runtime import OPENAI_RESPONSES_ENDPOINT
from aigol.runtime.models import FailClosedRuntimeError


MILESTONE_ID = "AIGOL_LIVE_OPENAI_EXECUTOR_V1"

OpenUrl = Callable[..., Any]


class GovernedLiveOpenAIExecutor:
    """Execute exactly one governed OpenAI HTTPS request without replaying secrets."""

    aigol_governed_live_openai_executor_v1 = True

    def __init__(self, *, opener: OpenUrl | None = None) -> None:
        self._opener = opener or request.urlopen

    def __call__(self, payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
        _validate_metadata(metadata)
        safe_payload = _validate_payload(payload)
        credential = _require_secret(metadata.get("_credential_secret"))
        timeout_seconds = _normalize_timeout(metadata.get("timeout_seconds"))
        http_request = request.Request(
            OPENAI_RESPONSES_ENDPOINT,
            data=json.dumps(safe_payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {credential}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with self._opener(http_request, timeout=timeout_seconds) as response:
                status_code = int(getattr(response, "status", 200))
                body = response.read()
        except TimeoutError as exc:
            raise FailClosedRuntimeError("live OpenAI executor failed closed: timeout") from exc
        except socket.timeout as exc:
            raise FailClosedRuntimeError("live OpenAI executor failed closed: timeout") from exc
        except error.HTTPError as exc:
            if exc.code == 429:
                raise FailClosedRuntimeError("live OpenAI executor failed closed: rate limit") from exc
            raise FailClosedRuntimeError("live OpenAI executor failed closed: transport unavailable") from exc
        except error.URLError as exc:
            reason = str(getattr(exc, "reason", exc)).lower()
            if "timed out" in reason or "timeout" in reason:
                raise FailClosedRuntimeError("live OpenAI executor failed closed: timeout") from exc
            raise FailClosedRuntimeError("live OpenAI executor failed closed: transport unavailable") from exc
        except Exception as exc:
            raise FailClosedRuntimeError("live OpenAI executor failed closed: transport unavailable") from exc
        parsed = _parse_response_body(body)
        response_text = _extract_response_text(parsed)
        return {
            "status_code": status_code,
            "response_json": parsed,
            "output_text": response_text,
            "openai_response_id": parsed.get("id"),
            "real_openai_called": True,
            "live_provider_call_performed": True,
            "credential_secret_replayed": False,
            "authorization_header_replayed": False,
            "request_count": 1,
        }


def create_governed_live_openai_executor(*, opener: OpenUrl | None = None) -> GovernedLiveOpenAIExecutor:
    return GovernedLiveOpenAIExecutor(opener=opener)


def _validate_metadata(metadata: dict[str, Any]) -> None:
    if not isinstance(metadata, dict):
        raise FailClosedRuntimeError("live OpenAI executor failed closed: metadata is required")
    if metadata.get("provider_id") != "openai":
        raise FailClosedRuntimeError("live OpenAI executor failed closed: unauthorized provider")
    if metadata.get("credential_secret_replayed") is not False:
        raise FailClosedRuntimeError("live OpenAI executor failed closed: credential replay violation")


def _validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise FailClosedRuntimeError("live OpenAI executor failed closed: malformed request")
    model = payload.get("model")
    prompt = payload.get("input")
    if not isinstance(model, str) or not model.strip():
        raise FailClosedRuntimeError("live OpenAI executor failed closed: malformed request")
    if not isinstance(prompt, str) or not prompt.strip():
        raise FailClosedRuntimeError("live OpenAI executor failed closed: malformed request")
    if payload.get("stream") is not False:
        raise FailClosedRuntimeError("live OpenAI executor failed closed: streaming is not allowed")
    return {
        "model": model,
        "input": prompt,
        "stream": False,
    }


def _require_secret(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError("live OpenAI executor failed closed: credential unavailable")
    return value


def _normalize_timeout(value: Any) -> int:
    if not isinstance(value, int) or value <= 0 or value > 60:
        raise FailClosedRuntimeError("live OpenAI executor failed closed: invalid timeout")
    return value


def _parse_response_body(body: bytes) -> dict[str, Any]:
    if not isinstance(body, bytes) or not body:
        raise FailClosedRuntimeError("live OpenAI executor failed closed: malformed response")
    try:
        parsed = json.loads(body.decode("utf-8"))
    except Exception as exc:
        raise FailClosedRuntimeError("live OpenAI executor failed closed: malformed response") from exc
    if not isinstance(parsed, dict):
        raise FailClosedRuntimeError("live OpenAI executor failed closed: malformed response")
    return parsed


def _extract_response_text(parsed: dict[str, Any]) -> str:
    for key in ("output_text", "text", "response_text"):
        value = parsed.get(key)
        if isinstance(value, str) and value.strip():
            return _bounded_text(value)
    output = parsed.get("output")
    if isinstance(output, list):
        parts: list[str] = []
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for content_item in content:
                if isinstance(content_item, dict) and isinstance(content_item.get("text"), str):
                    parts.append(content_item["text"])
        if parts:
            return _bounded_text("".join(parts))
    raise FailClosedRuntimeError("live OpenAI executor failed closed: malformed response")


def _bounded_text(value: str) -> str:
    text = value.strip()
    if not text or len(text) > 8192:
        raise FailClosedRuntimeError("live OpenAI executor failed closed: malformed response")
    return text
