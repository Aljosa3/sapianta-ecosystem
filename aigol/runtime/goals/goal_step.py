"""Immutable deterministic goal step."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class GoalStep:
    step_id: str
    goal_id: str
    step_order: int
    capability_request: dict[str, Any]
    policy_scope: str
    sandbox_profile: dict[str, Any]
    execution_state: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "step_id": self.step_id,
            "goal_id": self.goal_id,
            "step_order": self.step_order,
            "capability_request": deepcopy(self.capability_request),
            "policy_scope": self.policy_scope,
            "sandbox_profile": deepcopy(self.sandbox_profile),
            "execution_state": self.execution_state,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact

    @classmethod
    def from_dict(cls, goal_id: str, data: dict[str, Any], index: int) -> "GoalStep":
        step = cls(
            step_id=data.get("step_id", f"{goal_id}:step:{index}"),
            goal_id=goal_id,
            step_order=data.get("step_order", index),
            capability_request=deepcopy(data.get("capability_request", {})),
            policy_scope=data.get("policy_scope", "ANALYSIS_ONLY"),
            sandbox_profile=deepcopy(data.get("sandbox_profile", {})),
            execution_state=data.get("execution_state", "PENDING"),
        )
        replay_input = step.to_dict()
        replay_input.pop("replay_hash", None)
        return cls(
            step_id=step.step_id,
            goal_id=step.goal_id,
            step_order=step.step_order,
            capability_request=step.capability_request,
            policy_scope=step.policy_scope,
            sandbox_profile=step.sandbox_profile,
            execution_state=step.execution_state,
            replay_hash=replay_hash(replay_input),
        )
