"""Explicit active provider invocation request."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.runtime.runtime_binding import create_runtime_binding

from .invocation_binding import create_invocation_binding


@dataclass(frozen=True)
class InvocationRequest:
    invocation_id: str
    envelope: dict[str, Any]
    provider_id: str
    runtime_binding: dict[str, Any]
    invocation_binding: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "invocation_id": self.invocation_id,
            "envelope": self.envelope,
            "envelope_id": self.envelope.get("envelope_id", ""),
            "provider_id": self.provider_id,
            "replay_identity": self.envelope.get("replay_identity", ""),
            "runtime_binding": self.runtime_binding,
            "invocation_binding": self.invocation_binding,
            "provider_auto_selection": False,
            "routing_present": False,
            "retry_present": False,
            "fallback_present": False,
            "concurrent_execution_present": False,
            "replay_safe": True,
        }


def create_invocation_request(envelope: dict[str, Any], provider_id: str | None = None) -> InvocationRequest:
    explicit_provider_id = provider_id or envelope["provider_id"]
    runtime_binding = create_runtime_binding(envelope).to_dict()
    invocation_binding = create_invocation_binding(envelope, explicit_provider_id).to_dict()
    return InvocationRequest(
        invocation_id=invocation_binding["invocation_id"],
        envelope=envelope,
        provider_id=explicit_provider_id,
        runtime_binding=runtime_binding,
        invocation_binding=invocation_binding,
    )
