"""Bounded deterministic goal sequence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash

from .goal_step import GoalStep


@dataclass(frozen=True)
class GoalSequence:
    goal_id: str
    runtime_id: str
    steps: list[GoalStep]
    progression_state: str
    max_step_limit: int
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "goal_id": self.goal_id,
            "runtime_id": self.runtime_id,
            "steps": [step.to_dict() for step in self.steps],
            "progression_state": self.progression_state,
            "max_step_limit": self.max_step_limit,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact

    @classmethod
    def from_runtime_package(cls, runtime_package, contract) -> "GoalSequence":
        payload = runtime_package.payload if isinstance(runtime_package.payload, dict) else {}
        goal = payload.get("goal_sequence", {}) if isinstance(payload.get("goal_sequence", {}), dict) else {}
        raw_steps = goal.get("steps", [])
        if not isinstance(raw_steps, list):
            raise FailClosedRuntimeError("goal steps must be a list")
        steps = [GoalStep.from_dict(contract.goal_id, step, index) for index, step in enumerate(raw_steps)]
        sequence = cls(
            goal_id=contract.goal_id,
            runtime_id=runtime_package.runtime_id,
            steps=steps,
            progression_state=goal.get("progression_state", "PENDING"),
            max_step_limit=contract.max_step_limit,
        )
        replay_input = sequence.to_dict()
        replay_input.pop("replay_hash", None)
        return cls(
            goal_id=sequence.goal_id,
            runtime_id=sequence.runtime_id,
            steps=sequence.steps,
            progression_state=sequence.progression_state,
            max_step_limit=sequence.max_step_limit,
            replay_hash=replay_hash(replay_input),
        )

    def next_step(self) -> GoalStep | None:
        for step in sorted(self.steps, key=lambda item: item.step_order):
            if step.execution_state == "PENDING":
                return step
        return None
