"""Bounded proposal-only cognition attachment artifacts for AiGOL."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.runtime.governed_execution_session import ALLOWED_PROVIDER_NAMES
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CONTRACT_PROPOSAL = "CONTRACT_PROPOSAL"
ROUTING_PROPOSAL = "ROUTING_PROPOSAL"
GOVERNANCE_QUERY = "GOVERNANCE_QUERY"

GOVERNANCE_QUERY_CAPABILITY = "governance_query"

ALLOWED_PROPOSAL_TYPES = frozenset({CONTRACT_PROPOSAL, ROUTING_PROPOSAL, GOVERNANCE_QUERY})
ALLOWED_REQUESTED_CAPABILITIES = frozenset(set(ALLOWED_PROVIDER_NAMES) | {GOVERNANCE_QUERY_CAPABILITY})


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _proposal_hash_input(proposal: "BoundedCognitionProposal") -> dict[str, Any]:
    return {
        "proposal_id": proposal.proposal_id,
        "proposal_type": proposal.proposal_type,
        "proposal_summary": proposal.proposal_summary,
        "requested_capabilities": list(proposal.requested_capabilities),
        "proposed_contract_reference": proposal.proposed_contract_reference,
        "created_at": proposal.created_at,
    }


def _normalize_capabilities(capabilities: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    if not isinstance(capabilities, list | tuple) or not capabilities:
        raise FailClosedRuntimeError("requested_capabilities must be a non-empty list")
    normalized = tuple(capabilities)
    if len(set(normalized)) != len(normalized):
        raise FailClosedRuntimeError("requested_capabilities must not contain duplicates")
    for capability in normalized:
        if capability not in ALLOWED_REQUESTED_CAPABILITIES:
            raise FailClosedRuntimeError("unauthorized capability request")
    if tuple(sorted(normalized)) != normalized:
        raise FailClosedRuntimeError("requested_capabilities ordering is not deterministic")
    return normalized


@dataclass(frozen=True)
class BoundedCognitionProposal:
    """Immutable replay-visible proposal without execution authority."""

    proposal_id: str
    proposal_type: str
    proposal_summary: str
    requested_capabilities: tuple[str, ...]
    proposed_contract_reference: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.proposal_id, "proposal_id")
        _require_string(self.proposal_summary, "proposal_summary")
        _require_string(self.created_at, "created_at")
        if self.proposal_type not in ALLOWED_PROPOSAL_TYPES:
            raise FailClosedRuntimeError("unknown proposal type")
        normalized_capabilities = _normalize_capabilities(self.requested_capabilities)
        if self.proposal_type == GOVERNANCE_QUERY:
            if normalized_capabilities != (GOVERNANCE_QUERY_CAPABILITY,):
                raise FailClosedRuntimeError("governance query proposals may only request governance_query")
            if self.proposed_contract_reference:
                raise FailClosedRuntimeError("governance query proposals cannot carry contract references")
        else:
            _require_string(self.proposed_contract_reference, "proposed_contract_reference")
            if not self.proposed_contract_reference.startswith("contract:"):
                raise FailClosedRuntimeError("invalid contract translation boundary reference")
            if GOVERNANCE_QUERY_CAPABILITY in normalized_capabilities:
                raise FailClosedRuntimeError("contract and routing proposals cannot request governance_query")
        object.__setattr__(self, "requested_capabilities", normalized_capabilities)
        expected_hash = replay_hash(_proposal_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("cognition proposal evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "proposal_type": self.proposal_type,
            "proposal_summary": self.proposal_summary,
            "requested_capabilities": list(self.requested_capabilities),
            "proposed_contract_reference": self.proposed_contract_reference,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, artifact: dict[str, Any]) -> "BoundedCognitionProposal":
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("cognition proposal artifact must be a JSON object")
        required = {
            "proposal_id",
            "proposal_type",
            "proposal_summary",
            "requested_capabilities",
            "proposed_contract_reference",
            "created_at",
            "evidence_hash",
        }
        if set(artifact) != required:
            raise FailClosedRuntimeError("cognition proposal artifact has malformed structure")
        return cls(
            proposal_id=artifact["proposal_id"],
            proposal_type=artifact["proposal_type"],
            proposal_summary=artifact["proposal_summary"],
            requested_capabilities=tuple(artifact["requested_capabilities"]),
            proposed_contract_reference=artifact["proposed_contract_reference"],
            created_at=artifact["created_at"],
            evidence_hash=artifact["evidence_hash"],
        )


def create_bounded_cognition_proposal(
    *,
    proposal_id: str,
    proposal_type: str,
    proposal_summary: str,
    requested_capabilities: list[str],
    proposed_contract_reference: str,
    created_at: str,
) -> BoundedCognitionProposal:
    """Create proposal-only cognition evidence without governance authority."""

    return BoundedCognitionProposal(
        proposal_id=proposal_id,
        proposal_type=proposal_type,
        proposal_summary=proposal_summary,
        requested_capabilities=tuple(requested_capabilities),
        proposed_contract_reference=proposed_contract_reference,
        created_at=created_at,
    )


def reconstruct_cognition_lineage(proposals: list[BoundedCognitionProposal | dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(proposals, list):
        raise FailClosedRuntimeError("cognition lineage must be a list")
    reconstructed = []
    seen_proposal_ids: set[str] = set()
    previous_created_at = ""
    for index, proposal in enumerate(proposals):
        proposal_obj = BoundedCognitionProposal.from_dict(proposal) if isinstance(proposal, dict) else proposal
        if not isinstance(proposal_obj, BoundedCognitionProposal):
            raise FailClosedRuntimeError("cognition lineage entry is invalid")
        artifact = proposal_obj.to_dict()
        if artifact["proposal_id"] in seen_proposal_ids:
            raise FailClosedRuntimeError("cognition lineage contains duplicate proposal_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("cognition lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_proposal_ids.add(artifact["proposal_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "proposal_index": index,
                "proposal_id": artifact["proposal_id"],
                "proposal_type": artifact["proposal_type"],
                "proposed_contract_reference": artifact["proposed_contract_reference"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "proposal_count": len(reconstructed),
        "proposals": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage
