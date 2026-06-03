"""Route clarified Resource Selection intent into PPP-compatible input."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.clarified_intent_resource_selection_routing_runtime import (
    CLARIFIED_RESOURCE_SELECTION_INTENT_ROUTED,
    CLARIFIED_RESOURCE_SELECTION_ROUTED_INTENT_V1,
    CLARIFIED_RESOURCE_SELECTION_ROUTING_CLASSIFICATION_V1,
    CLARIFIED_RESOURCE_SELECTION_ROUTING_EVIDENCE_V1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_CLARIFIED_INTENT_RESOURCE_SELECTION_PPP_INTEGRATION_VERSION = (
    "AIGOL_CLARIFIED_INTENT_RESOURCE_SELECTION_PPP_INTEGRATION_V1"
)
CLARIFIED_PPP_ROUTED_INTENT_ARTIFACT_V1 = "CLARIFIED_PPP_ROUTED_INTENT_ARTIFACT_V1"
CLARIFIED_PPP_ROUTING_EVIDENCE_V1 = "CLARIFIED_PPP_ROUTING_EVIDENCE_V1"
CLARIFIED_PPP_ROUTING_CLASSIFICATION_V1 = "CLARIFIED_PPP_ROUTING_CLASSIFICATION_V1"
CLARIFIED_PPP_INTENT_ROUTED = "CLARIFIED_PPP_INTENT_ROUTED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "clarified_ppp_routing_evidence_recorded",
    "clarified_ppp_routing_classification_recorded",
    "clarified_ppp_routed_intent_recorded",
    "clarified_ppp_routing_returned",
)


def route_clarified_resource_selection_intent_to_ppp(
    *,
    routing_id: str,
    clarified_resource_selection_routed_intent_artifact: dict[str, Any],
    clarified_resource_selection_routing_evidence_artifact: dict[str, Any],
    clarified_resource_selection_routing_classification_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    ppp_stage: str = "PROPOSAL_PRODUCTION",
) -> dict[str, Any]:
    """Create source-agnostic PPP input without invoking PPP."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        routed = deepcopy(clarified_resource_selection_routed_intent_artifact)
        evidence = deepcopy(clarified_resource_selection_routing_evidence_artifact)
        classification = deepcopy(clarified_resource_selection_routing_classification_artifact)
        _validate_inputs(routed=routed, evidence=evidence, classification=classification)
        ppp_evidence = _ppp_routing_evidence_artifact(
            routing_id=routing_id,
            routed=routed,
            evidence=evidence,
            classification=classification,
            created_at=created_at,
            evidence_status="CLARIFIED_PPP_ROUTING_EVIDENCE_ACCEPTED",
            failure_reason=None,
        )
        ppp_classification = _ppp_routing_classification_artifact(
            routing_id=routing_id,
            ppp_evidence=ppp_evidence,
            routed=routed,
            ppp_stage=ppp_stage,
            created_at=created_at,
            classification_status="CLARIFIED_PPP_ROUTING_CLASSIFIED",
            failure_reason=None,
        )
        ppp_routed = _ppp_routed_intent_artifact(
            routing_id=routing_id,
            ppp_evidence=ppp_evidence,
            ppp_classification=ppp_classification,
            routed=routed,
            created_at=created_at,
            routing_status=CLARIFIED_PPP_INTENT_ROUTED,
            failure_reason=None,
        )
        returned = _returned_artifact(ppp_routed)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], ppp_evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], ppp_classification)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], ppp_routed)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(ppp_evidence, ppp_classification, ppp_routed, returned, replay_path)
    except Exception as exc:
        ppp_evidence = _failed_ppp_routing_evidence_artifact(
            routing_id=routing_id,
            clarified_resource_selection_routed_intent_artifact=clarified_resource_selection_routed_intent_artifact,
            clarified_resource_selection_routing_evidence_artifact=clarified_resource_selection_routing_evidence_artifact,
            clarified_resource_selection_routing_classification_artifact=clarified_resource_selection_routing_classification_artifact,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        ppp_classification = _failed_ppp_routing_classification_artifact(
            routing_id=routing_id,
            ppp_evidence=ppp_evidence,
            created_at=created_at,
        )
        ppp_routed = _failed_ppp_routed_intent_artifact(
            routing_id=routing_id,
            ppp_evidence=ppp_evidence,
            ppp_classification=ppp_classification,
            created_at=created_at,
            failure_reason=ppp_evidence["failure_reason"],
        )
        returned = _returned_artifact(ppp_routed)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], ppp_evidence)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], ppp_classification)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], ppp_routed)
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(ppp_evidence, ppp_classification, ppp_routed, returned, replay_path)


def reconstruct_clarified_intent_resource_selection_ppp_integration_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct clarified intent PPP integration replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("clarified PPP routing replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("clarified PPP routing replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "clarified PPP routing artifact")
        wrappers.append(wrapper)
    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    routed = wrappers[2]["artifact"]
    returned = wrappers[3]["artifact"]
    if classification.get("routing_evidence_reference") != evidence["routing_evidence_id"]:
        raise FailClosedRuntimeError("clarified PPP routing evidence reference mismatch")
    if classification.get("routing_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("clarified PPP routing evidence hash mismatch")
    if routed.get("routing_classification_reference") != classification["routing_classification_id"]:
        raise FailClosedRuntimeError("clarified PPP routing classification reference mismatch")
    if routed.get("routing_classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("clarified PPP routing classification hash mismatch")
    if returned.get("clarified_ppp_routed_intent_reference") != routed["clarified_ppp_routed_intent_id"]:
        raise FailClosedRuntimeError("clarified PPP routing returned reference mismatch")
    if returned.get("clarified_ppp_routed_intent_hash") != routed["artifact_hash"]:
        raise FailClosedRuntimeError("clarified PPP routing returned hash mismatch")
    contract = routed["ppp_input_contract"]
    return {
        "clarified_ppp_routed_intent_id": routed["clarified_ppp_routed_intent_id"],
        "routing_status": routed["routing_status"],
        "canonical_chain_id": routed["canonical_chain_id"],
        "ppp_input_type": routed["ppp_input_type"],
        "ppp_stage": contract["ppp_stage"] if contract else None,
        "workflow_type": contract["workflow_type"] if contract else None,
        "required_capability": contract["required_capability"] if contract else None,
        "requested_role_type": contract["requested_role_type"] if contract else None,
        "domain_id": contract["domain_id"] if contract else None,
        "selected_interpretation": routed["selected_interpretation"],
        "intent_source_visible_to_ppp": routed["intent_source_visible_to_ppp"],
        "source_lineage_preserved": routed["source_lineage_preserved"],
        "failure_reason": routed["failure_reason"],
        "ppp_proposal_production_invoked": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_inputs(*, routed: dict[str, Any], evidence: dict[str, Any], classification: dict[str, Any]) -> None:
    _validate_artifact(
        routed,
        CLARIFIED_RESOURCE_SELECTION_ROUTED_INTENT_V1,
        "clarified Resource Selection routed intent",
    )
    _validate_artifact(
        evidence,
        CLARIFIED_RESOURCE_SELECTION_ROUTING_EVIDENCE_V1,
        "clarified Resource Selection routing evidence",
    )
    _validate_artifact(
        classification,
        CLARIFIED_RESOURCE_SELECTION_ROUTING_CLASSIFICATION_V1,
        "clarified Resource Selection routing classification",
    )
    if routed.get("routing_status") != CLARIFIED_RESOURCE_SELECTION_INTENT_ROUTED:
        reason = str(routed.get("failure_reason") or "")
        if "clarification unresolved" in reason:
            raise FailClosedRuntimeError("clarified PPP routing failed closed: unresolved clarification")
        raise FailClosedRuntimeError("clarified PPP routing failed closed: invalid resource-selection lineage")
    if routed.get("intent_source_visible_to_resource_selection") is not False:
        raise FailClosedRuntimeError("clarified PPP routing failed closed: replay corruption")
    if routed.get("source_lineage_preserved") is not True:
        raise FailClosedRuntimeError("clarified PPP routing failed closed: invalid cognition lineage")
    contract = routed.get("resource_selection_input_contract")
    if not isinstance(contract, dict):
        raise FailClosedRuntimeError("clarified PPP routing failed closed: invalid resource-selection lineage")
    if contract.get("intent_source_visible_to_resource_selection") is not False:
        raise FailClosedRuntimeError("clarified PPP routing failed closed: replay corruption")
    if routed.get("routing_evidence_reference") != evidence.get("routing_evidence_id"):
        raise FailClosedRuntimeError("clarified PPP routing failed closed: invalid resource-selection lineage")
    if routed.get("routing_evidence_hash") != evidence.get("artifact_hash"):
        raise FailClosedRuntimeError("clarified PPP routing failed closed: invalid resource-selection lineage")
    if routed.get("routing_classification_reference") != classification.get("routing_classification_id"):
        raise FailClosedRuntimeError("clarified PPP routing failed closed: invalid resource-selection lineage")
    if routed.get("routing_classification_hash") != classification.get("artifact_hash"):
        raise FailClosedRuntimeError("clarified PPP routing failed closed: invalid resource-selection lineage")
    if classification.get("routing_evidence_reference") != evidence.get("routing_evidence_id"):
        raise FailClosedRuntimeError("clarified PPP routing failed closed: invalid resource-selection lineage")
    if classification.get("routing_evidence_hash") != evidence.get("artifact_hash"):
        raise FailClosedRuntimeError("clarified PPP routing failed closed: invalid resource-selection lineage")
    if routed.get("canonical_chain_id") != evidence.get("canonical_chain_id"):
        raise FailClosedRuntimeError("clarified PPP routing failed closed: broken chain continuity")
    if routed.get("canonical_chain_id") != classification.get("canonical_chain_id"):
        raise FailClosedRuntimeError("clarified PPP routing failed closed: broken chain continuity")
    selected = _require_string(routed.get("selected_interpretation"), "selected_interpretation")
    if selected != evidence.get("selected_interpretation") or selected != classification.get("selected_interpretation"):
        raise FailClosedRuntimeError("clarified PPP routing failed closed: invalid cognition lineage")
    if not isinstance(routed.get("clarification_history"), list):
        raise FailClosedRuntimeError("clarified PPP routing failed closed: invalid cognition lineage")
    if routed.get("clarification_history_hash") != replay_hash(routed["clarification_history"]):
        raise FailClosedRuntimeError("clarified PPP routing failed closed: replay corruption")
    _require_string(contract.get("intent_reference"), "intent_reference")
    _require_string(contract.get("workflow_type"), "workflow_type")
    _require_string(contract.get("required_capability"), "required_capability")
    _require_string(contract.get("requested_role_type"), "requested_role_type")
    _require_string(contract.get("domain_id"), "domain_id")
    _require_string(contract.get("provider_necessity_classification"), "provider_necessity_classification")
    _require_string(contract.get("confidence"), "confidence")


def _ppp_routing_evidence_artifact(
    *,
    routing_id: str,
    routed: dict[str, Any],
    evidence: dict[str, Any],
    classification: dict[str, Any],
    created_at: str,
    evidence_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    contract = routed["resource_selection_input_contract"]
    artifact = {
        "artifact_type": CLARIFIED_PPP_ROUTING_EVIDENCE_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_RESOURCE_SELECTION_PPP_INTEGRATION_VERSION,
        "routing_evidence_id": f"{_require_string(routing_id, 'routing_id')}:CLARIFIED-PPP-ROUTING-EVIDENCE",
        "routing_reference": routing_id,
        "canonical_chain_id": routed["canonical_chain_id"],
        "clarified_resource_selection_routed_intent_reference": routed[
            "clarified_resource_selection_routed_intent_id"
        ],
        "clarified_resource_selection_routed_intent_hash": routed["artifact_hash"],
        "clarified_resource_selection_routing_evidence_reference": evidence["routing_evidence_id"],
        "clarified_resource_selection_routing_evidence_hash": evidence["artifact_hash"],
        "clarified_resource_selection_routing_classification_reference": classification[
            "routing_classification_id"
        ],
        "clarified_resource_selection_routing_classification_hash": classification["artifact_hash"],
        "resource_selection_input_reference": contract["intent_reference"],
        "resource_selection_input_hash": replay_hash(contract),
        "clarification_history": deepcopy(routed["clarification_history"]),
        "clarification_history_hash": routed["clarification_history_hash"],
        "selected_interpretation": routed["selected_interpretation"],
        "source_lineage_preserved": True,
        "confidence": contract["confidence"],
        "domain_id": contract["domain_id"],
        "evidence_status": evidence_status,
        "ppp_proposal_production_invoked": False,
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


def _ppp_routing_classification_artifact(
    *,
    routing_id: str,
    ppp_evidence: dict[str, Any],
    routed: dict[str, Any],
    ppp_stage: str,
    created_at: str,
    classification_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    contract = routed["resource_selection_input_contract"]
    artifact = {
        "artifact_type": CLARIFIED_PPP_ROUTING_CLASSIFICATION_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_RESOURCE_SELECTION_PPP_INTEGRATION_VERSION,
        "routing_classification_id": f"{_require_string(routing_id, 'routing_id')}:CLARIFIED-PPP-ROUTING-CLASSIFICATION",
        "routing_reference": routing_id,
        "routing_evidence_reference": ppp_evidence["routing_evidence_id"],
        "routing_evidence_hash": ppp_evidence["artifact_hash"],
        "canonical_chain_id": routed["canonical_chain_id"],
        "ppp_input_type": "STRUCTURED_PPP_INTENT",
        "ppp_stage": _require_string(ppp_stage, "ppp_stage"),
        "intent_source_class": "HUMAN_CLARIFIED_INTENT",
        "source_normalized_for_ppp": True,
        "intent_source_visible_to_ppp": False,
        "workflow_type": contract["workflow_type"],
        "required_capability": contract["required_capability"],
        "requested_role_type": contract["requested_role_type"],
        "domain_id": contract["domain_id"],
        "worker_family_id": contract.get("worker_family_id"),
        "milestone_type": contract.get("milestone_type"),
        "provider_necessity_classification": contract["provider_necessity_classification"],
        "normalized_intent": routed["normalized_intent"],
        "normalized_intent_class": routed["normalized_intent_class"],
        "selected_interpretation": routed["selected_interpretation"],
        "confidence": contract["confidence"],
        "classification_status": classification_status,
        "ppp_proposal_production_invoked": False,
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


def _ppp_routed_intent_artifact(
    *,
    routing_id: str,
    ppp_evidence: dict[str, Any],
    ppp_classification: dict[str, Any],
    routed: dict[str, Any],
    created_at: str,
    routing_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    source_contract = routed["resource_selection_input_contract"]
    ppp_contract = {
        "intent_reference": f"{routing_id}:CLARIFIED-PPP-ROUTED-INTENT",
        "workflow_type": ppp_classification["workflow_type"],
        "required_capability": ppp_classification["required_capability"],
        "requested_role_type": ppp_classification["requested_role_type"],
        "domain_id": ppp_classification["domain_id"],
        "provider_necessity_classification": ppp_classification["provider_necessity_classification"],
        "confidence": ppp_classification["confidence"],
        "ppp_stage": ppp_classification["ppp_stage"],
        "intent_source_visible_to_ppp": False,
    }
    artifact = {
        "artifact_type": CLARIFIED_PPP_ROUTED_INTENT_ARTIFACT_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_RESOURCE_SELECTION_PPP_INTEGRATION_VERSION,
        "clarified_ppp_routed_intent_id": f"{_require_string(routing_id, 'routing_id')}:CLARIFIED-PPP-ROUTED-INTENT",
        "routing_id": routing_id,
        "routing_status": routing_status,
        "canonical_chain_id": routed["canonical_chain_id"],
        "ppp_input_type": ppp_classification["ppp_input_type"],
        "normalized_intent": ppp_classification["normalized_intent"],
        "normalized_intent_class": ppp_classification["normalized_intent_class"],
        "confidence": ppp_classification["confidence"],
        "selected_interpretation": ppp_classification["selected_interpretation"],
        "clarification_history": deepcopy(routed["clarification_history"]),
        "clarification_history_hash": routed["clarification_history_hash"],
        "source_lineage_preserved": True,
        "intent_source": "HUMAN_CLARIFICATION",
        "intent_source_visible_to_ppp": False,
        "ppp_input_contract": ppp_contract,
        "source_resource_selection_input_reference": source_contract["intent_reference"],
        "source_resource_selection_input_hash": replay_hash(source_contract),
        "routing_evidence_reference": ppp_evidence["routing_evidence_id"],
        "routing_evidence_hash": ppp_evidence["artifact_hash"],
        "routing_classification_reference": ppp_classification["routing_classification_id"],
        "routing_classification_hash": ppp_classification["artifact_hash"],
        "source_clarified_resource_selection_routed_intent_reference": routed[
            "clarified_resource_selection_routed_intent_id"
        ],
        "source_clarified_resource_selection_routed_intent_hash": routed["artifact_hash"],
        "source_clarified_cognition_input_reference": routed["source_clarified_cognition_input_reference"],
        "source_clarified_cognition_input_hash": routed["source_clarified_cognition_input_hash"],
        "resource_references": {
            "requested_role_type": ppp_contract["requested_role_type"],
            "required_capability": ppp_contract["required_capability"],
            "domain_id": ppp_contract["domain_id"],
            "provider_necessity_classification": ppp_contract["provider_necessity_classification"],
        },
        "ppp_proposal_production_invoked": False,
        "ppp_invoked": False,
        "proposal_created": False,
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


def _failed_ppp_routing_evidence_artifact(
    *,
    routing_id: str,
    clarified_resource_selection_routed_intent_artifact: dict[str, Any],
    clarified_resource_selection_routing_evidence_artifact: dict[str, Any],
    clarified_resource_selection_routing_classification_artifact: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    routed = (
        clarified_resource_selection_routed_intent_artifact
        if isinstance(clarified_resource_selection_routed_intent_artifact, dict)
        else {}
    )
    evidence = (
        clarified_resource_selection_routing_evidence_artifact
        if isinstance(clarified_resource_selection_routing_evidence_artifact, dict)
        else {}
    )
    classification = (
        clarified_resource_selection_routing_classification_artifact
        if isinstance(clarified_resource_selection_routing_classification_artifact, dict)
        else {}
    )
    contract = routed.get("resource_selection_input_contract")
    contract = contract if isinstance(contract, dict) else {}
    artifact = {
        "artifact_type": CLARIFIED_PPP_ROUTING_EVIDENCE_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_RESOURCE_SELECTION_PPP_INTEGRATION_VERSION,
        "routing_evidence_id": f"{routing_id}:CLARIFIED-PPP-ROUTING-EVIDENCE"
        if isinstance(routing_id, str)
        else "INVALID:CLARIFIED-PPP-ROUTING-EVIDENCE",
        "routing_reference": routing_id if isinstance(routing_id, str) else "INVALID",
        "canonical_chain_id": routed.get("canonical_chain_id"),
        "clarified_resource_selection_routed_intent_reference": routed.get(
            "clarified_resource_selection_routed_intent_id"
        ),
        "clarified_resource_selection_routed_intent_hash": routed.get("artifact_hash"),
        "clarified_resource_selection_routing_evidence_reference": evidence.get("routing_evidence_id"),
        "clarified_resource_selection_routing_evidence_hash": evidence.get("artifact_hash"),
        "clarified_resource_selection_routing_classification_reference": classification.get(
            "routing_classification_id"
        ),
        "clarified_resource_selection_routing_classification_hash": classification.get("artifact_hash"),
        "resource_selection_input_reference": contract.get("intent_reference"),
        "resource_selection_input_hash": replay_hash(contract) if contract else None,
        "clarification_history": [],
        "clarification_history_hash": replay_hash([]),
        "selected_interpretation": routed.get("selected_interpretation"),
        "source_lineage_preserved": False,
        "confidence": routed.get("confidence"),
        "domain_id": contract.get("domain_id"),
        "evidence_status": FAILED_CLOSED,
        "ppp_proposal_production_invoked": False,
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


def _failed_ppp_routing_classification_artifact(
    *,
    routing_id: str,
    ppp_evidence: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CLARIFIED_PPP_ROUTING_CLASSIFICATION_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_RESOURCE_SELECTION_PPP_INTEGRATION_VERSION,
        "routing_classification_id": f"{routing_id}:CLARIFIED-PPP-ROUTING-CLASSIFICATION"
        if isinstance(routing_id, str)
        else "INVALID:CLARIFIED-PPP-ROUTING-CLASSIFICATION",
        "routing_reference": routing_id if isinstance(routing_id, str) else "INVALID",
        "routing_evidence_reference": ppp_evidence["routing_evidence_id"],
        "routing_evidence_hash": ppp_evidence["artifact_hash"],
        "canonical_chain_id": ppp_evidence["canonical_chain_id"],
        "ppp_input_type": None,
        "ppp_stage": None,
        "intent_source_class": "HUMAN_CLARIFIED_INTENT",
        "source_normalized_for_ppp": False,
        "intent_source_visible_to_ppp": False,
        "workflow_type": None,
        "required_capability": None,
        "requested_role_type": None,
        "domain_id": ppp_evidence["domain_id"],
        "worker_family_id": None,
        "milestone_type": None,
        "provider_necessity_classification": None,
        "normalized_intent": None,
        "normalized_intent_class": None,
        "selected_interpretation": ppp_evidence["selected_interpretation"],
        "confidence": ppp_evidence["confidence"],
        "classification_status": FAILED_CLOSED,
        "ppp_proposal_production_invoked": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": created_at,
        "replay_visible": True,
        "failure_reason": ppp_evidence["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_ppp_routed_intent_artifact(
    *,
    routing_id: str,
    ppp_evidence: dict[str, Any],
    ppp_classification: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CLARIFIED_PPP_ROUTED_INTENT_ARTIFACT_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_RESOURCE_SELECTION_PPP_INTEGRATION_VERSION,
        "clarified_ppp_routed_intent_id": f"{routing_id}:CLARIFIED-PPP-ROUTED-INTENT"
        if isinstance(routing_id, str)
        else "INVALID:CLARIFIED-PPP-ROUTED-INTENT",
        "routing_id": routing_id if isinstance(routing_id, str) else "INVALID",
        "routing_status": FAILED_CLOSED,
        "canonical_chain_id": ppp_evidence["canonical_chain_id"],
        "ppp_input_type": None,
        "normalized_intent": None,
        "normalized_intent_class": None,
        "confidence": ppp_evidence["confidence"],
        "selected_interpretation": ppp_evidence["selected_interpretation"],
        "clarification_history": [],
        "clarification_history_hash": replay_hash([]),
        "source_lineage_preserved": False,
        "intent_source": "HUMAN_CLARIFICATION",
        "intent_source_visible_to_ppp": False,
        "ppp_input_contract": None,
        "source_resource_selection_input_reference": ppp_evidence["resource_selection_input_reference"],
        "source_resource_selection_input_hash": ppp_evidence["resource_selection_input_hash"],
        "routing_evidence_reference": ppp_evidence["routing_evidence_id"],
        "routing_evidence_hash": ppp_evidence["artifact_hash"],
        "routing_classification_reference": ppp_classification["routing_classification_id"],
        "routing_classification_hash": ppp_classification["artifact_hash"],
        "source_clarified_resource_selection_routed_intent_reference": ppp_evidence[
            "clarified_resource_selection_routed_intent_reference"
        ],
        "source_clarified_resource_selection_routed_intent_hash": ppp_evidence[
            "clarified_resource_selection_routed_intent_hash"
        ],
        "source_clarified_cognition_input_reference": None,
        "source_clarified_cognition_input_hash": None,
        "resource_references": None,
        "ppp_proposal_production_invoked": False,
        "ppp_invoked": False,
        "proposal_created": False,
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
    _verify_artifact_hash(routed, "clarified PPP routing artifact")
    artifact = {
        "event_type": "CLARIFIED_PPP_ROUTING_RETURNED",
        "clarified_ppp_routed_intent_reference": routed["clarified_ppp_routed_intent_id"],
        "clarified_ppp_routed_intent_hash": routed["artifact_hash"],
        "routing_status": routed["routing_status"],
        "canonical_chain_id": routed["canonical_chain_id"],
        "ppp_input_type": routed["ppp_input_type"],
        "ppp_input_contract": deepcopy(routed["ppp_input_contract"]),
        "intent_source_visible_to_ppp": routed["intent_source_visible_to_ppp"],
        "ppp_proposal_production_invoked": False,
        "ppp_invoked": False,
        "proposal_created": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
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
        "clarified_ppp_routing_evidence_artifact": deepcopy(evidence),
        "clarified_ppp_routing_classification_artifact": deepcopy(classification),
        "clarified_ppp_routed_intent_artifact": deepcopy(routed),
        "clarified_ppp_routing_replay": deepcopy(returned),
        "clarified_ppp_routing_replay_reference": str(replay_path),
        "routing_status": routed["routing_status"],
        "canonical_chain_id": routed["canonical_chain_id"],
        "ppp_input_type": routed["ppp_input_type"],
        "ppp_input_contract": deepcopy(routed["ppp_input_contract"]),
        "selected_interpretation": routed["selected_interpretation"],
        "clarification_history": deepcopy(routed["clarification_history"]),
        "intent_source_visible_to_ppp": routed["intent_source_visible_to_ppp"],
        "source_lineage_preserved": routed["source_lineage_preserved"],
        "resource_references": deepcopy(routed["resource_references"]),
        "fail_closed": routed["routing_status"] == FAILED_CLOSED,
        "failure_reason": routed["failure_reason"],
        "ppp_proposal_production_invoked": False,
        "ppp_invoked": False,
        "proposal_created": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["clarified_intent_resource_selection_ppp_integration_capture_hash"] = replay_hash(capture)
    return capture


def _validate_artifact(artifact: dict[str, Any], expected_type: str, label: str) -> None:
    if not isinstance(artifact, dict) or artifact.get("artifact_type") != expected_type:
        raise FailClosedRuntimeError(f"clarified PPP routing failed closed: {label} missing")
    _verify_artifact_hash(artifact, f"clarified PPP routing {label}")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"clarified PPP routing failed closed: {label} missing")
    return value


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("clarified PPP routing replay step ordering mismatch")
    _verify_artifact_hash(artifact, "clarified PPP routing artifact")
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
        raise FailClosedRuntimeError("clarified PPP routing replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("clarified PPP routing replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "clarified PPP routing failed closed"
