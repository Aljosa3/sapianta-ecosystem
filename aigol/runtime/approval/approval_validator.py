"""Approval validation."""

from __future__ import annotations

from copy import deepcopy

from aigol.runtime.models import AUTHORIZED, FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash

from .approval_registry import ApprovalRegistry


class ApprovalValidator:
    """Fail-closed validator for approval artifacts."""

    def __init__(self, registry: ApprovalRegistry | None = None) -> None:
        self.registry = registry or ApprovalRegistry()

    def validate(self, contract, request=None) -> dict[str, object]:
        self._verify_hash(contract.to_dict(), "approval contract")
        if contract.governance_state != AUTHORIZED:
            raise FailClosedRuntimeError("approval requires AUTHORIZED governance_state")
        if not contract.runtime_id or not contract.requested_capability:
            raise FailClosedRuntimeError("approval contract identifiers are required")
        if not isinstance(contract.lineage_refs, list) or not contract.lineage_refs:
            raise FailClosedRuntimeError("approval lineage_refs are required")
        risk_class = self.registry.risk_for_scope(contract.approval_scope)
        self.registry.validate_risk(risk_class)
        if request is not None:
            self._verify_hash(request.to_dict(), "approval request")
            self.registry.validate_risk(request.risk_class)
            if request.runtime_id != contract.runtime_id:
                raise FailClosedRuntimeError("approval request runtime mismatch")
        validation = {
            "status": "APPROVAL_VALIDATED",
            "approval_contract_id": contract.approval_contract_id,
            "runtime_id": contract.runtime_id,
            "approval_scope": contract.approval_scope,
            "risk_class": risk_class,
        }
        validation["replay_hash"] = replay_hash(validation)
        return validation

    def _verify_hash(self, artifact: dict, label: str) -> None:
        replay_input = deepcopy(artifact)
        actual = replay_input.pop("replay_hash", None)
        if actual != replay_hash(replay_input):
            raise FailClosedRuntimeError(f"{label} replay_hash mismatch")
