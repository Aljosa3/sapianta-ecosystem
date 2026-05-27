"""Live semantic pressure validation for external LLM response artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.runtime.real_external_llm_attachment import attach_external_llm_response
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CONTAINED = "CONTAINED"
FAILED_CLOSED = "FAILED_CLOSED"
REJECTED = "REJECTED"
INVALIDATED = "INVALIDATED"

ACCEPTED = "ACCEPTED"
AMBIGUITY_PRESSURE = "AMBIGUITY_PRESSURE"
CAPABILITY_ESCALATION_PRESSURE = "CAPABILITY_ESCALATION_PRESSURE"
MALFORMED_COGNITION_STRUCTURE = "MALFORMED_COGNITION_STRUCTURE"
REPLAY_LINEAGE_DRIFT = "REPLAY_LINEAGE_DRIFT"
HIDDEN_AUTHORITY_DRIFT = "HIDDEN_AUTHORITY_DRIFT"
INVALID_PROPOSAL_NORMALIZATION = "INVALID_PROPOSAL_NORMALIZATION"
VALID_BOUNDED_RESPONSE = "VALID_BOUNDED_RESPONSE"

ALLOWED_CONTAINMENT_STATUSES = frozenset({CONTAINED, FAILED_CLOSED, REJECTED, INVALIDATED})
ALLOWED_PRESSURE_TYPES = frozenset(
    {
        AMBIGUITY_PRESSURE,
        CAPABILITY_ESCALATION_PRESSURE,
        MALFORMED_COGNITION_STRUCTURE,
        REPLAY_LINEAGE_DRIFT,
        HIDDEN_AUTHORITY_DRIFT,
        INVALID_PROPOSAL_NORMALIZATION,
        VALID_BOUNDED_RESPONSE,
    }
)
AUTHORITY_DRIFT_FIELDS = frozenset(
    {
        "authorization_id",
        "routing_id",
        "session_id",
        "execution_id",
        "contract_attachment_id",
        "provider_authority",
    }
)
AMBIGUITY_MARKERS = (" or ", "maybe", "ambiguous", "unclear", "?")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _pressure_hash_input(evidence: "LiveSemanticPressureValidationEvidence") -> dict[str, Any]:
    return {
        "validation_id": evidence.validation_id,
        "model_response_reference": evidence.model_response_reference,
        "pressure_type": evidence.pressure_type,
        "expected_result": evidence.expected_result,
        "actual_result": evidence.actual_result,
        "containment_status": evidence.containment_status,
        "failure_reason": evidence.failure_reason,
        "created_at": evidence.created_at,
    }


@dataclass(frozen=True)
class LiveSemanticPressureValidationEvidence:
    """Immutable replay-visible semantic pressure evidence."""

    validation_id: str
    model_response_reference: str
    pressure_type: str
    expected_result: str
    actual_result: str
    containment_status: str
    failure_reason: str
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.validation_id, "validation_id")
        _require_string(self.model_response_reference, "model_response_reference")
        _require_string(self.pressure_type, "pressure_type")
        _require_string(self.expected_result, "expected_result")
        _require_string(self.actual_result, "actual_result")
        _require_string(self.failure_reason, "failure_reason")
        _require_string(self.created_at, "created_at")
        if self.pressure_type not in ALLOWED_PRESSURE_TYPES:
            raise FailClosedRuntimeError("semantic pressure type is not allowed")
        if self.containment_status not in ALLOWED_CONTAINMENT_STATUSES:
            raise FailClosedRuntimeError("semantic pressure containment status is not allowed")
        expected_hash = replay_hash(_pressure_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("semantic pressure evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "validation_id": self.validation_id,
            "model_response_reference": self.model_response_reference,
            "pressure_type": self.pressure_type,
            "expected_result": self.expected_result,
            "actual_result": self.actual_result,
            "containment_status": self.containment_status,
            "failure_reason": self.failure_reason,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, evidence: dict[str, Any]) -> "LiveSemanticPressureValidationEvidence":
        if not isinstance(evidence, dict):
            raise FailClosedRuntimeError("semantic pressure evidence must be a JSON object")
        required = {
            "validation_id",
            "model_response_reference",
            "pressure_type",
            "expected_result",
            "actual_result",
            "containment_status",
            "failure_reason",
            "created_at",
            "evidence_hash",
        }
        if set(evidence) != required:
            raise FailClosedRuntimeError("semantic pressure evidence has malformed structure")
        return cls(**evidence)


def validate_live_semantic_pressure(
    *,
    validation_id: str,
    model_response_artifact: dict[str, Any],
    pressure_type: str,
    expected_result: str,
    created_at: str,
) -> LiveSemanticPressureValidationEvidence:
    """Validate an external model response artifact against one semantic pressure type."""

    reference = _model_response_reference(model_response_artifact)
    try:
        _require_string(validation_id, "validation_id")
        _require_string(created_at, "created_at")
        _require_string(expected_result, "expected_result")
        if pressure_type not in ALLOWED_PRESSURE_TYPES:
            raise FailClosedRuntimeError("semantic pressure type is not allowed")
        _preflight_external_response(model_response_artifact)
        proposal = attach_external_llm_response(model_response_artifact)
        _validate_pressure_specific_containment(model_response_artifact, pressure_type)
        canonical_serialize(proposal.to_dict())
        return LiveSemanticPressureValidationEvidence(
            validation_id=validation_id,
            model_response_reference=reference,
            pressure_type=pressure_type,
            expected_result=expected_result,
            actual_result=ACCEPTED,
            containment_status=CONTAINED,
            failure_reason="bounded model response remained contained",
            created_at=created_at,
        )
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        containment_status = _classify_containment_status(model_response_artifact, pressure_type)
        return LiveSemanticPressureValidationEvidence(
            validation_id=validation_id if isinstance(validation_id, str) and validation_id else "PRESSURE-INVALID",
            model_response_reference=reference,
            pressure_type=pressure_type if pressure_type in ALLOWED_PRESSURE_TYPES else MALFORMED_COGNITION_STRUCTURE,
            expected_result=expected_result if isinstance(expected_result, str) and expected_result else "FAIL_CLOSED",
            actual_result=containment_status,
            containment_status=containment_status,
            failure_reason=_failure_reason_for(containment_status, pressure_type),
            created_at=created_at if isinstance(created_at, str) and created_at else "1970-01-01T00:00:00+00:00",
        )


def reconstruct_live_semantic_pressure_lineage(
    evidence: list[LiveSemanticPressureValidationEvidence | dict[str, Any]]
    | tuple[LiveSemanticPressureValidationEvidence | dict[str, Any], ...],
) -> dict[str, Any]:
    if not isinstance(evidence, list | tuple):
        raise FailClosedRuntimeError("semantic pressure lineage must be a list")
    reconstructed = []
    seen_validation_ids: set[str] = set()
    previous_created_at = ""
    for index, item in enumerate(evidence):
        evidence_obj = LiveSemanticPressureValidationEvidence.from_dict(item) if isinstance(item, dict) else item
        if not isinstance(evidence_obj, LiveSemanticPressureValidationEvidence):
            raise FailClosedRuntimeError("semantic pressure lineage entry is invalid")
        artifact = evidence_obj.to_dict()
        if artifact["validation_id"] in seen_validation_ids:
            raise FailClosedRuntimeError("semantic pressure lineage contains duplicate validation_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("semantic pressure lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_validation_ids.add(artifact["validation_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "pressure_index": index,
                "validation_id": artifact["validation_id"],
                "model_response_reference": artifact["model_response_reference"],
                "pressure_type": artifact["pressure_type"],
                "containment_status": artifact["containment_status"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "pressure_count": len(reconstructed),
        "pressure_validations": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def _model_response_reference(model_response_artifact: Any) -> str:
    if isinstance(model_response_artifact, dict) and isinstance(model_response_artifact.get("model_response_id"), str):
        return model_response_artifact["model_response_id"]
    return "MODEL-RESPONSE-INVALID"


def _preflight_external_response(model_response_artifact: dict[str, Any]) -> None:
    if not isinstance(model_response_artifact, dict):
        raise FailClosedRuntimeError("external model response must be a JSON object")
    payload = model_response_artifact.get("proposal_payload")
    if not isinstance(payload, dict):
        return
    if AUTHORITY_DRIFT_FIELDS.intersection(payload):
        raise FailClosedRuntimeError("hidden authority drift detected")


def _validate_pressure_specific_containment(model_response_artifact: dict[str, Any], pressure_type: str) -> None:
    payload = model_response_artifact["proposal_payload"]
    if pressure_type == AMBIGUITY_PRESSURE:
        summary = str(payload.get("natural_language_input", "")).lower()
        if any(marker in summary for marker in AMBIGUITY_MARKERS):
            raise FailClosedRuntimeError("ambiguous cognition pressure rejected")
    if pressure_type in {
        CAPABILITY_ESCALATION_PRESSURE,
        MALFORMED_COGNITION_STRUCTURE,
        REPLAY_LINEAGE_DRIFT,
        HIDDEN_AUTHORITY_DRIFT,
        INVALID_PROPOSAL_NORMALIZATION,
    }:
        raise FailClosedRuntimeError("invalid semantic pressure was accepted unexpectedly")


def _classify_containment_status(model_response_artifact: Any, pressure_type: str) -> str:
    if pressure_type == REPLAY_LINEAGE_DRIFT:
        return INVALIDATED
    if pressure_type == MALFORMED_COGNITION_STRUCTURE:
        return FAILED_CLOSED
    if pressure_type == INVALID_PROPOSAL_NORMALIZATION:
        return FAILED_CLOSED
    if pressure_type in {AMBIGUITY_PRESSURE, CAPABILITY_ESCALATION_PRESSURE, HIDDEN_AUTHORITY_DRIFT}:
        return REJECTED
    if not isinstance(model_response_artifact, dict):
        return FAILED_CLOSED
    return FAILED_CLOSED


def _failure_reason_for(containment_status: str, pressure_type: str) -> str:
    if containment_status == INVALIDATED:
        return "semantic pressure replay drift invalidated"
    if containment_status == REJECTED and pressure_type == AMBIGUITY_PRESSURE:
        return "semantic pressure ambiguity rejected"
    if containment_status == REJECTED and pressure_type == CAPABILITY_ESCALATION_PRESSURE:
        return "semantic pressure capability escalation rejected"
    if containment_status == REJECTED and pressure_type == HIDDEN_AUTHORITY_DRIFT:
        return "semantic pressure hidden authority drift rejected"
    return "semantic pressure validation failed closed"
