"""Deterministic review gate for translated cognition contract candidates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.runtime.governed_execution_session import ALLOWED_PROVIDER_NAMES, ALLOWED_PROVIDER_OPERATIONS
from aigol.runtime.governed_proposal_translation_layer import (
    TRANSLATED,
    GovernedProposalTranslationResult,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


REVIEWED = "REVIEWED"
REJECTED = "REJECTED"

LOW = "LOW"
MEDIUM = "MEDIUM"
HIGH = "HIGH"
CRITICAL = "CRITICAL"

ALLOWED_REVIEW_STATUSES = frozenset({REVIEWED, REJECTED})
ALLOWED_RISK_LEVELS = frozenset({LOW, MEDIUM, HIGH, CRITICAL})


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _review_hash_input(result: "GovernedCognitionReviewResult") -> dict[str, Any]:
    return {
        "review_id": result.review_id,
        "proposal_id": result.proposal_id,
        "translation_id": result.translation_id,
        "review_status": result.review_status,
        "review_reason": result.review_reason,
        "risk_level": result.risk_level,
        "created_at": result.created_at,
    }


@dataclass(frozen=True)
class GovernedCognitionReviewResult:
    """Immutable replay-visible cognition review evidence."""

    review_id: str
    proposal_id: str
    translation_id: str
    review_status: str
    review_reason: str
    risk_level: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.review_id, "review_id")
        _require_string(self.proposal_id, "proposal_id")
        _require_string(self.translation_id, "translation_id")
        _require_string(self.review_reason, "review_reason")
        _require_string(self.created_at, "created_at")
        if self.review_status not in ALLOWED_REVIEW_STATUSES:
            raise FailClosedRuntimeError("review status must be REVIEWED or REJECTED")
        if self.risk_level not in ALLOWED_RISK_LEVELS:
            raise FailClosedRuntimeError("review risk level must be LOW, MEDIUM, HIGH, or CRITICAL")
        expected_hash = replay_hash(_review_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("cognition review evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "review_id": self.review_id,
            "proposal_id": self.proposal_id,
            "translation_id": self.translation_id,
            "review_status": self.review_status,
            "review_reason": self.review_reason,
            "risk_level": self.risk_level,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, artifact: dict[str, Any]) -> "GovernedCognitionReviewResult":
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("cognition review artifact must be a JSON object")
        required = {
            "review_id",
            "proposal_id",
            "translation_id",
            "review_status",
            "review_reason",
            "risk_level",
            "created_at",
            "evidence_hash",
        }
        if set(artifact) != required:
            raise FailClosedRuntimeError("cognition review artifact has malformed structure")
        return cls(
            review_id=artifact["review_id"],
            proposal_id=artifact["proposal_id"],
            translation_id=artifact["translation_id"],
            review_status=artifact["review_status"],
            review_reason=artifact["review_reason"],
            risk_level=artifact["risk_level"],
            created_at=artifact["created_at"],
            evidence_hash=artifact["evidence_hash"],
        )


def review_translated_cognition_candidate(
    *,
    review_id: str,
    translation: GovernedProposalTranslationResult | dict[str, Any],
    created_at: str,
) -> GovernedCognitionReviewResult:
    """Review translated contract candidate evidence without granting authority."""

    try:
        _require_string(review_id, "review_id")
        _require_string(created_at, "created_at")
        translation_obj = GovernedProposalTranslationResult.from_dict(translation) if isinstance(translation, dict) else translation
        if not isinstance(translation_obj, GovernedProposalTranslationResult):
            raise FailClosedRuntimeError("translation must be a GovernedProposalTranslationResult")
        if translation_obj.translation_status != TRANSLATED:
            return _rejected(
                review_id,
                translation_obj.proposal_id,
                translation_obj.translation_id,
                "translation status is not TRANSLATED",
                CRITICAL,
                created_at,
            )
        candidate = translation_obj.to_dict()["translated_contract_candidate"]
        risk_level = _validate_candidate_and_classify_risk(candidate)
        return GovernedCognitionReviewResult(
            review_id=review_id,
            proposal_id=translation_obj.proposal_id,
            translation_id=translation_obj.translation_id,
            review_status=REVIEWED,
            review_reason="translated cognition contract candidate reviewed for governance eligibility",
            risk_level=risk_level,
            created_at=created_at,
        )
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        return _rejected(
            review_id if isinstance(review_id, str) and review_id else "REVIEW-INVALID",
            _proposal_id_or_invalid(translation),
            _translation_id_or_invalid(translation),
            "cognition review validation failed closed",
            CRITICAL,
            created_at if isinstance(created_at, str) and created_at else "1970-01-01T00:00:00+00:00",
        )


def reconstruct_cognition_review_lineage(
    reviews: list[GovernedCognitionReviewResult | dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(reviews, list):
        raise FailClosedRuntimeError("cognition review lineage must be a list")
    reconstructed = []
    seen_review_ids: set[str] = set()
    previous_created_at = ""
    for index, review in enumerate(reviews):
        review_obj = GovernedCognitionReviewResult.from_dict(review) if isinstance(review, dict) else review
        if not isinstance(review_obj, GovernedCognitionReviewResult):
            raise FailClosedRuntimeError("cognition review lineage entry is invalid")
        artifact = review_obj.to_dict()
        if artifact["review_id"] in seen_review_ids:
            raise FailClosedRuntimeError("cognition review lineage contains duplicate review_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("cognition review lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_review_ids.add(artifact["review_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "review_index": index,
                "review_id": artifact["review_id"],
                "proposal_id": artifact["proposal_id"],
                "translation_id": artifact["translation_id"],
                "review_status": artifact["review_status"],
                "risk_level": artifact["risk_level"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "review_count": len(reconstructed),
        "reviews": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _validate_candidate_and_classify_risk(candidate: dict[str, Any]) -> str:
    if set(candidate) != {
        "candidate_type",
        "source_proposal_id",
        "source_proposal_type",
        "contract_reference",
        "allowed_providers",
        "requested_operations",
        "governance_authority_required",
    }:
        raise FailClosedRuntimeError("translated contract candidate has malformed structure")
    if candidate["candidate_type"] != "GOVERNED_EXECUTION_CONTRACT_CANDIDATE":
        raise FailClosedRuntimeError("translated contract candidate type is invalid")
    if candidate["governance_authority_required"] is not True:
        raise FailClosedRuntimeError("translated contract candidate must require governance authority")
    allowed_providers = candidate["allowed_providers"]
    requested_operations = candidate["requested_operations"]
    if not isinstance(allowed_providers, list) or not allowed_providers:
        raise FailClosedRuntimeError("translated contract candidate has no allowed providers")
    if not isinstance(requested_operations, list) or not requested_operations:
        raise FailClosedRuntimeError("translated contract candidate has no requested operations")
    if allowed_providers != sorted(allowed_providers):
        raise FailClosedRuntimeError("translated contract candidate provider ordering is not deterministic")
    for provider in allowed_providers:
        if provider not in ALLOWED_PROVIDER_NAMES:
            raise FailClosedRuntimeError("translated contract candidate contains unauthorized capability")
    operation_ids = set()
    for operation in requested_operations:
        if set(operation) != {"provider", "operation", "operation_id", "created_at"}:
            raise FailClosedRuntimeError("translated contract candidate operation is malformed")
        provider = operation["provider"]
        if provider not in allowed_providers:
            raise FailClosedRuntimeError("translated contract candidate operation provider is not allowed")
        if operation["operation"] not in ALLOWED_PROVIDER_OPERATIONS[provider]:
            raise FailClosedRuntimeError("translated contract candidate operation is not allowed")
        if operation["operation_id"] in operation_ids:
            raise FailClosedRuntimeError("translated contract candidate operation ids must be unique")
        operation_ids.add(operation["operation_id"])
    if "readonly_filesystem_provider" in allowed_providers:
        return HIGH
    if len(allowed_providers) > 1:
        return MEDIUM
    return LOW


def _rejected(
    review_id: str,
    proposal_id: str,
    translation_id: str,
    reason: str,
    risk_level: str,
    created_at: str,
) -> GovernedCognitionReviewResult:
    return GovernedCognitionReviewResult(
        review_id=review_id,
        proposal_id=proposal_id,
        translation_id=translation_id,
        review_status=REJECTED,
        review_reason=reason,
        risk_level=risk_level,
        created_at=created_at,
    )


def _proposal_id_or_invalid(translation: GovernedProposalTranslationResult | dict[str, Any]) -> str:
    if isinstance(translation, GovernedProposalTranslationResult):
        return translation.proposal_id
    if isinstance(translation, dict) and isinstance(translation.get("proposal_id"), str) and translation["proposal_id"].strip():
        return translation["proposal_id"]
    return "PROPOSAL-INVALID"


def _translation_id_or_invalid(translation: GovernedProposalTranslationResult | dict[str, Any]) -> str:
    if isinstance(translation, GovernedProposalTranslationResult):
        return translation.translation_id
    if isinstance(translation, dict) and isinstance(translation.get("translation_id"), str) and translation["translation_id"].strip():
        return translation["translation_id"]
    return "TRANSLATION-INVALID"
