"""Live external LLM inference boundary for bounded proposal normalization."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Callable

from aigol.runtime.bounded_llm_attachment_architecture import BoundedCognitionProposal
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.real_external_llm_attachment import (
    attach_external_llm_response,
    external_model_response_hash,
    reconstruct_external_llm_proposal_lineage,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


INFERRED = "INFERRED"
REJECTED = "REJECTED"

LIVE_EXTERNAL_MODEL_PROVIDER = "external_llm_provider"
LIVE_EXTERNAL_MODEL_NAME = "bounded-proposal-model"
LIVE_ALLOWED_PROVIDER = "metadata_inspection_provider"
LIVE_ALLOWED_OPERATION = "inspect_runtime"
LIVE_OUTPUT_SCHEMA = "bounded_cognition_proposal_v1"

ALLOWED_LIVE_INFERENCE_STATUSES = frozenset({INFERRED, REJECTED})
LIVE_MODEL_OUTPUT_FIELDS = frozenset(
    {
        "proposal_id",
        "natural_language_input",
        "proposal_type",
        "requested_capabilities",
        "proposed_contract_reference",
        "created_at",
    }
)


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


def _inference_hash_input(evidence: "LiveExternalLLMInferenceEvidence") -> dict[str, Any]:
    return {
        "inference_id": evidence.inference_id,
        "model_provider": evidence.model_provider,
        "model_name": evidence.model_name,
        "normalized_request": _plain(evidence.normalized_request),
        "response_hash": evidence.response_hash,
        "proposal_evidence_hash": evidence.proposal_evidence_hash,
        "inference_status": evidence.inference_status,
        "reason": evidence.reason,
        "created_at": evidence.created_at,
    }


@dataclass(frozen=True)
class LiveExternalLLMInferenceEvidence:
    """Immutable replay-visible live inference evidence."""

    inference_id: str
    model_provider: str
    model_name: str
    normalized_request: MappingProxyType
    response_hash: str
    proposal_evidence_hash: str
    inference_status: str
    reason: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.inference_id, "inference_id")
        _require_string(self.model_provider, "model_provider")
        _require_string(self.model_name, "model_name")
        _require_string(self.reason, "reason")
        _require_string(self.created_at, "created_at")
        if self.model_provider != LIVE_EXTERNAL_MODEL_PROVIDER:
            raise FailClosedRuntimeError("live inference model provider is not allowed")
        if self.model_name != LIVE_EXTERNAL_MODEL_NAME:
            raise FailClosedRuntimeError("live inference model name is not allowed")
        if self.inference_status not in ALLOWED_LIVE_INFERENCE_STATUSES:
            raise FailClosedRuntimeError("live inference status must be INFERRED or REJECTED")
        if not isinstance(self.normalized_request, dict | MappingProxyType):
            raise FailClosedRuntimeError("normalized_request must be a JSON object")
        normalized = _immutable(_plain(self.normalized_request))
        canonical_serialize(_plain(normalized))
        object.__setattr__(self, "normalized_request", normalized)
        expected_hash = replay_hash(_inference_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("live inference evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "inference_id": self.inference_id,
            "model_provider": self.model_provider,
            "model_name": self.model_name,
            "normalized_request": _plain(self.normalized_request),
            "response_hash": self.response_hash,
            "proposal_evidence_hash": self.proposal_evidence_hash,
            "inference_status": self.inference_status,
            "reason": self.reason,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, evidence: dict[str, Any]) -> "LiveExternalLLMInferenceEvidence":
        if not isinstance(evidence, dict):
            raise FailClosedRuntimeError("live inference evidence must be a JSON object")
        required = {
            "inference_id",
            "model_provider",
            "model_name",
            "normalized_request",
            "response_hash",
            "proposal_evidence_hash",
            "inference_status",
            "reason",
            "created_at",
            "evidence_hash",
        }
        if set(evidence) != required:
            raise FailClosedRuntimeError("live inference evidence has malformed structure")
        return cls(**evidence)


def invoke_live_external_llm_provider(
    *,
    inference_id: str,
    prompt: str,
    inference_callable: Callable[[dict[str, Any]], dict[str, Any]],
    created_at: str,
) -> dict[str, Any]:
    """Invoke one synchronous external inference source and normalize its proposal output."""

    normalized_request: dict[str, Any] = {}
    created = created_at
    try:
        _require_string(inference_id, "inference_id")
        _require_string(created, "created_at")
        if not callable(inference_callable):
            raise FailClosedRuntimeError("inference_callable must be callable")
        normalized_request = _normalize_live_inference_request(inference_id, prompt, created)
        model_output = inference_callable(deepcopy(normalized_request))
        _validate_live_model_output(model_output)
        external_response = {
            "model_response_id": f"{inference_id}:RESPONSE",
            "model_provider": LIVE_EXTERNAL_MODEL_PROVIDER,
            "model_name": LIVE_EXTERNAL_MODEL_NAME,
            "proposal_payload": deepcopy(model_output),
            "created_at": created,
        }
        external_response["response_hash"] = external_model_response_hash(external_response)
        proposal = attach_external_llm_response(external_response)
        proposal_lineage = reconstruct_external_llm_proposal_lineage([proposal])
        evidence = LiveExternalLLMInferenceEvidence(
            inference_id=inference_id,
            model_provider=LIVE_EXTERNAL_MODEL_PROVIDER,
            model_name=LIVE_EXTERNAL_MODEL_NAME,
            normalized_request=normalized_request,
            response_hash=external_response["response_hash"],
            proposal_evidence_hash=proposal.evidence_hash,
            inference_status=INFERRED,
            reason="live external inference normalized into bounded proposal evidence",
            created_at=created,
        )
        return {
            "inference_evidence": evidence,
            "external_model_response": external_response,
            "proposal": proposal,
            "proposal_lineage": proposal_lineage,
            "governance_authority_separated": True,
        }
    except Exception:
        evidence = LiveExternalLLMInferenceEvidence(
            inference_id=inference_id if isinstance(inference_id, str) and inference_id else "INFERENCE-INVALID",
            model_provider=LIVE_EXTERNAL_MODEL_PROVIDER,
            model_name=LIVE_EXTERNAL_MODEL_NAME,
            normalized_request=normalized_request,
            response_hash="",
            proposal_evidence_hash="",
            inference_status=REJECTED,
            reason="live external inference normalization failed closed",
            created_at=created if isinstance(created, str) and created else "1970-01-01T00:00:00+00:00",
        )
        return {
            "inference_evidence": evidence,
            "external_model_response": None,
            "proposal": None,
            "proposal_lineage": None,
            "governance_authority_separated": True,
        }


def reconstruct_live_external_llm_inference_lineage(
    evidence: list[LiveExternalLLMInferenceEvidence | dict[str, Any]]
    | tuple[LiveExternalLLMInferenceEvidence | dict[str, Any], ...],
) -> dict[str, Any]:
    if not isinstance(evidence, list | tuple):
        raise FailClosedRuntimeError("live inference lineage must be a list")
    reconstructed = []
    seen_inference_ids: set[str] = set()
    previous_created_at = ""
    for index, item in enumerate(evidence):
        evidence_obj = LiveExternalLLMInferenceEvidence.from_dict(item) if isinstance(item, dict) else item
        if not isinstance(evidence_obj, LiveExternalLLMInferenceEvidence):
            raise FailClosedRuntimeError("live inference lineage entry is invalid")
        artifact = evidence_obj.to_dict()
        if artifact["inference_id"] in seen_inference_ids:
            raise FailClosedRuntimeError("live inference lineage contains duplicate inference_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("live inference lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_inference_ids.add(artifact["inference_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "inference_index": index,
                "inference_id": artifact["inference_id"],
                "model_provider": artifact["model_provider"],
                "model_name": artifact["model_name"],
                "inference_status": artifact["inference_status"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "inference_count": len(reconstructed),
        "inferences": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
        "llm_boundary": "live_external_inference_proposal_only",
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _normalize_live_inference_request(inference_id: str, prompt: str, created_at: str) -> dict[str, Any]:
    normalized_prompt = " ".join(_require_string(prompt, "prompt").split())
    if not normalized_prompt:
        raise FailClosedRuntimeError("prompt is required")
    return {
        "inference_id": inference_id,
        "model_provider": LIVE_EXTERNAL_MODEL_PROVIDER,
        "model_name": LIVE_EXTERNAL_MODEL_NAME,
        "prompt": normalized_prompt,
        "allowed_provider": LIVE_ALLOWED_PROVIDER,
        "allowed_operation": LIVE_ALLOWED_OPERATION,
        "output_schema": LIVE_OUTPUT_SCHEMA,
        "created_at": created_at,
    }


def _validate_live_model_output(model_output: Any) -> None:
    if not isinstance(model_output, dict):
        raise FailClosedRuntimeError("live model output must be a JSON object")
    if set(model_output) != LIVE_MODEL_OUTPUT_FIELDS:
        raise FailClosedRuntimeError("live model output has malformed structure")
    if model_output["proposal_type"] != "CONTRACT_PROPOSAL":
        raise FailClosedRuntimeError("live model output proposal type is not allowed")
    if model_output["requested_capabilities"] != [LIVE_ALLOWED_PROVIDER]:
        raise FailClosedRuntimeError("live model output requested capability is not allowed")
    proposed_contract_reference = _require_string(
        model_output["proposed_contract_reference"],
        "proposed_contract_reference",
    )
    if not proposed_contract_reference.startswith("contract:"):
        raise FailClosedRuntimeError("live model output contract reference is invalid")
