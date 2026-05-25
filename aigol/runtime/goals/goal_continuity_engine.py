"""Bounded goal continuity engine."""

from __future__ import annotations

from aigol.runtime.transport.serialization import replay_hash

from .goal_validator import GoalValidator


class GoalContinuityEngine:
    """Evaluates next bounded goal step without executing it."""

    def __init__(self, validator: GoalValidator | None = None) -> None:
        self.validator = validator or GoalValidator()

    def evaluate(self, contract, sequence) -> tuple[dict[str, object], dict[str, object]]:
        validation = self.validator.validate(contract, sequence)
        next_step = sequence.next_step()
        if next_step is None:
            decision = "STOP"
            reason = "goal sequence has no pending steps"
        else:
            decision = "CONTINUE"
            reason = "next bounded goal step is available"
        result = {
            "goal_result_id": f"{contract.goal_id}:result",
            "runtime_id": contract.runtime_id,
            "goal_id": contract.goal_id,
            "goal_decision": decision,
            "decision_reason": reason,
            "next_step_id": next_step.step_id if next_step else "",
            "step_count": len(sequence.steps),
            "max_step_limit": contract.max_step_limit,
            "created_at": contract.created_at,
        }
        result["replay_hash"] = replay_hash(result)
        return result, validation
