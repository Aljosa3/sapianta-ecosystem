"""Immutable retry request."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class RetryRequest:
    retry_request_id: str
    runtime_id: str
    requested_capability: str
    retry_reason: str
    retry_allowed: bool
    retry_scope: str
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "retry_request_id": self.retry_request_id,
            "runtime_id": self.runtime_id,
            "requested_capability": self.requested_capability,
            "retry_reason": self.retry_reason,
            "retry_allowed": self.retry_allowed,
            "retry_scope": self.retry_scope,
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact

    @classmethod
    def from_contract(cls, contract, retry_allowed: bool, retry_scope: str, requested_capability: str = "") -> "RetryRequest":
        request = cls(
            retry_request_id=f"{contract.retry_contract_id}:request",
            runtime_id=contract.runtime_id,
            requested_capability=requested_capability,
            retry_reason=contract.retry_reason,
            retry_allowed=retry_allowed,
            retry_scope=retry_scope,
            created_at=contract.created_at,
        )
        replay_input = request.to_dict()
        replay_input.pop("replay_hash", None)
        return cls(
            retry_request_id=request.retry_request_id,
            runtime_id=request.runtime_id,
            requested_capability=request.requested_capability,
            retry_reason=request.retry_reason,
            retry_allowed=request.retry_allowed,
            retry_scope=request.retry_scope,
            created_at=request.created_at,
            replay_hash=replay_hash(replay_input),
        )
