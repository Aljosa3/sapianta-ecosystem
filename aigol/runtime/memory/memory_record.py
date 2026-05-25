"""Immutable governed semantic continuity memory record."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class MemoryRecord:
    memory_id: str
    runtime_id: str
    goal_id: str
    continuity_scope: str
    semantic_summary: dict[str, Any]
    memory_class: str
    retention_policy: str
    lineage_refs: list[Any]
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "memory_id": self.memory_id,
            "runtime_id": self.runtime_id,
            "goal_id": self.goal_id,
            "continuity_scope": self.continuity_scope,
            "semantic_summary": deepcopy(self.semantic_summary),
            "memory_class": self.memory_class,
            "retention_policy": self.retention_policy,
            "lineage_refs": deepcopy(self.lineage_refs),
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact

    @classmethod
    def from_contract(cls, contract, semantic_summary: dict[str, Any]) -> "MemoryRecord":
        record = cls(
            memory_id=f"{contract.runtime_id}:{contract.goal_id}:memory",
            runtime_id=contract.runtime_id,
            goal_id=contract.goal_id,
            continuity_scope=contract.continuity_scope,
            semantic_summary=deepcopy(semantic_summary),
            memory_class="SEMANTIC_CONTINUITY",
            retention_policy=contract.retention_policy,
            lineage_refs=deepcopy(contract.lineage_refs),
            created_at=contract.created_at,
        )
        replay_input = record.to_dict()
        replay_input.pop("replay_hash", None)
        return cls(
            memory_id=record.memory_id,
            runtime_id=record.runtime_id,
            goal_id=record.goal_id,
            continuity_scope=record.continuity_scope,
            semantic_summary=record.semantic_summary,
            memory_class=record.memory_class,
            retention_policy=record.retention_policy,
            lineage_refs=record.lineage_refs,
            created_at=record.created_at,
            replay_hash=replay_hash(replay_input),
        )
