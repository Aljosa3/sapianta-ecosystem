"""Bounded runtime continuity engine."""

from __future__ import annotations

from .continuation_result import ContinuationResult
from .continuation_validator import ContinuationValidator
from .retry_policy import RetryPolicy
from aigol.runtime.transport.serialization import replay_hash


class RuntimeContinuityEngine:
    """Evaluates continuity without launching retries or recursive execution."""

    def __init__(self, validator: ContinuationValidator | None = None, retry_policy: RetryPolicy | None = None) -> None:
        self.validator = validator or ContinuationValidator()
        self.retry_policy = retry_policy or RetryPolicy()

    def evaluate(self, contract, sandbox_id: str | None = None) -> tuple[ContinuationResult, dict[str, object], dict[str, object]]:
        validation = self.validator.validate(contract, sandbox_id=sandbox_id)
        retry_evaluation = self.retry_policy.evaluate(contract)
        if retry_evaluation["retry_allowed"]:
            decision = "CONTINUE"
        else:
            decision = "STOP"
        retry_evaluation = dict(retry_evaluation)
        retry_evaluation.update(
            {
                "runtime_id": contract.runtime_id,
                "continuation_id": contract.continuation_id,
                "retry_count": contract.retry_count,
                "max_retry_limit": contract.max_retry_limit,
            }
        )
        retry_evaluation["replay_hash"] = replay_hash(retry_evaluation)
        result = ContinuationResult(
            continuation_result_id=f"{contract.continuation_id}:result",
            runtime_id=contract.runtime_id,
            continuation_decision=decision,
            decision_reason=retry_evaluation["decision_reason"],
            retry_count=contract.retry_count,
            retry_allowed=bool(retry_evaluation["retry_allowed"]),
            created_at=contract.created_at,
        )
        replay_input = result.to_dict()
        replay_input.pop("replay_hash", None)
        return (
            ContinuationResult(
                continuation_result_id=result.continuation_result_id,
                runtime_id=result.runtime_id,
                continuation_decision=result.continuation_decision,
                decision_reason=result.decision_reason,
                retry_count=result.retry_count,
                retry_allowed=result.retry_allowed,
                created_at=result.created_at,
                replay_hash=replay_hash(replay_input),
            ),
            validation,
            retry_evaluation,
        )
