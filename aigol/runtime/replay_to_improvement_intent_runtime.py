"""Replay gap to bounded improvement intent runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_gap_detection_runtime import (
    GAP_CLASSIFICATION_ARTIFACT_V1,
    GAP_DETECTION_ARTIFACT_V1,
    GAP_EVIDENCE_ARTIFACT_V1,
    GAPS_DETECTED,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_REPLAY_TO_IMPROVEMENT_INTENT_RUNTIME_VERSION = "AIGOL_REPLAY_TO_IMPROVEMENT_INTENT_RUNTIME_V1"
IMPROVEMENT_INTENT_ARTIFACT_V1 = "IMPROVEMENT_INTENT_ARTIFACT_V1"
IMPROVEMENT_INTENT_EVIDENCE_V1 = "IMPROVEMENT_INTENT_EVIDENCE_V1"
IMPROVEMENT_INTENT_CLASSIFICATION_V1 = "IMPROVEMENT_INTENT_CLASSIFICATION_V1"
PLATFORM_SEMANTIC_GAP_CLOSURE_G2_12_REPLAY_HARDENING_AND_REPLAY_DERIVED_CLASSIFIERS_V1 = (
    "PLATFORM_SEMANTIC_GAP_CLOSURE_G2_12_REPLAY_HARDENING_AND_REPLAY_DERIVED_CLASSIFIERS_V1"
)
IMPROVEMENT_INTENT_CREATED = "IMPROVEMENT_INTENT_CREATED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "improvement_intent_evidence_recorded",
    "improvement_intent_classification_recorded",
    "improvement_intent_created",
    "improvement_intent_returned",
)

CONFIDENCE_RANK = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "DETERMINISTIC": 4}
HIGH_RISK_DOMAINS = {"TRADING", "HEALTHCARE", "HR", "LEGAL", "CRITICAL_INFRASTRUCTURE", "AIGOL_CORE"}

IMPROVEMENT_CLASS_BY_GAP = {
    "PERFORMANCE_GAP": "RUNTIME_HARDENING",
    "POLICY_GAP": "GOVERNANCE_REVIEW",
    "VALIDATION_GAP": "RUNTIME_HARDENING",
    "REPLAY_INTEGRITY_GAP": "REPLAY_RECONSTRUCTION",
    "DOMAIN_EFFECTIVENESS_GAP": "DOMAIN_MODEL",
    "REPEATED_FAILURE_PATTERN": "OPERATOR_WORKFLOW",
    "ROUTING_MISMATCH": "OPERATOR_WORKFLOW",
    "REPLAY_CONTINUITY_BREAK": "REPLAY_RECONSTRUCTION",
    "MISSING_CONTINUATION": "OPERATOR_WORKFLOW",
    "FAIL_CLOSED_INTERRUPTION": "RUNTIME_HARDENING",
    "PROJECTION_INCONSISTENCY": "OPERATOR_WORKFLOW",
    "LIFECYCLE_STAGE_DEVIATION": "OPERATOR_WORKFLOW",
}

INTENT_SUMMARY_BY_GAP = {
    "PERFORMANCE_GAP": "Optimization needed.",
    "POLICY_GAP": "Policy refinement needed.",
    "VALIDATION_GAP": "Validation improvement required.",
    "REPLAY_INTEGRITY_GAP": "Replay integrity analysis required.",
    "DOMAIN_EFFECTIVENESS_GAP": "Domain effectiveness improvement required.",
    "REPEATED_FAILURE_PATTERN": "Failure pattern analysis required.",
    "ROUTING_MISMATCH": "Lifecycle routing mismatch review required.",
    "REPLAY_CONTINUITY_BREAK": "Replay continuity reconstruction review required.",
    "MISSING_CONTINUATION": "Lifecycle continuation review required.",
    "FAIL_CLOSED_INTERRUPTION": "Fail-closed interruption review required.",
    "PROJECTION_INCONSISTENCY": "Workflow status projection review required.",
    "LIFECYCLE_STAGE_DEVIATION": "Lifecycle stage progression review required.",
}

FORBIDDEN_INTENT_TERMS = (
    "add macd",
    "modify worker",
    "deploy strategy",
    "invoke worker",
    "invoke provider",
    "execute",
    "dispatch",
    "create execution request",
    "code change",
    "implementation detail",
)


def create_improvement_intent_from_replay_gap(
    *,
    improvement_intent_id: str,
    gap_detection_artifact: dict[str, Any],
    gap_classification_artifact: dict[str, Any],
    gap_evidence_artifact: dict[str, Any],
    canonical_chain_id: str,
    created_at: str,
    replay_dir: str | Path,
    affected_layer: str = "AIGOL_CORE",
    affected_worker_family: str | None = None,
    constraints: list[str] | None = None,
    confidence_threshold: str = "HIGH",
) -> dict[str, Any]:
    """Convert confirmed replay gaps into bounded improvement intent only."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        detection = deepcopy(gap_detection_artifact)
        classification = deepcopy(gap_classification_artifact)
        evidence = deepcopy(gap_evidence_artifact)
        _validate_gap_artifacts(
            detection=detection,
            classification=classification,
            evidence=evidence,
            canonical_chain_id=canonical_chain_id,
            confidence_threshold=confidence_threshold,
        )
        intent_evidence = _intent_evidence_artifact(
            improvement_intent_id=improvement_intent_id,
            detection=detection,
            classification=classification,
            evidence=evidence,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            evidence_status="IMPROVEMENT_INTENT_EVIDENCE_ACCEPTED",
            failure_reason=None,
        )
        intent_classification = _intent_classification_artifact(
            improvement_intent_id=improvement_intent_id,
            intent_evidence=intent_evidence,
            classification=classification,
            affected_layer=affected_layer,
            affected_worker_family=affected_worker_family,
            constraints=constraints,
            created_at=created_at,
            classification_status="IMPROVEMENT_INTENT_CLASSIFIED",
            failure_reason=None,
        )
        intent = _improvement_intent_artifact(
            improvement_intent_id=improvement_intent_id,
            intent_evidence=intent_evidence,
            intent_classification=intent_classification,
            detection=detection,
            evidence=evidence,
            created_at=created_at,
            intent_status=IMPROVEMENT_INTENT_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(intent)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], intent_evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], intent_classification)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], intent)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(intent_evidence, intent_classification, intent, returned, replay_path)
    except Exception as exc:
        intent_evidence = _failed_intent_evidence_artifact(
            improvement_intent_id=improvement_intent_id,
            gap_detection_artifact=gap_detection_artifact,
            gap_classification_artifact=gap_classification_artifact,
            gap_evidence_artifact=gap_evidence_artifact,
            canonical_chain_id=canonical_chain_id,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        intent_classification = _failed_intent_classification_artifact(
            improvement_intent_id=improvement_intent_id,
            intent_evidence=intent_evidence,
            created_at=created_at,
        )
        intent = _failed_improvement_intent_artifact(
            improvement_intent_id=improvement_intent_id,
            intent_evidence=intent_evidence,
            intent_classification=intent_classification,
            created_at=created_at,
            failure_reason=intent_evidence["failure_reason"],
        )
        returned = _returned_artifact(intent)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], intent_evidence)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], intent_classification)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], intent)
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(intent_evidence, intent_classification, intent, returned, replay_path)


def reconstruct_replay_to_improvement_intent_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct replay-to-improvement-intent evidence."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("replay to improvement intent replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("replay to improvement intent replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "replay to improvement intent artifact")
        wrappers.append(wrapper)
    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    intent = wrappers[2]["artifact"]
    returned = wrappers[3]["artifact"]
    if classification.get("intent_evidence_reference") != evidence["intent_evidence_id"]:
        raise FailClosedRuntimeError("replay to improvement intent evidence reference mismatch")
    if classification.get("intent_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("replay to improvement intent evidence hash mismatch")
    if intent.get("intent_classification_reference") != classification["intent_classification_id"]:
        raise FailClosedRuntimeError("replay to improvement intent classification reference mismatch")
    if intent.get("intent_classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("replay to improvement intent classification hash mismatch")
    if returned.get("improvement_intent_reference") != intent["improvement_intent_id"]:
        raise FailClosedRuntimeError("replay to improvement intent returned reference mismatch")
    if returned.get("improvement_intent_hash") != intent["artifact_hash"]:
        raise FailClosedRuntimeError("replay to improvement intent returned hash mismatch")
    return {
        "improvement_intent_id": intent["improvement_intent_id"],
        "intent_status": intent["intent_status"],
        "canonical_chain_id": intent["canonical_chain_id"],
        "affected_domain": intent["affected_domain"],
        "affected_layer": intent["affected_layer"],
        "improvement_class": intent["improvement_class"],
        "confidence": intent["confidence"],
        "replay_derived_classifier_source": intent.get("replay_derived_classifier_source"),
        "canonical_semantic_artifact_hashes": deepcopy(intent.get("canonical_semantic_artifact_hashes", [])),
        "upstream_semantic_comparison_hash": intent.get("upstream_semantic_comparison_hash"),
        "upstream_semantic_comparison_parity_status": intent.get("upstream_semantic_comparison_parity_status"),
        "migration_batch_id": intent.get("migration_batch_id"),
        "fallback_status": intent.get("fallback_status"),
        "human_review_required": intent["human_review_required"],
        "ppp_eligible": intent["ppp_eligible"],
        "failure_reason": intent["failure_reason"],
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_gap_artifacts(
    *,
    detection: dict[str, Any],
    classification: dict[str, Any],
    evidence: dict[str, Any],
    canonical_chain_id: str,
    confidence_threshold: str,
) -> None:
    _require_string(canonical_chain_id, "canonical_chain_id")
    _validate_artifact(detection, GAP_DETECTION_ARTIFACT_V1, "gap detection")
    _validate_artifact(classification, GAP_CLASSIFICATION_ARTIFACT_V1, "gap classification")
    _validate_artifact(evidence, GAP_EVIDENCE_ARTIFACT_V1, "gap evidence")
    if detection.get("detection_status") != GAPS_DETECTED:
        raise FailClosedRuntimeError("replay to improvement intent failed closed: confirmed gap required")
    if detection.get("improvement_intent_allowed") is not True:
        raise FailClosedRuntimeError("replay to improvement intent failed closed: confidence insufficient")
    if classification.get("improvement_intent_allowed") is not True:
        raise FailClosedRuntimeError("replay to improvement intent failed closed: confidence insufficient")
    if classification.get("evidence_reference") != evidence.get("evidence_id"):
        raise FailClosedRuntimeError("replay to improvement intent failed closed: replay broken")
    if classification.get("evidence_hash") != evidence.get("artifact_hash"):
        raise FailClosedRuntimeError("replay to improvement intent failed closed: replay broken")
    if detection.get("classification_reference") != classification.get("classification_id"):
        raise FailClosedRuntimeError("replay to improvement intent failed closed: classification ambiguous")
    if detection.get("classification_hash") != classification.get("artifact_hash"):
        raise FailClosedRuntimeError("replay to improvement intent failed closed: replay broken")
    threshold = _normalize_confidence(confidence_threshold)
    confidence = _normalize_confidence(detection.get("confidence"))
    if CONFIDENCE_RANK[confidence] < CONFIDENCE_RANK[threshold]:
        raise FailClosedRuntimeError("replay to improvement intent failed closed: confidence insufficient")
    if not detection.get("gap_categories"):
        raise FailClosedRuntimeError("replay to improvement intent failed closed: confirmed gap required")
    _validate_chain_continuity(evidence, canonical_chain_id)
    _validate_allowed_categories(detection.get("gap_categories"), classification.get("gap_classifications"))


def _intent_evidence_artifact(
    *,
    improvement_intent_id: str,
    detection: dict[str, Any],
    classification: dict[str, Any],
    evidence: dict[str, Any],
    canonical_chain_id: str,
    created_at: str,
    evidence_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": IMPROVEMENT_INTENT_EVIDENCE_V1,
        "runtime_version": AIGOL_REPLAY_TO_IMPROVEMENT_INTENT_RUNTIME_VERSION,
        "intent_evidence_id": f"{_require_string(improvement_intent_id, 'improvement_intent_id')}:INTENT-EVIDENCE",
        "improvement_intent_reference": improvement_intent_id,
        "canonical_chain_id": _require_string(canonical_chain_id, "canonical_chain_id"),
        "gap_detection_reference": detection["detection_id"],
        "gap_detection_hash": detection["artifact_hash"],
        "gap_classification_reference": classification["classification_id"],
        "gap_classification_hash": classification["artifact_hash"],
        "gap_evidence_reference": evidence["evidence_id"],
        "gap_evidence_hash": evidence["artifact_hash"],
        "source_replay_references": _source_replay_references(evidence),
        "source_replay_hashes": _source_replay_hashes(evidence),
        "affected_domain": detection["domain_id"],
        "confirmed_gap_count": detection["gap_count"],
        "gap_categories": deepcopy(detection["gap_categories"]),
        "confidence": detection["confidence"],
        "replay_derived_classifier_source": classification.get("replay_derived_classifier_source")
        or "COMPATIBILITY_FALLBACK",
        "canonical_semantic_artifact_references": deepcopy(
            classification.get("canonical_semantic_artifact_references", [])
        ),
        "canonical_semantic_artifact_hashes": deepcopy(classification.get("canonical_semantic_artifact_hashes", [])),
        "upstream_semantic_comparison_hash": classification.get("semantic_comparison_hash"),
        "upstream_semantic_comparison_parity_status": classification.get("semantic_comparison_parity_status"),
        "migration_batch_id": PLATFORM_SEMANTIC_GAP_CLOSURE_G2_12_REPLAY_HARDENING_AND_REPLAY_DERIVED_CLASSIFIERS_V1,
        "fallback_status": classification.get("fallback_status") or "COMPATIBILITY_FALLBACK_AUTHORITATIVE",
        "evidence_status": evidence_status,
        "false_positive_controls": {
            "confirmed_gap_required": True,
            "replay_evidence_required": True,
            "confidence_threshold_required": True,
            "chain_continuity_required": True,
        },
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _intent_classification_artifact(
    *,
    improvement_intent_id: str,
    intent_evidence: dict[str, Any],
    classification: dict[str, Any],
    affected_layer: str,
    affected_worker_family: str | None,
    constraints: list[str] | None,
    created_at: str,
    classification_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    primary_gap = _primary_gap(intent_evidence["gap_categories"])
    intent_summary = INTENT_SUMMARY_BY_GAP[primary_gap]
    _validate_bounded_statement(intent_summary)
    artifact = {
        "artifact_type": IMPROVEMENT_INTENT_CLASSIFICATION_V1,
        "runtime_version": AIGOL_REPLAY_TO_IMPROVEMENT_INTENT_RUNTIME_VERSION,
        "intent_classification_id": f"{_require_string(improvement_intent_id, 'improvement_intent_id')}:INTENT-CLASSIFICATION",
        "improvement_intent_reference": improvement_intent_id,
        "intent_evidence_reference": intent_evidence["intent_evidence_id"],
        "intent_evidence_hash": intent_evidence["artifact_hash"],
        "canonical_chain_id": intent_evidence["canonical_chain_id"],
        "affected_domain": intent_evidence["affected_domain"],
        "affected_layer": _normalize_layer(affected_layer),
        "affected_worker_family": affected_worker_family,
        "improvement_class": IMPROVEMENT_CLASS_BY_GAP[primary_gap],
        "intent_summary": intent_summary,
        "evidence_summary": _evidence_summary(classification),
        "constraints": _constraints(constraints),
        "known_gaps": deepcopy(intent_evidence["gap_categories"]),
        "replay_derived_classifier_source": intent_evidence["replay_derived_classifier_source"],
        "canonical_semantic_artifact_references": deepcopy(intent_evidence["canonical_semantic_artifact_references"]),
        "canonical_semantic_artifact_hashes": deepcopy(intent_evidence["canonical_semantic_artifact_hashes"]),
        "upstream_semantic_comparison_hash": intent_evidence["upstream_semantic_comparison_hash"],
        "upstream_semantic_comparison_parity_status": intent_evidence[
            "upstream_semantic_comparison_parity_status"
        ],
        "migration_batch_id": intent_evidence["migration_batch_id"],
        "fallback_status": intent_evidence["fallback_status"],
        "assumptions": ["Improvement intent remains proposal-eligible but non-authorizing."],
        "confidence": intent_evidence["confidence"],
        "human_review_required": intent_evidence["affected_domain"] in HIGH_RISK_DOMAINS
        or classification.get("human_review_required") is True,
        "high_risk_domain": intent_evidence["affected_domain"] in HIGH_RISK_DOMAINS,
        "ppp_eligible": True,
        "classification_status": classification_status,
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _improvement_intent_artifact(
    *,
    improvement_intent_id: str,
    intent_evidence: dict[str, Any],
    intent_classification: dict[str, Any],
    detection: dict[str, Any],
    evidence: dict[str, Any],
    created_at: str,
    intent_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": IMPROVEMENT_INTENT_ARTIFACT_V1,
        "improvement_intent_version": AIGOL_REPLAY_TO_IMPROVEMENT_INTENT_RUNTIME_VERSION,
        "improvement_intent_id": _require_string(improvement_intent_id, "improvement_intent_id"),
        "intent_status": intent_status,
        "intent_source": "REPLAY_GAP_DETECTION",
        "canonical_chain_id": intent_evidence["canonical_chain_id"],
        "gap_reference": detection["detection_id"],
        "gap_hash": detection["artifact_hash"],
        "source_replay_reference": intent_evidence["source_replay_references"],
        "source_replay_hash": intent_evidence["source_replay_hashes"],
        "intent_evidence_reference": intent_evidence["intent_evidence_id"],
        "intent_evidence_hash": intent_evidence["artifact_hash"],
        "intent_classification_reference": intent_classification["intent_classification_id"],
        "intent_classification_hash": intent_classification["artifact_hash"],
        "affected_layer": intent_classification["affected_layer"],
        "affected_domain": intent_classification["affected_domain"],
        "affected_worker_family": intent_classification["affected_worker_family"],
        "improvement_class": intent_classification["improvement_class"],
        "intent_summary": intent_classification["intent_summary"],
        "evidence_summary": intent_classification["evidence_summary"],
        "constraints": deepcopy(intent_classification["constraints"]),
        "known_gaps": deepcopy(intent_classification["known_gaps"]),
        "replay_derived_classifier_source": intent_classification["replay_derived_classifier_source"],
        "canonical_semantic_artifact_references": deepcopy(
            intent_classification["canonical_semantic_artifact_references"]
        ),
        "canonical_semantic_artifact_hashes": deepcopy(intent_classification["canonical_semantic_artifact_hashes"]),
        "upstream_semantic_comparison_hash": intent_classification["upstream_semantic_comparison_hash"],
        "upstream_semantic_comparison_parity_status": intent_classification[
            "upstream_semantic_comparison_parity_status"
        ],
        "migration_batch_id": intent_classification["migration_batch_id"],
        "fallback_status": intent_classification["fallback_status"],
        "assumptions": deepcopy(intent_classification["assumptions"]),
        "confidence": intent_classification["confidence"],
        "human_review_required": intent_classification["human_review_required"],
        "high_risk_domain": intent_classification["high_risk_domain"],
        "ppp_eligible": intent_classification["ppp_eligible"],
        "proposal_created": False,
        "ppp_invoked": False,
        "proposal_approved": False,
        "implementation_authorized": False,
        "implementation_applied": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "provider_authority": False,
        "worker_authority": False,
        "governance_authority": False,
        "self_modification_authority": False,
        "replay_mutated": False,
        "governance_mutated": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    _validate_bounded_statement(artifact["intent_summary"])
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_intent_evidence_artifact(
    *,
    improvement_intent_id: str,
    gap_detection_artifact: dict[str, Any],
    gap_classification_artifact: dict[str, Any],
    gap_evidence_artifact: dict[str, Any],
    canonical_chain_id: str,
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": IMPROVEMENT_INTENT_EVIDENCE_V1,
        "runtime_version": AIGOL_REPLAY_TO_IMPROVEMENT_INTENT_RUNTIME_VERSION,
        "intent_evidence_id": f"{improvement_intent_id}:INTENT-EVIDENCE" if isinstance(improvement_intent_id, str) else "INVALID_INTENT:INTENT-EVIDENCE",
        "improvement_intent_reference": improvement_intent_id if isinstance(improvement_intent_id, str) else "INVALID_INTENT",
        "canonical_chain_id": canonical_chain_id if isinstance(canonical_chain_id, str) else None,
        "gap_detection_reference": gap_detection_artifact.get("detection_id") if isinstance(gap_detection_artifact, dict) else None,
        "gap_detection_hash": gap_detection_artifact.get("artifact_hash") if isinstance(gap_detection_artifact, dict) else None,
        "gap_classification_reference": gap_classification_artifact.get("classification_id")
        if isinstance(gap_classification_artifact, dict)
        else None,
        "gap_classification_hash": gap_classification_artifact.get("artifact_hash")
        if isinstance(gap_classification_artifact, dict)
        else None,
        "gap_evidence_reference": gap_evidence_artifact.get("evidence_id") if isinstance(gap_evidence_artifact, dict) else None,
        "gap_evidence_hash": gap_evidence_artifact.get("artifact_hash") if isinstance(gap_evidence_artifact, dict) else None,
        "source_replay_references": [],
        "source_replay_hashes": [],
        "affected_domain": gap_detection_artifact.get("domain_id") if isinstance(gap_detection_artifact, dict) else None,
        "confirmed_gap_count": gap_detection_artifact.get("gap_count") if isinstance(gap_detection_artifact, dict) else 0,
        "gap_categories": gap_detection_artifact.get("gap_categories") if isinstance(gap_detection_artifact, dict) else [],
        "confidence": gap_detection_artifact.get("confidence") if isinstance(gap_detection_artifact, dict) else None,
        "replay_derived_classifier_source": (
            gap_classification_artifact.get("replay_derived_classifier_source")
            if isinstance(gap_classification_artifact, dict)
            else "COMPATIBILITY_FALLBACK"
        )
        or "COMPATIBILITY_FALLBACK",
        "canonical_semantic_artifact_references": (
            gap_classification_artifact.get("canonical_semantic_artifact_references")
            if isinstance(gap_classification_artifact, dict)
            else []
        )
        or [],
        "canonical_semantic_artifact_hashes": (
            gap_classification_artifact.get("canonical_semantic_artifact_hashes")
            if isinstance(gap_classification_artifact, dict)
            else []
        )
        or [],
        "upstream_semantic_comparison_hash": (
            gap_classification_artifact.get("semantic_comparison_hash")
            if isinstance(gap_classification_artifact, dict)
            else None
        ),
        "upstream_semantic_comparison_parity_status": (
            gap_classification_artifact.get("semantic_comparison_parity_status")
            if isinstance(gap_classification_artifact, dict)
            else None
        ),
        "migration_batch_id": PLATFORM_SEMANTIC_GAP_CLOSURE_G2_12_REPLAY_HARDENING_AND_REPLAY_DERIVED_CLASSIFIERS_V1,
        "fallback_status": (
            gap_classification_artifact.get("fallback_status")
            if isinstance(gap_classification_artifact, dict)
            else "COMPATIBILITY_FALLBACK_AUTHORITATIVE"
        )
        or "COMPATIBILITY_FALLBACK_AUTHORITATIVE",
        "evidence_status": FAILED_CLOSED,
        "false_positive_controls": {
            "confirmed_gap_required": True,
            "replay_evidence_required": True,
            "confidence_threshold_required": True,
            "chain_continuity_required": True,
        },
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": created_at,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_intent_classification_artifact(
    *,
    improvement_intent_id: str,
    intent_evidence: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": IMPROVEMENT_INTENT_CLASSIFICATION_V1,
        "runtime_version": AIGOL_REPLAY_TO_IMPROVEMENT_INTENT_RUNTIME_VERSION,
        "intent_classification_id": f"{improvement_intent_id}:INTENT-CLASSIFICATION"
        if isinstance(improvement_intent_id, str)
        else "INVALID_INTENT:INTENT-CLASSIFICATION",
        "improvement_intent_reference": improvement_intent_id if isinstance(improvement_intent_id, str) else "INVALID_INTENT",
        "intent_evidence_reference": intent_evidence["intent_evidence_id"],
        "intent_evidence_hash": intent_evidence["artifact_hash"],
        "canonical_chain_id": intent_evidence["canonical_chain_id"],
        "affected_domain": intent_evidence["affected_domain"],
        "affected_layer": None,
        "affected_worker_family": None,
        "improvement_class": None,
        "intent_summary": None,
        "evidence_summary": None,
        "constraints": [],
        "known_gaps": deepcopy(intent_evidence["gap_categories"]),
        "replay_derived_classifier_source": intent_evidence["replay_derived_classifier_source"],
        "canonical_semantic_artifact_references": deepcopy(intent_evidence["canonical_semantic_artifact_references"]),
        "canonical_semantic_artifact_hashes": deepcopy(intent_evidence["canonical_semantic_artifact_hashes"]),
        "upstream_semantic_comparison_hash": intent_evidence["upstream_semantic_comparison_hash"],
        "upstream_semantic_comparison_parity_status": intent_evidence[
            "upstream_semantic_comparison_parity_status"
        ],
        "migration_batch_id": intent_evidence["migration_batch_id"],
        "fallback_status": intent_evidence["fallback_status"],
        "assumptions": [],
        "confidence": intent_evidence["confidence"],
        "human_review_required": True,
        "high_risk_domain": False,
        "ppp_eligible": False,
        "classification_status": FAILED_CLOSED,
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": created_at,
        "replay_visible": True,
        "failure_reason": intent_evidence["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_improvement_intent_artifact(
    *,
    improvement_intent_id: str,
    intent_evidence: dict[str, Any],
    intent_classification: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": IMPROVEMENT_INTENT_ARTIFACT_V1,
        "improvement_intent_version": AIGOL_REPLAY_TO_IMPROVEMENT_INTENT_RUNTIME_VERSION,
        "improvement_intent_id": improvement_intent_id if isinstance(improvement_intent_id, str) else "INVALID_INTENT",
        "intent_status": FAILED_CLOSED,
        "intent_source": "REPLAY_GAP_DETECTION",
        "canonical_chain_id": intent_evidence["canonical_chain_id"],
        "gap_reference": intent_evidence["gap_detection_reference"],
        "gap_hash": intent_evidence["gap_detection_hash"],
        "source_replay_reference": [],
        "source_replay_hash": [],
        "intent_evidence_reference": intent_evidence["intent_evidence_id"],
        "intent_evidence_hash": intent_evidence["artifact_hash"],
        "intent_classification_reference": intent_classification["intent_classification_id"],
        "intent_classification_hash": intent_classification["artifact_hash"],
        "affected_layer": None,
        "affected_domain": intent_evidence["affected_domain"],
        "affected_worker_family": None,
        "improvement_class": None,
        "intent_summary": None,
        "evidence_summary": None,
        "constraints": [],
        "known_gaps": deepcopy(intent_evidence["gap_categories"]),
        "replay_derived_classifier_source": intent_classification["replay_derived_classifier_source"],
        "canonical_semantic_artifact_references": deepcopy(
            intent_classification["canonical_semantic_artifact_references"]
        ),
        "canonical_semantic_artifact_hashes": deepcopy(intent_classification["canonical_semantic_artifact_hashes"]),
        "upstream_semantic_comparison_hash": intent_classification["upstream_semantic_comparison_hash"],
        "upstream_semantic_comparison_parity_status": intent_classification[
            "upstream_semantic_comparison_parity_status"
        ],
        "migration_batch_id": intent_classification["migration_batch_id"],
        "fallback_status": intent_classification["fallback_status"],
        "assumptions": [],
        "confidence": intent_evidence["confidence"],
        "human_review_required": True,
        "high_risk_domain": False,
        "ppp_eligible": False,
        "proposal_created": False,
        "ppp_invoked": False,
        "proposal_approved": False,
        "implementation_authorized": False,
        "implementation_applied": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "provider_authority": False,
        "worker_authority": False,
        "governance_authority": False,
        "self_modification_authority": False,
        "replay_mutated": False,
        "governance_mutated": False,
        "created_at": created_at,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(intent: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(intent, "replay to improvement intent artifact")
    artifact = {
        "event_type": "REPLAY_TO_IMPROVEMENT_INTENT_RETURNED",
        "improvement_intent_reference": intent["improvement_intent_id"],
        "improvement_intent_hash": intent["artifact_hash"],
        "intent_status": intent["intent_status"],
        "canonical_chain_id": intent["canonical_chain_id"],
        "improvement_class": intent["improvement_class"],
        "ppp_eligible": intent["ppp_eligible"],
        "human_review_required": intent["human_review_required"],
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": intent["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    evidence: dict[str, Any],
    classification: dict[str, Any],
    intent: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "improvement_intent_evidence_artifact": deepcopy(evidence),
        "improvement_intent_classification_artifact": deepcopy(classification),
        "improvement_intent_artifact": deepcopy(intent),
        "improvement_intent_replay": deepcopy(returned),
        "improvement_intent_replay_reference": str(replay_path),
        "intent_status": intent["intent_status"],
        "canonical_chain_id": intent["canonical_chain_id"],
        "improvement_class": intent["improvement_class"],
        "intent_summary": intent["intent_summary"],
        "confidence": intent["confidence"],
        "replay_derived_classifier_source": intent.get("replay_derived_classifier_source"),
        "canonical_semantic_artifact_hashes": deepcopy(intent.get("canonical_semantic_artifact_hashes", [])),
        "upstream_semantic_comparison_hash": intent.get("upstream_semantic_comparison_hash"),
        "upstream_semantic_comparison_parity_status": intent.get("upstream_semantic_comparison_parity_status"),
        "migration_batch_id": intent.get("migration_batch_id"),
        "fallback_status": intent.get("fallback_status"),
        "human_review_required": intent["human_review_required"],
        "ppp_eligible": intent["ppp_eligible"],
        "fail_closed": intent["intent_status"] == FAILED_CLOSED,
        "failure_reason": intent["failure_reason"],
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["replay_to_improvement_intent_capture_hash"] = replay_hash(capture)
    return capture


def _validate_artifact(artifact: dict[str, Any], expected_type: str, label: str) -> None:
    if not isinstance(artifact, dict) or artifact.get("artifact_type") != expected_type:
        raise FailClosedRuntimeError(f"replay to improvement intent failed closed: {label} evidence missing")
    _verify_artifact_hash(artifact, f"replay to improvement intent {label}")


def _validate_chain_continuity(evidence: dict[str, Any], canonical_chain_id: str) -> None:
    for item in evidence.get("evidence_items", []):
        if item.get("canonical_chain_id") != canonical_chain_id:
            raise FailClosedRuntimeError("replay to improvement intent failed closed: chain continuity failed")


def _validate_allowed_categories(categories: Any, classifications: Any) -> None:
    if not isinstance(categories, list) or not isinstance(classifications, list):
        raise FailClosedRuntimeError("replay to improvement intent failed closed: classification ambiguous")
    for category in categories:
        if category not in IMPROVEMENT_CLASS_BY_GAP:
            raise FailClosedRuntimeError("replay to improvement intent failed closed: classification ambiguous")


def _primary_gap(categories: list[str]) -> str:
    priority = [
        "REPLAY_INTEGRITY_GAP",
        "POLICY_GAP",
        "VALIDATION_GAP",
        "REPLAY_CONTINUITY_BREAK",
        "FAIL_CLOSED_INTERRUPTION",
        "PROJECTION_INCONSISTENCY",
        "ROUTING_MISMATCH",
        "MISSING_CONTINUATION",
        "LIFECYCLE_STAGE_DEVIATION",
        "REPEATED_FAILURE_PATTERN",
        "DOMAIN_EFFECTIVENESS_GAP",
        "PERFORMANCE_GAP",
    ]
    for category in priority:
        if category in categories:
            return category
    raise FailClosedRuntimeError("replay to improvement intent failed closed: classification ambiguous")


def _source_replay_references(evidence: dict[str, Any]) -> list[str]:
    return [item["source_replay_reference"] for item in evidence.get("evidence_items", [])]


def _source_replay_hashes(evidence: dict[str, Any]) -> list[str]:
    return [item["source_replay_hash"] for item in evidence.get("evidence_items", [])]


def _evidence_summary(classification: dict[str, Any]) -> str:
    categories = ", ".join(classification.get("gap_categories", []))
    return f"Replay gap evidence confirmed categories: {categories}."


def _constraints(value: list[str] | None) -> list[str]:
    base = [
        "NO_IMPLEMENTATION_DETAILS",
        "NO_CODE_CHANGES",
        "NO_PROVIDER_INVOCATION",
        "NO_WORKER_INVOCATION",
        "NO_EXECUTION_REQUESTS",
        "PROPOSAL_ONLY_AFTER_PPP",
    ]
    if value is None:
        return base
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise FailClosedRuntimeError("replay to improvement intent failed closed: constraints missing")
    return base + value


def _normalize_layer(value: str) -> str:
    layer = _require_string(value, "affected_layer").strip().upper().replace("-", "_").replace(" ", "_")
    if layer not in {"COGNITION", "RESOURCE_SELECTION", "PPP", "GOVERNANCE", "EXECUTION", "REPLAY", "DOMAIN", "AIGOL_CORE"}:
        raise FailClosedRuntimeError("replay to improvement intent failed closed: classification ambiguous")
    return layer


def _normalize_confidence(value: Any) -> str:
    confidence = _require_string(value, "confidence").strip().upper().replace("-", "_").replace(" ", "_")
    if confidence not in CONFIDENCE_RANK:
        raise FailClosedRuntimeError("replay to improvement intent failed closed: confidence insufficient")
    return confidence


def _validate_bounded_statement(value: str) -> None:
    lowered = _require_string(value, "intent_summary").lower()
    if any(term in lowered for term in FORBIDDEN_INTENT_TERMS):
        raise FailClosedRuntimeError("replay to improvement intent failed closed: implementation details prohibited")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"replay to improvement intent failed closed: {label} missing")
    return value


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("replay to improvement intent replay step ordering mismatch")
    _verify_artifact_hash(artifact, "replay to improvement intent artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": step.upper(),
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        pass


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("replay to improvement intent replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("replay to improvement intent replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "replay to improvement intent failed closed"
