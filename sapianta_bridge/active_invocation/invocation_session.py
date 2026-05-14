"""Deterministic active invocation session identity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .invocation_binding import create_invocation_binding


@dataclass(frozen=True)
class InvocationSession:
    invocation_id: str
    envelope_id: str
    provider_id: str
    replay_identity: str
    invocation_binding: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "invocation_id": self.invocation_id,
            "envelope_id": self.envelope_id,
            "provider_id": self.provider_id,
            "replay_identity": self.replay_identity,
            "invocation_binding": self.invocation_binding,
            "mutable_state_present": False,
            "replay_safe": True,
        }


def create_invocation_session(envelope: dict[str, Any], provider_id: str | None = None) -> InvocationSession:
    binding = create_invocation_binding(envelope, provider_id).to_dict()
    return InvocationSession(
        invocation_id=binding["invocation_id"],
        envelope_id=envelope["envelope_id"],
        provider_id=provider_id or envelope["provider_id"],
        replay_identity=envelope["replay_identity"],
        invocation_binding=binding,
    )
