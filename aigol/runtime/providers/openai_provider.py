"""Governed OpenAI cognition provider adapter."""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any, Callable
from urllib import request

from aigol.runtime.models import FailClosedRuntimeError, ProviderResponse, RuntimePackage
from aigol.runtime.provider_interface import ProviderInterface
from aigol.runtime.transport.serialization import replay_hash

from .provider_config import ProviderConfig
from .provider_envelope import ProviderEnvelope
from .provider_gate import ProviderActivationGate


OpenAITransport = Callable[[dict[str, Any], str], dict[str, Any]]


class OpenAIProvider(ProviderInterface):
    """Minimal governed OpenAI adapter for prompt-to-response cognition only."""

    def __init__(self, config: ProviderConfig | None = None, transport: OpenAITransport | None = None) -> None:
        self.config = config or ProviderConfig()
        self.transport = transport

    def provider_name(self) -> str:
        return self.config.provider

    def execute(self, runtime_package: RuntimePackage) -> ProviderResponse:
        return self.execute_governed(runtime_package, runtime_store=None, registered_providers={self.provider_name()})

    def execute_governed(
        self,
        runtime_package: RuntimePackage,
        runtime_store=None,
        registered_providers=None,
    ) -> ProviderResponse:
        envelope = ProviderEnvelope.from_runtime_package(runtime_package)
        gate = ProviderActivationGate(
            registered_providers=registered_providers or {self.provider_name()},
            allowed_invocation_types=self.config.allowed_invocation_types,
        )
        gate.validate(envelope)
        envelope_artifact = envelope.to_dict()
        if runtime_store is not None:
            runtime_store.persist_provider_envelope(runtime_package.runtime_id, envelope_artifact)
        response_artifact = self.invoke(envelope)
        if runtime_store is not None:
            runtime_store.persist_provider_response(runtime_package.runtime_id, response_artifact)
        return ProviderResponse(
            provider=self.provider_name(),
            status="PROVIDER_RETURNED",
            output=deepcopy(response_artifact),
            metadata={
                "provider_request_id": envelope.provider_request_id,
                "invocation_replay_hash": envelope_artifact["replay_hash"],
                "provider_response_replay_hash": response_artifact["replay_hash"],
                "tool_execution": False,
                "shell_execution": False,
                "filesystem_authority": False,
                "provider_authority": False,
            },
        )

    def invoke(self, envelope: ProviderEnvelope) -> dict[str, Any]:
        api_key = self.config.api_key()
        if not api_key:
            raise FailClosedRuntimeError("AIGOL_OPENAI_API_KEY is required for OpenAIProvider")
        request_body = {
            "model": self.config.model,
            "input": self._prompt_text(envelope.request_payload),
        }
        raw_response = self.transport(request_body, api_key) if self.transport else self._https_invoke(request_body, api_key)
        response_text = self._extract_text(raw_response)
        artifact = {
            "provider": self.provider_name(),
            "response_id": str(raw_response.get("id", f"{envelope.provider_request_id}:response")),
            "runtime_id": envelope.runtime_id,
            "package_id": envelope.package_id,
            "model": self.config.model,
            "response_text": response_text,
            "invocation_timestamp": envelope.created_at,
            "bounded_execution_guarantees": {
                "no_tool_execution": True,
                "no_shell_execution": True,
                "no_filesystem_execution": True,
                "no_worker_spawn": True,
                "no_recursive_runtime_dispatch": True,
            },
        }
        artifact["replay_hash"] = replay_hash(artifact)
        return artifact

    def _https_invoke(self, request_body: dict[str, Any], api_key: str) -> dict[str, Any]:
        body = json.dumps(request_body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        req = request.Request(
            "https://api.openai.com/v1/responses",
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        with request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    def _prompt_text(self, payload: Any) -> str:
        if isinstance(payload, str):
            return payload
        if isinstance(payload, dict) and isinstance(payload.get("prompt"), str):
            return payload["prompt"]
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

    def _extract_text(self, raw_response: dict[str, Any]) -> str:
        if isinstance(raw_response.get("output_text"), str):
            return raw_response["output_text"]
        output = raw_response.get("output")
        if isinstance(output, list):
            chunks = []
            for item in output:
                for content in item.get("content", []) if isinstance(item, dict) else []:
                    if isinstance(content, dict) and isinstance(content.get("text"), str):
                        chunks.append(content["text"])
            if chunks:
                return "".join(chunks)
        if isinstance(raw_response.get("text"), str):
            return raw_response["text"]
        raise FailClosedRuntimeError("OpenAI response did not include bounded response text")
