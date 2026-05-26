"""Human governance approval engine."""

from __future__ import annotations

from aigol.runtime.transport.serialization import replay_hash

from .approval_request import ApprovalRequest
from .approval_result import ApprovalResult
from .approval_validator import ApprovalValidator


class ApprovalEngine:
    """Evaluates approval boundaries without simulating human approval."""

    def __init__(self, validator: ApprovalValidator | None = None) -> None:
        self.validator = validator or ApprovalValidator()

    def evaluate(self, contract) -> tuple[ApprovalRequest, ApprovalResult, dict[str, object]]:
        validation = self.validator.validate(contract)
        risk_class = validation["risk_class"]
        approval_required = contract.approval_scope == "HUMAN_APPROVAL_REQUIRED"
        request = ApprovalRequest.from_contract(contract, risk_class, approval_required)
        validation = self.validator.validate(contract, request=request)
        if contract.approval_scope == "READ_ONLY_AUTO_ALLOWED":
            state = "APPROVED"
            reason = "approval scope permits low-risk read-only execution"
            allowed = True
        elif contract.approval_scope == "HUMAN_APPROVAL_REQUIRED":
            state = "PENDING_HUMAN_APPROVAL"
            reason = "human approval required and no human approval artifact was provided"
            allowed = False
        else:
            state = "BLOCKED"
            reason = "restricted approval scope blocks execution"
            allowed = False
        result = ApprovalResult(
            approval_result_id=f"{contract.approval_contract_id}:result",
            runtime_id=contract.runtime_id,
            approval_state=state,
            approval_reason=reason,
            risk_class=risk_class,
            execution_allowed=allowed,
            created_at=contract.created_at,
        )
        replay_input = result.to_dict()
        replay_input.pop("replay_hash", None)
        result = ApprovalResult(
            approval_result_id=result.approval_result_id,
            runtime_id=result.runtime_id,
            approval_state=result.approval_state,
            approval_reason=result.approval_reason,
            risk_class=result.risk_class,
            execution_allowed=result.execution_allowed,
            created_at=result.created_at,
            replay_hash=replay_hash(replay_input),
        )
        return request, result, validation
