"""Bounded semantic summary for operational continuity memory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


MAX_SUMMARY_LENGTH = 2000


@dataclass(frozen=True)
class SemanticSummary:
    operational_continuity: str
    prior_runtime_decisions: str
    capability_outcomes: str
    goal_progression_checkpoints: str
    policy_continuity_constraints: str

    def to_dict(self) -> dict[str, str]:
        artifact = {
            "operational_continuity": self.operational_continuity,
            "prior_runtime_decisions": self.prior_runtime_decisions,
            "capability_outcomes": self.capability_outcomes,
            "goal_progression_checkpoints": self.goal_progression_checkpoints,
            "policy_continuity_constraints": self.policy_continuity_constraints,
        }
        text = self.as_text(artifact)
        if len(text) > MAX_SUMMARY_LENGTH:
            raise FailClosedRuntimeError("semantic summary exceeds bounded length")
        artifact["summary_replay_hash"] = replay_hash(artifact)
        return artifact

    @staticmethod
    def as_text(artifact: dict[str, Any]) -> str:
        return "|".join(str(artifact[key]) for key in sorted(artifact) if key != "summary_replay_hash")

    @classmethod
    def from_goal_artifacts(cls, goal_contract: dict, goal_sequence: dict, goal_result: dict) -> "SemanticSummary":
        return cls(
            operational_continuity=f"runtime={goal_contract.get('runtime_id')} scope={goal_contract.get('continuity_scope')}",
            prior_runtime_decisions=f"goal_decision={goal_result.get('goal_decision')}",
            capability_outcomes=f"steps={len(goal_sequence.get('steps', []))}",
            goal_progression_checkpoints=f"next_step={goal_result.get('next_step_id', '')}",
            policy_continuity_constraints="bounded_replay_visible_no_vector_memory_no_search",
        )
