"""Deterministic bounded extraction discipline for raw provider responses.

Provider-agnostic AiGOL core layer: takes raw provider response text and
returns ONLY a valid BoundedCognitionProposal-shaped model_output dict, with
deterministic failure classification when extraction or schema validation
fails. Strictly one-shot deterministic parsing; no permissive heuristics
are permitted.

The layer's contract:
    raw provider output
    -> bounded JSON extraction
    -> schema validation
    -> bounded proposal normalization (handled downstream)

Only normalized BoundedCognitionProposal artifacts are allowed past this
boundary into governance.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


NORMALIZED = "NORMALIZED"
REJECTED = "REJECTED"
ALLOWED_EXTRACTION_STATUSES = frozenset({NORMALIZED, REJECTED})

# Extraction stages (recorded as the stage where success was last achieved
# or where the failure occurred).
STAGE_RAW_INPUT = "RAW_INPUT"
STAGE_JSON_PARSE = "JSON_PARSE"
STAGE_JSON_OBJECT_SHAPE = "JSON_OBJECT_SHAPE"
STAGE_SCHEMA_VALIDATION = "SCHEMA_VALIDATION"
STAGE_BOUNDED_NORMALIZATION = "BOUNDED_NORMALIZATION"
ALLOWED_EXTRACTION_STAGES = frozenset(
    {
        STAGE_RAW_INPUT,
        STAGE_JSON_PARSE,
        STAGE_JSON_OBJECT_SHAPE,
        STAGE_SCHEMA_VALIDATION,
        STAGE_BOUNDED_NORMALIZATION,
    }
)

# Normalization (text/parse-level) failure classification.
NORMALIZATION_FAILURE_NONE = "NONE"
NORMALIZATION_FAILURE_EMPTY_RESPONSE = "EMPTY_RESPONSE"
NORMALIZATION_FAILURE_INVALID_JSON = "INVALID_JSON"
NORMALIZATION_FAILURE_MIXED_CONTENT = "MIXED_CONTENT"
NORMALIZATION_FAILURE_NON_JSON_OBJECT = "NON_JSON_OBJECT"
ALLOWED_NORMALIZATION_FAILURE_TYPES = frozenset(
    {
        NORMALIZATION_FAILURE_NONE,
        NORMALIZATION_FAILURE_EMPTY_RESPONSE,
        NORMALIZATION_FAILURE_INVALID_JSON,
        NORMALIZATION_FAILURE_MIXED_CONTENT,
        NORMALIZATION_FAILURE_NON_JSON_OBJECT,
    }
)

# Schema (structure/contract-level) failure classification.
SCHEMA_FAILURE_NONE = "NONE"
SCHEMA_FAILURE_MISSING_FIELDS = "MISSING_FIELDS"
SCHEMA_FAILURE_EXTRA_FIELDS = "EXTRA_FIELDS"
SCHEMA_FAILURE_INVALID_FIELD_TYPE = "INVALID_FIELD_TYPE"
SCHEMA_FAILURE_INVALID_PROPOSAL_TYPE = "INVALID_PROPOSAL_TYPE"
SCHEMA_FAILURE_UNAUTHORIZED_CAPABILITY = "UNAUTHORIZED_CAPABILITY"
SCHEMA_FAILURE_INVALID_CONTRACT_REFERENCE = "INVALID_CONTRACT_REFERENCE"
SCHEMA_FAILURE_BOUNDED_PROPOSAL_CONSTRUCTION = "BOUNDED_PROPOSAL_CONSTRUCTION"
ALLOWED_SCHEMA_FAILURE_TYPES = frozenset(
    {
        SCHEMA_FAILURE_NONE,
        SCHEMA_FAILURE_MISSING_FIELDS,
        SCHEMA_FAILURE_EXTRA_FIELDS,
        SCHEMA_FAILURE_INVALID_FIELD_TYPE,
        SCHEMA_FAILURE_INVALID_PROPOSAL_TYPE,
        SCHEMA_FAILURE_UNAUTHORIZED_CAPABILITY,
        SCHEMA_FAILURE_INVALID_CONTRACT_REFERENCE,
        SCHEMA_FAILURE_BOUNDED_PROPOSAL_CONSTRUCTION,
    }
)

BOUNDED_SCHEMA_V1 = "bounded_cognition_proposal_v1"
LIVE_READONLY_ALLOWED_PROPOSAL_TYPE = "CONTRACT_PROPOSAL"
LIVE_READONLY_ALLOWED_CAPABILITY = "metadata_inspection_provider"
CONTRACT_REFERENCE_PREFIX = "contract:"

REQUIRED_BOUNDED_PROPOSAL_FIELDS = frozenset(
    {
        "proposal_id",
        "natural_language_input",
        "proposal_type",
        "requested_capabilities",
        "proposed_contract_reference",
        "created_at",
    }
)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _extraction_hash_input(evidence: "BoundedExtractionEvidence") -> dict[str, Any]:
    return {
        "extraction_id": evidence.extraction_id,
        "bounded_schema_id": evidence.bounded_schema_id,
        "raw_response_hash": evidence.raw_response_hash,
        "raw_response_present": evidence.raw_response_present,
        "extraction_stage": evidence.extraction_stage,
        "extraction_status": evidence.extraction_status,
        "extraction_reason": evidence.extraction_reason,
        "normalization_failure_type": evidence.normalization_failure_type,
        "schema_failure_type": evidence.schema_failure_type,
        "proposal_evidence_hash": evidence.proposal_evidence_hash,
        "model_output_hash": evidence.model_output_hash,
        "created_at": evidence.created_at,
    }


@dataclass(frozen=True)
class BoundedExtractionEvidence:
    """Immutable replay-visible bounded extraction evidence."""

    extraction_id: str
    bounded_schema_id: str
    raw_response_hash: str
    raw_response_present: bool
    extraction_stage: str
    extraction_status: str
    extraction_reason: str
    normalization_failure_type: str
    schema_failure_type: str
    proposal_evidence_hash: str
    model_output_hash: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.extraction_id, "extraction_id")
        _require_string(self.bounded_schema_id, "bounded_schema_id")
        _require_string(self.extraction_reason, "extraction_reason")
        _require_string(self.created_at, "created_at")
        if self.bounded_schema_id != BOUNDED_SCHEMA_V1:
            raise FailClosedRuntimeError("bounded extraction schema id is not allowed")
        if self.extraction_status not in ALLOWED_EXTRACTION_STATUSES:
            raise FailClosedRuntimeError("bounded extraction status is not allowed")
        if self.extraction_stage not in ALLOWED_EXTRACTION_STAGES:
            raise FailClosedRuntimeError("bounded extraction stage is not allowed")
        if self.normalization_failure_type not in ALLOWED_NORMALIZATION_FAILURE_TYPES:
            raise FailClosedRuntimeError("bounded extraction normalization failure type is not allowed")
        if self.schema_failure_type not in ALLOWED_SCHEMA_FAILURE_TYPES:
            raise FailClosedRuntimeError("bounded extraction schema failure type is not allowed")
        if not isinstance(self.raw_response_present, bool):
            raise FailClosedRuntimeError("raw_response_present must be boolean")
        for field_name in ("raw_response_hash", "proposal_evidence_hash", "model_output_hash"):
            value = getattr(self, field_name)
            if not isinstance(value, str):
                raise FailClosedRuntimeError(f"{field_name} must be a string")
        if self.extraction_status == NORMALIZED:
            if self.normalization_failure_type != NORMALIZATION_FAILURE_NONE:
                raise FailClosedRuntimeError("normalized extraction must not classify a normalization failure")
            if self.schema_failure_type != SCHEMA_FAILURE_NONE:
                raise FailClosedRuntimeError("normalized extraction must not classify a schema failure")
            if self.extraction_stage != STAGE_BOUNDED_NORMALIZATION:
                raise FailClosedRuntimeError("normalized extraction must complete at bounded normalization stage")
            if not self.proposal_evidence_hash:
                raise FailClosedRuntimeError("normalized extraction requires proposal_evidence_hash")
            if not self.model_output_hash:
                raise FailClosedRuntimeError("normalized extraction requires model_output_hash")
        else:
            if (
                self.normalization_failure_type == NORMALIZATION_FAILURE_NONE
                and self.schema_failure_type == SCHEMA_FAILURE_NONE
            ):
                raise FailClosedRuntimeError("rejected extraction must classify a failure")
            if self.proposal_evidence_hash:
                raise FailClosedRuntimeError("rejected extraction must not carry proposal_evidence_hash")
            if self.model_output_hash:
                raise FailClosedRuntimeError("rejected extraction must not carry model_output_hash")
        expected_hash = replay_hash(_extraction_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("bounded extraction evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "extraction_id": self.extraction_id,
            "bounded_schema_id": self.bounded_schema_id,
            "raw_response_hash": self.raw_response_hash,
            "raw_response_present": self.raw_response_present,
            "extraction_stage": self.extraction_stage,
            "extraction_status": self.extraction_status,
            "extraction_reason": self.extraction_reason,
            "normalization_failure_type": self.normalization_failure_type,
            "schema_failure_type": self.schema_failure_type,
            "proposal_evidence_hash": self.proposal_evidence_hash,
            "model_output_hash": self.model_output_hash,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, evidence: dict[str, Any]) -> "BoundedExtractionEvidence":
        if not isinstance(evidence, dict):
            raise FailClosedRuntimeError("bounded extraction evidence must be a JSON object")
        required = {
            "extraction_id",
            "bounded_schema_id",
            "raw_response_hash",
            "raw_response_present",
            "extraction_stage",
            "extraction_status",
            "extraction_reason",
            "normalization_failure_type",
            "schema_failure_type",
            "proposal_evidence_hash",
            "model_output_hash",
            "created_at",
            "evidence_hash",
        }
        if set(evidence) != required:
            raise FailClosedRuntimeError("bounded extraction evidence has malformed structure")
        return cls(**evidence)


def extract_bounded_cognition_proposal(
    *,
    extraction_id: str,
    raw_response_text: str | None,
    created_at: str,
) -> dict[str, Any]:
    """Deterministically extract a bounded cognition proposal from raw provider text.

    Returns a dict containing the immutable evidence artifact, the validated
    model output dict (only on NORMALIZED), and a deterministic extraction
    lineage. Everything that does not strictly match the bounded schema is
    REJECTED with a deterministic failure classification; the layer performs
    no permissive parsing of any kind.
    """

    try:
        _require_string(extraction_id, "extraction_id")
        _require_string(created_at, "created_at")
    except FailClosedRuntimeError:
        evidence = _rejected_evidence(
            extraction_id=extraction_id if isinstance(extraction_id, str) and extraction_id else "EXTRACTION-INVALID",
            raw_response_hash="",
            raw_response_present=False,
            stage=STAGE_RAW_INPUT,
            reason="bounded extraction inputs invalid",
            normalization_failure_type=NORMALIZATION_FAILURE_EMPTY_RESPONSE,
            schema_failure_type=SCHEMA_FAILURE_NONE,
            created_at=created_at if isinstance(created_at, str) and created_at else "1970-01-01T00:00:00+00:00",
        )
        return _result(evidence, model_output=None)

    if raw_response_text is None or not isinstance(raw_response_text, str) or raw_response_text == "":
        evidence = _rejected_evidence(
            extraction_id=extraction_id,
            raw_response_hash="",
            raw_response_present=False,
            stage=STAGE_RAW_INPUT,
            reason="raw provider response text is empty",
            normalization_failure_type=NORMALIZATION_FAILURE_EMPTY_RESPONSE,
            schema_failure_type=SCHEMA_FAILURE_NONE,
            created_at=created_at,
        )
        return _result(evidence, model_output=None)

    raw_hash = replay_hash(raw_response_text)
    stripped = raw_response_text.strip()
    if not stripped or stripped[0] != "{" or stripped[-1] != "}":
        evidence = _rejected_evidence(
            extraction_id=extraction_id,
            raw_response_hash=raw_hash,
            raw_response_present=True,
            stage=STAGE_JSON_PARSE,
            reason="raw provider response is not a pure JSON object",
            normalization_failure_type=NORMALIZATION_FAILURE_MIXED_CONTENT,
            schema_failure_type=SCHEMA_FAILURE_NONE,
            created_at=created_at,
        )
        return _result(evidence, model_output=None)

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        evidence = _rejected_evidence(
            extraction_id=extraction_id,
            raw_response_hash=raw_hash,
            raw_response_present=True,
            stage=STAGE_JSON_PARSE,
            reason="raw provider response is not valid JSON",
            normalization_failure_type=NORMALIZATION_FAILURE_INVALID_JSON,
            schema_failure_type=SCHEMA_FAILURE_NONE,
            created_at=created_at,
        )
        return _result(evidence, model_output=None)

    if not isinstance(parsed, dict):
        evidence = _rejected_evidence(
            extraction_id=extraction_id,
            raw_response_hash=raw_hash,
            raw_response_present=True,
            stage=STAGE_JSON_OBJECT_SHAPE,
            reason="raw provider response did not decode to a JSON object",
            normalization_failure_type=NORMALIZATION_FAILURE_NON_JSON_OBJECT,
            schema_failure_type=SCHEMA_FAILURE_NONE,
            created_at=created_at,
        )
        return _result(evidence, model_output=None)

    schema_failure_type, schema_reason = _classify_schema(parsed)
    if schema_failure_type != SCHEMA_FAILURE_NONE:
        evidence = _rejected_evidence(
            extraction_id=extraction_id,
            raw_response_hash=raw_hash,
            raw_response_present=True,
            stage=STAGE_SCHEMA_VALIDATION,
            reason=schema_reason,
            normalization_failure_type=NORMALIZATION_FAILURE_NONE,
            schema_failure_type=schema_failure_type,
            created_at=created_at,
        )
        return _result(evidence, model_output=None)

    model_output: dict[str, Any] = deepcopy(parsed)
    model_output_hash = replay_hash(model_output)
    proposal_evidence_hash = replay_hash(
        {
            "proposal_id": model_output["proposal_id"],
            "proposal_type": model_output["proposal_type"],
            "proposal_summary": model_output["natural_language_input"],
            "requested_capabilities": list(model_output["requested_capabilities"]),
            "proposed_contract_reference": model_output["proposed_contract_reference"],
            "created_at": model_output["created_at"],
        }
    )
    evidence = BoundedExtractionEvidence(
        extraction_id=extraction_id,
        bounded_schema_id=BOUNDED_SCHEMA_V1,
        raw_response_hash=raw_hash,
        raw_response_present=True,
        extraction_stage=STAGE_BOUNDED_NORMALIZATION,
        extraction_status=NORMALIZED,
        extraction_reason="raw provider response normalized into bounded cognition proposal",
        normalization_failure_type=NORMALIZATION_FAILURE_NONE,
        schema_failure_type=SCHEMA_FAILURE_NONE,
        proposal_evidence_hash=proposal_evidence_hash,
        model_output_hash=model_output_hash,
        created_at=created_at,
    )
    return _result(evidence, model_output=model_output)


def reconstruct_bounded_extraction_lineage(
    extractions: list[BoundedExtractionEvidence | dict[str, Any]]
    | tuple[BoundedExtractionEvidence | dict[str, Any], ...],
) -> dict[str, Any]:
    if not isinstance(extractions, list | tuple):
        raise FailClosedRuntimeError("bounded extraction lineage must be a list")
    reconstructed = []
    seen_ids: set[str] = set()
    previous_created_at = ""
    for index, extraction in enumerate(extractions):
        extraction_obj = (
            BoundedExtractionEvidence.from_dict(extraction)
            if isinstance(extraction, dict)
            else extraction
        )
        if not isinstance(extraction_obj, BoundedExtractionEvidence):
            raise FailClosedRuntimeError("bounded extraction lineage entry is invalid")
        artifact = extraction_obj.to_dict()
        if artifact["extraction_id"] in seen_ids:
            raise FailClosedRuntimeError("bounded extraction lineage contains duplicate extraction_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("bounded extraction lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_ids.add(artifact["extraction_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "extraction_index": index,
                "extraction_id": artifact["extraction_id"],
                "extraction_stage": artifact["extraction_stage"],
                "extraction_status": artifact["extraction_status"],
                "normalization_failure_type": artifact["normalization_failure_type"],
                "schema_failure_type": artifact["schema_failure_type"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "extraction_count": len(reconstructed),
        "bounded_extractions": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
        "bounded_schema_id": BOUNDED_SCHEMA_V1,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _classify_schema(parsed: dict[str, Any]) -> tuple[str, str]:
    actual_fields = set(parsed)
    missing = REQUIRED_BOUNDED_PROPOSAL_FIELDS - actual_fields
    extra = actual_fields - REQUIRED_BOUNDED_PROPOSAL_FIELDS
    if missing:
        return (
            SCHEMA_FAILURE_MISSING_FIELDS,
            f"bounded proposal is missing required fields: {canonical_serialize(sorted(missing))}",
        )
    if extra:
        return (
            SCHEMA_FAILURE_EXTRA_FIELDS,
            f"bounded proposal contains unexpected fields: {canonical_serialize(sorted(extra))}",
        )
    if not isinstance(parsed["proposal_id"], str) or not parsed["proposal_id"].strip():
        return SCHEMA_FAILURE_INVALID_FIELD_TYPE, "bounded proposal proposal_id must be a non-empty string"
    if not isinstance(parsed["natural_language_input"], str) or not parsed["natural_language_input"].strip():
        return (
            SCHEMA_FAILURE_INVALID_FIELD_TYPE,
            "bounded proposal natural_language_input must be a non-empty string",
        )
    if not isinstance(parsed["created_at"], str) or not parsed["created_at"].strip():
        return SCHEMA_FAILURE_INVALID_FIELD_TYPE, "bounded proposal created_at must be a non-empty string"
    if parsed["proposal_type"] != LIVE_READONLY_ALLOWED_PROPOSAL_TYPE:
        return (
            SCHEMA_FAILURE_INVALID_PROPOSAL_TYPE,
            "bounded proposal proposal_type is not allowed for the live readonly runtime",
        )
    requested_capabilities = parsed["requested_capabilities"]
    if not isinstance(requested_capabilities, list):
        return (
            SCHEMA_FAILURE_INVALID_FIELD_TYPE,
            "bounded proposal requested_capabilities must be a JSON list",
        )
    if requested_capabilities != [LIVE_READONLY_ALLOWED_CAPABILITY]:
        return (
            SCHEMA_FAILURE_UNAUTHORIZED_CAPABILITY,
            "bounded proposal requested_capabilities is not authorized for the live readonly runtime",
        )
    proposed_contract_reference = parsed["proposed_contract_reference"]
    if not isinstance(proposed_contract_reference, str) or not proposed_contract_reference.strip():
        return (
            SCHEMA_FAILURE_INVALID_CONTRACT_REFERENCE,
            "bounded proposal proposed_contract_reference must be a non-empty string",
        )
    if not proposed_contract_reference.startswith(CONTRACT_REFERENCE_PREFIX):
        return (
            SCHEMA_FAILURE_INVALID_CONTRACT_REFERENCE,
            "bounded proposal proposed_contract_reference does not begin with 'contract:'",
        )
    return SCHEMA_FAILURE_NONE, ""


def _rejected_evidence(
    *,
    extraction_id: str,
    raw_response_hash: str,
    raw_response_present: bool,
    stage: str,
    reason: str,
    normalization_failure_type: str,
    schema_failure_type: str,
    created_at: str,
) -> BoundedExtractionEvidence:
    return BoundedExtractionEvidence(
        extraction_id=extraction_id,
        bounded_schema_id=BOUNDED_SCHEMA_V1,
        raw_response_hash=raw_response_hash,
        raw_response_present=raw_response_present,
        extraction_stage=stage,
        extraction_status=REJECTED,
        extraction_reason=reason,
        normalization_failure_type=normalization_failure_type,
        schema_failure_type=schema_failure_type,
        proposal_evidence_hash="",
        model_output_hash="",
        created_at=created_at,
    )


def _result(evidence: BoundedExtractionEvidence, *, model_output: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "extraction_evidence": evidence,
        "model_output": deepcopy(model_output) if isinstance(model_output, dict) else None,
        "extraction_lineage": reconstruct_bounded_extraction_lineage([evidence]),
        "governance_authority_separated": True,
    }
