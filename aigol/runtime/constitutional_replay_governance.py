"""Read-only constitutional Governance assessment from Validator Replay.

Governance consumes only the Replay reconstruction boundary.  It never calls
the Validator, writes Replay, changes evidence, or creates Certification or
execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path
from typing import Any

from aigol.runtime.constitutional_validator_replay import (
    reconstruct_constitutional_validator_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CONSTITUTIONAL_REPLAY_GOVERNANCE_VERSION = "CONSTITUTIONAL_REPLAY_GOVERNANCE_V1"
CONSTITUTIONAL_GOVERNANCE_ASSESSMENT_V1 = "CONSTITUTIONAL_GOVERNANCE_ASSESSMENT_V1"
REPLAY_RECONSTRUCTION_VERIFIED = "REPLAY_RECONSTRUCTION_VERIFIED"
VALIDATOR_OUTCOME_INTERPRETED = "VALIDATOR_OUTCOME_INTERPRETED"


class ConstitutionalGovernanceStatus(str, Enum):
    """Read-only constitutional meanings derived from immutable Validator outcomes."""

    COMPLIANT = "CONSTITUTIONALLY_COMPLIANT"
    NON_COMPLIANT = "CONSTITUTIONALLY_NON_COMPLIANT"


@dataclass(frozen=True)
class ConstitutionalGovernanceAssessment:
    """Deterministic, non-authorizing interpretation of one Replay record."""

    artifact_type: str
    schema_version: str
    governance_version: str
    assessment_id: str
    replay_identity: str
    replay_hash: str
    validator_execution_id: str
    validator_result_hash: str
    contract_hash: str
    manifest_hash: str
    validator_status: str
    constitutional_status: ConstitutionalGovernanceStatus
    assessment_basis: tuple[str, ...]
    failure_codes: tuple[str, ...]
    deterministic: bool = True
    read_only: bool = True
    governance_assessed: bool = True
    replay_modified: bool = False
    validator_invoked: bool = False
    evidence_modified: bool = False
    certification_performed: bool = False
    authorization_created: bool = False
    worker_assigned: bool = False
    provider_invoked: bool = False
    execution_requested: bool = False
    assessment_hash: str = ""

    def to_dict(self, *, include_hash: bool = True) -> dict[str, Any]:
        result: dict[str, Any] = {
            "artifact_type": self.artifact_type,
            "assessment_basis": list(self.assessment_basis),
            "assessment_id": self.assessment_id,
            "authorization_created": self.authorization_created,
            "certification_performed": self.certification_performed,
            "constitutional_status": self.constitutional_status.value,
            "contract_hash": self.contract_hash,
            "deterministic": self.deterministic,
            "evidence_modified": self.evidence_modified,
            "execution_requested": self.execution_requested,
            "failure_codes": list(self.failure_codes),
            "governance_assessed": self.governance_assessed,
            "governance_version": self.governance_version,
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
            "validator_status": self.validator_status,
            "worker_assigned": self.worker_assigned,
        }
        if include_hash:
            result["assessment_hash"] = self.assessment_hash
        return result

    def with_assessment_hash(self) -> "ConstitutionalGovernanceAssessment":
        return replace(self, assessment_hash=replay_hash(self.to_dict(include_hash=False)))


def read_constitutional_validator_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Read and integrity-verify the immutable Validator Replay boundary."""

    return reconstruct_constitutional_validator_replay(replay_dir)


def evaluate_constitutional_replay(replay_dir: str | Path) -> ConstitutionalGovernanceAssessment:
    """Interpret a verified Validator Replay without changing any runtime state."""

    replay = read_constitutional_validator_replay(replay_dir)
    _verify_reconstruction(replay)
    validator_status = replay["overall_status"]
    constitutional_status = (
        ConstitutionalGovernanceStatus.COMPLIANT
        if validator_status == "PASS"
        else ConstitutionalGovernanceStatus.NON_COMPLIANT
    )
    assessment_id = _assessment_id(replay, constitutional_status)
    assessment = ConstitutionalGovernanceAssessment(
        artifact_type=CONSTITUTIONAL_GOVERNANCE_ASSESSMENT_V1,
        schema_version="1.0.0",
        governance_version=CONSTITUTIONAL_REPLAY_GOVERNANCE_VERSION,
        assessment_id=assessment_id,
        replay_identity=replay["replay_identity"],
        replay_hash=replay["replay_hash"],
        validator_execution_id=replay["validator_execution_id"],
        validator_result_hash=replay["validator_result_hash"],
        contract_hash=replay["contract"]["contract_hash"],
        manifest_hash=replay["evidence_manifest"]["manifest_hash"],
        validator_status=validator_status,
        constitutional_status=constitutional_status,
        assessment_basis=(REPLAY_RECONSTRUCTION_VERIFIED, VALIDATOR_OUTCOME_INTERPRETED),
        failure_codes=tuple(replay["result_summary"]["failure_codes"]),
    )
    return assessment.with_assessment_hash()


def _verify_reconstruction(replay: Any) -> None:
    if not isinstance(replay, dict):
        raise FailClosedRuntimeError("constitutional Governance requires a Replay reconstruction")
    required_strings = (
        "replay_identity",
        "replay_hash",
        "validator_execution_id",
        "validator_result_hash",
        "overall_status",
    )
    for field in required_strings:
        if not isinstance(replay.get(field), str) or not replay[field]:
            raise FailClosedRuntimeError("constitutional Governance Replay reconstruction is invalid")
    if replay["overall_status"] not in {"PASS", "FAIL"}:
        raise FailClosedRuntimeError("constitutional Governance received an invalid Validator outcome")
    if replay.get("replay_owner") != "PLATFORM_CORE_REPLAY" or replay.get("replay_visible") is not True:
        raise FailClosedRuntimeError("constitutional Governance requires Platform Replay evidence")
    if replay.get("replay_artifact_count") != 1:
        raise FailClosedRuntimeError("constitutional Governance Replay ordering is invalid")
    if not isinstance(replay.get("contract"), dict) or not isinstance(replay.get("evidence_manifest"), dict):
        raise FailClosedRuntimeError("constitutional Governance Replay lineage is invalid")
    for record, field in ((replay["contract"], "contract_hash"), (replay["evidence_manifest"], "manifest_hash")):
        if not isinstance(record.get(field), str) or not record[field]:
            raise FailClosedRuntimeError("constitutional Governance Replay lineage hash is invalid")
    summary = replay.get("result_summary")
    if not isinstance(summary, dict) or not isinstance(summary.get("failure_codes"), list):
        raise FailClosedRuntimeError("constitutional Governance Replay summary is invalid")
    if any(not isinstance(code, str) for code in summary["failure_codes"]):
        raise FailClosedRuntimeError("constitutional Governance Replay failure codes are invalid")
    if any(
        replay.get(field) is not False
        for field in (
            "governance_assessed",
            "certification_performed",
            "authorization_created",
            "worker_assigned",
            "provider_invoked",
            "execution_requested",
        )
    ):
        raise FailClosedRuntimeError("constitutional Governance requires pre-assessment Replay evidence")


def _assessment_id(
    replay: dict[str, Any], constitutional_status: ConstitutionalGovernanceStatus
) -> str:
    seed = {
        "replay_identity": replay["replay_identity"],
        "replay_hash": replay["replay_hash"],
        "validator_execution_id": replay["validator_execution_id"],
        "validator_result_hash": replay["validator_result_hash"],
        "constitutional_status": constitutional_status.value,
    }
    return "CONSTITUTIONAL-GOVERNANCE-ASSESSMENT-" + replay_hash(seed).split(":", 1)[1]


__all__ = [
    "CONSTITUTIONAL_GOVERNANCE_ASSESSMENT_V1",
    "CONSTITUTIONAL_REPLAY_GOVERNANCE_VERSION",
    "ConstitutionalGovernanceAssessment",
    "ConstitutionalGovernanceStatus",
    "REPLAY_RECONSTRUCTION_VERIFIED",
    "VALIDATOR_OUTCOME_INTERPRETED",
    "evaluate_constitutional_replay",
    "read_constitutional_validator_replay",
]
