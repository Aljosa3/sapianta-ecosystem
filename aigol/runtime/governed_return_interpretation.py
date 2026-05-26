"""Governed return normalization for bounded provider execution evidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.runtime.minimal_governed_execution_path import (
    EXECUTED,
    MinimalGovernedExecutionPathResult,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.production_isolation_foundation import ISOLATED, ProductionIsolationEvidence
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


ACCEPTED = "ACCEPTED"
REJECTED = "REJECTED"

ALLOWED_RETURN_STATUSES = frozenset({ACCEPTED, REJECTED})
ALLOWED_PROVIDER_REFERENCE = "metadata_inspection_provider.inspect_runtime"


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _return_hash_input(artifact: "GovernedReturnInterpretationArtifact") -> dict[str, Any]:
    return {
        "return_id": artifact.return_id,
        "execution_reference": artifact.execution_reference,
        "provider_reference": artifact.provider_reference,
        "normalized_return_summary": artifact.normalized_return_summary,
        "return_status": artifact.return_status,
        "created_at": artifact.created_at,
    }


@dataclass(frozen=True)
class GovernedReturnInterpretationArtifact:
    """Immutable replay-visible governed return artifact."""

    return_id: str
    execution_reference: str
    provider_reference: str
    normalized_return_summary: str
    return_status: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.return_id, "return_id")
        _require_string(self.execution_reference, "execution_reference")
        _require_string(self.normalized_return_summary, "normalized_return_summary")
        _require_string(self.created_at, "created_at")
        if self.return_status not in ALLOWED_RETURN_STATUSES:
            raise FailClosedRuntimeError("return status must be ACCEPTED or REJECTED")
        if self.return_status == ACCEPTED:
            _require_string(self.provider_reference, "provider_reference")
        expected_hash = replay_hash(_return_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("governed return interpretation evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "return_id": self.return_id,
            "execution_reference": self.execution_reference,
            "provider_reference": self.provider_reference,
            "normalized_return_summary": self.normalized_return_summary,
            "return_status": self.return_status,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, artifact: dict[str, Any]) -> "GovernedReturnInterpretationArtifact":
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("governed return artifact must be a JSON object")
        required = {
            "return_id",
            "execution_reference",
            "provider_reference",
            "normalized_return_summary",
            "return_status",
            "created_at",
            "evidence_hash",
        }
        if set(artifact) != required:
            raise FailClosedRuntimeError("governed return artifact has malformed structure")
        return cls(**artifact)


def interpret_governed_execution_return(
    *,
    return_id: str,
    execution_result: MinimalGovernedExecutionPathResult | dict[str, Any],
    provider_evidence: dict[str, Any],
    session_lineage: dict[str, Any],
    isolation_evidence: ProductionIsolationEvidence | dict[str, Any],
    created_at: str,
) -> GovernedReturnInterpretationArtifact:
    """Normalize provider return evidence without invoking providers or cognition."""

    try:
        _require_string(return_id, "return_id")
        _require_string(created_at, "created_at")
        execution = MinimalGovernedExecutionPathResult.from_dict(execution_result) if isinstance(execution_result, dict) else execution_result
        isolation = ProductionIsolationEvidence.from_dict(isolation_evidence) if isinstance(isolation_evidence, dict) else isolation_evidence
        if not isinstance(execution, MinimalGovernedExecutionPathResult):
            raise FailClosedRuntimeError("execution_result must be MinimalGovernedExecutionPathResult")
        if not isinstance(isolation, ProductionIsolationEvidence):
            raise FailClosedRuntimeError("isolation_evidence must be ProductionIsolationEvidence")
        _validate_execution_continuity(execution, provider_evidence, session_lineage, isolation)
        summary = _normalize_provider_return_summary(provider_evidence)
        return GovernedReturnInterpretationArtifact(
            return_id=return_id,
            execution_reference=execution.execution_id,
            provider_reference=f"{execution.provider}.{execution.provider_operation}",
            normalized_return_summary=summary,
            return_status=ACCEPTED,
            created_at=created_at,
        )
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        execution_reference = ""
        if isinstance(execution_result, MinimalGovernedExecutionPathResult):
            execution_reference = execution_result.execution_id
        elif isinstance(execution_result, dict) and isinstance(execution_result.get("execution_id"), str):
            execution_reference = execution_result["execution_id"]
        return GovernedReturnInterpretationArtifact(
            return_id=return_id if isinstance(return_id, str) and return_id else "RETURN-INVALID",
            execution_reference=execution_reference or "EXECUTION-INVALID",
            provider_reference="",
            normalized_return_summary="governed return interpretation failed closed",
            return_status=REJECTED,
            created_at=created_at if isinstance(created_at, str) and created_at else "1970-01-01T00:00:00+00:00",
        )


def reconstruct_governed_return_lineage(
    returns: list[GovernedReturnInterpretationArtifact | dict[str, Any]]
    | tuple[GovernedReturnInterpretationArtifact | dict[str, Any], ...],
) -> dict[str, Any]:
    if not isinstance(returns, list | tuple):
        raise FailClosedRuntimeError("governed return lineage must be a list")
    reconstructed = []
    seen_return_ids: set[str] = set()
    previous_created_at = ""
    for index, return_artifact in enumerate(returns):
        return_obj = GovernedReturnInterpretationArtifact.from_dict(return_artifact) if isinstance(return_artifact, dict) else return_artifact
        if not isinstance(return_obj, GovernedReturnInterpretationArtifact):
            raise FailClosedRuntimeError("governed return lineage entry is invalid")
        artifact = return_obj.to_dict()
        if artifact["return_id"] in seen_return_ids:
            raise FailClosedRuntimeError("governed return lineage contains duplicate return_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("governed return lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_return_ids.add(artifact["return_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "return_index": index,
                "return_id": artifact["return_id"],
                "execution_reference": artifact["execution_reference"],
                "provider_reference": artifact["provider_reference"],
                "return_status": artifact["return_status"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "return_count": len(reconstructed),
        "returns": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _validate_execution_continuity(
    execution: MinimalGovernedExecutionPathResult,
    provider_evidence: dict[str, Any],
    session_lineage: dict[str, Any],
    isolation: ProductionIsolationEvidence,
) -> None:
    if execution.execution_status != EXECUTED:
        raise FailClosedRuntimeError("execution return requires EXECUTED status")
    if f"{execution.provider}.{execution.provider_operation}" != ALLOWED_PROVIDER_REFERENCE:
        raise FailClosedRuntimeError("execution return provider is not authorized")
    if isolation.isolation_status != ISOLATED:
        raise FailClosedRuntimeError("execution return requires isolated execution evidence")
    if isolation.execution_id != execution.execution_id:
        raise FailClosedRuntimeError("isolation evidence does not match execution")
    if not isinstance(provider_evidence, dict):
        raise FailClosedRuntimeError("provider evidence must be a JSON object")
    if provider_evidence.get("operation") != execution.provider_operation:
        raise FailClosedRuntimeError("provider evidence operation does not match execution")
    if provider_evidence.get("evidence_hash") != execution.provider_evidence_hash:
        raise FailClosedRuntimeError("provider evidence hash does not match execution")
    expected_provider_hash = replay_hash({key: value for key, value in provider_evidence.items() if key != "evidence_hash"})
    if expected_provider_hash != provider_evidence.get("evidence_hash"):
        raise FailClosedRuntimeError("provider evidence replay hash mismatch")
    if not isinstance(session_lineage, dict):
        raise FailClosedRuntimeError("session lineage must be a JSON object")
    if session_lineage.get("replay_valid") is not True:
        raise FailClosedRuntimeError("session lineage is not replay valid")
    if replay_hash(session_lineage) != execution.session_lineage_hash:
        raise FailClosedRuntimeError("session lineage hash does not match execution")
    canonical_serialize(provider_evidence)
    canonical_serialize(session_lineage)


def _normalize_provider_return_summary(provider_evidence: dict[str, Any]) -> str:
    inspected_fields = provider_evidence.get("inspected_fields")
    blocked_fields = provider_evidence.get("blocked_fields")
    metadata = provider_evidence.get("metadata")
    if not isinstance(inspected_fields, list) or not isinstance(blocked_fields, list) or not isinstance(metadata, dict):
        raise FailClosedRuntimeError("provider return structure is malformed")
    return (
        f"operation=inspect_runtime;"
        f"status={provider_evidence.get('status')};"
        f"inspected_fields={len(inspected_fields)};"
        f"blocked_fields={len(blocked_fields)};"
        f"metadata_keys={','.join(sorted(metadata))}"
    )
