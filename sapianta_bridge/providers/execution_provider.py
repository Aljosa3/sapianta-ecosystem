"""Canonical bounded execution provider abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .normalized_result import NormalizedExecutionResult, validate_normalized_result
from .provider_contracts import ProviderContract, validate_provider_contract


class ExecutionProvider(ABC):
    """Structural provider interface.

    Implementations receive bounded envelopes only. This base class does not
    route, schedule, optimize, retry, or select providers.
    """

    contract: ProviderContract

    def validate_contract(self) -> dict[str, Any]:
        return validate_provider_contract(self.contract)

    def validate_envelope(self, envelope: dict[str, Any]) -> dict[str, Any]:
        errors: list[dict[str, str]] = []
        if not isinstance(envelope, dict):
            errors.append({"field": "envelope", "reason": "execution envelope must be an object"})
        elif envelope.get("bounded") is not True:
            errors.append({"field": "bounded", "reason": "provider requires bounded execution envelope"})
        if envelope.get("governance_authority_granted") is True:
            errors.append(
                {"field": "governance_authority_granted", "reason": "provider cannot receive governance authority"}
            )
        return {"valid": not errors, "errors": errors}

    @abstractmethod
    def execute(self, envelope: dict[str, Any]) -> NormalizedExecutionResult:
        raise NotImplementedError

    def validate_result(self, result: NormalizedExecutionResult) -> dict[str, Any]:
        return validate_normalized_result(result)
