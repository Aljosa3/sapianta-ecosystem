"""Routing contract validator."""

from __future__ import annotations

from copy import deepcopy

from aigol.runtime.models import AUTHORIZED, FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash

from .routing_registry import RoutingRegistry


class RoutingValidator:
    """Fail-closed validation for routing contracts and routes."""

    def __init__(self, registry: RoutingRegistry | None = None) -> None:
        self.registry = registry or RoutingRegistry()

    def validate(self, contract, route=None) -> dict[str, object]:
        self._verify_hash(contract.to_dict(), "routing contract")
        if contract.governance_state != AUTHORIZED:
            raise FailClosedRuntimeError("routing requires AUTHORIZED governance_state")
        if not contract.runtime_id or not contract.requested_capability:
            raise FailClosedRuntimeError("routing contract identifiers are required")
        if not contract.requested_target:
            raise FailClosedRuntimeError("routing requested_target is required")
        if not isinstance(contract.lineage_refs, list) or not contract.lineage_refs:
            raise FailClosedRuntimeError("routing lineage_refs are required")
        registered = self.registry.get(contract.requested_capability)
        if route is not None:
            self._verify_hash(route.to_dict(), "capability route")
            self.registry.validate_surface(route.execution_surface)
            if route.capability_name != contract.requested_capability:
                raise FailClosedRuntimeError("route capability mismatch")
        validation = {
            "status": "ROUTING_VALIDATED",
            "routing_contract_id": contract.routing_contract_id,
            "runtime_id": contract.runtime_id,
            "requested_capability": contract.requested_capability,
            "execution_surface": route.execution_surface if route else registered["execution_surface"],
        }
        validation["replay_hash"] = replay_hash(validation)
        return validation

    def _verify_hash(self, artifact: dict, label: str) -> None:
        replay_input = deepcopy(artifact)
        actual = replay_input.pop("replay_hash", None)
        if actual != replay_hash(replay_input):
            raise FailClosedRuntimeError(f"{label} replay_hash mismatch")
