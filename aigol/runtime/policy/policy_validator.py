"""Runtime policy contract validator."""

from __future__ import annotations

from copy import deepcopy

from aigol.runtime.models import AUTHORIZED, FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash

from .policy_contract import PolicyContract
from .policy_registry import PolicyRegistry


class PolicyValidator:
    """Fail-closed validation for runtime policy contracts."""

    def __init__(self, registry: PolicyRegistry | None = None) -> None:
        self.registry = registry or PolicyRegistry()

    def validate(self, contract: PolicyContract, sandbox_context=None) -> dict[str, object]:
        data = contract.to_dict()
        replay_input = deepcopy(data)
        actual_hash = replay_input.pop("replay_hash", None)
        if actual_hash != replay_hash(replay_input):
            raise FailClosedRuntimeError("policy contract replay_hash mismatch")
        if contract.governance_state != AUTHORIZED:
            raise FailClosedRuntimeError("policy evaluation requires AUTHORIZED governance_state")
        if not contract.runtime_id or not contract.sandbox_id or not contract.capability_request_id:
            raise FailClosedRuntimeError("policy contract identifiers are required")
        if not contract.requested_capability:
            raise FailClosedRuntimeError("policy requested_capability is required")
        if not contract.requested_target:
            raise FailClosedRuntimeError("policy requested_target is required")
        if not isinstance(contract.lineage_refs, list) or not contract.lineage_refs:
            raise FailClosedRuntimeError("policy lineage_refs are required")
        if sandbox_context is not None and contract.sandbox_id != sandbox_context.sandbox_id:
            raise FailClosedRuntimeError("policy sandbox compatibility mismatch")
        allowed = self.registry.capabilities_for_scope(contract.policy_scope)
        if self.registry.is_capability_forbidden(contract.requested_capability):
            raise FailClosedRuntimeError("policy requested capability is forbidden")
        return {
            "status": "POLICY_VALIDATED",
            "policy_id": contract.policy_id,
            "runtime_id": contract.runtime_id,
            "capability_request_id": contract.capability_request_id,
            "policy_scope": contract.policy_scope,
            "allowed_capabilities": allowed,
            "replay_hash": replay_hash(
                {
                    "status": "POLICY_VALIDATED",
                    "policy_id": contract.policy_id,
                    "runtime_id": contract.runtime_id,
                    "capability_request_id": contract.capability_request_id,
                    "policy_scope": contract.policy_scope,
                    "allowed_capabilities": allowed,
                }
            ),
        }
