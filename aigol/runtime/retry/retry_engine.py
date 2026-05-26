"""Controlled governed retry execution engine."""

from __future__ import annotations

from aigol.runtime.transport.serialization import replay_hash

from .retry_policy import RetryPolicy
from .retry_request import RetryRequest
from .retry_result import RetryResult
from .retry_validator import RetryValidator


class RetryEngine:
    """Executes bounded retry decisions as replay-visible local artifacts only."""

    def __init__(self, validator: RetryValidator | None = None, policy: RetryPolicy | None = None) -> None:
        self.validator = validator or RetryValidator()
        self.policy = policy or RetryPolicy()

    def evaluate(self, contract, requested_capability: str = "", approval_state: str = "APPROVED") -> tuple[RetryRequest, RetryResult, dict[str, object]]:
        validation = self.validator.validate(contract)
        policy_decision = self.policy.evaluate(contract, approval_state=approval_state)
        request = RetryRequest.from_contract(
            contract,
            retry_allowed=bool(policy_decision["retry_allowed"]),
            retry_scope=str(policy_decision["retry_scope"]),
            requested_capability=requested_capability,
        )
        validation = self.validator.validate(contract, request=request)
        if policy_decision["retry_allowed"]:
            state = "RETRY_EXECUTED"
        elif policy_decision["retry_scope"] == "LIMIT_REACHED":
            state = "RETRY_LIMIT_REACHED"
        else:
            state = "RETRY_BLOCKED"
        result = RetryResult(
            retry_result_id=f"{contract.retry_contract_id}:result",
            runtime_id=contract.runtime_id,
            retry_state=state,
            retry_reason=str(policy_decision["decision_reason"]),
            retry_count=contract.retry_count,
            created_at=contract.created_at,
        )
        replay_input = result.to_dict()
        replay_input.pop("replay_hash", None)
        result = RetryResult(
            retry_result_id=result.retry_result_id,
            runtime_id=result.runtime_id,
            retry_state=result.retry_state,
            retry_reason=result.retry_reason,
            retry_count=result.retry_count,
            created_at=result.created_at,
            replay_hash=replay_hash(replay_input),
        )
        validation = dict(validation)
        validation.update(
            {
                "retry_scope": policy_decision["retry_scope"],
                "retry_allowed": policy_decision["retry_allowed"],
                "decision_reason": policy_decision["decision_reason"],
                "bounded_local_only": True,
                "orchestration": False,
                "recursive_autonomous_execution": False,
                "hidden_retry_loop": False,
            }
        )
        validation.pop("replay_hash", None)
        validation["replay_hash"] = replay_hash(validation)
        return request, result, validation
