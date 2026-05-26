"""Deterministic promotion eligibility evidence for governed changes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.runtime.governance_resilience_certification_gate import (
    CERTIFIED,
    GovernanceResilienceCertificationResult,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


ELIGIBLE = "ELIGIBLE"
BLOCKED = "BLOCKED"
ALLOWED_PROMOTION_STATUSES = frozenset({ELIGIBLE, BLOCKED})


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _promotion_hash_input(result: "GovernancePromotionResult") -> dict[str, Any]:
    return {
        "promotion_id": result.promotion_id,
        "related_change_id": result.related_change_id,
        "certification_id": result.certification_id,
        "promotion_status": result.promotion_status,
        "promotion_reason": result.promotion_reason,
        "created_at": result.created_at,
    }


@dataclass(frozen=True)
class GovernancePromotionResult:
    """Immutable replay-visible promotion eligibility evidence."""

    promotion_id: str
    related_change_id: str
    certification_id: str
    promotion_status: str
    promotion_reason: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.promotion_id, "promotion_id")
        _require_string(self.related_change_id, "related_change_id")
        _require_string(self.promotion_reason, "promotion_reason")
        _require_string(self.created_at, "created_at")
        if self.promotion_status not in ALLOWED_PROMOTION_STATUSES:
            raise FailClosedRuntimeError("promotion status must be ELIGIBLE or BLOCKED")
        if self.promotion_status == ELIGIBLE:
            _require_string(self.certification_id, "certification_id")
        expected_hash = replay_hash(_promotion_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("promotion evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "promotion_id": self.promotion_id,
            "related_change_id": self.related_change_id,
            "certification_id": self.certification_id,
            "promotion_status": self.promotion_status,
            "promotion_reason": self.promotion_reason,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, artifact: dict[str, Any]) -> "GovernancePromotionResult":
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("promotion artifact must be a JSON object")
        required = {
            "promotion_id",
            "related_change_id",
            "certification_id",
            "promotion_status",
            "promotion_reason",
            "created_at",
            "evidence_hash",
        }
        if set(artifact) != required:
            raise FailClosedRuntimeError("promotion artifact has malformed structure")
        return cls(
            promotion_id=artifact["promotion_id"],
            related_change_id=artifact["related_change_id"],
            certification_id=artifact["certification_id"],
            promotion_status=artifact["promotion_status"],
            promotion_reason=artifact["promotion_reason"],
            created_at=artifact["created_at"],
            evidence_hash=artifact["evidence_hash"],
        )


def evaluate_governance_promotion(
    *,
    promotion_id: str,
    related_change_id: str,
    certification: GovernanceResilienceCertificationResult | dict[str, Any] | None,
    created_at: str,
) -> GovernancePromotionResult:
    """Evaluate promotion eligibility from supplied certification evidence only."""

    try:
        _require_string(promotion_id, "promotion_id")
        _require_string(related_change_id, "related_change_id")
        _require_string(created_at, "created_at")
        if certification is None:
            return _blocked(promotion_id, related_change_id, "", "missing certification", created_at)
        certification_obj = GovernanceResilienceCertificationResult.from_dict(certification) if isinstance(certification, dict) else certification
        if not isinstance(certification_obj, GovernanceResilienceCertificationResult):
            raise FailClosedRuntimeError("certification evidence is invalid")
        if certification_obj.related_change_id != related_change_id:
            return _blocked(
                promotion_id,
                related_change_id,
                certification_obj.certification_id,
                "certification related_change_id does not match promotion request",
                created_at,
            )
        if certification_obj.certification_status != CERTIFIED:
            return _blocked(
                promotion_id,
                related_change_id,
                certification_obj.certification_id,
                "certification status is not CERTIFIED",
                created_at,
            )
        if certification_obj.failure_summary["promotion_eligible"] is not True:
            return _blocked(
                promotion_id,
                related_change_id,
                certification_obj.certification_id,
                "certification does not establish promotion eligibility",
                created_at,
            )
        return GovernancePromotionResult(
            promotion_id=promotion_id,
            related_change_id=related_change_id,
            certification_id=certification_obj.certification_id,
            promotion_status=ELIGIBLE,
            promotion_reason="resilience certification permits promotion eligibility",
            created_at=created_at,
        )
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        return _blocked(
            promotion_id if isinstance(promotion_id, str) and promotion_id else "PROMOTION-INVALID",
            related_change_id if isinstance(related_change_id, str) else "",
            "",
            "promotion validation failed closed",
            created_at if isinstance(created_at, str) and created_at else "1970-01-01T00:00:00+00:00",
        )


def reconstruct_promotion_lineage(promotions: list[GovernancePromotionResult | dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(promotions, list):
        raise FailClosedRuntimeError("promotion lineage must be a list")
    reconstructed = []
    seen_promotion_ids: set[str] = set()
    previous_created_at = ""
    for index, promotion in enumerate(promotions):
        promotion_obj = GovernancePromotionResult.from_dict(promotion) if isinstance(promotion, dict) else promotion
        if not isinstance(promotion_obj, GovernancePromotionResult):
            raise FailClosedRuntimeError("promotion lineage entry is invalid")
        artifact = promotion_obj.to_dict()
        if artifact["promotion_id"] in seen_promotion_ids:
            raise FailClosedRuntimeError("promotion lineage contains duplicate promotion_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("promotion lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_promotion_ids.add(artifact["promotion_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "promotion_index": index,
                "promotion_id": artifact["promotion_id"],
                "related_change_id": artifact["related_change_id"],
                "certification_id": artifact["certification_id"],
                "promotion_status": artifact["promotion_status"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "promotion_count": len(reconstructed),
        "promotions": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _blocked(
    promotion_id: str,
    related_change_id: str,
    certification_id: str,
    reason: str,
    created_at: str,
) -> GovernancePromotionResult:
    return GovernancePromotionResult(
        promotion_id=promotion_id,
        related_change_id=related_change_id,
        certification_id=certification_id,
        promotion_status=BLOCKED,
        promotion_reason=reason,
        created_at=created_at,
    )
