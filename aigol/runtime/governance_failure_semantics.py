"""Deterministic governance failure semantics for AiGOL."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


FAIL_CLOSED = "FAIL_CLOSED"
REJECT = "REJECT"
INVALIDATE_LINEAGE = "INVALIDATE_LINEAGE"
TERMINATE_SESSION = "TERMINATE_SESSION"
QUARANTINE_REQUIRED = "QUARANTINE_REQUIRED"

LOW = "LOW"
MEDIUM = "MEDIUM"
HIGH = "HIGH"
CRITICAL = "CRITICAL"

ALLOWED_FAILURE_TYPES = frozenset({FAIL_CLOSED, REJECT, INVALIDATE_LINEAGE, TERMINATE_SESSION, QUARANTINE_REQUIRED})
ALLOWED_SEVERITIES = frozenset({LOW, MEDIUM, HIGH, CRITICAL})


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _failure_hash_input(failure: "GovernanceFailureEvidence") -> dict[str, Any]:
    return {
        "failure_id": failure.failure_id,
        "failure_type": failure.failure_type,
        "severity": failure.severity,
        "related_session_id": failure.related_session_id,
        "related_contract_id": failure.related_contract_id,
        "related_authorization_id": failure.related_authorization_id,
        "reason": failure.reason,
        "created_at": failure.created_at,
    }


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


@dataclass(frozen=True)
class GovernanceFailureEvidence:
    """Immutable replay-visible governance failure evidence."""

    failure_id: str
    failure_type: str
    severity: str
    related_session_id: str
    related_contract_id: str
    related_authorization_id: str
    reason: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.failure_id, "failure_id")
        _require_string(self.reason, "reason")
        _require_string(self.created_at, "created_at")
        if self.failure_type not in ALLOWED_FAILURE_TYPES:
            raise FailClosedRuntimeError("unknown governance failure type")
        if self.severity not in ALLOWED_SEVERITIES:
            raise FailClosedRuntimeError("unknown governance failure severity")
        expected_hash = replay_hash(_failure_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("governance failure evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "failure_id": self.failure_id,
            "failure_type": self.failure_type,
            "severity": self.severity,
            "related_session_id": self.related_session_id,
            "related_contract_id": self.related_contract_id,
            "related_authorization_id": self.related_authorization_id,
            "reason": self.reason,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, artifact: dict[str, Any]) -> "GovernanceFailureEvidence":
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("governance failure artifact must be a JSON object")
        required = {
            "failure_id",
            "failure_type",
            "severity",
            "related_session_id",
            "related_contract_id",
            "related_authorization_id",
            "reason",
            "created_at",
            "evidence_hash",
        }
        if set(artifact) != required:
            raise FailClosedRuntimeError("governance failure artifact has malformed structure")
        return cls(
            failure_id=artifact["failure_id"],
            failure_type=artifact["failure_type"],
            severity=artifact["severity"],
            related_session_id=artifact["related_session_id"],
            related_contract_id=artifact["related_contract_id"],
            related_authorization_id=artifact["related_authorization_id"],
            reason=artifact["reason"],
            created_at=artifact["created_at"],
            evidence_hash=artifact["evidence_hash"],
        )


def classify_governance_failure(
    *,
    failure_id: str,
    failure_type: str,
    severity: str,
    reason: str,
    created_at: str | None = None,
    related_session_id: str = "",
    related_contract_id: str = "",
    related_authorization_id: str = "",
) -> GovernanceFailureEvidence:
    """Classify a governance failure without runtime mutation."""

    return GovernanceFailureEvidence(
        failure_id=failure_id,
        failure_type=failure_type,
        severity=severity,
        related_session_id=related_session_id,
        related_contract_id=related_contract_id,
        related_authorization_id=related_authorization_id,
        reason=reason,
        created_at=created_at or _utc_timestamp(),
    )


def reconstruct_failure_lineage(failures: list[GovernanceFailureEvidence | dict[str, Any]]) -> dict[str, Any]:
    """Reconstruct deterministic append-only failure lineage from evidence."""

    if not isinstance(failures, list):
        raise FailClosedRuntimeError("failure lineage must be a list")
    reconstructed = []
    seen_failure_ids: set[str] = set()
    previous_created_at = ""
    for index, failure in enumerate(failures):
        failure_obj = GovernanceFailureEvidence.from_dict(failure) if isinstance(failure, dict) else failure
        if not isinstance(failure_obj, GovernanceFailureEvidence):
            raise FailClosedRuntimeError("failure lineage entry is invalid")
        artifact = failure_obj.to_dict()
        canonical_serialize(artifact)
        if artifact["failure_id"] in seen_failure_ids:
            raise FailClosedRuntimeError("failure lineage contains duplicate failure_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("failure lineage ordering is not deterministic")
        seen_failure_ids.add(artifact["failure_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "failure_index": index,
                "failure_id": artifact["failure_id"],
                "failure_type": artifact["failure_type"],
                "severity": artifact["severity"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "failure_count": len(reconstructed),
        "failures": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage
