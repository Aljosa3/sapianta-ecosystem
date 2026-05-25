"""Centralized runtime constitutional policy engine."""

from __future__ import annotations

from .policy_contract import PolicyContract
from .policy_registry import PolicyRegistry
from .policy_result import PolicyResult
from .policy_validator import PolicyValidator
from aigol.runtime.transport.serialization import replay_hash


class RuntimePolicyEngine:
    """Evaluates runtime policy contracts deterministically."""

    def __init__(self, validator: PolicyValidator | None = None, registry: PolicyRegistry | None = None) -> None:
        self.registry = registry or PolicyRegistry()
        self.validator = validator or PolicyValidator(self.registry)

    def evaluate(self, contract: PolicyContract, sandbox_context=None) -> tuple[PolicyResult, dict[str, object]]:
        validation = self.validator.validate(contract, sandbox_context=sandbox_context)
        allowed = validation["allowed_capabilities"]
        if contract.requested_capability in allowed:
            decision = "ALLOW"
            reason = "capability allowed by registered policy scope"
        else:
            decision = "DENY"
            reason = "capability denied by registered policy scope"
        denied = self.registry.forbidden_capabilities()
        result = PolicyResult(
            policy_result_id=f"{contract.policy_id}:result",
            runtime_id=contract.runtime_id,
            capability_request_id=contract.capability_request_id,
            decision=decision,
            decision_reason=reason,
            allowed_capabilities=list(allowed),
            denied_capabilities=denied,
            created_at=contract.created_at,
        )
        replay_input = result.to_dict()
        replay_input.pop("replay_hash", None)
        return (
            PolicyResult(
                policy_result_id=result.policy_result_id,
                runtime_id=result.runtime_id,
                capability_request_id=result.capability_request_id,
                decision=result.decision,
                decision_reason=result.decision_reason,
                allowed_capabilities=result.allowed_capabilities,
                denied_capabilities=result.denied_capabilities,
                created_at=result.created_at,
                replay_hash=replay_hash(replay_input),
            ),
            validation,
        )
