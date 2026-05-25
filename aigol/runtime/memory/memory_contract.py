"""Immutable governed memory contract."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class MemoryContract:
    memory_contract_id: str
    runtime_id: str
    goal_id: str
    continuity_scope: str
    governance_state: str
    retention_policy: str
    lineage_refs: list[Any]
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "memory_contract_id": self.memory_contract_id,
            "runtime_id": self.runtime_id,
            "goal_id": self.goal_id,
            "continuity_scope": self.continuity_scope,
            "governance_state": self.governance_state,
            "retention_policy": self.retention_policy,
            "lineage_refs": deepcopy(self.lineage_refs),
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact

    @classmethod
    def from_goal_contract(cls, goal_contract: dict) -> "MemoryContract":
        contract = cls(
            memory_contract_id=f"{goal_contract['runtime_id']}:{goal_contract['goal_id']}:memory_contract",
            runtime_id=goal_contract["runtime_id"],
            goal_id=goal_contract["goal_id"],
            continuity_scope=goal_contract["continuity_scope"],
            governance_state=goal_contract["governance_state"],
            retention_policy="SESSION",
            lineage_refs=deepcopy(goal_contract["lineage_refs"]),
            created_at=goal_contract["created_at"],
        )
        replay_input = contract.to_dict()
        replay_input.pop("replay_hash", None)
        return cls(
            memory_contract_id=contract.memory_contract_id,
            runtime_id=contract.runtime_id,
            goal_id=contract.goal_id,
            continuity_scope=contract.continuity_scope,
            governance_state=contract.governance_state,
            retention_policy=contract.retention_policy,
            lineage_refs=contract.lineage_refs,
            created_at=contract.created_at,
            replay_hash=replay_hash(replay_input),
        )
