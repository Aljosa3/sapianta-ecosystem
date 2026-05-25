"""Deterministic continuation result."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class ContinuationResult:
    continuation_result_id: str
    runtime_id: str
    continuation_decision: str
    decision_reason: str
    retry_count: int
    retry_allowed: bool
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "continuation_result_id": self.continuation_result_id,
            "runtime_id": self.runtime_id,
            "continuation_decision": self.continuation_decision,
            "decision_reason": self.decision_reason,
            "retry_count": self.retry_count,
            "retry_allowed": self.retry_allowed,
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact
