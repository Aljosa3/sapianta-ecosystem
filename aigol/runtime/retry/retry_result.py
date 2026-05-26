"""Immutable retry execution result."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class RetryResult:
    retry_result_id: str
    runtime_id: str
    retry_state: str
    retry_reason: str
    retry_count: int
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "retry_result_id": self.retry_result_id,
            "runtime_id": self.runtime_id,
            "retry_state": self.retry_state,
            "retry_reason": self.retry_reason,
            "retry_count": self.retry_count,
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact
