"""Provider contract model and validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .provider_identity import ProviderIdentity, validate_provider_identity


PROVIDER_TYPES = ("REMOTE_LLM", "LOCAL_EXECUTOR", "DETERMINISTIC_MOCK", "SYMBOLIC_EXECUTOR")


@dataclass(frozen=True)
class ProviderContract:
    provider_id: str
    provider_type: str
    bounded_execution: bool = True
    governance_authority: bool = False
    replay_safe: bool = True
    self_authorization_allowed: bool = False
    governance_mutation_allowed: bool = False
    replay_mutation_allowed: bool = False
    authority_escalation_allowed: bool = False
    validation_bypass_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "provider_type": self.provider_type,
            "bounded_execution": self.bounded_execution,
            "governance_authority": self.governance_authority,
            "replay_safe": self.replay_safe,
            "self_authorization_allowed": self.self_authorization_allowed,
            "governance_mutation_allowed": self.governance_mutation_allowed,
            "replay_mutation_allowed": self.replay_mutation_allowed,
            "authority_escalation_allowed": self.authority_escalation_allowed,
            "validation_bypass_allowed": self.validation_bypass_allowed,
        }


def provider_contract_from_identity(identity: ProviderIdentity) -> ProviderContract:
    return ProviderContract(provider_id=identity.provider_id, provider_type=identity.provider_type)


def validate_provider_contract(contract: Any) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    value = contract.to_dict() if isinstance(contract, ProviderContract) else contract
    if not isinstance(value, dict):
        return {
            "valid": False,
            "errors": [{"field": "provider_contract", "reason": "provider contract must be an object"}],
        }
    identity_result = validate_provider_identity(value)
    errors.extend(identity_result["errors"])
    if value.get("provider_type") not in PROVIDER_TYPES:
        errors.append({"field": "provider_type", "reason": "unsupported provider type"})
    required_booleans = {
        "bounded_execution": True,
        "governance_authority": False,
        "replay_safe": True,
        "self_authorization_allowed": False,
        "governance_mutation_allowed": False,
        "replay_mutation_allowed": False,
        "authority_escalation_allowed": False,
        "validation_bypass_allowed": False,
    }
    for field, expected in required_booleans.items():
        if value.get(field) is not expected:
            errors.append({"field": field, "reason": f"provider contract requires {expected}"})
    return {
        "valid": not errors,
        "errors": errors,
        "provider_contract_valid": not errors,
        "governance_independent": value.get("governance_authority") is False,
        "authority_escalation_detected": value.get("authority_escalation_allowed") is True,
    }


def provider_contract_evidence(contract: ProviderContract) -> dict[str, Any]:
    validation = validate_provider_contract(contract)
    return {
        "provider_id": contract.provider_id,
        "provider_contract_valid": validation["valid"],
        "governance_independent": contract.governance_authority is False,
        "authority_escalation_detected": contract.authority_escalation_allowed is True,
        "replay_safe": contract.replay_safe is True,
    }
