"""Convert resolved human clarification into cognition-compatible input."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.intent_clarification_dialog_runtime import (
    CLARIFICATION_RESOLVED,
    HUMAN_CLARIFICATION_REQUEST_ARTIFACT_V1,
    HUMAN_CLARIFICATION_RESOLUTION_ARTIFACT_V1,
    HUMAN_CLARIFICATION_RESPONSE_ARTIFACT_V1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_INTENT_CLARIFICATION_COGNITION_INTEGRATION_VERSION = (
    "AIGOL_INTENT_CLARIFICATION_COGNITION_INTEGRATION_V1"
)
CLARIFIED_COGNITION_INPUT_ARTIFACT_V1 = "CLARIFIED_COGNITION_INPUT_ARTIFACT_V1"
CLARIFICATION_COGNITION_EVIDENCE_V1 = "CLARIFICATION_COGNITION_EVIDENCE_V1"
CLARIFICATION_COGNITION_CLASSIFICATION_V1 = "CLARIFICATION_COGNITION_CLASSIFICATION_V1"
CLARIFIED_COGNITION_INPUT_CREATED = "CLARIFIED_COGNITION_INPUT_CREATED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "clarification_cognition_evidence_recorded",
    "clarification_cognition_classification_recorded",
    "clarified_cognition_input_recorded",
    "clarification_cognition_integration_returned",
)

HIGH_RISK_DOMAINS = {"TRADING", "HEALTHCARE", "LEGAL", "CRITICAL_INFRASTRUCTURE", "PUBLIC_SERVICES"}


def integrate_clarification_resolution_with_cognition(
    *,
    integration_id: str,
    clarification_request_artifact: dict[str, Any],
    clarification_response_artifact: dict[str, Any],
    clarification_resolution_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    confidence: str = "DETERMINISTIC",
) -> dict[str, Any]:
    """Create source-agnostic cognition input from a resolved clarification."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        request = deepcopy(clarification_request_artifact)
        response = deepcopy(clarification_response_artifact)
        resolution = deepcopy(clarification_resolution_artifact)
        _validate_inputs(request=request, response=response, resolution=resolution)
        evidence = _evidence_artifact(
            integration_id=integration_id,
            request=request,
            response=response,
            resolution=resolution,
            confidence=confidence,
            created_at=created_at,
            evidence_status="CLARIFICATION_COGNITION_EVIDENCE_ACCEPTED",
            failure_reason=None,
        )
        classification = _classification_artifact(
            integration_id=integration_id,
            evidence=evidence,
            resolution=resolution,
            confidence=confidence,
            created_at=created_at,
            classification_status="CLARIFICATION_COGNITION_CLASSIFIED",
            failure_reason=None,
        )
        clarified_input = _clarified_input_artifact(
            integration_id=integration_id,
            evidence=evidence,
            classification=classification,
            resolution=resolution,
            confidence=confidence,
            created_at=created_at,
            integration_status=CLARIFIED_COGNITION_INPUT_CREATED,
            failure_reason=None,
        )
        returned = _returned_artifact(clarified_input)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], classification)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], clarified_input)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(evidence, classification, clarified_input, returned, replay_path)
    except Exception as exc:
        evidence = _failed_evidence_artifact(
            integration_id=integration_id,
            clarification_request_artifact=clarification_request_artifact,
            clarification_response_artifact=clarification_response_artifact,
            clarification_resolution_artifact=clarification_resolution_artifact,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        classification = _failed_classification_artifact(
            integration_id=integration_id,
            evidence=evidence,
            created_at=created_at,
        )
        clarified_input = _failed_clarified_input_artifact(
            integration_id=integration_id,
            evidence=evidence,
            classification=classification,
            created_at=created_at,
            failure_reason=evidence["failure_reason"],
        )
        returned = _returned_artifact(clarified_input)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], evidence)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], classification)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], clarified_input)
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(evidence, classification, clarified_input, returned, replay_path)


def reconstruct_intent_clarification_cognition_integration_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct clarification-to-cognition integration replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("clarification cognition integration replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("clarification cognition integration replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "clarification cognition integration artifact")
        wrappers.append(wrapper)
    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    clarified_input = wrappers[2]["artifact"]
    returned = wrappers[3]["artifact"]
    if classification.get("integration_evidence_reference") != evidence["integration_evidence_id"]:
        raise FailClosedRuntimeError("clarification cognition evidence reference mismatch")
    if classification.get("integration_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("clarification cognition evidence hash mismatch")
    if clarified_input.get("classification_reference") != classification["classification_id"]:
        raise FailClosedRuntimeError("clarification cognition classification reference mismatch")
    if clarified_input.get("classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("clarification cognition classification hash mismatch")
    if returned.get("clarified_cognition_input_reference") != clarified_input["clarified_cognition_input_id"]:
        raise FailClosedRuntimeError("clarification cognition returned reference mismatch")
    if returned.get("clarified_cognition_input_hash") != clarified_input["artifact_hash"]:
        raise FailClosedRuntimeError("clarification cognition returned hash mismatch")
    return {
        "clarified_cognition_input_id": clarified_input["clarified_cognition_input_id"],
        "integration_status": clarified_input["integration_status"],
        "canonical_chain_id": clarified_input["canonical_chain_id"],
        "cognition_input_type": clarified_input["cognition_input_type"],
        "normalized_intent": clarified_input["normalized_intent"],
        "normalized_intent_class": clarified_input["normalized_intent_class"],
        "domain_id": clarified_input["domain_id"],
        "confidence": clarified_input["confidence"],
        "intent_source_visible_to_cognition": clarified_input["intent_source_visible_to_cognition"],
        "failure_reason": clarified_input["failure_reason"],
        "cognition_invoked": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_inputs(*, request: dict[str, Any], response: dict[str, Any], resolution: dict[str, Any]) -> None:
    _validate_artifact(request, HUMAN_CLARIFICATION_REQUEST_ARTIFACT_V1, "clarification request")
    _validate_artifact(response, HUMAN_CLARIFICATION_RESPONSE_ARTIFACT_V1, "clarification response")
    _validate_artifact(resolution, HUMAN_CLARIFICATION_RESOLUTION_ARTIFACT_V1, "clarification resolution")
    if resolution.get("resolution_status") != CLARIFICATION_RESOLVED:
        reason = resolution.get("failure_reason") or "clarification unresolved"
        if "contradictory answers detected" in str(reason):
            raise FailClosedRuntimeError("clarification cognition integration failed closed: contradictory clarification")
        raise FailClosedRuntimeError("clarification cognition integration failed closed: clarification unresolved")
    if response.get("clarification_request_reference") != request.get("clarification_request_id"):
        raise FailClosedRuntimeError("clarification cognition integration failed closed: replay corruption")
    if response.get("clarification_request_hash") != request.get("artifact_hash"):
        raise FailClosedRuntimeError("clarification cognition integration failed closed: replay corruption")
    if resolution.get("clarification_request_reference") != request.get("clarification_request_id"):
        raise FailClosedRuntimeError("clarification cognition integration failed closed: replay corruption")
    if resolution.get("clarification_request_hash") != request.get("artifact_hash"):
        raise FailClosedRuntimeError("clarification cognition integration failed closed: replay corruption")
    if resolution.get("clarification_response_reference") != response.get("clarification_response_id"):
        raise FailClosedRuntimeError("clarification cognition integration failed closed: replay corruption")
    if resolution.get("clarification_response_hash") != response.get("artifact_hash"):
        raise FailClosedRuntimeError("clarification cognition integration failed closed: replay corruption")
    if request.get("canonical_chain_id") != response.get("canonical_chain_id"):
        raise FailClosedRuntimeError("clarification cognition integration failed closed: invalid chain continuity")
    if request.get("canonical_chain_id") != resolution.get("canonical_chain_id"):
        raise FailClosedRuntimeError("clarification cognition integration failed closed: invalid chain continuity")
    resolved_intent = resolution.get("resolved_intent")
    if not isinstance(resolved_intent, dict):
        raise FailClosedRuntimeError("clarification cognition integration failed closed: clarification unresolved")
    _require_string(resolved_intent.get("domain_id"), "domain_id")
    _require_string(resolved_intent.get("intent_reference"), "intent_reference")
    _require_string(resolution.get("selected_interpretation"), "selected_interpretation")
    for artifact in (request, response, resolution):
        if artifact.get("provider_invoked") is not False or artifact.get("worker_invoked") is not False:
            raise FailClosedRuntimeError("clarification cognition integration failed closed: replay corruption")
        if artifact.get("execution_requested") is not False or artifact.get("dispatch_requested") is not False:
            raise FailClosedRuntimeError("clarification cognition integration failed closed: replay corruption")


def _evidence_artifact(
    *,
    integration_id: str,
    request: dict[str, Any],
    response: dict[str, Any],
    resolution: dict[str, Any],
    confidence: str,
    created_at: str,
    evidence_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CLARIFICATION_COGNITION_EVIDENCE_V1,
        "runtime_version": AIGOL_INTENT_CLARIFICATION_COGNITION_INTEGRATION_VERSION,
        "integration_evidence_id": f"{_require_string(integration_id, 'integration_id')}:CLARIFICATION-COGNITION-EVIDENCE",
        "integration_reference": integration_id,
        "canonical_chain_id": resolution["canonical_chain_id"],
        "clarification_request_reference": request["clarification_request_id"],
        "clarification_request_hash": request["artifact_hash"],
        "clarification_response_reference": response["clarification_response_id"],
        "clarification_response_hash": response["artifact_hash"],
        "clarification_resolution_reference": resolution["clarification_resolution_id"],
        "clarification_resolution_hash": resolution["artifact_hash"],
        "clarification_history": deepcopy(resolution["clarification_history"]),
        "clarification_history_hash": replay_hash(resolution["clarification_history"]),
        "resolved_intent_reference": resolution["resolved_intent_reference"],
        "selected_interpretation": resolution["selected_interpretation"],
        "domain_id": resolution["resolved_intent"]["domain_id"],
        "confidence": _normalize_confidence(confidence),
        "source_lineage_preserved": True,
        "evidence_status": evidence_status,
        "cognition_invoked": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _classification_artifact(
    *,
    integration_id: str,
    evidence: dict[str, Any],
    resolution: dict[str, Any],
    confidence: str,
    created_at: str,
    classification_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    resolved = resolution["resolved_intent"]
    artifact = {
        "artifact_type": CLARIFICATION_COGNITION_CLASSIFICATION_V1,
        "runtime_version": AIGOL_INTENT_CLARIFICATION_COGNITION_INTEGRATION_VERSION,
        "classification_id": f"{_require_string(integration_id, 'integration_id')}:CLARIFICATION-COGNITION-CLASSIFICATION",
        "integration_reference": integration_id,
        "integration_evidence_reference": evidence["integration_evidence_id"],
        "integration_evidence_hash": evidence["artifact_hash"],
        "canonical_chain_id": resolution["canonical_chain_id"],
        "cognition_input_type": "STRUCTURED_INTENT",
        "intent_source_class": "HUMAN_CLARIFIED_INTENT",
        "source_normalized_for_cognition": True,
        "intent_source_visible_to_cognition": False,
        "normalized_intent": _normalized_intent(resolved),
        "normalized_intent_class": _normalized_intent_class(resolved),
        "selected_interpretation": resolution["selected_interpretation"],
        "domain_id": resolved["domain_id"],
        "worker_family_id": resolved.get("worker_family_id"),
        "milestone_type": resolved.get("milestone_type"),
        "capability_id": resolved.get("capability_id"),
        "resource_category": resolved.get("resource_category"),
        "confidence": _normalize_confidence(confidence),
        "classification_status": classification_status,
        "cognition_invoked": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _clarified_input_artifact(
    *,
    integration_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    resolution: dict[str, Any],
    confidence: str,
    created_at: str,
    integration_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    cognition_contract = {
        "intent_reference": f"{integration_id}:CLARIFIED-COGNITION-INPUT",
        "normalized_intent": classification["normalized_intent"],
        "normalized_intent_class": classification["normalized_intent_class"],
        "domain_id": classification["domain_id"],
        "worker_family_id": classification["worker_family_id"],
        "milestone_type": classification["milestone_type"],
        "capability_id": classification["capability_id"],
        "resource_category": classification["resource_category"],
        "confidence": _normalize_confidence(confidence),
        "intent_source_visible_to_cognition": False,
    }
    artifact = {
        "artifact_type": CLARIFIED_COGNITION_INPUT_ARTIFACT_V1,
        "runtime_version": AIGOL_INTENT_CLARIFICATION_COGNITION_INTEGRATION_VERSION,
        "clarified_cognition_input_id": f"{_require_string(integration_id, 'integration_id')}:CLARIFIED-COGNITION-INPUT",
        "integration_id": integration_id,
        "integration_status": integration_status,
        "canonical_chain_id": resolution["canonical_chain_id"],
        "cognition_input_type": classification["cognition_input_type"],
        "normalized_intent": classification["normalized_intent"],
        "normalized_intent_class": classification["normalized_intent_class"],
        "domain_id": classification["domain_id"],
        "worker_family_id": classification["worker_family_id"],
        "milestone_type": classification["milestone_type"],
        "capability_id": classification["capability_id"],
        "resource_category": classification["resource_category"],
        "confidence": _normalize_confidence(confidence),
        "selected_interpretation": classification["selected_interpretation"],
        "source_lineage_preserved": True,
        "intent_source": "HUMAN_CLARIFICATION",
        "intent_source_visible_to_cognition": False,
        "cognition_input_contract": cognition_contract,
        "evidence_reference": evidence["integration_evidence_id"],
        "evidence_hash": evidence["artifact_hash"],
        "classification_reference": classification["classification_id"],
        "classification_hash": classification["artifact_hash"],
        "source_clarification_resolution_reference": resolution["clarification_resolution_id"],
        "source_clarification_resolution_hash": resolution["artifact_hash"],
        "clarification_history": deepcopy(resolution["clarification_history"]),
        "clarification_history_hash": replay_hash(resolution["clarification_history"]),
        "human_review_required": classification["domain_id"] in HIGH_RISK_DOMAINS,
        "high_risk_domain": classification["domain_id"] in HIGH_RISK_DOMAINS,
        "cognition_invoked": False,
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_evidence_artifact(
    *,
    integration_id: str,
    clarification_request_artifact: dict[str, Any],
    clarification_response_artifact: dict[str, Any],
    clarification_resolution_artifact: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    resolution = clarification_resolution_artifact if isinstance(clarification_resolution_artifact, dict) else {}
    request = clarification_request_artifact if isinstance(clarification_request_artifact, dict) else {}
    response = clarification_response_artifact if isinstance(clarification_response_artifact, dict) else {}
    artifact = {
        "artifact_type": CLARIFICATION_COGNITION_EVIDENCE_V1,
        "runtime_version": AIGOL_INTENT_CLARIFICATION_COGNITION_INTEGRATION_VERSION,
        "integration_evidence_id": f"{integration_id}:CLARIFICATION-COGNITION-EVIDENCE"
        if isinstance(integration_id, str)
        else "INVALID:CLARIFICATION-COGNITION-EVIDENCE",
        "integration_reference": integration_id if isinstance(integration_id, str) else "INVALID",
        "canonical_chain_id": resolution.get("canonical_chain_id"),
        "clarification_request_reference": request.get("clarification_request_id"),
        "clarification_request_hash": request.get("artifact_hash"),
        "clarification_response_reference": response.get("clarification_response_id"),
        "clarification_response_hash": response.get("artifact_hash"),
        "clarification_resolution_reference": resolution.get("clarification_resolution_id"),
        "clarification_resolution_hash": resolution.get("artifact_hash"),
        "clarification_history": [],
        "clarification_history_hash": replay_hash([]),
        "resolved_intent_reference": resolution.get("resolved_intent_reference"),
        "selected_interpretation": resolution.get("selected_interpretation"),
        "domain_id": None,
        "confidence": None,
        "source_lineage_preserved": False,
        "evidence_status": FAILED_CLOSED,
        "cognition_invoked": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": created_at,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_classification_artifact(
    *,
    integration_id: str,
    evidence: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CLARIFICATION_COGNITION_CLASSIFICATION_V1,
        "runtime_version": AIGOL_INTENT_CLARIFICATION_COGNITION_INTEGRATION_VERSION,
        "classification_id": f"{integration_id}:CLARIFICATION-COGNITION-CLASSIFICATION"
        if isinstance(integration_id, str)
        else "INVALID:CLARIFICATION-COGNITION-CLASSIFICATION",
        "integration_reference": integration_id if isinstance(integration_id, str) else "INVALID",
        "integration_evidence_reference": evidence["integration_evidence_id"],
        "integration_evidence_hash": evidence["artifact_hash"],
        "canonical_chain_id": evidence["canonical_chain_id"],
        "cognition_input_type": None,
        "intent_source_class": "HUMAN_CLARIFIED_INTENT",
        "source_normalized_for_cognition": False,
        "intent_source_visible_to_cognition": False,
        "normalized_intent": None,
        "normalized_intent_class": None,
        "selected_interpretation": None,
        "domain_id": evidence["domain_id"],
        "worker_family_id": None,
        "milestone_type": None,
        "capability_id": None,
        "resource_category": None,
        "confidence": evidence["confidence"],
        "classification_status": FAILED_CLOSED,
        "cognition_invoked": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": created_at,
        "replay_visible": True,
        "failure_reason": evidence["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_clarified_input_artifact(
    *,
    integration_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CLARIFIED_COGNITION_INPUT_ARTIFACT_V1,
        "runtime_version": AIGOL_INTENT_CLARIFICATION_COGNITION_INTEGRATION_VERSION,
        "clarified_cognition_input_id": f"{integration_id}:CLARIFIED-COGNITION-INPUT"
        if isinstance(integration_id, str)
        else "INVALID:CLARIFIED-COGNITION-INPUT",
        "integration_id": integration_id if isinstance(integration_id, str) else "INVALID",
        "integration_status": FAILED_CLOSED,
        "canonical_chain_id": evidence["canonical_chain_id"],
        "cognition_input_type": None,
        "normalized_intent": None,
        "normalized_intent_class": None,
        "domain_id": evidence["domain_id"],
        "worker_family_id": None,
        "milestone_type": None,
        "capability_id": None,
        "resource_category": None,
        "confidence": evidence["confidence"],
        "selected_interpretation": classification["selected_interpretation"],
        "source_lineage_preserved": False,
        "intent_source": "HUMAN_CLARIFICATION",
        "intent_source_visible_to_cognition": False,
        "cognition_input_contract": None,
        "evidence_reference": evidence["integration_evidence_id"],
        "evidence_hash": evidence["artifact_hash"],
        "classification_reference": classification["classification_id"],
        "classification_hash": classification["artifact_hash"],
        "source_clarification_resolution_reference": evidence["clarification_resolution_reference"],
        "source_clarification_resolution_hash": evidence["clarification_resolution_hash"],
        "clarification_history": [],
        "clarification_history_hash": replay_hash([]),
        "human_review_required": True,
        "high_risk_domain": False,
        "cognition_invoked": False,
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "created_at": created_at,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(clarified_input: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(clarified_input, "clarified cognition input artifact")
    artifact = {
        "event_type": "CLARIFICATION_COGNITION_INTEGRATION_RETURNED",
        "clarified_cognition_input_reference": clarified_input["clarified_cognition_input_id"],
        "clarified_cognition_input_hash": clarified_input["artifact_hash"],
        "integration_status": clarified_input["integration_status"],
        "canonical_chain_id": clarified_input["canonical_chain_id"],
        "cognition_input_type": clarified_input["cognition_input_type"],
        "intent_source_visible_to_cognition": clarified_input["intent_source_visible_to_cognition"],
        "cognition_invoked": False,
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": clarified_input["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    evidence: dict[str, Any],
    classification: dict[str, Any],
    clarified_input: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "clarification_cognition_evidence_artifact": deepcopy(evidence),
        "clarification_cognition_classification_artifact": deepcopy(classification),
        "clarified_cognition_input_artifact": deepcopy(clarified_input),
        "clarification_cognition_integration_replay": deepcopy(returned),
        "clarification_cognition_integration_replay_reference": str(replay_path),
        "integration_status": clarified_input["integration_status"],
        "canonical_chain_id": clarified_input["canonical_chain_id"],
        "cognition_input_type": clarified_input["cognition_input_type"],
        "normalized_intent": clarified_input["normalized_intent"],
        "cognition_input_contract": deepcopy(clarified_input["cognition_input_contract"]),
        "clarification_history": deepcopy(clarified_input["clarification_history"]),
        "confidence": clarified_input["confidence"],
        "intent_source_visible_to_cognition": clarified_input["intent_source_visible_to_cognition"],
        "fail_closed": clarified_input["integration_status"] == FAILED_CLOSED,
        "failure_reason": clarified_input["failure_reason"],
        "cognition_invoked": False,
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["intent_clarification_cognition_integration_capture_hash"] = replay_hash(capture)
    return capture


def _normalized_intent(resolved: dict[str, Any]) -> str:
    pieces = [
        resolved.get("domain_id"),
        resolved.get("worker_family_id"),
        resolved.get("milestone_type"),
        resolved.get("capability_id"),
    ]
    return " ".join(piece for piece in pieces if isinstance(piece, str) and piece.strip())


def _normalized_intent_class(resolved: dict[str, Any]) -> str:
    if resolved.get("milestone_type"):
        return resolved["milestone_type"]
    if resolved.get("capability_id"):
        return resolved["capability_id"]
    return "CLARIFIED_INTENT"


def _normalize_confidence(value: Any) -> str:
    confidence = _require_string(value, "confidence").strip().upper().replace("-", "_").replace(" ", "_")
    if confidence not in {"LOW", "MEDIUM", "HIGH", "DETERMINISTIC"}:
        raise FailClosedRuntimeError("clarification cognition integration failed closed: confidence invalid")
    return confidence


def _validate_artifact(artifact: dict[str, Any], expected_type: str, label: str) -> None:
    if not isinstance(artifact, dict) or artifact.get("artifact_type") != expected_type:
        raise FailClosedRuntimeError(f"clarification cognition integration failed closed: {label} missing")
    _verify_artifact_hash(artifact, f"clarification cognition integration {label}")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"clarification cognition integration failed closed: {label} missing")
    return value


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("clarification cognition integration replay step ordering mismatch")
    _verify_artifact_hash(artifact, "clarification cognition integration artifact")
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
        raise FailClosedRuntimeError("clarification cognition integration replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("clarification cognition integration replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "clarification cognition integration failed closed"
