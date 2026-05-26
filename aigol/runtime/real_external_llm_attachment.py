"""External LLM response attachment for bounded cognition proposals."""

from __future__ import annotations

from typing import Any

from aigol.runtime.bounded_llm_attachment_architecture import BoundedCognitionProposal
from aigol.runtime.minimal_real_llm_proposal_flow import (
    normalize_real_llm_proposal_input,
    reconstruct_real_llm_proposal_lineage,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


EXTERNAL_MODEL_RESPONSE_FIELDS = frozenset(
    {
        "model_response_id",
        "model_provider",
        "model_name",
        "proposal_payload",
        "created_at",
        "response_hash",
    }
)


def attach_external_llm_response(external_model_response: dict[str, Any]) -> BoundedCognitionProposal:
    """Normalize an externally produced model response into bounded proposal evidence."""

    if not isinstance(external_model_response, dict):
        raise FailClosedRuntimeError("external model response must be a JSON object")
    if set(external_model_response) != EXTERNAL_MODEL_RESPONSE_FIELDS:
        raise FailClosedRuntimeError("external model response has malformed structure")
    _require_string(external_model_response["model_response_id"], "model_response_id")
    _require_string(external_model_response["model_provider"], "model_provider")
    _require_string(external_model_response["model_name"], "model_name")
    _require_string(external_model_response["created_at"], "created_at")
    expected_hash = replay_hash(
        {
            "model_response_id": external_model_response["model_response_id"],
            "model_provider": external_model_response["model_provider"],
            "model_name": external_model_response["model_name"],
            "proposal_payload": external_model_response["proposal_payload"],
            "created_at": external_model_response["created_at"],
        }
    )
    if external_model_response["response_hash"] != expected_hash:
        raise FailClosedRuntimeError("external model response hash mismatch")
    proposal_payload = external_model_response["proposal_payload"]
    if not isinstance(proposal_payload, dict):
        raise FailClosedRuntimeError("external model proposal_payload must be a JSON object")
    normalized_payload = {
        "proposal_id": proposal_payload.get("proposal_id"),
        "natural_language_input": proposal_payload.get("natural_language_input"),
        "proposal_type": proposal_payload.get("proposal_type"),
        "requested_capabilities": proposal_payload.get("requested_capabilities"),
        "proposed_contract_reference": proposal_payload.get("proposed_contract_reference"),
        "created_at": proposal_payload.get("created_at"),
    }
    return normalize_real_llm_proposal_input(normalized_payload)


def reconstruct_external_llm_proposal_lineage(
    proposals: list[BoundedCognitionProposal | dict[str, Any]],
) -> dict[str, Any]:
    """Reconstruct replay-visible proposal lineage from external LLM outputs."""

    lineage = reconstruct_real_llm_proposal_lineage(proposals)
    return {
        "proposal_count": lineage["proposal_count"],
        "proposals": lineage["proposals"],
        "append_only_valid": lineage["append_only_valid"],
        "lineage_valid": lineage["lineage_valid"],
        "governance_authority_separated": lineage["governance_authority_separated"],
        "llm_boundary": "external_response_proposal_only",
        "lineage_hash": lineage["lineage_hash"],
    }


def external_model_response_hash(external_model_response: dict[str, Any]) -> str:
    """Compute deterministic response hash for an external model response payload."""

    if not isinstance(external_model_response, dict):
        raise FailClosedRuntimeError("external model response must be a JSON object")
    required_without_hash = EXTERNAL_MODEL_RESPONSE_FIELDS.difference({"response_hash"})
    if set(external_model_response) != required_without_hash:
        raise FailClosedRuntimeError("external model response hash input has malformed structure")
    return replay_hash(external_model_response)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
