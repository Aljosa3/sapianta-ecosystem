"""Minimal real-LLM-facing proposal normalization for AiGOL."""

from __future__ import annotations

from typing import Any

from aigol.runtime.bounded_llm_attachment_architecture import (
    BoundedCognitionProposal,
    create_bounded_cognition_proposal,
    reconstruct_cognition_lineage,
)
from aigol.runtime.models import FailClosedRuntimeError


LLM_PROPOSAL_INPUT_FIELDS = frozenset(
    {
        "proposal_id",
        "natural_language_input",
        "proposal_type",
        "requested_capabilities",
        "proposed_contract_reference",
        "created_at",
    }
)


def normalize_real_llm_proposal_input(llm_proposal_input: dict[str, Any]) -> BoundedCognitionProposal:
    """Normalize bounded LLM proposal input into governed cognition proposal evidence."""

    if not isinstance(llm_proposal_input, dict):
        raise FailClosedRuntimeError("LLM proposal input must be a JSON object")
    if set(llm_proposal_input) != LLM_PROPOSAL_INPUT_FIELDS:
        raise FailClosedRuntimeError("LLM proposal input has malformed structure")
    proposal_summary = _normalize_natural_language(llm_proposal_input["natural_language_input"])
    requested_capabilities = llm_proposal_input["requested_capabilities"]
    if not isinstance(requested_capabilities, list):
        raise FailClosedRuntimeError("LLM proposal requested_capabilities must be a list")
    return create_bounded_cognition_proposal(
        proposal_id=_require_string(llm_proposal_input["proposal_id"], "proposal_id"),
        proposal_type=_require_string(llm_proposal_input["proposal_type"], "proposal_type"),
        proposal_summary=proposal_summary,
        requested_capabilities=requested_capabilities,
        proposed_contract_reference=_require_optional_string(
            llm_proposal_input["proposed_contract_reference"],
            "proposed_contract_reference",
        ),
        created_at=_require_string(llm_proposal_input["created_at"], "created_at"),
    )


def reconstruct_real_llm_proposal_lineage(
    proposals: list[BoundedCognitionProposal | dict[str, Any]],
) -> dict[str, Any]:
    """Reconstruct replay-visible LLM proposal lineage from bounded proposals."""

    lineage = reconstruct_cognition_lineage(proposals)
    return {
        "proposal_count": lineage["proposal_count"],
        "proposals": lineage["proposals"],
        "append_only_valid": lineage["append_only_valid"],
        "lineage_valid": lineage["lineage_valid"],
        "governance_authority_separated": lineage["governance_authority_separated"],
        "llm_boundary": "proposal_only",
        "lineage_hash": lineage["lineage_hash"],
    }


def _normalize_natural_language(value: Any) -> str:
    raw = _require_string(value, "natural_language_input")
    normalized = " ".join(raw.split())
    if not normalized:
        raise FailClosedRuntimeError("natural_language_input is required")
    return normalized


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _require_optional_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise FailClosedRuntimeError(f"{field_name} must be a string")
    return value
