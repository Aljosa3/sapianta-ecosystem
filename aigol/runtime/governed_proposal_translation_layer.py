"""Deterministic proposal-to-contract-candidate translation for AiGOL."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from aigol.runtime.bounded_llm_attachment_architecture import (
    CONTRACT_PROPOSAL,
    GOVERNANCE_QUERY,
    ROUTING_PROPOSAL,
    BoundedCognitionProposal,
)
from aigol.runtime.governed_execution_session import ALLOWED_PROVIDER_OPERATIONS
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


TRANSLATED = "TRANSLATED"
REJECTED = "REJECTED"
ALLOWED_TRANSLATION_STATUSES = frozenset({TRANSLATED, REJECTED})


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


def _translation_hash_input(result: "GovernedProposalTranslationResult") -> dict[str, Any]:
    return {
        "translation_id": result.translation_id,
        "proposal_id": result.proposal_id,
        "translated_contract_candidate": _plain(result.translated_contract_candidate),
        "translation_status": result.translation_status,
        "translation_reason": result.translation_reason,
        "created_at": result.created_at,
    }


@dataclass(frozen=True)
class GovernedProposalTranslationResult:
    """Immutable replay-visible translation evidence without execution authority."""

    translation_id: str
    proposal_id: str
    translated_contract_candidate: MappingProxyType
    translation_status: str
    translation_reason: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.translation_id, "translation_id")
        _require_string(self.proposal_id, "proposal_id")
        _require_string(self.translation_reason, "translation_reason")
        _require_string(self.created_at, "created_at")
        if self.translation_status not in ALLOWED_TRANSLATION_STATUSES:
            raise FailClosedRuntimeError("translation status must be TRANSLATED or REJECTED")
        if not isinstance(self.translated_contract_candidate, dict | MappingProxyType):
            raise FailClosedRuntimeError("translated_contract_candidate must be a JSON object")
        candidate = _immutable(_plain(self.translated_contract_candidate))
        canonical_serialize(_plain(candidate))
        object.__setattr__(self, "translated_contract_candidate", candidate)
        expected_hash = replay_hash(_translation_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("translation evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "translation_id": self.translation_id,
            "proposal_id": self.proposal_id,
            "translated_contract_candidate": _plain(self.translated_contract_candidate),
            "translation_status": self.translation_status,
            "translation_reason": self.translation_reason,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, artifact: dict[str, Any]) -> "GovernedProposalTranslationResult":
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("translation artifact must be a JSON object")
        required = {
            "translation_id",
            "proposal_id",
            "translated_contract_candidate",
            "translation_status",
            "translation_reason",
            "created_at",
            "evidence_hash",
        }
        if set(artifact) != required:
            raise FailClosedRuntimeError("translation artifact has malformed structure")
        return cls(
            translation_id=artifact["translation_id"],
            proposal_id=artifact["proposal_id"],
            translated_contract_candidate=artifact["translated_contract_candidate"],
            translation_status=artifact["translation_status"],
            translation_reason=artifact["translation_reason"],
            created_at=artifact["created_at"],
            evidence_hash=artifact["evidence_hash"],
        )


def translate_bounded_proposal(
    *,
    translation_id: str,
    proposal: BoundedCognitionProposal | dict[str, Any],
    created_at: str,
) -> GovernedProposalTranslationResult:
    """Translate bounded cognition proposal evidence into a contract candidate only."""

    try:
        _require_string(translation_id, "translation_id")
        _require_string(created_at, "created_at")
        proposal_obj = BoundedCognitionProposal.from_dict(proposal) if isinstance(proposal, dict) else proposal
        if not isinstance(proposal_obj, BoundedCognitionProposal):
            raise FailClosedRuntimeError("proposal must be a BoundedCognitionProposal")
        if proposal_obj.proposal_type == GOVERNANCE_QUERY:
            return _rejected(
                translation_id,
                proposal_obj.proposal_id,
                "governance query proposals do not translate into contract candidates",
                created_at,
            )
        candidate = _candidate_from_proposal(proposal_obj)
        return GovernedProposalTranslationResult(
            translation_id=translation_id,
            proposal_id=proposal_obj.proposal_id,
            translated_contract_candidate=candidate,
            translation_status=TRANSLATED,
            translation_reason="bounded cognition proposal translated into governed contract candidate",
            created_at=created_at,
        )
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        return _rejected(
            translation_id if isinstance(translation_id, str) and translation_id else "TRANSLATION-INVALID",
            _proposal_id_or_invalid(proposal),
            "translation validation failed closed",
            created_at if isinstance(created_at, str) and created_at else "1970-01-01T00:00:00+00:00",
        )


def reconstruct_translation_lineage(
    translations: list[GovernedProposalTranslationResult | dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(translations, list):
        raise FailClosedRuntimeError("translation lineage must be a list")
    reconstructed = []
    seen_translation_ids: set[str] = set()
    previous_created_at = ""
    for index, translation in enumerate(translations):
        translation_obj = GovernedProposalTranslationResult.from_dict(translation) if isinstance(translation, dict) else translation
        if not isinstance(translation_obj, GovernedProposalTranslationResult):
            raise FailClosedRuntimeError("translation lineage entry is invalid")
        artifact = translation_obj.to_dict()
        if artifact["translation_id"] in seen_translation_ids:
            raise FailClosedRuntimeError("translation lineage contains duplicate translation_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("translation lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_translation_ids.add(artifact["translation_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "translation_index": index,
                "translation_id": artifact["translation_id"],
                "proposal_id": artifact["proposal_id"],
                "translation_status": artifact["translation_status"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "translation_count": len(reconstructed),
        "translations": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _candidate_from_proposal(proposal: BoundedCognitionProposal) -> dict[str, Any]:
    requested_capabilities = list(proposal.requested_capabilities)
    requested_operations = []
    for provider in requested_capabilities:
        operation = sorted(ALLOWED_PROVIDER_OPERATIONS[provider])[0]
        requested_operations.append(
            {
                "provider": provider,
                "operation": operation,
                "operation_id": f"{proposal.proposal_id}:{provider}:candidate",
                "created_at": proposal.created_at,
            }
        )
    return {
        "candidate_type": "GOVERNED_EXECUTION_CONTRACT_CANDIDATE",
        "source_proposal_id": proposal.proposal_id,
        "source_proposal_type": proposal.proposal_type,
        "contract_reference": proposal.proposed_contract_reference,
        "allowed_providers": requested_capabilities,
        "requested_operations": requested_operations,
        "governance_authority_required": True,
    }


def _rejected(
    translation_id: str,
    proposal_id: str,
    reason: str,
    created_at: str,
) -> GovernedProposalTranslationResult:
    return GovernedProposalTranslationResult(
        translation_id=translation_id,
        proposal_id=proposal_id,
        translated_contract_candidate={},
        translation_status=REJECTED,
        translation_reason=reason,
        created_at=created_at,
    )


def _proposal_id_or_invalid(proposal: BoundedCognitionProposal | dict[str, Any]) -> str:
    if isinstance(proposal, BoundedCognitionProposal):
        return proposal.proposal_id
    if isinstance(proposal, dict) and isinstance(proposal.get("proposal_id"), str) and proposal["proposal_id"].strip():
        return proposal["proposal_id"]
    return "PROPOSAL-INVALID"
