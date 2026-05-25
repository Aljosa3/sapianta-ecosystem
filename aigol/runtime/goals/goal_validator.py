"""Goal continuity validator."""

from __future__ import annotations

from copy import deepcopy

from aigol.runtime.models import AUTHORIZED, FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


class GoalValidator:
    """Fail-closed validation for bounded goal continuity."""

    def validate(self, contract, sequence) -> dict[str, object]:
        self._verify_hash(contract.to_dict(), "goal contract")
        self._verify_hash(sequence.to_dict(), "goal sequence")
        if contract.governance_state != AUTHORIZED:
            raise FailClosedRuntimeError("goal continuity requires AUTHORIZED governance_state")
        if not contract.goal_id or not contract.runtime_id:
            raise FailClosedRuntimeError("goal identifiers are required")
        if not contract.requested_objective:
            raise FailClosedRuntimeError("requested_objective is required")
        if not isinstance(contract.lineage_refs, list) or not contract.lineage_refs:
            raise FailClosedRuntimeError("goal lineage_refs are required")
        if not isinstance(contract.max_step_limit, int) or contract.max_step_limit <= 0:
            raise FailClosedRuntimeError("max_step_limit is required")
        if len(sequence.steps) > contract.max_step_limit:
            raise FailClosedRuntimeError("goal step limit exceeded")
        orders = [step.step_order for step in sequence.steps]
        if orders != sorted(orders) or orders != list(range(len(sequence.steps))):
            raise FailClosedRuntimeError("goal step ordering is invalid")
        for step in sequence.steps:
            self._verify_hash(step.to_dict(), "goal step")
            if step.goal_id != contract.goal_id:
                raise FailClosedRuntimeError("goal step goal_id mismatch")
            if not step.capability_request:
                raise FailClosedRuntimeError("goal step capability_request is required")
        validation = {
            "status": "GOAL_VALIDATED",
            "goal_id": contract.goal_id,
            "runtime_id": contract.runtime_id,
            "step_count": len(sequence.steps),
            "max_step_limit": contract.max_step_limit,
        }
        validation["replay_hash"] = replay_hash(validation)
        return validation

    def _verify_hash(self, artifact: dict, label: str) -> None:
        replay_input = deepcopy(artifact)
        actual = replay_input.pop("replay_hash", None)
        if actual != replay_hash(replay_input):
            raise FailClosedRuntimeError(f"{label} replay_hash mismatch")
