"""Immutable models emitted by the Automatic Constitutional Validator Kernel."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any

from .canonical import canonical_hash


class ValidationStatus(str, Enum):
    """The only constitutional validator outcomes."""

    PASS = "PASS"
    FAIL = "FAIL"


@dataclass(frozen=True)
class ValidationTrustAnchors:
    """Invocation-scoped authenticity anchors supplied by Platform Core."""

    contract_id: str
    contract_hash: str
    manifest_id: str
    manifest_hash: str
    constitutional_version: str = "V31"
    platform_core_version: str = "V31"


@dataclass(frozen=True)
class ValidationCheck:
    phase: str
    status: ValidationStatus
    code: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "detail": self.detail,
            "phase": self.phase,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class EvidenceAuthenticationResult:
    evidence_id: str
    evidence_type: str
    artifact_reference: str
    artifact_hash: str
    status: ValidationStatus

    def to_dict(self) -> dict[str, str]:
        return {
            "artifact_hash": self.artifact_hash,
            "artifact_reference": self.artifact_reference,
            "evidence_id": self.evidence_id,
            "evidence_type": self.evidence_type,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class RequirementEvaluationResult:
    requirement_id: str
    status: ValidationStatus
    reason_code: str
    dependencies: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    evaluation_detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "dependencies": list(self.dependencies),
            "evaluation_detail": self.evaluation_detail,
            "evidence_ids": list(self.evidence_ids),
            "reason_code": self.reason_code,
            "requirement_id": self.requirement_id,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class ConstitutionalValidationResult:
    artifact_type: str
    schema_version: str
    validator_id: str
    validator_version: str
    status: ValidationStatus
    contract_id: str
    contract_version: str
    contract_hash: str
    manifest_id: str
    manifest_version: str
    manifest_hash: str
    validation_id: str
    invocation_id: str
    session_id: str
    chain_id: str
    scheduled_requirements: tuple[str, ...]
    checks: tuple[ValidationCheck, ...]
    evidence_results: tuple[EvidenceAuthenticationResult, ...]
    requirement_results: tuple[RequirementEvaluationResult, ...]
    failure_codes: tuple[str, ...]
    deterministic: bool = True
    read_only: bool = True
    authority_effect: str = "NONE"
    replay_persisted: bool = False
    governance_assessed: bool = False
    certification_performed: bool = False
    result_hash: str = ""

    def to_dict(self, *, include_hash: bool = True) -> dict[str, Any]:
        result: dict[str, Any] = {
            "artifact_type": self.artifact_type,
            "authority_effect": self.authority_effect,
            "certification_performed": self.certification_performed,
            "chain_id": self.chain_id,
            "checks": [check.to_dict() for check in self.checks],
            "contract_hash": self.contract_hash,
            "contract_id": self.contract_id,
            "contract_version": self.contract_version,
            "deterministic": self.deterministic,
            "evidence_results": [item.to_dict() for item in self.evidence_results],
            "failure_codes": list(self.failure_codes),
            "governance_assessed": self.governance_assessed,
            "invocation_id": self.invocation_id,
            "manifest_hash": self.manifest_hash,
            "manifest_id": self.manifest_id,
            "manifest_version": self.manifest_version,
            "read_only": self.read_only,
            "replay_persisted": self.replay_persisted,
            "requirement_results": [item.to_dict() for item in self.requirement_results],
            "scheduled_requirements": list(self.scheduled_requirements),
            "schema_version": self.schema_version,
            "session_id": self.session_id,
            "status": self.status.value,
            "validation_id": self.validation_id,
            "validator_id": self.validator_id,
            "validator_version": self.validator_version,
        }
        if include_hash:
            result["result_hash"] = self.result_hash
        return result

    def with_result_hash(self) -> "ConstitutionalValidationResult":
        return replace(self, result_hash=canonical_hash(self.to_dict(include_hash=False)))


__all__ = [
    "ConstitutionalValidationResult",
    "EvidenceAuthenticationResult",
    "RequirementEvaluationResult",
    "ValidationCheck",
    "ValidationStatus",
    "ValidationTrustAnchors",
]
