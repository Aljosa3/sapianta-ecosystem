"""Readonly inspection of why a live governed cognition request was rejected.

AiGOL core (provider-agnostic): consumes only normalized BoundedCognitionProposal
artifacts and the generic RawProviderResponseEvidence captured by the provider
adapter. No provider-specific extraction logic lives in this module.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from aigol.runtime.bounded_extraction_layer import (
    BoundedExtractionEvidence,
    NORMALIZATION_FAILURE_NONE,
    NORMALIZED as EXTRACTION_NORMALIZED,
    SCHEMA_FAILURE_NONE,
)
from aigol.runtime.bounded_llm_attachment_architecture import BoundedCognitionProposal
from aigol.runtime.governed_cognition_review_gate import (
    REVIEWED,
    GovernedCognitionReviewResult,
)
from aigol.runtime.governed_contract_authorization_gate import (
    AUTHORIZED,
    ContractAuthorizationResult,
)
from aigol.runtime.governed_contract_router import (
    ROUTED,
    ContractRoutingResult,
)
from aigol.runtime.governed_return_interpretation import (
    ACCEPTED,
    GovernedReturnInterpretationArtifact,
)
from aigol.runtime.live_runtime_usage_validation import REJECTED as USAGE_REJECTED, VALIDATED
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.production_isolation_foundation import (
    ISOLATED,
    ProductionIsolationEvidence,
)
from aigol.runtime.raw_provider_response_capture import (
    NORMALIZED as RAW_NORMALIZED,
    RawProviderResponseEvidence,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


ANALYSIS_MODE = "READONLY_REJECTION_INSPECTION"
STAGE_NONE = "NONE"
STAGE_RAW_PROVIDER_RESPONSE = "RAW_PROVIDER_RESPONSE"
STAGE_BOUNDED_EXTRACTION = "BOUNDED_EXTRACTION"
STAGE_PROPOSAL_NORMALIZATION = "PROPOSAL_NORMALIZATION"
STAGE_OPENAI_INVOCATION = STAGE_PROPOSAL_NORMALIZATION  # alias kept only for incoming evidence diffs
STAGE_GOVERNED_EXECUTION = "GOVERNED_EXECUTION"
STAGE_COGNITION_REVIEW = "COGNITION_REVIEW"
STAGE_CONTRACT_AUTHORIZATION = "CONTRACT_AUTHORIZATION"
STAGE_CONTRACT_ROUTING = "CONTRACT_ROUTING"
STAGE_PRODUCTION_ISOLATION = "PRODUCTION_ISOLATION"
STAGE_GOVERNED_RETURN = "GOVERNED_RETURN"
STAGE_USAGE_INPUT = "USAGE_INPUT"

ALLOWED_REJECTION_STAGES = frozenset(
    {
        STAGE_NONE,
        STAGE_USAGE_INPUT,
        STAGE_RAW_PROVIDER_RESPONSE,
        STAGE_BOUNDED_EXTRACTION,
        STAGE_PROPOSAL_NORMALIZATION,
        STAGE_GOVERNED_EXECUTION,
        STAGE_COGNITION_REVIEW,
        STAGE_CONTRACT_AUTHORIZATION,
        STAGE_CONTRACT_ROUTING,
        STAGE_PRODUCTION_ISOLATION,
        STAGE_GOVERNED_RETURN,
    }
)

ALLOWED_USAGE_STATUSES = frozenset({VALIDATED, USAGE_REJECTED})


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _plain(value: Any) -> Any:
    if isinstance(value, MappingProxyType):
        return {key: _plain(value[key]) for key in value}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: _plain(value[key]) for key in value}
    if isinstance(value, list):
        return [_plain(item) for item in value]
    return deepcopy(value)


def _analysis_hash_input(evidence: "LiveCognitionRejectionAnalysisEvidence") -> dict[str, Any]:
    return {
        "analysis_id": evidence.analysis_id,
        "usage_id": evidence.usage_id,
        "usage_status": evidence.usage_status,
        "analysis_mode": evidence.analysis_mode,
        "rejection_stage": evidence.rejection_stage,
        "rejection_reason": evidence.rejection_reason,
        "provider_connector_status": evidence.provider_connector_status,
        "provider_connector_reason": evidence.provider_connector_reason,
        "raw_provider_response_provider_name": evidence.raw_provider_response_provider_name,
        "raw_provider_response_model_name": evidence.raw_provider_response_model_name,
        "raw_provider_response_present": evidence.raw_provider_response_present,
        "raw_provider_response_hash": evidence.raw_provider_response_hash,
        "raw_provider_response_evidence_hash": evidence.raw_provider_response_evidence_hash,
        "raw_provider_response_normalization_status": evidence.raw_provider_response_normalization_status,
        "raw_provider_response_normalization_reason": evidence.raw_provider_response_normalization_reason,
        "bounded_extraction_status": evidence.bounded_extraction_status,
        "bounded_extraction_stage": evidence.bounded_extraction_stage,
        "bounded_extraction_reason": evidence.bounded_extraction_reason,
        "bounded_extraction_evidence_hash": evidence.bounded_extraction_evidence_hash,
        "normalization_failure_type": evidence.normalization_failure_type,
        "schema_failure_type": evidence.schema_failure_type,
        "normalized_proposal_present": evidence.normalized_proposal_present,
        "normalized_proposal_hash": evidence.normalized_proposal_hash,
        "cognition_review_decision": _plain(evidence.cognition_review_decision),
        "authorization_decision": _plain(evidence.authorization_decision),
        "routing_decision": _plain(evidence.routing_decision),
        "isolation_decision": _plain(evidence.isolation_decision),
        "governed_return_decision": _plain(evidence.governed_return_decision),
        "governance_authority_separated": evidence.governance_authority_separated,
        "created_at": evidence.created_at,
    }


@dataclass(frozen=True)
class LiveCognitionRejectionAnalysisEvidence:
    """Immutable replay-visible rejection analysis evidence."""

    analysis_id: str
    usage_id: str
    usage_status: str
    analysis_mode: str
    rejection_stage: str
    rejection_reason: str
    provider_connector_status: str
    provider_connector_reason: str
    raw_provider_response_provider_name: str
    raw_provider_response_model_name: str
    raw_provider_response_present: bool
    raw_provider_response_hash: str
    raw_provider_response_evidence_hash: str
    raw_provider_response_normalization_status: str
    raw_provider_response_normalization_reason: str
    bounded_extraction_status: str
    bounded_extraction_stage: str
    bounded_extraction_reason: str
    bounded_extraction_evidence_hash: str
    normalization_failure_type: str
    schema_failure_type: str
    normalized_proposal_present: bool
    normalized_proposal_hash: str
    cognition_review_decision: MappingProxyType | dict[str, Any]
    authorization_decision: MappingProxyType | dict[str, Any]
    routing_decision: MappingProxyType | dict[str, Any]
    isolation_decision: MappingProxyType | dict[str, Any]
    governed_return_decision: MappingProxyType | dict[str, Any]
    governance_authority_separated: bool
    created_at: str
    evidence_hash: str = ""

    def __post_init__(self) -> None:
        _require_string(self.analysis_id, "analysis_id")
        _require_string(self.usage_id, "usage_id")
        _require_string(self.analysis_mode, "analysis_mode")
        _require_string(self.rejection_reason, "rejection_reason")
        _require_string(self.provider_connector_status, "provider_connector_status")
        _require_string(self.bounded_extraction_status, "bounded_extraction_status")
        _require_string(self.bounded_extraction_stage, "bounded_extraction_stage")
        _require_string(self.bounded_extraction_reason, "bounded_extraction_reason")
        _require_string(self.normalization_failure_type, "normalization_failure_type")
        _require_string(self.schema_failure_type, "schema_failure_type")
        _require_string(self.created_at, "created_at")
        if self.analysis_mode != ANALYSIS_MODE:
            raise FailClosedRuntimeError("rejection analysis mode is not allowed")
        if self.usage_status not in ALLOWED_USAGE_STATUSES:
            raise FailClosedRuntimeError("rejection analysis usage status is not allowed")
        if self.rejection_stage not in ALLOWED_REJECTION_STAGES:
            raise FailClosedRuntimeError("rejection analysis stage is not allowed")
        for boolean_field in (
            "raw_provider_response_present",
            "normalized_proposal_present",
            "governance_authority_separated",
        ):
            if not isinstance(getattr(self, boolean_field), bool):
                raise FailClosedRuntimeError(f"{boolean_field} must be boolean")
        for decision_field in (
            "cognition_review_decision",
            "authorization_decision",
            "routing_decision",
            "isolation_decision",
            "governed_return_decision",
        ):
            value = getattr(self, decision_field)
            if not isinstance(value, dict | MappingProxyType):
                raise FailClosedRuntimeError(f"{decision_field} must be a JSON object")
            canonical_serialize(_plain(value))
        expected_hash = replay_hash(_analysis_hash_input(self))
        if self.evidence_hash and self.evidence_hash != expected_hash:
            raise FailClosedRuntimeError("rejection analysis evidence hash mismatch")
        object.__setattr__(self, "evidence_hash", self.evidence_hash or expected_hash)

    def to_dict(self) -> dict[str, Any]:
        return {
            "analysis_id": self.analysis_id,
            "usage_id": self.usage_id,
            "usage_status": self.usage_status,
            "analysis_mode": self.analysis_mode,
            "rejection_stage": self.rejection_stage,
            "rejection_reason": self.rejection_reason,
            "provider_connector_status": self.provider_connector_status,
            "provider_connector_reason": self.provider_connector_reason,
            "raw_provider_response_provider_name": self.raw_provider_response_provider_name,
            "raw_provider_response_model_name": self.raw_provider_response_model_name,
            "raw_provider_response_present": self.raw_provider_response_present,
            "raw_provider_response_hash": self.raw_provider_response_hash,
            "raw_provider_response_evidence_hash": self.raw_provider_response_evidence_hash,
            "raw_provider_response_normalization_status": self.raw_provider_response_normalization_status,
            "raw_provider_response_normalization_reason": self.raw_provider_response_normalization_reason,
            "bounded_extraction_status": self.bounded_extraction_status,
            "bounded_extraction_stage": self.bounded_extraction_stage,
            "bounded_extraction_reason": self.bounded_extraction_reason,
            "bounded_extraction_evidence_hash": self.bounded_extraction_evidence_hash,
            "normalization_failure_type": self.normalization_failure_type,
            "schema_failure_type": self.schema_failure_type,
            "normalized_proposal_present": self.normalized_proposal_present,
            "normalized_proposal_hash": self.normalized_proposal_hash,
            "cognition_review_decision": _plain(self.cognition_review_decision),
            "authorization_decision": _plain(self.authorization_decision),
            "routing_decision": _plain(self.routing_decision),
            "isolation_decision": _plain(self.isolation_decision),
            "governed_return_decision": _plain(self.governed_return_decision),
            "governance_authority_separated": self.governance_authority_separated,
            "created_at": self.created_at,
            "evidence_hash": self.evidence_hash,
        }

    @classmethod
    def from_dict(cls, evidence: dict[str, Any]) -> "LiveCognitionRejectionAnalysisEvidence":
        if not isinstance(evidence, dict):
            raise FailClosedRuntimeError("rejection analysis evidence must be a JSON object")
        required = {
            "analysis_id",
            "usage_id",
            "usage_status",
            "analysis_mode",
            "rejection_stage",
            "rejection_reason",
            "provider_connector_status",
            "provider_connector_reason",
            "raw_provider_response_provider_name",
            "raw_provider_response_model_name",
            "raw_provider_response_present",
            "raw_provider_response_hash",
            "raw_provider_response_evidence_hash",
            "raw_provider_response_normalization_status",
            "raw_provider_response_normalization_reason",
            "bounded_extraction_status",
            "bounded_extraction_stage",
            "bounded_extraction_reason",
            "bounded_extraction_evidence_hash",
            "normalization_failure_type",
            "schema_failure_type",
            "normalized_proposal_present",
            "normalized_proposal_hash",
            "cognition_review_decision",
            "authorization_decision",
            "routing_decision",
            "isolation_decision",
            "governed_return_decision",
            "governance_authority_separated",
            "created_at",
            "evidence_hash",
        }
        if set(evidence) != required:
            raise FailClosedRuntimeError("rejection analysis evidence has malformed structure")
        return cls(**evidence)


def analyze_live_cognition_rejection(
    *,
    analysis_id: str,
    usage_record: dict[str, Any] | None,
    created_at: str,
) -> dict[str, Any]:
    """Inspect one live runtime usage record and emit replay-visible rejection evidence."""

    try:
        _require_string(analysis_id, "analysis_id")
        _require_string(created_at, "created_at")
        if not isinstance(usage_record, dict):
            return _fail_closed_analysis(analysis_id, created_at, "usage_record is not a JSON object")
        usage_id = usage_record.get("usage_id")
        usage_status = usage_record.get("usage_status")
        if not isinstance(usage_id, str) or not usage_id.strip():
            return _fail_closed_analysis(analysis_id, created_at, "usage_record usage_id is missing")
        if usage_status not in ALLOWED_USAGE_STATUSES:
            return _fail_closed_analysis(analysis_id, created_at, "usage_record usage_status is not allowed")
        connector_status, connector_reason = _connector_view(usage_record)
        raw_view = _raw_provider_response_view(usage_record)
        extraction_view = _bounded_extraction_view(usage_record)
        normalized_proposal = _normalized_proposal(usage_record)
        review_view = _review_view(usage_record)
        authorization_view = _authorization_view(usage_record)
        routing_view = _routing_view(usage_record)
        isolation_view = _isolation_view(usage_record)
        governed_return_view = _governed_return_view(usage_record)
        rejection_stage, rejection_reason = _resolve_rejection(
            usage_status=usage_status,
            usage_reason=usage_record.get("usage_reason", ""),
            connector_status=connector_status,
            connector_reason=connector_reason,
            raw_view=raw_view,
            extraction_view=extraction_view,
            review_view=review_view,
            authorization_view=authorization_view,
            routing_view=routing_view,
            isolation_view=isolation_view,
            governed_return_view=governed_return_view,
            execution_present=usage_record.get("execution") is not None,
        )
        evidence = LiveCognitionRejectionAnalysisEvidence(
            analysis_id=analysis_id,
            usage_id=usage_id,
            usage_status=usage_status,
            analysis_mode=ANALYSIS_MODE,
            rejection_stage=rejection_stage,
            rejection_reason=rejection_reason,
            provider_connector_status=connector_status,
            provider_connector_reason=connector_reason,
            raw_provider_response_provider_name=raw_view["provider_name"],
            raw_provider_response_model_name=raw_view["model_name"],
            raw_provider_response_present=raw_view["present"],
            raw_provider_response_hash=raw_view["raw_response_hash"],
            raw_provider_response_evidence_hash=raw_view["evidence_hash"],
            raw_provider_response_normalization_status=raw_view["normalization_status"],
            raw_provider_response_normalization_reason=raw_view["normalization_reason"],
            bounded_extraction_status=extraction_view["status"],
            bounded_extraction_stage=extraction_view["stage"],
            bounded_extraction_reason=extraction_view["reason"],
            bounded_extraction_evidence_hash=extraction_view["evidence_hash"],
            normalization_failure_type=extraction_view["normalization_failure_type"],
            schema_failure_type=extraction_view["schema_failure_type"],
            normalized_proposal_present=normalized_proposal is not None,
            normalized_proposal_hash=replay_hash(normalized_proposal) if normalized_proposal is not None else "",
            cognition_review_decision=review_view,
            authorization_decision=authorization_view,
            routing_decision=routing_view,
            isolation_decision=isolation_view,
            governed_return_decision=governed_return_view,
            governance_authority_separated=True,
            created_at=created_at,
        )
        return {
            "analysis_evidence": evidence,
            "raw_provider_response_evidence": raw_view["evidence_object"],
            "bounded_extraction_evidence": extraction_view["evidence_object"],
            "normalized_proposal": normalized_proposal,
            "analysis_lineage": reconstruct_live_cognition_rejection_analysis_lineage([evidence]),
            "governance_authority_separated": True,
        }
    except (FailClosedRuntimeError, TypeError, ValueError, KeyError):
        return _fail_closed_analysis(
            analysis_id if isinstance(analysis_id, str) and analysis_id else "ANALYSIS-INVALID",
            created_at if isinstance(created_at, str) and created_at else "1970-01-01T00:00:00+00:00",
            "rejection analysis failed closed",
        )


def reconstruct_live_cognition_rejection_analysis_lineage(
    analyses: list[LiveCognitionRejectionAnalysisEvidence | dict[str, Any]]
    | tuple[LiveCognitionRejectionAnalysisEvidence | dict[str, Any], ...],
) -> dict[str, Any]:
    if not isinstance(analyses, list | tuple):
        raise FailClosedRuntimeError("rejection analysis lineage must be a list")
    reconstructed = []
    seen_analysis_ids: set[str] = set()
    previous_created_at = ""
    for index, analysis in enumerate(analyses):
        analysis_obj = (
            LiveCognitionRejectionAnalysisEvidence.from_dict(analysis)
            if isinstance(analysis, dict)
            else analysis
        )
        if not isinstance(analysis_obj, LiveCognitionRejectionAnalysisEvidence):
            raise FailClosedRuntimeError("rejection analysis lineage entry is invalid")
        artifact = analysis_obj.to_dict()
        if artifact["analysis_id"] in seen_analysis_ids:
            raise FailClosedRuntimeError("rejection analysis lineage contains duplicate analysis_id")
        if previous_created_at and artifact["created_at"] < previous_created_at:
            raise FailClosedRuntimeError("rejection analysis lineage ordering is not deterministic")
        canonical_serialize(artifact)
        seen_analysis_ids.add(artifact["analysis_id"])
        previous_created_at = artifact["created_at"]
        reconstructed.append(
            {
                "analysis_index": index,
                "analysis_id": artifact["analysis_id"],
                "usage_id": artifact["usage_id"],
                "usage_status": artifact["usage_status"],
                "rejection_stage": artifact["rejection_stage"],
                "evidence_hash": artifact["evidence_hash"],
            }
        )
    lineage = {
        "analysis_count": len(reconstructed),
        "rejection_analyses": reconstructed,
        "append_only_valid": True,
        "lineage_valid": True,
        "governance_authority_separated": True,
    }
    lineage["lineage_hash"] = replay_hash(lineage)
    return lineage


def render_rejection_analysis_summary(evidence: LiveCognitionRejectionAnalysisEvidence) -> str:
    if not isinstance(evidence, LiveCognitionRejectionAnalysisEvidence):
        raise FailClosedRuntimeError("rejection analysis evidence must be LiveCognitionRejectionAnalysisEvidence")
    review = _plain(evidence.cognition_review_decision)
    authorization = _plain(evidence.authorization_decision)
    routing = _plain(evidence.routing_decision)
    isolation = _plain(evidence.isolation_decision)
    governed_return = _plain(evidence.governed_return_decision)
    lines = [
        f"analysis_id={evidence.analysis_id}",
        f"usage_id={evidence.usage_id}",
        f"usage_status={evidence.usage_status}",
        f"rejection_stage={evidence.rejection_stage}",
        f"rejection_reason={evidence.rejection_reason}",
        f"provider_connector_status={evidence.provider_connector_status}",
        f"provider_connector_reason={evidence.provider_connector_reason}",
        f"raw_provider_response_provider_name={evidence.raw_provider_response_provider_name}",
        f"raw_provider_response_model_name={evidence.raw_provider_response_model_name}",
        f"raw_provider_response_present={evidence.raw_provider_response_present}",
        f"raw_provider_response_hash={evidence.raw_provider_response_hash}",
        f"raw_provider_response_evidence_hash={evidence.raw_provider_response_evidence_hash}",
        f"raw_provider_response_normalization_status={evidence.raw_provider_response_normalization_status}",
        f"raw_provider_response_normalization_reason={evidence.raw_provider_response_normalization_reason}",
        f"bounded_extraction_status={evidence.bounded_extraction_status}",
        f"bounded_extraction_stage={evidence.bounded_extraction_stage}",
        f"bounded_extraction_reason={evidence.bounded_extraction_reason}",
        f"bounded_extraction_evidence_hash={evidence.bounded_extraction_evidence_hash}",
        f"normalization_failure_type={evidence.normalization_failure_type}",
        f"schema_failure_type={evidence.schema_failure_type}",
        f"normalized_proposal_present={evidence.normalized_proposal_present}",
        f"normalized_proposal_hash={evidence.normalized_proposal_hash}",
        f"cognition_review_status={review.get('status', 'ABSENT')}",
        f"cognition_review_reason={review.get('reason', '')}",
        f"cognition_review_risk_level={review.get('risk_level', '')}",
        f"authorization_status={authorization.get('status', 'ABSENT')}",
        f"authorization_requested_providers={canonical_serialize(authorization.get('requested_providers', []))}",
        f"authorization_authorized_providers={canonical_serialize(authorization.get('authorized_providers', []))}",
        f"authorization_rejected_providers={canonical_serialize(authorization.get('rejected_providers', []))}",
        f"routing_status={routing.get('status', 'ABSENT')}",
        f"routing_reason={routing.get('reason', '')}",
        f"isolation_status={isolation.get('status', 'ABSENT')}",
        f"isolation_reason={isolation.get('reason', '')}",
        f"governed_return_status={governed_return.get('status', 'ABSENT')}",
        f"governed_return_summary={governed_return.get('normalized_return_summary', '')}",
        f"analysis_evidence_hash={evidence.evidence_hash}",
    ]
    return "\n".join(lines)


def _fail_closed_analysis(analysis_id: str, created_at: str, reason: str) -> dict[str, Any]:
    evidence = LiveCognitionRejectionAnalysisEvidence(
        analysis_id=analysis_id,
        usage_id="USAGE-INVALID",
        usage_status=USAGE_REJECTED,
        analysis_mode=ANALYSIS_MODE,
        rejection_stage=STAGE_USAGE_INPUT,
        rejection_reason=reason,
        provider_connector_status="ABSENT",
        provider_connector_reason="",
        raw_provider_response_provider_name="",
        raw_provider_response_model_name="",
        raw_provider_response_present=False,
        raw_provider_response_hash="",
        raw_provider_response_evidence_hash="",
        raw_provider_response_normalization_status="ABSENT",
        raw_provider_response_normalization_reason="",
        bounded_extraction_status="ABSENT",
        bounded_extraction_stage="ABSENT",
        bounded_extraction_reason="bounded extraction evidence absent",
        bounded_extraction_evidence_hash="",
        normalization_failure_type="ABSENT",
        schema_failure_type="ABSENT",
        normalized_proposal_present=False,
        normalized_proposal_hash="",
        cognition_review_decision={},
        authorization_decision={},
        routing_decision={},
        isolation_decision={},
        governed_return_decision={},
        governance_authority_separated=True,
        created_at=created_at,
    )
    return {
        "analysis_evidence": evidence,
        "raw_provider_response_evidence": None,
        "bounded_extraction_evidence": None,
        "normalized_proposal": None,
        "analysis_lineage": reconstruct_live_cognition_rejection_analysis_lineage([evidence]),
        "governance_authority_separated": True,
    }


def _connector_view(usage_record: dict[str, Any]) -> tuple[str, str]:
    invocation = usage_record.get("invocation")
    if not isinstance(invocation, dict):
        return "ABSENT", ""
    connector = invocation.get("connector")
    if connector is None:
        invocation_evidence = invocation.get("invocation_evidence")
        if invocation_evidence is not None and getattr(invocation_evidence, "invocation_status", None) != "INVOKED":
            return "REJECTED", getattr(invocation_evidence, "reason", "")
        return "ABSENT", ""
    connector_evidence = connector.get("connector_evidence")
    status = getattr(connector_evidence, "connector_status", None)
    reason = getattr(connector_evidence, "reason", "")
    if not isinstance(status, str) or not status:
        return "ABSENT", ""
    if not isinstance(reason, str):
        reason = ""
    return status, reason


def _raw_provider_response_view(usage_record: dict[str, Any]) -> dict[str, Any]:
    invocation = usage_record.get("invocation")
    raw_evidence: RawProviderResponseEvidence | None = None
    if isinstance(invocation, dict):
        connector = invocation.get("connector")
        if isinstance(connector, dict):
            candidate = connector.get("raw_provider_response")
            if isinstance(candidate, RawProviderResponseEvidence):
                raw_evidence = candidate
    if raw_evidence is None:
        return {
            "provider_name": "",
            "model_name": "",
            "present": False,
            "raw_response_hash": "",
            "evidence_hash": "",
            "normalization_status": "ABSENT",
            "normalization_reason": "",
            "evidence_object": None,
        }
    artifact = raw_evidence.to_dict()
    return {
        "provider_name": artifact["provider_name"],
        "model_name": artifact["model_name"],
        "present": artifact["raw_response_present"],
        "raw_response_hash": artifact["raw_response_hash"],
        "evidence_hash": artifact["evidence_hash"],
        "normalization_status": artifact["normalization_status"],
        "normalization_reason": artifact["normalization_reason"],
        "evidence_object": raw_evidence,
    }


def _bounded_extraction_view(usage_record: dict[str, Any]) -> dict[str, Any]:
    invocation = usage_record.get("invocation")
    extraction_evidence: BoundedExtractionEvidence | None = None
    if isinstance(invocation, dict):
        connector = invocation.get("connector")
        if isinstance(connector, dict):
            bounded_extraction = connector.get("bounded_extraction")
            if isinstance(bounded_extraction, dict):
                candidate = bounded_extraction.get("extraction_evidence")
                if isinstance(candidate, BoundedExtractionEvidence):
                    extraction_evidence = candidate
    if extraction_evidence is None:
        return {
            "status": "ABSENT",
            "stage": "ABSENT",
            "reason": "bounded extraction evidence absent",
            "evidence_hash": "",
            "normalization_failure_type": "ABSENT",
            "schema_failure_type": "ABSENT",
            "evidence_object": None,
        }
    artifact = extraction_evidence.to_dict()
    return {
        "status": artifact["extraction_status"],
        "stage": artifact["extraction_stage"],
        "reason": artifact["extraction_reason"],
        "evidence_hash": artifact["evidence_hash"],
        "normalization_failure_type": artifact["normalization_failure_type"],
        "schema_failure_type": artifact["schema_failure_type"],
        "evidence_object": extraction_evidence,
    }


def _normalized_proposal(usage_record: dict[str, Any]) -> dict[str, Any] | None:
    invocation = usage_record.get("invocation")
    if not isinstance(invocation, dict):
        return None
    proposal = invocation.get("proposal")
    if not isinstance(proposal, BoundedCognitionProposal):
        return None
    return proposal.to_dict()


def _review_view(usage_record: dict[str, Any]) -> dict[str, Any]:
    execution = usage_record.get("execution")
    if not isinstance(execution, dict):
        return {}
    review = execution.get("review")
    if not isinstance(review, GovernedCognitionReviewResult):
        return {}
    artifact = review.to_dict()
    return {
        "status": artifact["review_status"],
        "reason": artifact["review_reason"],
        "risk_level": artifact["risk_level"],
        "review_id": artifact["review_id"],
        "proposal_id": artifact["proposal_id"],
        "translation_id": artifact["translation_id"],
        "evidence_hash": artifact["evidence_hash"],
    }


def _authorization_view(usage_record: dict[str, Any]) -> dict[str, Any]:
    execution = usage_record.get("execution")
    if not isinstance(execution, dict):
        return {}
    authorization = execution.get("authorization")
    if not isinstance(authorization, ContractAuthorizationResult):
        return {}
    artifact = authorization.to_dict()
    return {
        "status": artifact["status"],
        "authorization_id": artifact["authorization_id"],
        "contract_id": artifact["contract_id"],
        "session_id": artifact["session_id"],
        "requested_providers": artifact["requested_providers"],
        "authorized_providers": artifact["authorized_providers"],
        "rejected_providers": artifact["rejected_providers"],
        "evidence_hash": artifact["evidence_hash"],
    }


def _routing_view(usage_record: dict[str, Any]) -> dict[str, Any]:
    execution = usage_record.get("execution")
    if not isinstance(execution, dict):
        return {}
    routing = execution.get("routing")
    if not isinstance(routing, ContractRoutingResult):
        return {}
    artifact = routing.to_dict()
    return {
        "status": artifact["status"],
        "reason": artifact["reason"],
        "routing_id": artifact["routing_id"],
        "contract_id": artifact["contract_id"],
        "session_id": artifact["session_id"],
        "authorization_id": artifact["authorization_id"],
        "attached": artifact["attached"],
        "evidence_hash": artifact["evidence_hash"],
    }


def _isolation_view(usage_record: dict[str, Any]) -> dict[str, Any]:
    isolation = usage_record.get("isolation")
    if not isinstance(isolation, ProductionIsolationEvidence):
        return {}
    artifact = isolation.to_dict()
    return {
        "status": artifact["isolation_status"],
        "reason": artifact["reason"],
        "isolation_id": artifact["isolation_id"],
        "execution_id": artifact["execution_id"],
        "evidence_hash": artifact["evidence_hash"],
    }


def _governed_return_view(usage_record: dict[str, Any]) -> dict[str, Any]:
    governed_return = usage_record.get("governed_return")
    if not isinstance(governed_return, GovernedReturnInterpretationArtifact):
        return {}
    artifact = governed_return.to_dict()
    return {
        "status": artifact["return_status"],
        "normalized_return_summary": artifact["normalized_return_summary"],
        "return_id": artifact["return_id"],
        "execution_reference": artifact["execution_reference"],
        "provider_reference": artifact["provider_reference"],
        "evidence_hash": artifact["evidence_hash"],
    }


def _resolve_rejection(
    *,
    usage_status: str,
    usage_reason: Any,
    connector_status: str,
    connector_reason: str,
    raw_view: dict[str, Any],
    extraction_view: dict[str, Any],
    review_view: dict[str, Any],
    authorization_view: dict[str, Any],
    routing_view: dict[str, Any],
    isolation_view: dict[str, Any],
    governed_return_view: dict[str, Any],
    execution_present: bool,
) -> tuple[str, str]:
    if usage_status == VALIDATED:
        return STAGE_NONE, "live runtime usage validated"
    if not raw_view["present"]:
        return (
            STAGE_RAW_PROVIDER_RESPONSE,
            raw_view["normalization_reason"] or connector_reason or "raw provider response absent",
        )
    extraction_status = extraction_view["status"]
    if extraction_status != EXTRACTION_NORMALIZED:
        if extraction_view["normalization_failure_type"] not in (NORMALIZATION_FAILURE_NONE, "ABSENT"):
            return STAGE_BOUNDED_EXTRACTION, extraction_view["reason"]
        if extraction_view["schema_failure_type"] not in (SCHEMA_FAILURE_NONE, "ABSENT"):
            return STAGE_BOUNDED_EXTRACTION, extraction_view["reason"]
        return STAGE_PROPOSAL_NORMALIZATION, extraction_view["reason"] or connector_reason or "proposal normalization failed closed"
    if raw_view["normalization_status"] != RAW_NORMALIZED:
        return (
            STAGE_PROPOSAL_NORMALIZATION,
            raw_view["normalization_reason"] or connector_reason or "proposal normalization failed closed",
        )
    if connector_status != "NORMALIZED":
        return STAGE_PROPOSAL_NORMALIZATION, connector_reason or "provider adapter did not normalize"
    if not execution_present:
        return STAGE_GOVERNED_EXECUTION, _coerce_reason(usage_reason, "governed execution evidence absent")
    review_status = review_view.get("status")
    if review_view and review_status != REVIEWED:
        return STAGE_COGNITION_REVIEW, review_view.get("reason", "cognition review rejected")
    authorization_status = authorization_view.get("status")
    if authorization_view and authorization_status != AUTHORIZED:
        return STAGE_CONTRACT_AUTHORIZATION, _authorization_reason(authorization_view)
    routing_status = routing_view.get("status")
    if routing_view and routing_status != ROUTED:
        return STAGE_CONTRACT_ROUTING, routing_view.get("reason", "contract routing rejected")
    isolation_status = isolation_view.get("status")
    if isolation_view and isolation_status != ISOLATED:
        return STAGE_PRODUCTION_ISOLATION, isolation_view.get("reason", "production isolation rejected")
    governed_return_status = governed_return_view.get("status")
    if governed_return_view and governed_return_status != ACCEPTED:
        return STAGE_GOVERNED_RETURN, _coerce_reason(usage_reason, "governed return rejected")
    return STAGE_GOVERNED_EXECUTION, _coerce_reason(usage_reason, "governed execution rejected")


def _authorization_reason(authorization_view: dict[str, Any]) -> str:
    rejected = authorization_view.get("rejected_providers") or []
    if rejected:
        return f"authorization rejected providers: {canonical_serialize(rejected)}"
    return "contract authorization rejected"


def _coerce_reason(value: Any, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return value
    return fallback
