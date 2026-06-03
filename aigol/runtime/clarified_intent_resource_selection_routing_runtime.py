"""Route clarified human intent into Resource Selection-compatible input."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.intent_clarification_cognition_integration import (
    CLARIFICATION_COGNITION_CLASSIFICATION_V1,
    CLARIFICATION_COGNITION_EVIDENCE_V1,
    CLARIFIED_COGNITION_INPUT_ARTIFACT_V1,
    CLARIFIED_COGNITION_INPUT_CREATED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.unified_resource_selection_runtime import PROVIDER_ROLE


AIGOL_CLARIFIED_INTENT_RESOURCE_SELECTION_ROUTING_VERSION = (
    "AIGOL_CLARIFIED_INTENT_RESOURCE_SELECTION_ROUTING_V1"
)
CLARIFIED_RESOURCE_SELECTION_ROUTED_INTENT_V1 = "CLARIFIED_RESOURCE_SELECTION_ROUTED_INTENT_V1"
CLARIFIED_RESOURCE_SELECTION_ROUTING_EVIDENCE_V1 = "CLARIFIED_RESOURCE_SELECTION_ROUTING_EVIDENCE_V1"
CLARIFIED_RESOURCE_SELECTION_ROUTING_CLASSIFICATION_V1 = (
    "CLARIFIED_RESOURCE_SELECTION_ROUTING_CLASSIFICATION_V1"
)
CLARIFIED_RESOURCE_SELECTION_INTENT_ROUTED = "CLARIFIED_RESOURCE_SELECTION_INTENT_ROUTED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "clarified_resource_selection_routing_evidence_recorded",
    "clarified_resource_selection_routing_classification_recorded",
    "clarified_resource_selection_routed_intent_recorded",
    "clarified_resource_selection_routing_returned",
)

CONFIDENCE_RANK = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "DETERMINISTIC": 4}

CAPABILITY_BY_INTENT_CLASS = {
    "WORKER_FOUNDATION": "PROPOSAL_GENERATION",
    "WORKER_RUNTIME": "PROPOSAL_GENERATION",
    "WORKER_CERTIFICATION": "PROPOSAL_GENERATION",
    "WORKER_ACCEPTANCE": "PROPOSAL_GENERATION",
    "DOMAIN_FOUNDATION": "PROPOSAL_GENERATION",
    "DOMAIN_MODEL": "PROPOSAL_GENERATION",
    "PORTAL_FOUNDATION": "PROPOSAL_GENERATION",
    "GOVERNANCE_REVIEW": "PROPOSAL_GENERATION",
    "CLARIFIED_INTENT": "PROPOSAL_GENERATION",
}


def route_clarified_intent_to_resource_selection(
    *,
    routing_id: str,
    clarified_cognition_input_artifact: dict[str, Any],
    clarification_cognition_evidence_artifact: dict[str, Any],
    clarification_cognition_classification_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    requested_role_type: str = PROVIDER_ROLE,
    provider_necessity_classification: str = "PROVIDER_REQUIRED",
    confidence_threshold: str = "HIGH",
) -> dict[str, Any]:
    """Create Resource Selection input from clarified cognition input without selecting a resource."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        clarified = deepcopy(clarified_cognition_input_artifact)
        evidence = deepcopy(clarification_cognition_evidence_artifact)
        classification = deepcopy(clarification_cognition_classification_artifact)
        _validate_inputs(
            clarified=clarified,
            evidence=evidence,
            classification=classification,
            confidence_threshold=confidence_threshold,
        )
        routing_evidence = _routing_evidence_artifact(
            routing_id=routing_id,
            clarified=clarified,
            evidence=evidence,
            classification=classification,
            created_at=created_at,
            evidence_status="CLARIFIED_RESOURCE_SELECTION_ROUTING_EVIDENCE_ACCEPTED",
            failure_reason=None,
        )
        routing_classification = _routing_classification_artifact(
            routing_id=routing_id,
            routing_evidence=routing_evidence,
            clarified=clarified,
            requested_role_type=requested_role_type,
            provider_necessity_classification=provider_necessity_classification,
            created_at=created_at,
            classification_status="CLARIFIED_RESOURCE_SELECTION_ROUTING_CLASSIFIED",
            failure_reason=None,
        )
        routed = _routed_intent_artifact(
            routing_id=routing_id,
            routing_evidence=routing_evidence,
            routing_classification=routing_classification,
            clarified=clarified,
            created_at=created_at,
            routing_status=CLARIFIED_RESOURCE_SELECTION_INTENT_ROUTED,
            failure_reason=None,
        )
        returned = _returned_artifact(routed)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], routing_evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], routing_classification)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], routed)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(routing_evidence, routing_classification, routed, returned, replay_path)
    except Exception as exc:
        routing_evidence = _failed_routing_evidence_artifact(
            routing_id=routing_id,
            clarified_cognition_input_artifact=clarified_cognition_input_artifact,
            clarification_cognition_evidence_artifact=clarification_cognition_evidence_artifact,
            clarification_cognition_classification_artifact=clarification_cognition_classification_artifact,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        routing_classification = _failed_routing_classification_artifact(
            routing_id=routing_id,
            routing_evidence=routing_evidence,
            created_at=created_at,
        )
        routed = _failed_routed_intent_artifact(
            routing_id=routing_id,
            routing_evidence=routing_evidence,
            routing_classification=routing_classification,
            created_at=created_at,
            failure_reason=routing_evidence["failure_reason"],
        )
        returned = _returned_artifact(routed)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], routing_evidence)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], routing_classification)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], routed)
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(routing_evidence, routing_classification, routed, returned, replay_path)


def reconstruct_clarified_intent_resource_selection_routing_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct clarified intent Resource Selection routing replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("clarified Resource Selection routing replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("clarified Resource Selection routing replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "clarified Resource Selection routing artifact")
        wrappers.append(wrapper)
    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    routed = wrappers[2]["artifact"]
    returned = wrappers[3]["artifact"]
    if classification.get("routing_evidence_reference") != evidence["routing_evidence_id"]:
        raise FailClosedRuntimeError("clarified Resource Selection routing evidence reference mismatch")
    if classification.get("routing_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("clarified Resource Selection routing evidence hash mismatch")
    if routed.get("routing_classification_reference") != classification["routing_classification_id"]:
        raise FailClosedRuntimeError("clarified Resource Selection routing classification reference mismatch")
    if routed.get("routing_classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("clarified Resource Selection routing classification hash mismatch")
    if returned.get("clarified_resource_selection_routed_intent_reference") != routed[
        "clarified_resource_selection_routed_intent_id"
    ]:
        raise FailClosedRuntimeError("clarified Resource Selection routing returned reference mismatch")
    if returned.get("clarified_resource_selection_routed_intent_hash") != routed["artifact_hash"]:
        raise FailClosedRuntimeError("clarified Resource Selection routing returned hash mismatch")
    contract = routed["resource_selection_input_contract"]
    return {
        "clarified_resource_selection_routed_intent_id": routed[
            "clarified_resource_selection_routed_intent_id"
        ],
        "routing_status": routed["routing_status"],
        "canonical_chain_id": routed["canonical_chain_id"],
        "workflow_type": contract["workflow_type"] if contract else None,
        "required_capability": contract["required_capability"] if contract else None,
        "requested_role_type": contract["requested_role_type"] if contract else None,
        "domain_id": contract["domain_id"] if contract else None,
        "selected_interpretation": routed["selected_interpretation"],
        "intent_source_visible_to_resource_selection": routed["intent_source_visible_to_resource_selection"],
        "source_lineage_preserved": routed["source_lineage_preserved"],
        "failure_reason": routed["failure_reason"],
        "resource_selection_invoked": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_inputs(
    *,
    clarified: dict[str, Any],
    evidence: dict[str, Any],
    classification: dict[str, Any],
    confidence_threshold: str,
) -> None:
    _validate_artifact(clarified, CLARIFIED_COGNITION_INPUT_ARTIFACT_V1, "clarified cognition input")
    _validate_artifact(evidence, CLARIFICATION_COGNITION_EVIDENCE_V1, "clarification cognition evidence")
    _validate_artifact(
        classification,
        CLARIFICATION_COGNITION_CLASSIFICATION_V1,
        "clarification cognition classification",
    )
    if clarified.get("integration_status") != CLARIFIED_COGNITION_INPUT_CREATED:
        reason = str(clarified.get("failure_reason") or "")
        if "clarification unresolved" in reason:
            raise FailClosedRuntimeError("clarified Resource Selection routing failed closed: clarification unresolved")
        raise FailClosedRuntimeError("clarified Resource Selection routing failed closed: cognition integration invalid")
    if clarified.get("intent_source_visible_to_cognition") is not False:
        raise FailClosedRuntimeError("clarified Resource Selection routing failed closed: replay corruption")
    contract = clarified.get("cognition_input_contract")
    if not isinstance(contract, dict):
        raise FailClosedRuntimeError("clarified Resource Selection routing failed closed: cognition integration invalid")
    if contract.get("intent_source_visible_to_cognition") is not False:
        raise FailClosedRuntimeError("clarified Resource Selection routing failed closed: replay corruption")
    if clarified.get("evidence_reference") != evidence.get("integration_evidence_id"):
        raise FailClosedRuntimeError("clarified Resource Selection routing failed closed: replay corruption")
    if clarified.get("evidence_hash") != evidence.get("artifact_hash"):
        raise FailClosedRuntimeError("clarified Resource Selection routing failed closed: replay corruption")
    if clarified.get("classification_reference") != classification.get("classification_id"):
        raise FailClosedRuntimeError("clarified Resource Selection routing failed closed: replay corruption")
    if clarified.get("classification_hash") != classification.get("artifact_hash"):
        raise FailClosedRuntimeError("clarified Resource Selection routing failed closed: replay corruption")
    if classification.get("integration_evidence_reference") != evidence.get("integration_evidence_id"):
        raise FailClosedRuntimeError("clarified Resource Selection routing failed closed: replay corruption")
    if classification.get("integration_evidence_hash") != evidence.get("artifact_hash"):
        raise FailClosedRuntimeError("clarified Resource Selection routing failed closed: replay corruption")
    if clarified.get("canonical_chain_id") != evidence.get("canonical_chain_id"):
        raise FailClosedRuntimeError("clarified Resource Selection routing failed closed: invalid chain continuity")
    if clarified.get("canonical_chain_id") != classification.get("canonical_chain_id"):
        raise FailClosedRuntimeError("clarified Resource Selection routing failed closed: invalid chain continuity")
    selected = _require_string(clarified.get("selected_interpretation"), "selected_interpretation")
    if selected != classification.get("selected_interpretation") or selected in {"REJECT_ALL", "CANCEL", "ADDITIONAL_CLARIFICATION"}:
        raise FailClosedRuntimeError("clarified Resource Selection routing failed closed: ambiguous selected interpretation")
    if CONFIDENCE_RANK[_normalize_confidence(clarified.get("confidence"))] < CONFIDENCE_RANK[
        _normalize_confidence(confidence_threshold)
    ]:
        raise FailClosedRuntimeError("clarified Resource Selection routing failed closed: confidence insufficient")
    _require_string(clarified.get("normalized_intent"), "normalized_intent")
    _require_string(clarified.get("normalized_intent_class"), "normalized_intent_class")
    _require_string(clarified.get("domain_id"), "domain_id")


def _routing_evidence_artifact(
    *,
    routing_id: str,
    clarified: dict[str, Any],
    evidence: dict[str, Any],
    classification: dict[str, Any],
    created_at: str,
    evidence_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CLARIFIED_RESOURCE_SELECTION_ROUTING_EVIDENCE_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_RESOURCE_SELECTION_ROUTING_VERSION,
        "routing_evidence_id": f"{_require_string(routing_id, 'routing_id')}:CLARIFIED-RESOURCE-SELECTION-ROUTING-EVIDENCE",
        "routing_reference": routing_id,
        "canonical_chain_id": clarified["canonical_chain_id"],
        "clarified_cognition_input_reference": clarified["clarified_cognition_input_id"],
        "clarified_cognition_input_hash": clarified["artifact_hash"],
        "clarification_cognition_evidence_reference": evidence["integration_evidence_id"],
        "clarification_cognition_evidence_hash": evidence["artifact_hash"],
        "clarification_cognition_classification_reference": classification["classification_id"],
        "clarification_cognition_classification_hash": classification["artifact_hash"],
        "clarification_history": deepcopy(clarified["clarification_history"]),
        "clarification_history_hash": clarified["clarification_history_hash"],
        "selected_interpretation": clarified["selected_interpretation"],
        "source_lineage_preserved": True,
        "confidence": clarified["confidence"],
        "domain_id": clarified["domain_id"],
        "evidence_status": evidence_status,
        "resource_selection_invoked": False,
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


def _routing_classification_artifact(
    *,
    routing_id: str,
    routing_evidence: dict[str, Any],
    clarified: dict[str, Any],
    requested_role_type: str,
    provider_necessity_classification: str,
    created_at: str,
    classification_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    required_capability = _required_capability(clarified)
    artifact = {
        "artifact_type": CLARIFIED_RESOURCE_SELECTION_ROUTING_CLASSIFICATION_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_RESOURCE_SELECTION_ROUTING_VERSION,
        "routing_classification_id": f"{_require_string(routing_id, 'routing_id')}:CLARIFIED-RESOURCE-SELECTION-ROUTING-CLASSIFICATION",
        "routing_reference": routing_id,
        "routing_evidence_reference": routing_evidence["routing_evidence_id"],
        "routing_evidence_hash": routing_evidence["artifact_hash"],
        "canonical_chain_id": clarified["canonical_chain_id"],
        "resource_selection_input_type": "STRUCTURED_RESOURCE_SELECTION_REQUIREMENTS",
        "intent_source_class": "HUMAN_CLARIFIED_INTENT",
        "source_normalized_for_resource_selection": True,
        "intent_source_visible_to_resource_selection": False,
        "workflow_type": "NATIVE_DEVELOPMENT",
        "required_capability": required_capability,
        "requested_role_type": _require_string(requested_role_type, "requested_role_type"),
        "domain_id": clarified["domain_id"],
        "worker_family_id": clarified.get("worker_family_id"),
        "milestone_type": clarified.get("milestone_type"),
        "provider_necessity_classification": _require_string(
            provider_necessity_classification,
            "provider_necessity_classification",
        ),
        "normalized_intent": clarified["normalized_intent"],
        "normalized_intent_class": clarified["normalized_intent_class"],
        "selected_interpretation": clarified["selected_interpretation"],
        "confidence": clarified["confidence"],
        "classification_status": classification_status,
        "resource_selection_invoked": False,
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


def _routed_intent_artifact(
    *,
    routing_id: str,
    routing_evidence: dict[str, Any],
    routing_classification: dict[str, Any],
    clarified: dict[str, Any],
    created_at: str,
    routing_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    contract = {
        "intent_reference": f"{routing_id}:CLARIFIED-RESOURCE-SELECTION-ROUTED-INTENT",
        "workflow_type": routing_classification["workflow_type"],
        "required_capability": routing_classification["required_capability"],
        "requested_role_type": routing_classification["requested_role_type"],
        "domain_id": routing_classification["domain_id"],
        "worker_family_id": routing_classification["worker_family_id"],
        "milestone_type": routing_classification["milestone_type"],
        "provider_necessity_classification": routing_classification["provider_necessity_classification"],
        "confidence": routing_classification["confidence"],
        "intent_source_visible_to_resource_selection": False,
    }
    artifact = {
        "artifact_type": CLARIFIED_RESOURCE_SELECTION_ROUTED_INTENT_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_RESOURCE_SELECTION_ROUTING_VERSION,
        "clarified_resource_selection_routed_intent_id": f"{_require_string(routing_id, 'routing_id')}:CLARIFIED-RESOURCE-SELECTION-ROUTED-INTENT",
        "routing_id": routing_id,
        "routing_status": routing_status,
        "canonical_chain_id": clarified["canonical_chain_id"],
        "resource_selection_input_type": routing_classification["resource_selection_input_type"],
        "normalized_intent": routing_classification["normalized_intent"],
        "normalized_intent_class": routing_classification["normalized_intent_class"],
        "confidence": routing_classification["confidence"],
        "selected_interpretation": routing_classification["selected_interpretation"],
        "clarification_history": deepcopy(clarified["clarification_history"]),
        "clarification_history_hash": clarified["clarification_history_hash"],
        "source_lineage_preserved": True,
        "intent_source": "HUMAN_CLARIFICATION",
        "intent_source_visible_to_resource_selection": False,
        "resource_selection_input_contract": contract,
        "routing_evidence_reference": routing_evidence["routing_evidence_id"],
        "routing_evidence_hash": routing_evidence["artifact_hash"],
        "routing_classification_reference": routing_classification["routing_classification_id"],
        "routing_classification_hash": routing_classification["artifact_hash"],
        "source_clarified_cognition_input_reference": clarified["clarified_cognition_input_id"],
        "source_clarified_cognition_input_hash": clarified["artifact_hash"],
        "resource_selection_invoked": False,
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


def _failed_routing_evidence_artifact(
    *,
    routing_id: str,
    clarified_cognition_input_artifact: dict[str, Any],
    clarification_cognition_evidence_artifact: dict[str, Any],
    clarification_cognition_classification_artifact: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    clarified = clarified_cognition_input_artifact if isinstance(clarified_cognition_input_artifact, dict) else {}
    evidence = clarification_cognition_evidence_artifact if isinstance(clarification_cognition_evidence_artifact, dict) else {}
    classification = (
        clarification_cognition_classification_artifact
        if isinstance(clarification_cognition_classification_artifact, dict)
        else {}
    )
    artifact = {
        "artifact_type": CLARIFIED_RESOURCE_SELECTION_ROUTING_EVIDENCE_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_RESOURCE_SELECTION_ROUTING_VERSION,
        "routing_evidence_id": f"{routing_id}:CLARIFIED-RESOURCE-SELECTION-ROUTING-EVIDENCE"
        if isinstance(routing_id, str)
        else "INVALID:CLARIFIED-RESOURCE-SELECTION-ROUTING-EVIDENCE",
        "routing_reference": routing_id if isinstance(routing_id, str) else "INVALID",
        "canonical_chain_id": clarified.get("canonical_chain_id"),
        "clarified_cognition_input_reference": clarified.get("clarified_cognition_input_id"),
        "clarified_cognition_input_hash": clarified.get("artifact_hash"),
        "clarification_cognition_evidence_reference": evidence.get("integration_evidence_id"),
        "clarification_cognition_evidence_hash": evidence.get("artifact_hash"),
        "clarification_cognition_classification_reference": classification.get("classification_id"),
        "clarification_cognition_classification_hash": classification.get("artifact_hash"),
        "clarification_history": [],
        "clarification_history_hash": replay_hash([]),
        "selected_interpretation": clarified.get("selected_interpretation"),
        "source_lineage_preserved": False,
        "confidence": clarified.get("confidence"),
        "domain_id": clarified.get("domain_id"),
        "evidence_status": FAILED_CLOSED,
        "resource_selection_invoked": False,
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


def _failed_routing_classification_artifact(
    *,
    routing_id: str,
    routing_evidence: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CLARIFIED_RESOURCE_SELECTION_ROUTING_CLASSIFICATION_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_RESOURCE_SELECTION_ROUTING_VERSION,
        "routing_classification_id": f"{routing_id}:CLARIFIED-RESOURCE-SELECTION-ROUTING-CLASSIFICATION"
        if isinstance(routing_id, str)
        else "INVALID:CLARIFIED-RESOURCE-SELECTION-ROUTING-CLASSIFICATION",
        "routing_reference": routing_id if isinstance(routing_id, str) else "INVALID",
        "routing_evidence_reference": routing_evidence["routing_evidence_id"],
        "routing_evidence_hash": routing_evidence["artifact_hash"],
        "canonical_chain_id": routing_evidence["canonical_chain_id"],
        "resource_selection_input_type": None,
        "intent_source_class": "HUMAN_CLARIFIED_INTENT",
        "source_normalized_for_resource_selection": False,
        "intent_source_visible_to_resource_selection": False,
        "workflow_type": None,
        "required_capability": None,
        "requested_role_type": None,
        "domain_id": routing_evidence["domain_id"],
        "worker_family_id": None,
        "milestone_type": None,
        "provider_necessity_classification": None,
        "normalized_intent": None,
        "normalized_intent_class": None,
        "selected_interpretation": routing_evidence["selected_interpretation"],
        "confidence": routing_evidence["confidence"],
        "classification_status": FAILED_CLOSED,
        "resource_selection_invoked": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": created_at,
        "replay_visible": True,
        "failure_reason": routing_evidence["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_routed_intent_artifact(
    *,
    routing_id: str,
    routing_evidence: dict[str, Any],
    routing_classification: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CLARIFIED_RESOURCE_SELECTION_ROUTED_INTENT_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_RESOURCE_SELECTION_ROUTING_VERSION,
        "clarified_resource_selection_routed_intent_id": f"{routing_id}:CLARIFIED-RESOURCE-SELECTION-ROUTED-INTENT"
        if isinstance(routing_id, str)
        else "INVALID:CLARIFIED-RESOURCE-SELECTION-ROUTED-INTENT",
        "routing_id": routing_id if isinstance(routing_id, str) else "INVALID",
        "routing_status": FAILED_CLOSED,
        "canonical_chain_id": routing_evidence["canonical_chain_id"],
        "resource_selection_input_type": None,
        "normalized_intent": None,
        "normalized_intent_class": None,
        "confidence": routing_evidence["confidence"],
        "selected_interpretation": routing_evidence["selected_interpretation"],
        "clarification_history": [],
        "clarification_history_hash": replay_hash([]),
        "source_lineage_preserved": False,
        "intent_source": "HUMAN_CLARIFICATION",
        "intent_source_visible_to_resource_selection": False,
        "resource_selection_input_contract": None,
        "routing_evidence_reference": routing_evidence["routing_evidence_id"],
        "routing_evidence_hash": routing_evidence["artifact_hash"],
        "routing_classification_reference": routing_classification["routing_classification_id"],
        "routing_classification_hash": routing_classification["artifact_hash"],
        "source_clarified_cognition_input_reference": routing_evidence["clarified_cognition_input_reference"],
        "source_clarified_cognition_input_hash": routing_evidence["clarified_cognition_input_hash"],
        "resource_selection_invoked": False,
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


def _returned_artifact(routed: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(routed, "clarified Resource Selection routing artifact")
    artifact = {
        "event_type": "CLARIFIED_RESOURCE_SELECTION_ROUTING_RETURNED",
        "clarified_resource_selection_routed_intent_reference": routed[
            "clarified_resource_selection_routed_intent_id"
        ],
        "clarified_resource_selection_routed_intent_hash": routed["artifact_hash"],
        "routing_status": routed["routing_status"],
        "canonical_chain_id": routed["canonical_chain_id"],
        "resource_selection_input_type": routed["resource_selection_input_type"],
        "resource_selection_input_contract": deepcopy(routed["resource_selection_input_contract"]),
        "intent_source_visible_to_resource_selection": routed["intent_source_visible_to_resource_selection"],
        "resource_selection_invoked": False,
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": routed["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    evidence: dict[str, Any],
    classification: dict[str, Any],
    routed: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "clarified_resource_selection_routing_evidence_artifact": deepcopy(evidence),
        "clarified_resource_selection_routing_classification_artifact": deepcopy(classification),
        "clarified_resource_selection_routed_intent_artifact": deepcopy(routed),
        "clarified_resource_selection_routing_replay": deepcopy(returned),
        "clarified_resource_selection_routing_replay_reference": str(replay_path),
        "routing_status": routed["routing_status"],
        "canonical_chain_id": routed["canonical_chain_id"],
        "resource_selection_input_type": routed["resource_selection_input_type"],
        "resource_selection_input_contract": deepcopy(routed["resource_selection_input_contract"]),
        "selected_interpretation": routed["selected_interpretation"],
        "clarification_history": deepcopy(routed["clarification_history"]),
        "intent_source_visible_to_resource_selection": routed["intent_source_visible_to_resource_selection"],
        "source_lineage_preserved": routed["source_lineage_preserved"],
        "fail_closed": routed["routing_status"] == FAILED_CLOSED,
        "failure_reason": routed["failure_reason"],
        "resource_selection_invoked": False,
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["clarified_intent_resource_selection_routing_capture_hash"] = replay_hash(capture)
    return capture


def _required_capability(clarified: dict[str, Any]) -> str:
    key = _require_string(clarified.get("normalized_intent_class"), "normalized_intent_class").strip().upper()
    if key in CAPABILITY_BY_INTENT_CLASS:
        return CAPABILITY_BY_INTENT_CLASS[key]
    capability = clarified.get("capability_id")
    if isinstance(capability, str) and capability.strip().upper() in {"PROPOSAL_GENERATION", "PROPOSAL_REPAIR"}:
        return capability.strip().upper()
    raise FailClosedRuntimeError("clarified Resource Selection routing failed closed: ambiguous selected interpretation")


def _normalize_confidence(value: Any) -> str:
    confidence = _require_string(value, "confidence").strip().upper().replace("-", "_").replace(" ", "_")
    if confidence not in CONFIDENCE_RANK:
        raise FailClosedRuntimeError("clarified Resource Selection routing failed closed: confidence insufficient")
    return confidence


def _validate_artifact(artifact: dict[str, Any], expected_type: str, label: str) -> None:
    if not isinstance(artifact, dict) or artifact.get("artifact_type") != expected_type:
        raise FailClosedRuntimeError(f"clarified Resource Selection routing failed closed: {label} missing")
    _verify_artifact_hash(artifact, f"clarified Resource Selection routing {label}")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"clarified Resource Selection routing failed closed: {label} missing")
    return value


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("clarified Resource Selection routing replay step ordering mismatch")
    _verify_artifact_hash(artifact, "clarified Resource Selection routing artifact")
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
        raise FailClosedRuntimeError("clarified Resource Selection routing replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("clarified Resource Selection routing replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "clarified Resource Selection routing failed closed"
