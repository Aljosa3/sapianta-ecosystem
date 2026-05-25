"""Deterministic capability routing engine."""

from __future__ import annotations

from aigol.runtime.transport.serialization import replay_hash

from .capability_route import CapabilityRoute
from .routing_registry import RoutingRegistry
from .routing_result import RoutingResult
from .routing_validator import RoutingValidator


class RoutingEngine:
    """Classifies capability requests without executing or escalating them."""

    def __init__(self, registry: RoutingRegistry | None = None, validator: RoutingValidator | None = None) -> None:
        self.registry = registry or RoutingRegistry()
        self.validator = validator or RoutingValidator(self.registry)

    def evaluate(self, contract) -> tuple[CapabilityRoute, RoutingResult, dict[str, object]]:
        route_data = self.registry.get(contract.requested_capability)
        route = CapabilityRoute(
            route_id=f"{contract.runtime_id}:{contract.requested_capability}:route",
            capability_name=contract.requested_capability,
            capability_class=route_data["capability_class"],
            sandbox_profile=route_data["sandbox_profile"],
            policy_scope=route_data["policy_scope"],
            execution_surface=route_data["execution_surface"],
            approval_required=route_data["approval_required"],
            lineage_refs=contract.lineage_refs,
            created_at=contract.created_at,
        )
        route_input = route.to_dict()
        route_input.pop("replay_hash", None)
        route = CapabilityRoute(
            route_id=route.route_id,
            capability_name=route.capability_name,
            capability_class=route.capability_class,
            sandbox_profile=route.sandbox_profile,
            policy_scope=route.policy_scope,
            execution_surface=route.execution_surface,
            approval_required=route.approval_required,
            lineage_refs=route.lineage_refs,
            created_at=route.created_at,
            replay_hash=replay_hash(route_input),
        )
        validation = self.validator.validate(contract, route)
        result = RoutingResult(
            routing_result_id=f"{contract.routing_contract_id}:result",
            runtime_id=contract.runtime_id,
            requested_capability=contract.requested_capability,
            routing_decision="ROUTE_ASSIGNED",
            execution_surface=route.execution_surface,
            approval_required=route.approval_required,
            created_at=contract.created_at,
        )
        result_input = result.to_dict()
        result_input.pop("replay_hash", None)
        result = RoutingResult(
            routing_result_id=result.routing_result_id,
            runtime_id=result.runtime_id,
            requested_capability=result.requested_capability,
            routing_decision=result.routing_decision,
            execution_surface=result.execution_surface,
            approval_required=result.approval_required,
            created_at=result.created_at,
            replay_hash=replay_hash(result_input),
        )
        return route, result, validation
