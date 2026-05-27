"""Live OpenAI runtime connector for bounded proposal normalization.

This module is the OpenAI provider adapter; it is the only place in the
runtime that knows about OpenAI's API surface. Provider-agnostic AiGOL core
(bounded extraction, raw provider response capture, bounded proposal schema)
is delegated to dedicated AiGOL modules so the same flow can support other
providers without touching this adapter.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Callable

from aigol.runtime.bounded_extraction_layer import (
    NORMALIZED as EXTRACTION_NORMALIZED,
    extract_bounded_cognition_proposal,
)
from aigol.runtime.bounded_llm_attachment_architecture import BoundedCognitionProposal
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.raw_provider_response_capture import (
    NORMALIZED as RAW_NORMALIZED,
    REJECTED as RAW_REJECTED,
    RawProviderResponseEvidence,
    capture_raw_provider_response,
)
from aigol.runtime.real_external_llm_attachment import (
    attach_external_llm_response,
    external_model_response_hash,
    reconstruct_external_llm_proposal_lineage,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


NORMALIZED = "NORMALIZED"
REJECTED = "REJECTED"

OPENAI_PROVIDER = "openai"
OPENAI_MODEL_IDENTIFIER = "gpt-5.5"
OPENAI_ALLOWED_PROVIDER = "metadata_inspection_provider"
OPENAI_ALLOWED_OPERATION = "inspect_runtime"
OPENAI_OUTPUT_SCHEMA = "bounded_cognition_proposal_v1"

ALLOWED_OPENAI_CONNECTOR_STATUSES = frozenset({NORMALIZED, REJECTED})

NORMALIZATION_NORMALIZED_REASON = "OpenAI output normalized into bounded proposal evidence"
NORMALIZATION_REJECTED_REASON = "OpenAI output normalization failed closed"
CONNECTOR_NORMALIZED_REASON = "OpenAI inference normalized into bounded proposal evidence"
CONNECTOR_REJECTED_REASON = "OpenAI inference normalization failed closed"
DEFAULT_CREATED_AT = "1970-01-01T00:00:00+00:00"


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


def _connector_hash_input(evidence: "LiveOpenAIRuntimeConnectorEvidence") -> dict[str, Any]:
    return {
        "inference_id": evidence.inference_id,
        "openai_provider": evidence.openai_provider,
        "model_identifier": evidence.model_identifier,
        "normalized_request": _plain(evidence.normalized_request),
        "raw_response_evidence_hash": evidence.raw_response_evidence_hash,
        "extraction_evidence_hash": evidence.extraction_evidence_hash,
        "response_hash": evidence.response_hash,
        "proposal_evidence_hash": evidence.proposal_evidence_hash,
        "connector_status": evidence.connector_status,
        "reason": evidence.reason,
        "created_at": evidence.created_at,
    }


@dataclass(frozen=True)
class LiveOpenAIRuntimeConnectorEvidence:
    """Immutable replay-visible OpenAI connector evidence."""

    inference_id: str
    openai_provider: str
    model_identifier: str
    normalized_request: MappingProxyType
    raw_response_evidence_hash: str
    extraction_evidence_hash: str
    response_hash: str
    proposal_evidence_hash: str
    connector_status: str
    reason: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.inference_id, "inference_id")
        _require_string(self.openai_provider, "openai_provider")
        _require_string(self.model_identifier, "model_identifier")
        _require_string(self.reason, "reason")
        _require_string(self.created_at, "created_at")
        _require_string(self.raw_response_evidence_hash, "raw_response_evidence_hash")
        _require_string(self.extraction_evidence_hash, "extraction_evidence_hash")
        if self.openai_provider != OPENAI_PROVIDER:
            raise FailClosedRuntimeError("OpenAI connector provider is not allowed")
        if self.model_identifier != OPENAI_MODEL_IDENTIFIER:
            raise FailClosedRuntimeError("OpenAI connector model identifier is not allowed")
        if self.connector_status not in ALLOWED_OPENAI_CONNECTOR_STATUSES:
            raise FailClosedRuntimeError("OpenAI connector status must be NORMALIZED or REJECTED")
        if not isinstance(self.normalized_request, dict | MappingProxyType):
            raise FailClosedRuntimeError("normalized_request must be a JSON object")
        normalized = _immutable(_plain(self.normalized_request))
        canonical_serialize(_plain(normalized))
        object.__setattr__(self, "normalized_request", normalized)
        expected_hash = replay_hash(_connector_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("OpenAI connector evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "inference_id": self.inference_id,
            "openai_provider": self.openai_provider,
            "model_identifier": self.model_identifier,
            "normalized_request": _plain(self.normalized_request),
            "raw_response_evidence_hash": self.raw_response_evidence_hash,
            "extraction_evidence_hash": self.extraction_evidence_hash,
            "response_hash": self.response_hash,
            "proposal_evidence_hash": self.proposal_evidence_hash,
            "connector_status": self.connector_status,
            "reason": self.reason,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, evidence: dict[str, Any]) -> "LiveOpenAIRuntimeConnectorEvidence":
        if not isinstance(evidence, dict):
            raise FailClosedRuntimeError("OpenAI connector evidence must be a JSON object")
        required = {
            "inference_id",
            "openai_provider",
            "model_identifier",
            "normalized_request",
            "raw_response_evidence_hash",
            "extraction_evidence_hash",
            "response_hash",
            "proposal_evidence_hash",
            "connector_status",
            "reason",
            "created_at",
            "evidence_hash",
        }
        if set(evidence) != required:
            raise FailClosedRuntimeError("OpenAI connector evidence has malformed structure")
        return cls(**evidence)


def invoke_live_openai_runtime_connector(
    *,
    inference_id: str,
    prompt: str,
    openai_call: Callable[[dict[str, Any]], Any],
    created_at: str,
) -> dict[str, Any]:
    """Invoke one synchronous OpenAI call surface and normalize bounded proposal output.

    Provider adapter boundary:
      1. Calls OpenAI.
      2. Captures the raw provider response into RawProviderResponseEvidence
         BEFORE attempting normalization (provider-agnostic capture).
      3. Delegates bounded JSON extraction + schema validation to the
         provider-agnostic bounded extraction layer.
      4. Builds bounded proposal evidence only when the extraction layer
         reports NORMALIZED.
    """

    normalized_request: dict[str, Any] = {}
    created = created_at
    inference_identifier = inference_id if isinstance(inference_id, str) and inference_id else "OPENAI-INFERENCE-INVALID"
    raw_text: str | None = None

    try:
        _require_string(inference_id, "inference_id")
        _require_string(created, "created_at")
        if not callable(openai_call):
            raise FailClosedRuntimeError("openai_call must be callable")
        normalized_request = _normalize_openai_request(inference_id, prompt, created)
        raw_response = openai_call(deepcopy(normalized_request))
        raw_text = _extract_raw_response_text(raw_response)
    except Exception:
        raw_text = raw_text if raw_text is not None else None

    raw_evidence_created_at = created if isinstance(created, str) and created else DEFAULT_CREATED_AT
    extraction = extract_bounded_cognition_proposal(
        extraction_id=f"{inference_identifier}:EXTRACTION",
        raw_response_text=raw_text,
        created_at=raw_evidence_created_at,
    )
    extraction_evidence = extraction["extraction_evidence"]
    model_output = extraction["model_output"]

    if extraction_evidence.extraction_status == EXTRACTION_NORMALIZED and isinstance(model_output, dict):
        external_response = {
            "model_response_id": f"{inference_identifier}:OPENAI_RESPONSE",
            "model_provider": OPENAI_PROVIDER,
            "model_name": OPENAI_MODEL_IDENTIFIER,
            "proposal_payload": deepcopy(model_output),
            "created_at": raw_evidence_created_at,
        }
        external_response["response_hash"] = external_model_response_hash(external_response)
        proposal: BoundedCognitionProposal | None = attach_external_llm_response(external_response)
        proposal_lineage = reconstruct_external_llm_proposal_lineage([proposal])
        normalization_status = RAW_NORMALIZED
        normalization_reason = NORMALIZATION_NORMALIZED_REASON
    else:
        external_response = None
        proposal = None
        proposal_lineage = None
        normalization_status = RAW_REJECTED
        normalization_reason = NORMALIZATION_REJECTED_REASON

    raw_evidence = capture_raw_provider_response(
        raw_response_id=f"{inference_identifier}:RAW_PROVIDER_RESPONSE",
        provider_name=OPENAI_PROVIDER,
        model_name=OPENAI_MODEL_IDENTIFIER,
        raw_response_text=raw_text,
        normalization_status=normalization_status,
        normalization_reason=normalization_reason,
        created_at=raw_evidence_created_at,
    )

    connector_status = NORMALIZED if normalization_status == RAW_NORMALIZED else REJECTED
    connector_reason = (
        CONNECTOR_NORMALIZED_REASON if connector_status == NORMALIZED else CONNECTOR_REJECTED_REASON
    )
    evidence = LiveOpenAIRuntimeConnectorEvidence(
        inference_id=inference_identifier,
        openai_provider=OPENAI_PROVIDER,
        model_identifier=OPENAI_MODEL_IDENTIFIER,
        normalized_request=normalized_request,
        raw_response_evidence_hash=raw_evidence.evidence_hash,
        extraction_evidence_hash=extraction_evidence.evidence_hash,
        response_hash=external_response["response_hash"] if external_response else "",
        proposal_evidence_hash=proposal.evidence_hash if proposal else "",
        connector_status=connector_status,
        reason=connector_reason,
        created_at=raw_evidence_created_at,
    )
    return {
        "connector_evidence": evidence,
        "raw_provider_response": raw_evidence,
        "bounded_extraction": extraction,
        "external_model_response": external_response,
        "proposal": proposal,
        "proposal_lineage": proposal_lineage,
        "governance_authority_separated": True,
    }


def reconstruct_live_openai_runtime_lineage(
    evidence: list[LiveOpenAIRuntimeConnectorEvidence | dict[str, Any]]
    | tuple[LiveOpenAIRuntimeConnectorEvidence | dict[str, Any], ...],
) -> dict[str, Any]:
    if not isinstance(evidence, list | tuple):
        raise FailClosedRuntimeError("OpenAI connector lineage must be a list")
    reconstructed = []
    seen_inference_ids: set[str] = set()
    previous_created_at = ""
    for index, item in enumerate(evidence):
        evidence_obj = LiveOpenAIRuntimeConnectorEvidence.from_dict(item) if isinstance(item, dict) else item
        if not isinstance(evidence_obj, LiveOpenAIRuntimeConnectorEvidence):
            raise FailClosedRuntimeError("OpenAI connector lineage entry is invalid")
        artifact = evidence_obj.to_dict()
        if artifact["inference_id"] in seen_inference_ids:
            raise FailClosedRuntimeError("OpenAI connector lineage contains duplicate inference_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("OpenAI connector lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_inference_ids.add(artifact["inference_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "inference_index": index,
                "inference_id": artifact["inference_id"],
                "openai_provider": artifact["openai_provider"],
                "model_identifier": artifact["model_identifier"],
                "connector_status": artifact["connector_status"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "inference_count": len(reconstructed),
        "openai_inferences": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
        "llm_boundary": "openai_inference_proposal_only",
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _normalize_openai_request(inference_id: str, prompt: str, created_at: str) -> dict[str, Any]:
    normalized_prompt = " ".join(_require_string(prompt, "prompt").split())
    if not normalized_prompt:
        raise FailClosedRuntimeError("prompt is required")
    return {
        "inference_id": inference_id,
        "provider": OPENAI_PROVIDER,
        "model": OPENAI_MODEL_IDENTIFIER,
        "input": normalized_prompt,
        "allowed_provider": OPENAI_ALLOWED_PROVIDER,
        "allowed_operation": OPENAI_ALLOWED_OPERATION,
        "output_schema": OPENAI_OUTPUT_SCHEMA,
        "created_at": created_at,
    }


def _extract_raw_response_text(raw_response: Any) -> str | None:
    """Provider-specific raw text extraction — returns string or None, does not raise."""

    try:
        if isinstance(raw_response, dict):
            output_text = raw_response.get("output_text", "")
        else:
            output_text = getattr(raw_response, "output_text", "")
    except Exception:
        return None
    if not isinstance(output_text, str) or not output_text:
        return None
    return output_text
