"""First real operator usage evidence for the live governed runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.real_runtime_activation import ACTIVATED, activate_real_runtime
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


OPERATOR_COMPLETED = "COMPLETED"
OPERATOR_REJECTED = "REJECTED"
OPERATOR_USAGE_MODE = "READONLY_GOVERNED_OPERATOR_REQUEST"
ALLOWED_OPERATOR_USAGE_STATUSES = frozenset({OPERATOR_COMPLETED, OPERATOR_REJECTED})


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _operator_hash_input(evidence: "FirstRealOperatorUsageEvidence") -> dict[str, Any]:
    return {
        "operator_usage_id": evidence.operator_usage_id,
        "operator_id": evidence.operator_id,
        "operator_request": evidence.operator_request,
        "operator_usage_mode": evidence.operator_usage_mode,
        "activation_evidence_hash": evidence.activation_evidence_hash,
        "governed_return_summary": evidence.governed_return_summary,
        "operator_usage_status": evidence.operator_usage_status,
        "operator_usage_reason": evidence.operator_usage_reason,
        "created_at": evidence.created_at,
    }


@dataclass(frozen=True)
class FirstRealOperatorUsageEvidence:
    """Immutable replay-visible operator usage evidence."""

    operator_usage_id: str
    operator_id: str
    operator_request: str
    operator_usage_mode: str
    activation_evidence_hash: str
    governed_return_summary: str
    operator_usage_status: str
    operator_usage_reason: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.operator_usage_id, "operator_usage_id")
        _require_string(self.operator_id, "operator_id")
        _require_string(self.operator_request, "operator_request")
        _require_string(self.operator_usage_mode, "operator_usage_mode")
        _require_string(self.governed_return_summary, "governed_return_summary")
        _require_string(self.operator_usage_reason, "operator_usage_reason")
        _require_string(self.created_at, "created_at")
        if self.operator_usage_mode != OPERATOR_USAGE_MODE:
            raise FailClosedRuntimeError("operator usage mode is not allowed")
        if self.operator_usage_status not in ALLOWED_OPERATOR_USAGE_STATUSES:
            raise FailClosedRuntimeError("operator usage status is not allowed")
        expected_hash = replay_hash(_operator_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("first real operator usage evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "operator_usage_id": self.operator_usage_id,
            "operator_id": self.operator_id,
            "operator_request": self.operator_request,
            "operator_usage_mode": self.operator_usage_mode,
            "activation_evidence_hash": self.activation_evidence_hash,
            "governed_return_summary": self.governed_return_summary,
            "operator_usage_status": self.operator_usage_status,
            "operator_usage_reason": self.operator_usage_reason,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, evidence: dict[str, Any]) -> "FirstRealOperatorUsageEvidence":
        if not isinstance(evidence, dict):
            raise FailClosedRuntimeError("first real operator usage evidence must be a JSON object")
        required = {
            "operator_usage_id",
            "operator_id",
            "operator_request",
            "operator_usage_mode",
            "activation_evidence_hash",
            "governed_return_summary",
            "operator_usage_status",
            "operator_usage_reason",
            "created_at",
            "evidence_hash",
        }
        if set(evidence) != required:
            raise FailClosedRuntimeError("first real operator usage evidence has malformed structure")
        return cls(**evidence)


def run_first_real_operator_usage(
    *,
    operator_usage_id: str,
    operator_id: str,
    operator_request: str,
    created_at: str,
    timeout_seconds: int = 20,
) -> dict[str, Any]:
    """Run one real readonly operator request through the activated governed runtime."""

    try:
        _require_string(operator_usage_id, "operator_usage_id")
        normalized_operator_id = " ".join(_require_string(operator_id, "operator_id").split())
        normalized_request = " ".join(_require_string(operator_request, "operator_request").split())
        _require_string(created_at, "created_at")
        activation = activate_real_runtime(
            activation_id=f"{operator_usage_id}:ACTIVATION",
            human_prompt=normalized_request,
            created_at=created_at,
            timeout_seconds=timeout_seconds,
        )
        activation_evidence = activation["activation_evidence"]
        if activation_evidence.activation_status != ACTIVATED:
            return _operator_rejected(
                operator_usage_id,
                normalized_operator_id,
                normalized_request,
                activation_evidence.evidence_hash,
                "operator request rejected by governed runtime activation",
                created_at,
                activation,
            )
        governed_return_summary = _extract_governed_return_summary(activation)
        evidence = FirstRealOperatorUsageEvidence(
            operator_usage_id=operator_usage_id,
            operator_id=normalized_operator_id,
            operator_request=normalized_request,
            operator_usage_mode=OPERATOR_USAGE_MODE,
            activation_evidence_hash=activation_evidence.evidence_hash,
            governed_return_summary=governed_return_summary,
            operator_usage_status=OPERATOR_COMPLETED,
            operator_usage_reason="readonly operator request completed through governed runtime",
            created_at=created_at,
        )
        return {
            "operator_usage_evidence": evidence,
            "activation": activation,
            "operator_return": governed_return_summary,
            "operator_lineage": reconstruct_first_real_operator_usage_lineage([evidence]),
            "governance_authority_separated": True,
        }
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        return _operator_rejected(
            operator_usage_id if isinstance(operator_usage_id, str) and operator_usage_id else "OPERATOR-USAGE-INVALID",
            operator_id if isinstance(operator_id, str) and operator_id else "OPERATOR-INVALID",
            operator_request if isinstance(operator_request, str) and operator_request else "REQUEST-INVALID",
            "",
            "first real operator usage failed closed",
            created_at if isinstance(created_at, str) and created_at else "1970-01-01T00:00:00+00:00",
        )


def reconstruct_first_real_operator_usage_lineage(
    usages: list[FirstRealOperatorUsageEvidence | dict[str, Any]]
    | tuple[FirstRealOperatorUsageEvidence | dict[str, Any], ...],
) -> dict[str, Any]:
    if not isinstance(usages, list | tuple):
        raise FailClosedRuntimeError("first real operator usage lineage must be a list")
    reconstructed = []
    seen_usage_ids: set[str] = set()
    previous_created_at = ""
    for index, usage in enumerate(usages):
        usage_obj = FirstRealOperatorUsageEvidence.from_dict(usage) if isinstance(usage, dict) else usage
        if not isinstance(usage_obj, FirstRealOperatorUsageEvidence):
            raise FailClosedRuntimeError("first real operator usage lineage entry is invalid")
        artifact = usage_obj.to_dict()
        if artifact["operator_usage_id"] in seen_usage_ids:
            raise FailClosedRuntimeError("first real operator usage lineage contains duplicate operator_usage_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("first real operator usage lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_usage_ids.add(artifact["operator_usage_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "operator_usage_index": index,
                "operator_usage_id": artifact["operator_usage_id"],
                "operator_id": artifact["operator_id"],
                "operator_usage_status": artifact["operator_usage_status"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "operator_usage_count": len(reconstructed),
        "operator_usages": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _extract_governed_return_summary(activation: dict[str, Any]) -> str:
    usage_records = activation["usage_validation"]["usage_records"]
    if not isinstance(usage_records, list) or len(usage_records) != 1:
        raise FailClosedRuntimeError("operator usage requires exactly one governed usage record")
    governed_return = usage_records[0]["governed_return"]
    return _require_string(governed_return.normalized_return_summary, "governed_return_summary")


def _operator_rejected(
    operator_usage_id: str,
    operator_id: str,
    operator_request: str,
    activation_evidence_hash: str,
    reason: str,
    created_at: str,
    activation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    evidence = FirstRealOperatorUsageEvidence(
        operator_usage_id=operator_usage_id,
        operator_id=operator_id,
        operator_request=operator_request,
        operator_usage_mode=OPERATOR_USAGE_MODE,
        activation_evidence_hash=activation_evidence_hash,
        governed_return_summary="operator usage rejected",
        operator_usage_status=OPERATOR_REJECTED,
        operator_usage_reason=reason,
        created_at=created_at,
    )
    return {
        "operator_usage_evidence": evidence,
        "activation": activation,
        "operator_return": "operator usage rejected",
        "operator_lineage": reconstruct_first_real_operator_usage_lineage([evidence]),
        "governance_authority_separated": True,
    }
