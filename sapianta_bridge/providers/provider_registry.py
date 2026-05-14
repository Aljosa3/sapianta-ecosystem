"""Passive deterministic provider registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .execution_provider import ExecutionProvider
from .provider_contracts import validate_provider_contract


@dataclass
class ProviderRegistry:
    _providers: dict[str, ExecutionProvider] = field(default_factory=dict)

    def register(self, provider: ExecutionProvider) -> dict[str, Any]:
        contract = provider.contract
        validation = validate_provider_contract(contract)
        if not validation["valid"]:
            return {"registered": False, "errors": validation["errors"]}
        if contract.provider_id in self._providers:
            return {
                "registered": False,
                "errors": [{"field": "provider_id", "reason": "duplicate provider registration"}],
            }
        self._providers[contract.provider_id] = provider
        return {"registered": True, "errors": []}

    def get(self, provider_id: str) -> ExecutionProvider | None:
        return self._providers.get(provider_id)

    def metadata(self) -> list[dict[str, Any]]:
        return [
            provider.contract.to_dict()
            for provider_id, provider in sorted(self._providers.items(), key=lambda item: item[0])
        ]

    def validate(self) -> dict[str, Any]:
        results = {
            provider_id: validate_provider_contract(provider.contract)
            for provider_id, provider in sorted(self._providers.items(), key=lambda item: item[0])
        }
        return {
            "valid": all(result["valid"] for result in results.values()),
            "providers": results,
            "scheduling_present": False,
            "dynamic_selection_present": False,
            "routing_present": False,
            "optimization_present": False,
        }
