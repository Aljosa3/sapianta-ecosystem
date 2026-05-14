"""Deterministic result return session."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .result_binding import create_result_binding


@dataclass(frozen=True)
class ResultSession:
    result_return_id: str
    invocation_id: str
    provider_id: str
    envelope_id: str
    replay_identity: str
    result_binding: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_return_id": self.result_return_id,
            "invocation_id": self.invocation_id,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "replay_identity": self.replay_identity,
            "result_binding": self.result_binding,
            "mutable_state_present": False,
            "replay_safe": True,
        }


def create_result_session(invocation_result: dict[str, Any], invocation_evidence: dict[str, Any]) -> ResultSession:
    binding = create_result_binding(invocation_result, invocation_evidence).to_dict()
    return ResultSession(
        result_return_id=binding["result_return_id"],
        invocation_id=binding["invocation_id"],
        provider_id=binding["provider_id"],
        envelope_id=binding["envelope_id"],
        replay_identity=binding["replay_identity"],
        result_binding=binding,
    )
