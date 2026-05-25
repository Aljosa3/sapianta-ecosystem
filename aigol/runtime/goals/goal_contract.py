"""Immutable goal continuity contract."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class GoalContract:
    goal_id: str
    runtime_id: str
    parent_goal_id: str
    goal_type: str
    requested_objective: str
    governance_state: str
    continuity_scope: str
    max_step_limit: int
    lineage_refs: list[Any]
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "goal_id": self.goal_id,
            "runtime_id": self.runtime_id,
            "parent_goal_id": self.parent_goal_id,
            "goal_type": self.goal_type,
            "requested_objective": self.requested_objective,
            "governance_state": self.governance_state,
            "continuity_scope": self.continuity_scope,
            "max_step_limit": self.max_step_limit,
            "lineage_refs": deepcopy(self.lineage_refs),
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact

    @classmethod
    def from_runtime_package(cls, runtime_package) -> "GoalContract":
        payload = runtime_package.payload if isinstance(runtime_package.payload, dict) else {}
        goal = payload.get("goal_sequence", {}) if isinstance(payload.get("goal_sequence", {}), dict) else {}
        contract = cls(
            goal_id=goal.get("goal_id", f"{runtime_package.runtime_id}:goal"),
            runtime_id=runtime_package.runtime_id,
            parent_goal_id=goal.get("parent_goal_id", ""),
            goal_type=goal.get("goal_type", "BOUNDED_OPERATIONAL_SEQUENCE"),
            requested_objective=goal.get("requested_objective", ""),
            governance_state=runtime_package.governance_state,
            continuity_scope=goal.get("continuity_scope", "BOUNDED_SEQUENCE"),
            max_step_limit=goal.get("max_step_limit", 3),
            lineage_refs=deepcopy(runtime_package.lineage_refs),
            created_at=runtime_package.created_at,
        )
        replay_input = contract.to_dict()
        replay_input.pop("replay_hash", None)
        return cls(
            goal_id=contract.goal_id,
            runtime_id=contract.runtime_id,
            parent_goal_id=contract.parent_goal_id,
            goal_type=contract.goal_type,
            requested_objective=contract.requested_objective,
            governance_state=contract.governance_state,
            continuity_scope=contract.continuity_scope,
            max_step_limit=contract.max_step_limit,
            lineage_refs=contract.lineage_refs,
            created_at=contract.created_at,
            replay_hash=replay_hash(replay_input),
        )
