"""Deterministic provider invocation envelope."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


def provider_boundary_guarantees() -> dict[str, bool]:
    return {
        "tool_execution": False,
        "shell_execution": False,
        "filesystem_authority": False,
        "orchestration": False,
        "autonomous_execution": False,
        "provider_authority": False,
        "governance_mutation": False,
    }


@dataclass(frozen=True)
class ProviderEnvelope:
    provider_request_id: str
    runtime_id: str
    package_id: str
    provider: str
    governance_state: str
    invocation_type: str
    request_payload: Any
    lineage_refs: list[Any]
    created_at: str
    boundary_guarantees: dict[str, bool] | None = None
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "provider_request_id": self.provider_request_id,
            "runtime_id": self.runtime_id,
            "package_id": self.package_id,
            "provider": self.provider,
            "governance_state": self.governance_state,
            "invocation_type": self.invocation_type,
            "request_payload": deepcopy(self.request_payload),
            "lineage_refs": deepcopy(self.lineage_refs),
            "boundary_guarantees": deepcopy(self.boundary_guarantees or provider_boundary_guarantees()),
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact

    @classmethod
    def from_runtime_package(cls, runtime_package, invocation_type: str = "prompt_response") -> "ProviderEnvelope":
        provider_request_id = f"{runtime_package.runtime_id}:{runtime_package.package_id}:{runtime_package.provider}"
        envelope = cls(
            provider_request_id=provider_request_id,
            runtime_id=runtime_package.runtime_id,
            package_id=runtime_package.package_id,
            provider=runtime_package.provider,
            governance_state=runtime_package.governance_state,
            invocation_type=invocation_type,
            request_payload=deepcopy(runtime_package.payload),
            lineage_refs=deepcopy(runtime_package.lineage_refs),
            created_at=runtime_package.created_at,
        )
        replay_input = envelope.to_dict()
        replay_input.pop("replay_hash", None)
        return cls(
            provider_request_id=envelope.provider_request_id,
            runtime_id=envelope.runtime_id,
            package_id=envelope.package_id,
            provider=envelope.provider,
            governance_state=envelope.governance_state,
            invocation_type=envelope.invocation_type,
            request_payload=envelope.request_payload,
            lineage_refs=envelope.lineage_refs,
            boundary_guarantees=envelope.boundary_guarantees or provider_boundary_guarantees(),
            created_at=envelope.created_at,
            replay_hash=replay_hash(replay_input),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProviderEnvelope":
        if not isinstance(data, dict):
            raise FailClosedRuntimeError("provider envelope must be a JSON object")
        return cls(
            provider_request_id=data.get("provider_request_id", ""),
            runtime_id=data.get("runtime_id", ""),
            package_id=data.get("package_id", ""),
            provider=data.get("provider", ""),
            governance_state=data.get("governance_state", ""),
            invocation_type=data.get("invocation_type", ""),
            request_payload=deepcopy(data.get("request_payload")),
            lineage_refs=deepcopy(data.get("lineage_refs", [])),
            boundary_guarantees=deepcopy(data.get("boundary_guarantees")),
            created_at=data.get("created_at", ""),
            replay_hash=data.get("replay_hash", ""),
        )
