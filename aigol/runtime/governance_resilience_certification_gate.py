"""Deterministic resilience certification gate for governance promotion."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.synthetic_cognition_pressure_simulator import (
    ALLOWED_SIMULATION_TYPES,
    SyntheticCognitionPressureArtifact,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CERTIFIED = "CERTIFIED"
REJECTED = "REJECTED"
ALLOWED_CERTIFICATION_STATUSES = frozenset({CERTIFIED, REJECTED})


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


def _certification_hash_input(result: "GovernanceResilienceCertificationResult") -> dict[str, Any]:
    return {
        "certification_id": result.certification_id,
        "related_change_id": result.related_change_id,
        "resilience_suite_version": result.resilience_suite_version,
        "certification_status": result.certification_status,
        "validated_simulation_types": list(result.validated_simulation_types),
        "failure_summary": _plain(result.failure_summary),
        "created_at": result.created_at,
    }


@dataclass(frozen=True)
class GovernanceResilienceCertificationResult:
    """Immutable replay-visible resilience certification evidence."""

    certification_id: str
    related_change_id: str
    resilience_suite_version: str
    certification_status: str
    validated_simulation_types: tuple[str, ...]
    failure_summary: MappingProxyType
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.certification_id, "certification_id")
        _require_string(self.related_change_id, "related_change_id")
        _require_string(self.resilience_suite_version, "resilience_suite_version")
        _require_string(self.created_at, "created_at")
        if self.certification_status not in ALLOWED_CERTIFICATION_STATUSES:
            raise FailClosedRuntimeError("certification status must be CERTIFIED or REJECTED")
        if not isinstance(self.validated_simulation_types, list | tuple):
            raise FailClosedRuntimeError("validated_simulation_types must be a list")
        normalized_types = tuple(self.validated_simulation_types)
        if len(set(normalized_types)) != len(normalized_types):
            raise FailClosedRuntimeError("validated_simulation_types must not contain duplicates")
        for simulation_type in normalized_types:
            if simulation_type not in ALLOWED_SIMULATION_TYPES:
                raise FailClosedRuntimeError("unknown simulation type in certification")
        if tuple(sorted(normalized_types)) != normalized_types:
            raise FailClosedRuntimeError("validated_simulation_types ordering is not deterministic")
        if not isinstance(self.failure_summary, dict | MappingProxyType):
            raise FailClosedRuntimeError("failure_summary must be a JSON object")
        immutable_summary = _immutable(_plain(self.failure_summary))
        canonical_serialize(_plain(immutable_summary))
        object.__setattr__(self, "validated_simulation_types", normalized_types)
        object.__setattr__(self, "failure_summary", immutable_summary)
        expected_hash = replay_hash(_certification_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("resilience certification evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "certification_id": self.certification_id,
            "related_change_id": self.related_change_id,
            "resilience_suite_version": self.resilience_suite_version,
            "certification_status": self.certification_status,
            "validated_simulation_types": list(self.validated_simulation_types),
            "failure_summary": _plain(self.failure_summary),
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, artifact: dict[str, Any]) -> "GovernanceResilienceCertificationResult":
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("resilience certification artifact must be a JSON object")
        required = {
            "certification_id",
            "related_change_id",
            "resilience_suite_version",
            "certification_status",
            "validated_simulation_types",
            "failure_summary",
            "created_at",
            "evidence_hash",
        }
        if set(artifact) != required:
            raise FailClosedRuntimeError("resilience certification artifact has malformed structure")
        return cls(
            certification_id=artifact["certification_id"],
            related_change_id=artifact["related_change_id"],
            resilience_suite_version=artifact["resilience_suite_version"],
            certification_status=artifact["certification_status"],
            validated_simulation_types=tuple(artifact["validated_simulation_types"]),
            failure_summary=artifact["failure_summary"],
            created_at=artifact["created_at"],
            evidence_hash=artifact["evidence_hash"],
        )


def certify_governance_resilience(
    *,
    certification_id: str,
    related_change_id: str,
    resilience_suite_version: str,
    resilience_evidence: list[SyntheticCognitionPressureArtifact | dict[str, Any]],
    created_at: str,
) -> GovernanceResilienceCertificationResult:
    """Validate supplied resilience evidence before governance promotion eligibility."""

    try:
        _require_string(certification_id, "certification_id")
        _require_string(related_change_id, "related_change_id")
        _require_string(resilience_suite_version, "resilience_suite_version")
        _require_string(created_at, "created_at")
        if not isinstance(resilience_evidence, list) or not resilience_evidence:
            return _rejected(
                certification_id,
                related_change_id,
                resilience_suite_version,
                (),
                "missing resilience evidence",
                created_at,
            )
        validated = _validate_resilience_evidence(resilience_evidence)
        missing_types = sorted(ALLOWED_SIMULATION_TYPES.difference(validated))
        if missing_types:
            return _rejected(
                certification_id,
                related_change_id,
                resilience_suite_version,
                tuple(sorted(validated)),
                "incomplete simulation coverage",
                created_at,
                missing_simulation_types=missing_types,
            )
        return GovernanceResilienceCertificationResult(
            certification_id=certification_id,
            related_change_id=related_change_id,
            resilience_suite_version=resilience_suite_version,
            certification_status=CERTIFIED,
            validated_simulation_types=tuple(sorted(validated)),
            failure_summary={
                "expected_fail_closed_results": len(validated),
                "promotion_eligible": True,
                "rejection_reason": "",
                "missing_simulation_types": [],
            },
            created_at=created_at,
        )
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        return _rejected(
            certification_id if isinstance(certification_id, str) and certification_id else "CERTIFICATION-INVALID",
            related_change_id if isinstance(related_change_id, str) else "",
            resilience_suite_version if isinstance(resilience_suite_version, str) else "",
            (),
            "certification validation failed closed",
            created_at if isinstance(created_at, str) and created_at else "1970-01-01T00:00:00+00:00",
        )


def reconstruct_certification_lineage(
    certifications: list[GovernanceResilienceCertificationResult | dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(certifications, list):
        raise FailClosedRuntimeError("certification lineage must be a list")
    reconstructed = []
    seen_certification_ids: set[str] = set()
    previous_created_at = ""
    for index, certification in enumerate(certifications):
        certification_obj = GovernanceResilienceCertificationResult.from_dict(certification) if isinstance(certification, dict) else certification
        if not isinstance(certification_obj, GovernanceResilienceCertificationResult):
            raise FailClosedRuntimeError("certification lineage entry is invalid")
        artifact = certification_obj.to_dict()
        if artifact["certification_id"] in seen_certification_ids:
            raise FailClosedRuntimeError("certification lineage contains duplicate certification_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("certification lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_certification_ids.add(artifact["certification_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "certification_index": index,
                "certification_id": artifact["certification_id"],
                "related_change_id": artifact["related_change_id"],
                "certification_status": artifact["certification_status"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "certification_count": len(reconstructed),
        "certifications": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _validate_resilience_evidence(resilience_evidence: list[SyntheticCognitionPressureArtifact | dict[str, Any]]) -> set[str]:
    validated_types: set[str] = set()
    previous_created_at = ""
    for evidence in resilience_evidence:
        evidence_obj = SyntheticCognitionPressureArtifact.from_dict(evidence) if isinstance(evidence, dict) else evidence
        if not isinstance(evidence_obj, SyntheticCognitionPressureArtifact):
            raise FailClosedRuntimeError("resilience evidence entry is invalid")
        artifact = evidence_obj.to_dict()
        if artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("resilience evidence ordering is not deterministic")
        if artifact["simulation_type"] in validated_types:
            raise FailClosedRuntimeError("resilience evidence contains duplicate simulation coverage")
        validated_types.add(artifact["simulation_type"])
        previous_created_at = artifact["created_at"]
    return validated_types


def _rejected(
    certification_id: str,
    related_change_id: str,
    resilience_suite_version: str,
    validated_simulation_types: tuple[str, ...],
    reason: str,
    created_at: str,
    *,
    missing_simulation_types: list[str] | None = None,
) -> GovernanceResilienceCertificationResult:
    return GovernanceResilienceCertificationResult(
        certification_id=certification_id,
        related_change_id=related_change_id,
        resilience_suite_version=resilience_suite_version,
        certification_status=REJECTED,
        validated_simulation_types=tuple(sorted(validated_simulation_types)),
        failure_summary={
            "expected_fail_closed_results": len(validated_simulation_types),
            "promotion_eligible": False,
            "rejection_reason": reason,
            "missing_simulation_types": missing_simulation_types or [],
        },
        created_at=created_at,
    )
