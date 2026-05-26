"""Deterministic runtime summary model."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class RuntimeSummary:
    runtime_id: str
    goal_state: str
    approval_state: str
    routing_state: str
    retry_state: str
    continuity_state: str
    replay_integrity_state: str
    created_at: str
    lineage_refs: list[Any]
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "runtime_id": self.runtime_id,
            "goal_state": self.goal_state,
            "approval_state": self.approval_state,
            "routing_state": self.routing_state,
            "retry_state": self.retry_state,
            "continuity_state": self.continuity_state,
            "replay_integrity_state": self.replay_integrity_state,
            "created_at": self.created_at,
            "lineage_refs": deepcopy(self.lineage_refs),
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact
