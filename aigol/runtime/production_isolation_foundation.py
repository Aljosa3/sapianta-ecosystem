"""Production containment evidence for bounded governed execution."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from aigol.runtime.minimal_governed_execution_path import (
    EXECUTED,
    MinimalGovernedExecutionPathResult,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


ISOLATED = "ISOLATED"
REJECTED = "REJECTED"

ALLOWED_ISOLATION_STATUSES = frozenset({ISOLATED, REJECTED})
ALLOWED_PROVIDER = "metadata_inspection_provider"
ALLOWED_OPERATION = "inspect_runtime"


def _immutable(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _immutable(value[key]) for key in sorted(value)})
    if isinstance(value, list | tuple):
        return tuple(_immutable(item) for item in value)
    return deepcopy(value)


def _plain(value: Any) -> Any:
    if isinstance(value, MappingProxyType):
        return {key: _plain(value[key]) for key in value}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    return deepcopy(value)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _isolation_hash_input(evidence: "ProductionIsolationEvidence") -> dict[str, Any]:
    return {
        "isolation_id": evidence.isolation_id,
        "execution_id": evidence.execution_id,
        "isolation_status": evidence.isolation_status,
        "quota_policy": _plain(evidence.quota_policy),
        "isolation_metadata": _plain(evidence.isolation_metadata),
        "replay_durability_hash": evidence.replay_durability_hash,
        "reason": evidence.reason,
        "created_at": evidence.created_at,
    }


@dataclass(frozen=True)
class ProductionIsolationEvidence:
    """Immutable replay-visible production isolation evidence."""

    isolation_id: str
    execution_id: str
    isolation_status: str
    quota_policy: MappingProxyType
    isolation_metadata: MappingProxyType
    replay_durability_hash: str
    reason: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.isolation_id, "isolation_id")
        _require_string(self.execution_id, "execution_id")
        _require_string(self.reason, "reason")
        _require_string(self.created_at, "created_at")
        if self.isolation_status not in ALLOWED_ISOLATION_STATUSES:
            raise FailClosedRuntimeError("isolation status must be ISOLATED or REJECTED")
        if not isinstance(self.quota_policy, dict | MappingProxyType):
            raise FailClosedRuntimeError("quota_policy must be a JSON object")
        if not isinstance(self.isolation_metadata, dict | MappingProxyType):
            raise FailClosedRuntimeError("isolation_metadata must be a JSON object")
        quota_policy = _immutable(_plain(self.quota_policy))
        isolation_metadata = _immutable(_plain(self.isolation_metadata))
        canonical_serialize(_plain(quota_policy))
        canonical_serialize(_plain(isolation_metadata))
        object.__setattr__(self, "quota_policy", quota_policy)
        object.__setattr__(self, "isolation_metadata", isolation_metadata)
        expected_hash = replay_hash(_isolation_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("production isolation evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "isolation_id": self.isolation_id,
            "execution_id": self.execution_id,
            "isolation_status": self.isolation_status,
            "quota_policy": _plain(self.quota_policy),
            "isolation_metadata": _plain(self.isolation_metadata),
            "replay_durability_hash": self.replay_durability_hash,
            "reason": self.reason,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, artifact: dict[str, Any]) -> "ProductionIsolationEvidence":
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("production isolation artifact must be a JSON object")
        required = {
            "isolation_id",
            "execution_id",
            "isolation_status",
            "quota_policy",
            "isolation_metadata",
            "replay_durability_hash",
            "reason",
            "created_at",
            "evidence_hash",
        }
        if set(artifact) != required:
            raise FailClosedRuntimeError("production isolation artifact has malformed structure")
        return cls(**artifact)


def validate_production_isolation(
    *,
    isolation_id: str,
    execution_result: MinimalGovernedExecutionPathResult | dict[str, Any],
    quota_policy: dict[str, Any],
    isolation_metadata: dict[str, Any],
    created_at: str,
) -> ProductionIsolationEvidence:
    """Validate local containment evidence around one governed execution result."""

    created = created_at
    try:
        _require_string(isolation_id, "isolation_id")
        _require_string(created, "created_at")
        execution = MinimalGovernedExecutionPathResult.from_dict(execution_result) if isinstance(execution_result, dict) else execution_result
        if not isinstance(execution, MinimalGovernedExecutionPathResult):
            raise FailClosedRuntimeError("execution_result must be MinimalGovernedExecutionPathResult")
        normalized_quota = _normalize_quota_policy(quota_policy)
        normalized_metadata = _normalize_isolation_metadata(isolation_metadata)
        _validate_execution_against_quota(execution, normalized_quota)
        replay_durability_hash = replay_hash(
            {
                "execution_evidence_hash": execution.evidence_hash,
                "provider_evidence_hash": execution.provider_evidence_hash,
                "session_lineage_hash": execution.session_lineage_hash,
                "isolation_metadata": normalized_metadata,
            }
        )
        return ProductionIsolationEvidence(
            isolation_id=isolation_id,
            execution_id=execution.execution_id,
            isolation_status=ISOLATED,
            quota_policy=normalized_quota,
            isolation_metadata=normalized_metadata,
            replay_durability_hash=replay_durability_hash,
            reason="production isolation containment validated",
            created_at=created,
        )
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        execution_id = ""
        if isinstance(execution_result, MinimalGovernedExecutionPathResult):
            execution_id = execution_result.execution_id
        elif isinstance(execution_result, dict) and isinstance(execution_result.get("execution_id"), str):
            execution_id = execution_result["execution_id"]
        return ProductionIsolationEvidence(
            isolation_id=isolation_id if isinstance(isolation_id, str) and isolation_id else "ISOLATION-INVALID",
            execution_id=execution_id or "EXECUTION-INVALID",
            isolation_status=REJECTED,
            quota_policy={},
            isolation_metadata={},
            replay_durability_hash="",
            reason="production isolation validation failed closed",
            created_at=created if isinstance(created, str) and created else "1970-01-01T00:00:00+00:00",
        )


def reconstruct_production_isolation_lineage(
    evidence: list[ProductionIsolationEvidence | dict[str, Any]]
    | tuple[ProductionIsolationEvidence | dict[str, Any], ...],
) -> dict[str, Any]:
    if not isinstance(evidence, list | tuple):
        raise FailClosedRuntimeError("production isolation lineage must be a list")
    reconstructed = []
    seen_isolation_ids: set[str] = set()
    previous_created_at = ""
    for index, item in enumerate(evidence):
        evidence_obj = ProductionIsolationEvidence.from_dict(item) if isinstance(item, dict) else item
        if not isinstance(evidence_obj, ProductionIsolationEvidence):
            raise FailClosedRuntimeError("production isolation lineage entry is invalid")
        artifact = evidence_obj.to_dict()
        if artifact["isolation_id"] in seen_isolation_ids:
            raise FailClosedRuntimeError("production isolation lineage contains duplicate isolation_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("production isolation lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_isolation_ids.add(artifact["isolation_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "isolation_index": index,
                "isolation_id": artifact["isolation_id"],
                "execution_id": artifact["execution_id"],
                "isolation_status": artifact["isolation_status"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "isolation_count": len(reconstructed),
        "isolation_checks": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _normalize_quota_policy(policy: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(policy, dict) or set(policy) != {"max_provider_invocations", "allowed_provider", "allowed_operation"}:
        raise FailClosedRuntimeError("quota policy has malformed structure")
    max_provider_invocations = policy["max_provider_invocations"]
    if not isinstance(max_provider_invocations, int) or max_provider_invocations != 1:
        raise FailClosedRuntimeError("quota policy only allows one provider invocation")
    if policy["allowed_provider"] != ALLOWED_PROVIDER:
        raise FailClosedRuntimeError("quota policy provider is not allowed")
    if policy["allowed_operation"] != ALLOWED_OPERATION:
        raise FailClosedRuntimeError("quota policy operation is not allowed")
    return {
        "allowed_operation": ALLOWED_OPERATION,
        "allowed_provider": ALLOWED_PROVIDER,
        "max_provider_invocations": 1,
    }


def _normalize_isolation_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    required = {
        "isolation_mode",
        "provider_state_mutation_allowed",
        "runtime_state_mutation_allowed",
        "network_mutation_allowed",
        "replay_durability",
        "governance_authority_separated",
    }
    if not isinstance(metadata, dict) or set(metadata) != required:
        raise FailClosedRuntimeError("isolation metadata has malformed structure")
    if metadata["isolation_mode"] != "LOCAL_READONLY_SINGLE_PROVIDER":
        raise FailClosedRuntimeError("isolation metadata mode is invalid")
    if metadata["provider_state_mutation_allowed"] is not False:
        raise FailClosedRuntimeError("provider state mutation must be blocked")
    if metadata["runtime_state_mutation_allowed"] is not False:
        raise FailClosedRuntimeError("runtime state mutation must be blocked")
    if metadata["network_mutation_allowed"] is not False:
        raise FailClosedRuntimeError("network mutation must be blocked")
    if metadata["replay_durability"] != "APPEND_ONLY_HASHED_EVIDENCE":
        raise FailClosedRuntimeError("replay durability metadata is invalid")
    if metadata["governance_authority_separated"] is not True:
        raise FailClosedRuntimeError("governance authority separation must be preserved")
    return {
        "governance_authority_separated": True,
        "isolation_mode": "LOCAL_READONLY_SINGLE_PROVIDER",
        "network_mutation_allowed": False,
        "provider_state_mutation_allowed": False,
        "replay_durability": "APPEND_ONLY_HASHED_EVIDENCE",
        "runtime_state_mutation_allowed": False,
    }


def _validate_execution_against_quota(execution: MinimalGovernedExecutionPathResult, policy: dict[str, Any]) -> None:
    if execution.execution_status != EXECUTED:
        raise FailClosedRuntimeError("execution must be EXECUTED before isolation validation")
    if execution.provider != policy["allowed_provider"]:
        raise FailClosedRuntimeError("execution provider violates quota policy")
    if execution.provider_operation != policy["allowed_operation"]:
        raise FailClosedRuntimeError("execution operation violates quota policy")
    if not execution.provider_evidence_hash or not execution.session_lineage_hash:
        raise FailClosedRuntimeError("execution replay durability evidence is incomplete")
    if execution.governance_authority_separated is not True:
        raise FailClosedRuntimeError("execution governance authority separation is not preserved")
