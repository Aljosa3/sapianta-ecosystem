"""Deterministic constitutional Certification from Governance assessments only.

This surface accepts an already immutable Governance assessment and returns an
in-memory certification record. It has no access to upstream constitutional
inputs, persistence, authorization, or execution surfaces.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any

from aigol.runtime.constitutional_replay_governance import (
    CONSTITUTIONAL_GOVERNANCE_ASSESSMENT_V1,
    ConstitutionalGovernanceAssessment,
    ConstitutionalGovernanceStatus,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CONSTITUTIONAL_GOVERNANCE_CERTIFICATION_VERSION = "CONSTITUTIONAL_GOVERNANCE_CERTIFICATION_V1"
CONSTITUTIONAL_CERTIFICATION_V1 = "CONSTITUTIONAL_CERTIFICATION_V1"
GOVERNANCE_ASSESSMENT_CERTIFIED = "GOVERNANCE_ASSESSMENT_CERTIFIED"


class ConstitutionalCertificationStatus(str, Enum):
    """Certification of the constitutional meaning already determined by Governance."""

    COMPLIANCE_CERTIFIED = "CERTIFIED_CONSTITUTIONAL_COMPLIANCE"
    NON_COMPLIANCE_CERTIFIED = "CERTIFIED_CONSTITUTIONAL_NON_COMPLIANCE"


@dataclass(frozen=True)
class CertificationCompatibilityMetadata:
    """Immutable compatibility information for a Certification consumer."""

    governance_artifact_type: str
    governance_schema_version: str
    governance_version: str
    certification_version: str

    def to_dict(self) -> dict[str, str]:
        return {
            "certification_version": self.certification_version,
            "governance_artifact_type": self.governance_artifact_type,
            "governance_schema_version": self.governance_schema_version,
            "governance_version": self.governance_version,
        }


@dataclass(frozen=True)
class ConstitutionalCertification:
    """Immutable, non-authorizing certification of one Governance conclusion."""

    artifact_type: str
    schema_version: str
    certification_version: str
    certification_id: str
    certification_status: ConstitutionalCertificationStatus
    constitutional_status: ConstitutionalGovernanceStatus
    governance_assessment_id: str
    governance_assessment_hash: str
    replay_identity: str
    replay_hash: str
    validator_execution_id: str
    validator_result_hash: str
    contract_hash: str
    manifest_hash: str
    failure_codes: tuple[str, ...]
    compatibility: CertificationCompatibilityMetadata
    deterministic: bool = True
    read_only: bool = True
    certification_performed: bool = True
    governance_modified: bool = False
    replay_modified: bool = False
    validator_invoked: bool = False
    evidence_accessed: bool = False
    authorization_created: bool = False
    worker_assigned: bool = False
    provider_invoked: bool = False
    execution_requested: bool = False
    certification_hash: str = ""

    def to_dict(self, *, include_hash: bool = True) -> dict[str, Any]:
        result: dict[str, Any] = {
            "artifact_type": self.artifact_type,
            "authorization_created": self.authorization_created,
            "certification_id": self.certification_id,
            "certification_performed": self.certification_performed,
            "certification_status": self.certification_status.value,
            "certification_version": self.certification_version,
            "compatibility": self.compatibility.to_dict(),
            "constitutional_status": self.constitutional_status.value,
            "contract_hash": self.contract_hash,
            "deterministic": self.deterministic,
            "evidence_accessed": self.evidence_accessed,
            "execution_requested": self.execution_requested,
            "failure_codes": list(self.failure_codes),
            "governance_assessment_hash": self.governance_assessment_hash,
            "governance_assessment_id": self.governance_assessment_id,
            "governance_modified": self.governance_modified,
            "manifest_hash": self.manifest_hash,
            "provider_invoked": self.provider_invoked,
            "read_only": self.read_only,
            "replay_hash": self.replay_hash,
            "replay_identity": self.replay_identity,
            "replay_modified": self.replay_modified,
            "schema_version": self.schema_version,
            "validator_execution_id": self.validator_execution_id,
            "validator_invoked": self.validator_invoked,
            "validator_result_hash": self.validator_result_hash,
            "worker_assigned": self.worker_assigned,
        }
        if include_hash:
            result["certification_hash"] = self.certification_hash
        return result

    def with_certification_hash(self) -> "ConstitutionalCertification":
        return replace(self, certification_hash=replay_hash(self.to_dict(include_hash=False)))


def certify_constitutional_governance(
    assessment: ConstitutionalGovernanceAssessment,
) -> ConstitutionalCertification:
    """Certify one verified Governance assessment without changing any state."""

    _verify_governance_assessment(assessment)
    certification_status = _certification_status(assessment.constitutional_status)
    compatibility = CertificationCompatibilityMetadata(
        governance_artifact_type=assessment.artifact_type,
        governance_schema_version=assessment.schema_version,
        governance_version=assessment.governance_version,
        certification_version=CONSTITUTIONAL_GOVERNANCE_CERTIFICATION_VERSION,
    )
    certification = ConstitutionalCertification(
        artifact_type=CONSTITUTIONAL_CERTIFICATION_V1,
        schema_version="1.0.0",
        certification_version=CONSTITUTIONAL_GOVERNANCE_CERTIFICATION_VERSION,
        certification_id=_certification_id(assessment, certification_status),
        certification_status=certification_status,
        constitutional_status=assessment.constitutional_status,
        governance_assessment_id=assessment.assessment_id,
        governance_assessment_hash=assessment.assessment_hash,
        replay_identity=assessment.replay_identity,
        replay_hash=assessment.replay_hash,
        validator_execution_id=assessment.validator_execution_id,
        validator_result_hash=assessment.validator_result_hash,
        contract_hash=assessment.contract_hash,
        manifest_hash=assessment.manifest_hash,
        failure_codes=assessment.failure_codes,
        compatibility=compatibility,
    )
    return certification.with_certification_hash()


def _verify_governance_assessment(assessment: Any) -> None:
    if not isinstance(assessment, ConstitutionalGovernanceAssessment):
        raise FailClosedRuntimeError("constitutional Certification requires an immutable Governance assessment")
    actual_hash = assessment.assessment_hash
    if not isinstance(actual_hash, str) or actual_hash != replay_hash(assessment.to_dict(include_hash=False)):
        raise FailClosedRuntimeError("constitutional Certification Governance assessment hash mismatch")
    if assessment.artifact_type != CONSTITUTIONAL_GOVERNANCE_ASSESSMENT_V1:
        raise FailClosedRuntimeError("constitutional Certification Governance artifact type is invalid")
    if assessment.schema_version != "1.0.0" or not assessment.governance_version:
        raise FailClosedRuntimeError("constitutional Certification Governance compatibility is invalid")
    if assessment.governance_assessed is not True:
        raise FailClosedRuntimeError("constitutional Certification requires a completed Governance assessment")
    if assessment.assessment_id != _expected_governance_assessment_id(assessment):
        raise FailClosedRuntimeError("constitutional Certification Governance assessment identity is invalid")
    if assessment.constitutional_status not in {
        ConstitutionalGovernanceStatus.COMPLIANT,
        ConstitutionalGovernanceStatus.NON_COMPLIANT,
    }:
        raise FailClosedRuntimeError("constitutional Certification Governance status is invalid")
    if any(
        getattr(assessment, field) is not False
        for field in (
            "replay_modified",
            "validator_invoked",
            "evidence_modified",
            "certification_performed",
            "authorization_created",
            "worker_assigned",
            "provider_invoked",
            "execution_requested",
        )
    ):
        raise FailClosedRuntimeError("constitutional Certification Governance boundary is invalid")
    for field in (
        "assessment_id",
        "replay_identity",
        "replay_hash",
        "validator_execution_id",
        "validator_result_hash",
        "contract_hash",
        "manifest_hash",
        "validator_status",
    ):
        value = getattr(assessment, field)
        if not isinstance(value, str) or not value:
            raise FailClosedRuntimeError("constitutional Certification Governance identity is invalid")
    if not isinstance(assessment.failure_codes, tuple) or any(
        not isinstance(code, str) for code in assessment.failure_codes
    ):
        raise FailClosedRuntimeError("constitutional Certification Governance failure codes are invalid")
    expected_status = (
        ConstitutionalGovernanceStatus.COMPLIANT
        if assessment.validator_status == "PASS"
        else ConstitutionalGovernanceStatus.NON_COMPLIANT
        if assessment.validator_status == "FAIL"
        else None
    )
    if assessment.constitutional_status is not expected_status:
        raise FailClosedRuntimeError("constitutional Certification Governance conclusion is invalid")


def _certification_status(
    constitutional_status: ConstitutionalGovernanceStatus,
) -> ConstitutionalCertificationStatus:
    if constitutional_status is ConstitutionalGovernanceStatus.COMPLIANT:
        return ConstitutionalCertificationStatus.COMPLIANCE_CERTIFIED
    if constitutional_status is ConstitutionalGovernanceStatus.NON_COMPLIANT:
        return ConstitutionalCertificationStatus.NON_COMPLIANCE_CERTIFIED
    raise FailClosedRuntimeError("constitutional Certification Governance status is invalid")


def _expected_governance_assessment_id(assessment: ConstitutionalGovernanceAssessment) -> str:
    seed = {
        "replay_identity": assessment.replay_identity,
        "replay_hash": assessment.replay_hash,
        "validator_execution_id": assessment.validator_execution_id,
        "validator_result_hash": assessment.validator_result_hash,
        "constitutional_status": assessment.constitutional_status.value,
    }
    return "CONSTITUTIONAL-GOVERNANCE-ASSESSMENT-" + replay_hash(seed).split(":", 1)[1]


def _certification_id(
    assessment: ConstitutionalGovernanceAssessment,
    certification_status: ConstitutionalCertificationStatus,
) -> str:
    seed = {
        "certification_version": CONSTITUTIONAL_GOVERNANCE_CERTIFICATION_VERSION,
        "governance_assessment_id": assessment.assessment_id,
        "governance_assessment_hash": assessment.assessment_hash,
        "replay_identity": assessment.replay_identity,
        "constitutional_status": assessment.constitutional_status.value,
        "certification_status": certification_status.value,
    }
    return "CONSTITUTIONAL-CERTIFICATION-" + replay_hash(seed).split(":", 1)[1]


__all__ = [
    "CONSTITUTIONAL_CERTIFICATION_V1",
    "CONSTITUTIONAL_GOVERNANCE_CERTIFICATION_VERSION",
    "GOVERNANCE_ASSESSMENT_CERTIFIED",
    "CertificationCompatibilityMetadata",
    "ConstitutionalCertification",
    "ConstitutionalCertificationStatus",
    "certify_constitutional_governance",
]
