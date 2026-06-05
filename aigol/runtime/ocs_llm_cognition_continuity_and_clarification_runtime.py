"""OCS LLM cognition continuity and clarification runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.cognition_artifact_runtime import LLM_COGNITION_ARTIFACT_V1
from aigol.runtime.cognition_comparison_runtime import COGNITION_COMPARISON_ARTIFACT_V1
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_OCS_LLM_COGNITION_CONTINUITY_AND_CLARIFICATION_V1"
FINAL_CLASSIFICATION = "AIGOL_OCS_LLM_COGNITION_CONTINUITY_AND_CLARIFICATION_STATUS"
CERTIFIED_CLASSIFICATION = "CERTIFIED_COGNITION_CONTINUITY_AND_CLARIFICATION_RUNTIME"

COGNITION_CONTINUITY_ARTIFACT_V1 = "COGNITION_CONTINUITY_ARTIFACT_V1"
COGNITION_CLARIFICATION_ARTIFACT_V1 = "COGNITION_CLARIFICATION_ARTIFACT_V1"
COGNITION_HISTORY_REFERENCE_V1 = "COGNITION_HISTORY_REFERENCE_V1"
COGNITION_CONTINUITY_AND_CLARIFICATION_RETURNED_V1 = "COGNITION_CONTINUITY_AND_CLARIFICATION_RETURNED_V1"

STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED_CLOSED = "FAILED_CLOSED"
CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
CLARIFICATION_NOT_REQUIRED = "CLARIFICATION_NOT_REQUIRED"

REPLAY_STEPS = (
    "cognition_history_reference",
    "cognition_continuity_artifact",
    "cognition_clarification_artifact",
    "cognition_continuity_and_clarification_returned",
)

AUTHORITY_FLAGS = {
    "provider_authority": False,
    "approval_authority": False,
    "execution_authority": False,
    "worker_authority": False,
    "governance_authority": False,
    "replay_authority": False,
}

CONFIDENCE_RANK = {
    "UNKNOWN": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "DETERMINISTIC": 4,
}


def run_ocs_llm_cognition_continuity_and_clarification(
    *,
    continuity_id: str,
    clarification_id: str,
    current_comparison_artifact: dict[str, Any],
    prior_cognition_artifacts: list[dict[str, Any]] | None = None,
    prior_comparison_artifacts: list[dict[str, Any]] | None = None,
    prior_clarification_artifacts: list[dict[str, Any]] | None = None,
    created_at: str,
    replay_dir: str | Path,
    disagreement_threshold: int = 1,
    uncertainty_threshold: int = 1,
    minimum_confidence: str = "HIGH",
) -> dict[str, Any]:
    """Create cognition continuity and clarification artifacts from comparison evidence."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        current = _validate_comparison_artifact(current_comparison_artifact)
        prior_cognition = [_validate_cognition_artifact(artifact) for artifact in (prior_cognition_artifacts or [])]
        prior_comparisons = [_validate_comparison_artifact(artifact) for artifact in (prior_comparison_artifacts or [])]
        prior_clarifications = [
            _validate_prior_clarification_artifact(artifact) for artifact in (prior_clarification_artifacts or [])
        ]
        history = _history_reference_artifact(
            continuity_id=continuity_id,
            current_comparison=current,
            prior_cognition_artifacts=prior_cognition,
            prior_comparison_artifacts=prior_comparisons,
            prior_clarification_artifacts=prior_clarifications,
            created_at=created_at,
        )
        continuity = _continuity_artifact(
            continuity_id=continuity_id,
            current_comparison=current,
            history=history,
            prior_cognition_artifacts=prior_cognition,
            prior_comparison_artifacts=prior_comparisons,
            prior_clarification_artifacts=prior_clarifications,
            created_at=created_at,
        )
        clarification = _clarification_artifact(
            clarification_id=clarification_id,
            current_comparison=current,
            continuity=continuity,
            history=history,
            disagreement_threshold=disagreement_threshold,
            uncertainty_threshold=uncertainty_threshold,
            minimum_confidence=minimum_confidence,
            created_at=created_at,
        )
        returned = _returned_artifact(history=history, continuity=continuity, clarification=clarification)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], history)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], continuity)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], clarification)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(
            final_status=STATUS_COMPLETED,
            history=history,
            continuity=continuity,
            clarification=clarification,
            returned=returned,
            replay_path=replay_path,
            failure_reason="",
        )
    except Exception as exc:
        failure_reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "cognition continuity failed closed"
        history = _failed_history_reference(
            continuity_id=continuity_id if _is_nonempty_string(continuity_id) else "COGNITION-CONTINUITY-INVALID",
            created_at=created_at if _is_nonempty_string(created_at) else "1970-01-01T00:00:00Z",
            failure_reason=failure_reason,
        )
        continuity = _failed_continuity_artifact(
            continuity_id=history["continuity_id"],
            history=history,
            created_at=created_at if _is_nonempty_string(created_at) else "1970-01-01T00:00:00Z",
            failure_reason=failure_reason,
        )
        clarification = _failed_clarification_artifact(
            clarification_id=clarification_id if _is_nonempty_string(clarification_id) else "COGNITION-CLARIFICATION-INVALID",
            continuity=continuity,
            history=history,
            created_at=created_at if _is_nonempty_string(created_at) else "1970-01-01T00:00:00Z",
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(history=history, continuity=continuity, clarification=clarification)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], history)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], continuity)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], clarification)
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(
            final_status=STATUS_FAILED_CLOSED,
            history=history,
            continuity=continuity,
            clarification=clarification,
            returned=returned,
            replay_path=replay_path,
            failure_reason=failure_reason,
        )


def reconstruct_ocs_llm_cognition_continuity_and_clarification_replay(replay_dir: str | Path) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("cognition continuity replay ordering mismatch")
        _verify_replay_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("cognition continuity replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "cognition continuity replay artifact")
        wrappers.append(wrapper)
    history = wrappers[0]["artifact"]
    continuity = wrappers[1]["artifact"]
    clarification = wrappers[2]["artifact"]
    returned = wrappers[3]["artifact"]
    if continuity.get("history_reference_hash") != history["artifact_hash"]:
        raise FailClosedRuntimeError("cognition continuity history reference mismatch")
    if clarification.get("continuity_artifact_hash") != continuity["artifact_hash"]:
        raise FailClosedRuntimeError("cognition clarification continuity reference mismatch")
    if returned.get("history_reference_hash") != history["artifact_hash"]:
        raise FailClosedRuntimeError("cognition returned history hash mismatch")
    if returned.get("continuity_artifact_hash") != continuity["artifact_hash"]:
        raise FailClosedRuntimeError("cognition returned continuity hash mismatch")
    if returned.get("clarification_artifact_hash") != clarification["artifact_hash"]:
        raise FailClosedRuntimeError("cognition returned clarification hash mismatch")
    if history.get("history_hash") != _compute_history_hash(history):
        raise FailClosedRuntimeError("cognition history hash mismatch")
    if continuity.get("continuity_hash") != _compute_continuity_hash(continuity):
        raise FailClosedRuntimeError("cognition continuity hash mismatch")
    if clarification.get("clarification_hash") != _compute_clarification_hash(clarification):
        raise FailClosedRuntimeError("cognition clarification hash mismatch")
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "classification": CERTIFIED_CLASSIFICATION,
        "history_reference_id": history["history_reference_id"],
        "continuity_id": continuity["continuity_id"],
        "clarification_id": clarification["clarification_id"],
        "continuity_status": continuity["continuity_status"],
        "clarification_status": clarification["clarification_status"],
        "clarification_required": clarification["clarification_required"],
        "clarification_candidate_count": len(clarification["clarification_candidates"]),
        "stale_cognition": deepcopy(continuity["stale_cognition"]),
        "repeated_uncertainty": deepcopy(continuity["repeated_uncertainty"]),
        "recurring_disagreement": deepcopy(continuity["recurring_disagreement"]),
        "replay_visible": True,
        "worker_invoked": False,
        "execution_requested": False,
        "approval_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _history_reference_artifact(
    *,
    continuity_id: str,
    current_comparison: dict[str, Any],
    prior_cognition_artifacts: list[dict[str, Any]],
    prior_comparison_artifacts: list[dict[str, Any]],
    prior_clarification_artifacts: list[dict[str, Any]],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": COGNITION_HISTORY_REFERENCE_V1,
        "runtime_version": MILESTONE_ID,
        "classification": CERTIFIED_CLASSIFICATION,
        "history_reference_id": f"{_require_string(continuity_id, 'continuity_id')}:HISTORY",
        "continuity_id": _require_string(continuity_id, "continuity_id"),
        "current_comparison_reference": _comparison_reference(current_comparison),
        "prior_cognition_references": [_cognition_reference(item) for item in prior_cognition_artifacts],
        "prior_comparison_references": [_comparison_reference(item) for item in prior_comparison_artifacts],
        "prior_clarification_references": [_clarification_reference(item) for item in prior_clarification_artifacts],
        "history_counts": {
            "prior_cognition_artifact_count": len(prior_cognition_artifacts),
            "prior_comparison_artifact_count": len(prior_comparison_artifacts),
            "prior_clarification_artifact_count": len(prior_clarification_artifacts),
        },
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
        "history_status": STATUS_COMPLETED,
    }
    artifact["history_hash"] = _compute_history_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _continuity_artifact(
    *,
    continuity_id: str,
    current_comparison: dict[str, Any],
    history: dict[str, Any],
    prior_cognition_artifacts: list[dict[str, Any]],
    prior_comparison_artifacts: list[dict[str, Any]],
    prior_clarification_artifacts: list[dict[str, Any]],
    created_at: str,
) -> dict[str, Any]:
    stale = _stale_cognition(current_comparison, prior_cognition_artifacts, prior_comparison_artifacts)
    repeated_uncertainty = _repeated_uncertainty(current_comparison, prior_comparison_artifacts, prior_clarification_artifacts)
    recurring_disagreement = _recurring_disagreement(current_comparison, prior_comparison_artifacts)
    artifact = {
        "artifact_type": COGNITION_CONTINUITY_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "classification": CERTIFIED_CLASSIFICATION,
        "continuity_id": _require_string(continuity_id, "continuity_id"),
        "continuity_status": STATUS_COMPLETED,
        "history_reference_id": history["history_reference_id"],
        "history_reference_hash": history["artifact_hash"],
        "current_comparison_reference": _comparison_reference(current_comparison),
        "stale_cognition": stale,
        "repeated_uncertainty": repeated_uncertainty,
        "recurring_disagreement": recurring_disagreement,
        "continuity_summary": {
            "prior_cognition_reused": len(prior_cognition_artifacts),
            "prior_comparisons_reused": len(prior_comparison_artifacts),
            "prior_clarifications_reused": len(prior_clarification_artifacts),
            "stale_cognition_detected": bool(stale),
            "repeated_uncertainty_detected": bool(repeated_uncertainty),
            "recurring_disagreement_detected": bool(recurring_disagreement),
        },
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["continuity_hash"] = _compute_continuity_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _clarification_artifact(
    *,
    clarification_id: str,
    current_comparison: dict[str, Any],
    continuity: dict[str, Any],
    history: dict[str, Any],
    disagreement_threshold: int,
    uncertainty_threshold: int,
    minimum_confidence: str,
    created_at: str,
) -> dict[str, Any]:
    candidates = _clarification_candidates(
        current_comparison=current_comparison,
        continuity=continuity,
        disagreement_threshold=disagreement_threshold,
        uncertainty_threshold=uncertainty_threshold,
        minimum_confidence=minimum_confidence,
    )
    artifact = {
        "artifact_type": COGNITION_CLARIFICATION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "classification": CERTIFIED_CLASSIFICATION,
        "clarification_id": _require_string(clarification_id, "clarification_id"),
        "clarification_status": CLARIFICATION_REQUIRED if candidates else CLARIFICATION_NOT_REQUIRED,
        "clarification_required": bool(candidates),
        "clarification_candidates": candidates,
        "operator_response_required": bool(candidates),
        "history_reference_id": history["history_reference_id"],
        "history_reference_hash": history["artifact_hash"],
        "continuity_id": continuity["continuity_id"],
        "continuity_artifact_hash": continuity["artifact_hash"],
        "source_comparison_reference": _comparison_reference(current_comparison),
        "trigger_policy": {
            "disagreement_threshold": _normalize_threshold(disagreement_threshold, "disagreement_threshold"),
            "uncertainty_threshold": _normalize_threshold(uncertainty_threshold, "uncertainty_threshold"),
            "minimum_confidence": _normalize_confidence(minimum_confidence),
        },
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "non_authoritative": True,
        "human_facing": True,
        "replay_visible": True,
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["clarification_hash"] = _compute_clarification_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _clarification_candidates(
    *,
    current_comparison: dict[str, Any],
    continuity: dict[str, Any],
    disagreement_threshold: int,
    uncertainty_threshold: int,
    minimum_confidence: str,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    disagreement_count = (
        len(current_comparison.get("disagreement", []))
        + len(current_comparison.get("conflicting_assumptions", []))
        + len(current_comparison.get("conflicting_risks", []))
        + len(current_comparison.get("conflicting_alternatives", []))
    )
    uncertainty_count = len(current_comparison.get("uncertainty", []))
    missing_count = len(current_comparison.get("missing_information", []))
    minimum = _normalize_confidence(minimum_confidence)
    confidence = _normalize_confidence(current_comparison.get("comparison_confidence"))
    if disagreement_count >= _normalize_threshold(disagreement_threshold, "disagreement_threshold"):
        candidates.append(_candidate("DISAGREEMENT_THRESHOLD_EXCEEDED", "Provider cognition disagreement requires human clarification.", disagreement_count))
    if uncertainty_count >= _normalize_threshold(uncertainty_threshold, "uncertainty_threshold"):
        candidates.append(_candidate("UNCERTAINTY_THRESHOLD_EXCEEDED", "Provider cognition uncertainty requires human clarification.", uncertainty_count))
    if missing_count:
        candidates.append(_candidate("MISSING_INFORMATION_DETECTED", "Provider cognition comparison reported missing information.", missing_count))
    if CONFIDENCE_RANK[confidence] < CONFIDENCE_RANK[minimum]:
        candidates.append(_candidate("LOW_COMPARISON_CONFIDENCE", "Comparison confidence is below the configured threshold.", CONFIDENCE_RANK[confidence]))
    if continuity["repeated_uncertainty"]:
        candidates.append(_candidate("REPEATED_UNCERTAINTY", "Uncertainty recurs across cognition history.", len(continuity["repeated_uncertainty"])))
    if continuity["recurring_disagreement"]:
        candidates.append(_candidate("RECURRING_DISAGREEMENT", "Disagreement recurs across cognition history.", len(continuity["recurring_disagreement"])))
    deduped = {item["clarification_candidate_hash"]: item for item in candidates}
    return sorted(deduped.values(), key=lambda item: (item["trigger"], item["clarification_candidate_hash"]))


def _candidate(trigger: str, question: str, evidence_count: int) -> dict[str, Any]:
    payload = {
        "trigger": trigger,
        "question": question,
        "evidence_count": evidence_count,
    }
    return {
        "clarification_candidate_id": replay_hash(payload),
        "clarification_candidate_hash": replay_hash(payload),
        **payload,
        "operator_response_required": True,
        "authority": False,
    }


def _stale_cognition(
    current_comparison: dict[str, Any],
    prior_cognition_artifacts: list[dict[str, Any]],
    prior_comparison_artifacts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    current_context = current_comparison["context_hash"]
    stale: list[dict[str, Any]] = []
    for item in prior_cognition_artifacts:
        if item.get("context_hash") != current_context:
            stale.append(
                {
                    "source": "LLM_COGNITION_ARTIFACT_V1",
                    "source_id": item["cognition_artifact_id"],
                    "source_hash": item["artifact_hash"],
                    "prior_context_hash": item.get("context_hash"),
                    "current_context_hash": current_context,
                    "reason": "prior cognition context differs from current comparison context",
                }
            )
    for item in prior_comparison_artifacts:
        if item.get("context_hash") != current_context:
            stale.append(
                {
                    "source": "COGNITION_COMPARISON_ARTIFACT_V1",
                    "source_id": item["cognition_comparison_id"],
                    "source_hash": item["artifact_hash"],
                    "prior_context_hash": item.get("context_hash"),
                    "current_context_hash": current_context,
                    "reason": "prior comparison context differs from current comparison context",
                }
            )
    return sorted(stale, key=lambda item: (item["source"], item["source_id"]))


def _repeated_uncertainty(
    current_comparison: dict[str, Any],
    prior_comparison_artifacts: list[dict[str, Any]],
    prior_clarification_artifacts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    current = {_normalize_text(item.get("text")) for item in current_comparison.get("uncertainty", []) if item.get("text")}
    prior = set()
    for comparison in prior_comparison_artifacts:
        prior.update(_normalize_text(item.get("text")) for item in comparison.get("uncertainty", []) if item.get("text"))
    for clarification in prior_clarification_artifacts:
        prior.update(
            _normalize_text(item.get("question")) for item in clarification.get("clarification_candidates", []) if item.get("question")
        )
    repeated = sorted(current.intersection(prior))
    return [{"uncertainty_key": item, "reason": "uncertainty repeated across cognition history"} for item in repeated]


def _recurring_disagreement(current_comparison: dict[str, Any], prior_comparison_artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    current = _disagreement_keys(current_comparison)
    prior = set()
    for comparison in prior_comparison_artifacts:
        prior.update(_disagreement_keys(comparison))
    recurring = sorted(current.intersection(prior))
    return [{"disagreement_key": item, "reason": "disagreement repeated across cognition history"} for item in recurring]


def _disagreement_keys(comparison: dict[str, Any]) -> set[str]:
    keys = set()
    for field in ("disagreement", "conflicting_assumptions", "conflicting_risks", "conflicting_alternatives"):
        keys.update(_normalize_text(item.get("text")) for item in comparison.get(field, []) if item.get("text"))
    return keys


def _validate_comparison_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("cognition comparison artifact must be a JSON object")
    if artifact.get("artifact_type") != COGNITION_COMPARISON_ARTIFACT_V1:
        raise FailClosedRuntimeError("invalid cognition comparison artifact")
    if artifact.get("comparison_status") != STATUS_COMPLETED:
        raise FailClosedRuntimeError("cognition comparison must be completed")
    _verify_artifact_hash(artifact, "cognition comparison artifact")
    _reject_prohibited_flags(artifact, "cognition comparison artifact")
    _validate_authority_flags(artifact.get("authority_flags"))
    return deepcopy(artifact)


def _validate_cognition_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("cognition artifact must be a JSON object")
    if artifact.get("artifact_type") != LLM_COGNITION_ARTIFACT_V1:
        raise FailClosedRuntimeError("invalid LLM cognition artifact")
    _verify_artifact_hash(artifact, "LLM cognition artifact")
    _reject_prohibited_flags(artifact, "LLM cognition artifact")
    return deepcopy(artifact)


def _validate_prior_clarification_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("prior clarification artifact must be a JSON object")
    if artifact.get("artifact_type") != COGNITION_CLARIFICATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("invalid prior cognition clarification artifact")
    _verify_artifact_hash(artifact, "prior cognition clarification artifact")
    _reject_prohibited_flags(artifact, "prior cognition clarification artifact")
    return deepcopy(artifact)


def _comparison_reference(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_type": artifact["artifact_type"],
        "cognition_comparison_id": artifact["cognition_comparison_id"],
        "artifact_hash": artifact["artifact_hash"],
        "comparison_hash": artifact["comparison_hash"],
        "context_hash": artifact["context_hash"],
        "comparison_confidence": artifact["comparison_confidence"],
    }


def _cognition_reference(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_type": artifact["artifact_type"],
        "cognition_artifact_id": artifact["cognition_artifact_id"],
        "artifact_hash": artifact["artifact_hash"],
        "cognition_hash": artifact["cognition_hash"],
        "context_hash": artifact["context_hash"],
        "provider_identity": deepcopy(artifact.get("provider_identity")),
    }


def _clarification_reference(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_type": artifact["artifact_type"],
        "clarification_id": artifact["clarification_id"],
        "artifact_hash": artifact["artifact_hash"],
        "clarification_hash": artifact["clarification_hash"],
        "clarification_status": artifact["clarification_status"],
    }


def _returned_artifact(*, history: dict[str, Any], continuity: dict[str, Any], clarification: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": COGNITION_CONTINUITY_AND_CLARIFICATION_RETURNED_V1,
        "runtime_version": MILESTONE_ID,
        "history_reference_id": history["history_reference_id"],
        "history_reference_hash": history["artifact_hash"],
        "continuity_id": continuity["continuity_id"],
        "continuity_artifact_hash": continuity["artifact_hash"],
        "clarification_id": clarification["clarification_id"],
        "clarification_artifact_hash": clarification["artifact_hash"],
        "clarification_required": clarification["clarification_required"],
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_history_reference(*, continuity_id: str, created_at: str, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": COGNITION_HISTORY_REFERENCE_V1,
        "runtime_version": MILESTONE_ID,
        "classification": CERTIFIED_CLASSIFICATION,
        "history_reference_id": f"{continuity_id}:HISTORY",
        "continuity_id": continuity_id,
        "current_comparison_reference": None,
        "prior_cognition_references": [],
        "prior_comparison_references": [],
        "prior_clarification_references": [],
        "history_counts": {
            "prior_cognition_artifact_count": 0,
            "prior_comparison_artifact_count": 0,
            "prior_clarification_artifact_count": 0,
        },
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": created_at,
        "history_status": STATUS_FAILED_CLOSED,
        "failure_reason": failure_reason,
    }
    artifact["history_hash"] = _compute_history_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_continuity_artifact(*, continuity_id: str, history: dict[str, Any], created_at: str, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": COGNITION_CONTINUITY_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "classification": CERTIFIED_CLASSIFICATION,
        "continuity_id": continuity_id,
        "continuity_status": STATUS_FAILED_CLOSED,
        "history_reference_id": history["history_reference_id"],
        "history_reference_hash": history["artifact_hash"],
        "current_comparison_reference": None,
        "stale_cognition": [],
        "repeated_uncertainty": [],
        "recurring_disagreement": [],
        "continuity_summary": {
            "prior_cognition_reused": 0,
            "prior_comparisons_reused": 0,
            "prior_clarifications_reused": 0,
            "stale_cognition_detected": False,
            "repeated_uncertainty_detected": False,
            "recurring_disagreement_detected": False,
        },
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_visible": True,
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": created_at,
        "failure_reason": failure_reason,
    }
    artifact["continuity_hash"] = _compute_continuity_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_clarification_artifact(*, clarification_id: str, continuity: dict[str, Any], history: dict[str, Any], created_at: str, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": COGNITION_CLARIFICATION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "classification": CERTIFIED_CLASSIFICATION,
        "clarification_id": clarification_id,
        "clarification_status": STATUS_FAILED_CLOSED,
        "clarification_required": False,
        "clarification_candidates": [],
        "operator_response_required": False,
        "history_reference_id": history["history_reference_id"],
        "history_reference_hash": history["artifact_hash"],
        "continuity_id": continuity["continuity_id"],
        "continuity_artifact_hash": continuity["artifact_hash"],
        "source_comparison_reference": None,
        "trigger_policy": {},
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "non_authoritative": True,
        "human_facing": True,
        "replay_visible": True,
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": created_at,
        "failure_reason": failure_reason,
    }
    artifact["clarification_hash"] = _compute_clarification_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    *,
    final_status: str,
    history: dict[str, Any],
    continuity: dict[str, Any],
    clarification: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
    failure_reason: str,
) -> dict[str, Any]:
    result = {
        "command": "aigol ocs llm-cognition continuity-and-clarification",
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "classification": CERTIFIED_CLASSIFICATION,
        "final_status": final_status,
        "history_reference": deepcopy(history),
        "cognition_continuity_artifact": deepcopy(continuity),
        "cognition_clarification_artifact": deepcopy(clarification),
        "returned_artifact": deepcopy(returned),
        "clarification_required": clarification.get("clarification_required") is True,
        "clarification_candidate_count": len(clarification.get("clarification_candidates", [])),
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_reference": str(replay_path),
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "fail_closed": final_status != STATUS_COMPLETED,
        "failure_reason": failure_reason,
    }
    result["cognition_continuity_and_clarification_hash"] = replay_hash(result)
    return result


def _compute_history_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "history_reference_id": artifact["history_reference_id"],
            "continuity_id": artifact["continuity_id"],
            "current_comparison_reference": artifact["current_comparison_reference"],
            "prior_cognition_references": artifact["prior_cognition_references"],
            "prior_comparison_references": artifact["prior_comparison_references"],
            "prior_clarification_references": artifact["prior_clarification_references"],
            "history_counts": artifact["history_counts"],
            "authority_flags": artifact["authority_flags"],
            "history_status": artifact["history_status"],
            "failure_reason": artifact.get("failure_reason"),
        }
    )


def _compute_continuity_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "continuity_id": artifact["continuity_id"],
            "continuity_status": artifact["continuity_status"],
            "history_reference_hash": artifact["history_reference_hash"],
            "current_comparison_reference": artifact["current_comparison_reference"],
            "stale_cognition": artifact["stale_cognition"],
            "repeated_uncertainty": artifact["repeated_uncertainty"],
            "recurring_disagreement": artifact["recurring_disagreement"],
            "continuity_summary": artifact["continuity_summary"],
            "authority_flags": artifact["authority_flags"],
            "failure_reason": artifact.get("failure_reason"),
        }
    )


def _compute_clarification_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "clarification_id": artifact["clarification_id"],
            "clarification_status": artifact["clarification_status"],
            "clarification_required": artifact["clarification_required"],
            "clarification_candidates": artifact["clarification_candidates"],
            "history_reference_hash": artifact["history_reference_hash"],
            "continuity_artifact_hash": artifact["continuity_artifact_hash"],
            "source_comparison_reference": artifact["source_comparison_reference"],
            "trigger_policy": artifact["trigger_policy"],
            "authority_flags": artifact["authority_flags"],
            "failure_reason": artifact.get("failure_reason"),
        }
    )


def _normalize_confidence(value: Any) -> str:
    confidence = _require_string(value, "confidence").upper()
    if confidence not in CONFIDENCE_RANK:
        raise FailClosedRuntimeError("confidence value is not recognized")
    return confidence


def _normalize_threshold(value: int, field_name: str) -> int:
    if not isinstance(value, int) or value < 1:
        raise FailClosedRuntimeError(f"{field_name} must be a positive integer")
    return value


def _normalize_text(value: Any) -> str:
    return " ".join(_require_string(value, "text").lower().split())


def _reject_prohibited_flags(artifact: dict[str, Any], label: str) -> None:
    for flag in (
        "approval_created",
        "execution_requested",
        "dispatch_requested",
        "worker_invoked",
        "domain_created",
        "governance_modified",
        "replay_modified",
    ):
        if artifact.get(flag) is True:
            raise FailClosedRuntimeError(f"{label} carries prohibited authority flag: {flag}")
    flags = artifact.get("authority_flags")
    if isinstance(flags, dict):
        _validate_authority_flags(flags)


def _validate_authority_flags(flags: Any) -> None:
    if not isinstance(flags, dict):
        raise FailClosedRuntimeError("authority flags are missing")
    for flag, expected in AUTHORITY_FLAGS.items():
        if flags.get(flag) is not expected:
            raise FailClosedRuntimeError(f"authority flag must be false: {flag}")


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("cognition continuity replay step ordering mismatch")
    _verify_artifact_hash(artifact, "cognition continuity replay artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
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
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError(f"{label} artifact hash is required")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} artifact hash mismatch")


def _verify_replay_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("cognition continuity replay hash is required")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("cognition continuity replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not _is_nonempty_string(value):
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
