"""OpenAI provider adapter for FIRST_REAL_PROVIDER_ATTACHMENT_V1.

The adapter attaches OpenAI as a proposal source only. It does not execute,
authorize, govern, dispatch, mutate replay, or mutate memory.
"""

from __future__ import annotations

from copy import deepcopy
import json
import os
from typing import Any, Protocol
from urllib import error, request

from aigol.provider.provider_proposal_envelope import (
    ProviderProposalEnvelope,
    create_provider_proposal_envelope,
)
from aigol.provider.provider_registry import AVAILABLE, ProviderMetadata
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


OPENAI_PROVIDER_ID = "openai"
OPENAI_PROVIDER_TYPE = "llm"
OPENAI_PROVIDER_VERSION = "openai-responses-v1"
OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
OPENAI_RESPONSES_ENDPOINT = "https://api.openai.com/v1/responses"
DEFAULT_OPENAI_MODEL = "gpt-5.1"
DEFAULT_TIMEOUT_SECONDS = 20
MAX_OPENAI_RESPONSE_CHARS = 8192


class OpenAIClient(Protocol):
    def __call__(
        self,
        payload: dict[str, Any],
        *,
        api_key: str,
        endpoint: str,
        timeout_seconds: int,
    ) -> Any:
        """Return a raw OpenAI response object."""


class OpenAIProviderAdapter:
    """OpenAI adapter that returns ProviderProposalEnvelope only."""

    provider_id = OPENAI_PROVIDER_ID

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = DEFAULT_OPENAI_MODEL,
        provider_version: str = OPENAI_PROVIDER_VERSION,
        endpoint: str = OPENAI_RESPONSES_ENDPOINT,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        client: OpenAIClient | None = None,
    ) -> None:
        self.provider_version = _require_string(provider_version, "provider_version")
        self.model = _require_string(model, "model")
        self.endpoint = _require_string(endpoint, "endpoint")
        self.timeout_seconds = _require_positive_int(timeout_seconds, "timeout_seconds")
        self._api_key = api_key
        self._client = client or OpenAIHTTPClient()

    def generate_proposal(self, request: Any, *, proposal_id: str, timestamp: str) -> ProviderProposalEnvelope:
        api_key = _resolve_api_key(self._api_key)
        prompt = _extract_prompt(request)
        human_prompt = _extract_human_prompt(request, fallback=prompt)
        payload = _create_openai_payload(model=self.model, prompt=prompt)
        raw_response = self._call_openai(payload=payload, api_key=api_key)
        response_text = _extract_response_text(raw_response)
        provider_response = {
            "provider": OPENAI_PROVIDER_ID,
            "provider_version": self.provider_version,
            "model": self.model,
            "response_text": response_text,
            "raw_response": deepcopy(raw_response),
            "raw_response_hash": replay_hash(raw_response),
            "streaming": False,
            "tool_use": False,
            "function_calling": False,
            "memory": False,
        }
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request={
                "provider": OPENAI_PROVIDER_ID,
                "model": self.model,
                "endpoint": self.endpoint,
                "human_prompt": human_prompt,
                "original_request": _sanitize_original_request(request),
                "payload": payload,
                "api_key_captured": False,
                "single_request": True,
                "streaming": False,
                "tool_use": False,
                "function_calling": False,
                "memory": False,
            },
            response=provider_response,
            timestamp=timestamp,
        )

    def _call_openai(self, *, payload: dict[str, Any], api_key: str) -> Any:
        if not callable(self._client):
            raise FailClosedRuntimeError("OpenAI provider client is invalid")
        try:
            return self._client(
                deepcopy(payload),
                api_key=api_key,
                endpoint=self.endpoint,
                timeout_seconds=self.timeout_seconds,
            )
        except FailClosedRuntimeError:
            raise
        except Exception as exc:
            raise FailClosedRuntimeError("OpenAI provider unavailable") from exc


class OpenAIHTTPClient:
    """Small standard-library OpenAI Responses API client.

    It performs one non-streaming request. It does not retry, stream, call tools,
    dispatch work, or retain conversation state.
    """

    def __call__(
        self,
        payload: dict[str, Any],
        *,
        api_key: str,
        endpoint: str,
        timeout_seconds: int,
    ) -> Any:
        body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        http_request = request.Request(
            endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            raise FailClosedRuntimeError("OpenAI provider HTTP failure") from exc
        except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise FailClosedRuntimeError("OpenAI provider unavailable") from exc


def openai_provider_metadata(*, provider_version: str = OPENAI_PROVIDER_VERSION, status: str = AVAILABLE) -> ProviderMetadata:
    return ProviderMetadata(
        provider_id=OPENAI_PROVIDER_ID,
        provider_type=OPENAI_PROVIDER_TYPE,
        provider_version=provider_version,
        provider_status=status,
    )


def _create_openai_payload(*, model: str, prompt: str) -> dict[str, Any]:
    return {
        "model": model,
        "input": prompt,
        "stream": False,
    }


def _extract_prompt(value: Any) -> str:
    if isinstance(value, str):
        return _require_string(value, "request")
    if isinstance(value, dict):
        for key in ("prompt", "human_prompt", "request"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
    raise FailClosedRuntimeError("OpenAI provider request prompt is required")


def _extract_human_prompt(value: Any, *, fallback: str) -> str:
    if isinstance(value, dict):
        candidate = value.get("human_prompt")
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return _require_string(fallback, "human_prompt")


def _sanitize_original_request(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized = {}
        for key, nested in value.items():
            if key.lower() in {"api_key", "authorization", "token", "secret"}:
                sanitized[key] = "REDACTED"
            else:
                sanitized[key] = _sanitize_original_request(nested)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_original_request(nested) for nested in value]
    return deepcopy(value)


def _extract_response_text(raw_response: Any) -> str:
    if isinstance(raw_response, str):
        return _bounded_response_text(raw_response)
    if not isinstance(raw_response, dict):
        raise FailClosedRuntimeError("OpenAI provider response is malformed")
    output_text = raw_response.get("output_text")
    if isinstance(output_text, str):
        return _bounded_response_text(output_text)
    output = raw_response.get("output")
    if isinstance(output, list):
        parts: list[str] = []
        for item in output:
            if isinstance(item, dict):
                content = item.get("content")
                if isinstance(content, list):
                    for content_item in content:
                        if isinstance(content_item, dict) and isinstance(content_item.get("text"), str):
                            parts.append(content_item["text"])
        if parts:
            return _bounded_response_text("".join(parts))
    raise FailClosedRuntimeError("OpenAI provider response is malformed")


def _bounded_response_text(value: str) -> str:
    text = _require_string(value, "openai_response")
    if len(text) > MAX_OPENAI_RESPONSE_CHARS:
        raise FailClosedRuntimeError("OpenAI provider response exceeds bounded size")
    return text


def _resolve_api_key(api_key: str | None) -> str:
    candidate = api_key if api_key is not None else os.environ.get(OPENAI_API_KEY_ENV)
    return _require_string(candidate, OPENAI_API_KEY_ENV)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _require_positive_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise FailClosedRuntimeError(f"{field_name} must be a positive integer")
    return value
