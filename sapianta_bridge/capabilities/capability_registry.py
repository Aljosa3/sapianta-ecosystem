"""Passive replay-safe capability registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .capability_declaration import CapabilityDeclaration
from .capability_validator import validate_capability_declaration


@dataclass
class CapabilityRegistry:
    _declarations: dict[tuple[str, str], CapabilityDeclaration] = field(default_factory=dict)

    def register(self, declaration: CapabilityDeclaration) -> dict[str, Any]:
        validation = validate_capability_declaration(declaration)
        if not validation["valid"]:
            return {"registered": False, "errors": validation["errors"]}
        key = (declaration.provider_id, declaration.capability_class)
        if key in self._declarations:
            return {"registered": False, "errors": [{"field": "capability_class", "reason": "duplicate capability"}]}
        self._declarations[key] = declaration
        return {"registered": True, "errors": []}

    def metadata(self) -> list[dict[str, Any]]:
        return [
            declaration.to_dict()
            for _, declaration in sorted(self._declarations.items(), key=lambda item: item[0])
        ]

    def validate(self) -> dict[str, Any]:
        results = {
            f"{provider_id}:{capability_class}": validate_capability_declaration(declaration)
            for (provider_id, capability_class), declaration in sorted(self._declarations.items())
        }
        return {
            "valid": all(result["valid"] for result in results.values()),
            "declarations": results,
            "routing_present": False,
            "orchestration_present": False,
            "dynamic_selection_present": False,
            "execution_authority_granted": False,
        }
