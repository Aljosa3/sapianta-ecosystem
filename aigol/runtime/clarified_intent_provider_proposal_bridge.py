"""Bridge clarified PPP routed intent into provider proposal production input."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.clarified_intent_resource_selection_ppp_integration_runtime import (
    CLARIFIED_PPP_INTENT_ROUTED,
    CLARIFIED_PPP_ROUTED_INTENT_ARTIFACT_V1,
    CLARIFIED_PPP_ROUTING_CLASSIFICATION_V1,
    CLARIFIED_PPP_ROUTING_EVIDENCE_V1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_proposal_production_runtime import PROVIDER_REQUEST_PACKET_V1
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_CLARIFIED_INTENT_PROVIDER_PROPOSAL_BRIDGE_VERSION = (
    "AIGOL_CLARIFIED_INTENT_PROVIDER_PROPOSAL_BRIDGE_V1"
)
CLARIFIED_PROVIDER_PROPOSAL_REQUEST_ARTIFACT_V1 = "CLARIFIED_PROVIDER_PROPOSAL_REQUEST_ARTIFACT_V1"
CLARIFIED_PROVIDER_PROPOSAL_BRIDGE_EVIDENCE_V1 = "CLARIFIED_PROVIDER_PROPOSAL_BRIDGE_EVIDENCE_V1"
CLARIFIED_PROVIDER_PROPOSAL_BRIDGE_CLASSIFICATION_V1 = (
    "CLARIFIED_PROVIDER_PROPOSAL_BRIDGE_CLASSIFICATION_V1"
)
CLARIFIED_PROVIDER_PROPOSAL_REQUEST_READY = "CLARIFIED_PROVIDER_PROPOSAL_REQUEST_READY"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "clarified_provider_proposal_bridge_evidence_recorded",
    "clarified_provider_proposal_bridge_classification_recorded",
    "clarified_provider_proposal_request_recorded",
    "clarified_provider_proposal_bridge_returned",
)


def bridge_clarified_ppp_intent_to_provider_proposal_request(
    *,
    bridge_id: str,
    provider_id: str,
    clarified_ppp_routed_intent_artifact: dict[str, Any],
    clarified_ppp_routing_evidence_artifact: dict[str, Any],
    clarified_ppp_routing_classification_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    selected_provider_id: str | None = None,
) -> dict[str, Any]:
    """Create a provider proposal request artifact without invoking a provider."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        routed = deepcopy(clarified_ppp_routed_intent_artifact)
        evidence = deepcopy(clarified_ppp_routing_evidence_artifact)
        classification = deepcopy(clarified_ppp_routing_classification_artifact)
        active_provider_id = _require_string(provider_id, "provider_id")
        selected = selected_provider_id if selected_provider_id is not None else active_provider_id
        _validate_inputs(
            routed=routed,
            evidence=evidence,
            classification=classification,
            provider_id=active_provider_id,
            selected_provider_id=selected,
        )
        bridge_evidence = _bridge_evidence_artifact(
            bridge_id=bridge_id,
            provider_id=active_provider_id,
            routed=routed,
            evidence=evidence,
            classification=classification,
            created_at=created_at,
            evidence_status="CLARIFIED_PROVIDER_PROPOSAL_BRIDGE_EVIDENCE_ACCEPTED",
            failure_reason=None,
        )
        bridge_classification = _bridge_classification_artifact(
            bridge_id=bridge_id,
            provider_id=active_provider_id,
            bridge_evidence=bridge_evidence,
            routed=routed,
            created_at=created_at,
            classification_status="CLARIFIED_PROVIDER_PROPOSAL_BRIDGE_CLASSIFIED",
            failure_reason=None,
        )
        request = _provider_request_artifact(
            bridge_id=bridge_id,
            provider_id=active_provider_id,
            bridge_evidence=bridge_evidence,
            bridge_classification=bridge_classification,
            routed=routed,
            created_at=created_at,
            request_status=CLARIFIED_PROVIDER_PROPOSAL_REQUEST_READY,
            failure_reason=None,
        )
        returned = _returned_artifact(request)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], bridge_evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], bridge_classification)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], request)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(bridge_evidence, bridge_classification, request, returned, replay_path)
    except Exception as exc:
        bridge_evidence = _failed_bridge_evidence_artifact(
            bridge_id=bridge_id,
            provider_id=provider_id,
            clarified_ppp_routed_intent_artifact=clarified_ppp_routed_intent_artifact,
            clarified_ppp_routing_evidence_artifact=clarified_ppp_routing_evidence_artifact,
            clarified_ppp_routing_classification_artifact=clarified_ppp_routing_classification_artifact,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        bridge_classification = _failed_bridge_classification_artifact(
            bridge_id=bridge_id,
            bridge_evidence=bridge_evidence,
            created_at=created_at,
        )
        request = _failed_provider_request_artifact(
            bridge_id=bridge_id,
            provider_id=provider_id,
            bridge_evidence=bridge_evidence,
            bridge_classification=bridge_classification,
            created_at=created_at,
            failure_reason=bridge_evidence["failure_reason"],
        )
        returned = _returned_artifact(request)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], bridge_evidence)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], bridge_classification)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], request)
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(bridge_evidence, bridge_classification, request, returned, replay_path)


def reconstruct_clarified_intent_provider_proposal_bridge_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct clarified provider proposal bridge replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("clarified provider proposal bridge replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("clarified provider proposal bridge replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "clarified provider proposal bridge artifact")
        wrappers.append(wrapper)
    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    request = wrappers[2]["artifact"]
    returned = wrappers[3]["artifact"]
    if classification.get("bridge_evidence_reference") != evidence["bridge_evidence_id"]:
        raise FailClosedRuntimeError("clarified provider proposal bridge evidence reference mismatch")
    if classification.get("bridge_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("clarified provider proposal bridge evidence hash mismatch")
    if request.get("bridge_classification_reference") != classification["bridge_classification_id"]:
        raise FailClosedRuntimeError("clarified provider proposal bridge classification reference mismatch")
    if request.get("bridge_classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("clarified provider proposal bridge classification hash mismatch")
    if returned.get("provider_proposal_request_reference") != request["provider_proposal_request_id"]:
        raise FailClosedRuntimeError("clarified provider proposal bridge returned reference mismatch")
    if returned.get("provider_proposal_request_hash") != request["artifact_hash"]:
        raise FailClosedRuntimeError("clarified provider proposal bridge returned hash mismatch")
    return {
        "provider_proposal_request_id": request["provider_proposal_request_id"],
        "request_status": request["request_status"],
        "provider_request_packet_type": request["provider_request_packet_type"],
        "provider_id": request["provider_id"],
        "canonical_chain_id": request["canonical_chain_id"],
        "clarified_ppp_routed_intent_reference": request["clarified_ppp_routed_intent_reference"],
        "selected_interpretation": request["selected_interpretation"],
        "domain_reference": request["domain_reference"],
        "failure_reason": request["failure_reason"],
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_inputs(
    *,
    routed: dict[str, Any],
    evidence: dict[str, Any],
    classification: dict[str, Any],
    provider_id: str,
    selected_provider_id: str,
) -> None:
    _validate_artifact(routed, CLARIFIED_PPP_ROUTED_INTENT_ARTIFACT_V1, "clarified PPP routed intent")
    _validate_artifact(evidence, CLARIFIED_PPP_ROUTING_EVIDENCE_V1, "clarified PPP routing evidence")
    _validate_artifact(
        classification,
        CLARIFIED_PPP_ROUTING_CLASSIFICATION_V1,
        "clarified PPP routing classification",
    )
    if provider_id != _require_string(selected_provider_id, "selected_provider_id"):
        raise FailClosedRuntimeError("clarified provider proposal bridge failed closed: provider mismatch")
    if routed.get("routing_status") != CLARIFIED_PPP_INTENT_ROUTED:
        reason = str(routed.get("failure_reason") or "")
        if "unresolved clarification" in reason:
            raise FailClosedRuntimeError("clarified provider proposal bridge failed closed: unresolved clarification")
        raise FailClosedRuntimeError("clarified provider proposal bridge failed closed: invalid PPP lineage")
    if routed.get("intent_source_visible_to_ppp") is not False:
        raise FailClosedRuntimeError("clarified provider proposal bridge failed closed: replay corruption")
    if routed.get("source_lineage_preserved") is not True:
        raise FailClosedRuntimeError("clarified provider proposal bridge failed closed: invalid PPP lineage")
    contract = routed.get("ppp_input_contract")
    if not isinstance(contract, dict):
        raise FailClosedRuntimeError("clarified provider proposal bridge failed closed: invalid PPP lineage")
    if contract.get("intent_source_visible_to_ppp") is not False:
        raise FailClosedRuntimeError("clarified provider proposal bridge failed closed: replay corruption")
    if routed.get("routing_evidence_reference") != evidence.get("routing_evidence_id"):
        raise FailClosedRuntimeError("clarified provider proposal bridge failed closed: invalid PPP lineage")
    if routed.get("routing_evidence_hash") != evidence.get("artifact_hash"):
        raise FailClosedRuntimeError("clarified provider proposal bridge failed closed: invalid PPP lineage")
    if routed.get("routing_classification_reference") != classification.get("routing_classification_id"):
        raise FailClosedRuntimeError("clarified provider proposal bridge failed closed: invalid PPP lineage")
    if routed.get("routing_classification_hash") != classification.get("artifact_hash"):
        raise FailClosedRuntimeError("clarified provider proposal bridge failed closed: invalid PPP lineage")
    if classification.get("routing_evidence_reference") != evidence.get("routing_evidence_id"):
        raise FailClosedRuntimeError("clarified provider proposal bridge failed closed: invalid PPP lineage")
    if classification.get("routing_evidence_hash") != evidence.get("artifact_hash"):
        raise FailClosedRuntimeError("clarified provider proposal bridge failed closed: invalid PPP lineage")
    if routed.get("canonical_chain_id") != evidence.get("canonical_chain_id"):
        raise FailClosedRuntimeError("clarified provider proposal bridge failed closed: chain continuity failure")
    if routed.get("canonical_chain_id") != classification.get("canonical_chain_id"):
        raise FailClosedRuntimeError("clarified provider proposal bridge failed closed: chain continuity failure")
    if not isinstance(routed.get("clarification_history"), list):
        raise FailClosedRuntimeError("clarified provider proposal bridge failed closed: invalid PPP lineage")
    if routed.get("clarification_history_hash") != replay_hash(routed["clarification_history"]):
        raise FailClosedRuntimeError("clarified provider proposal bridge failed closed: replay corruption")
    _require_string(routed.get("selected_interpretation"), "selected_interpretation")
    _require_string(contract.get("intent_reference"), "intent_reference")
    _require_string(contract.get("workflow_type"), "workflow_type")
    _require_string(contract.get("required_capability"), "required_capability")
    _require_string(contract.get("requested_role_type"), "requested_role_type")
    _require_string(contract.get("domain_id"), "domain_id")
    _require_string(contract.get("provider_necessity_classification"), "provider_necessity_classification")
    _require_string(contract.get("confidence"), "confidence")
    _require_string(contract.get("ppp_stage"), "ppp_stage")


def _bridge_evidence_artifact(
    *,
    bridge_id: str,
    provider_id: str,
    routed: dict[str, Any],
    evidence: dict[str, Any],
    classification: dict[str, Any],
    created_at: str,
    evidence_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CLARIFIED_PROVIDER_PROPOSAL_BRIDGE_EVIDENCE_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_PROVIDER_PROPOSAL_BRIDGE_VERSION,
        "bridge_evidence_id": f"{_require_string(bridge_id, 'bridge_id')}:BRIDGE-EVIDENCE",
        "bridge_reference": bridge_id,
        "provider_id": provider_id,
        "canonical_chain_id": routed["canonical_chain_id"],
        "clarified_ppp_routed_intent_reference": routed["clarified_ppp_routed_intent_id"],
        "clarified_ppp_routed_intent_hash": routed["artifact_hash"],
        "clarified_ppp_routing_evidence_reference": evidence["routing_evidence_id"],
        "clarified_ppp_routing_evidence_hash": evidence["artifact_hash"],
        "clarified_ppp_routing_classification_reference": classification["routing_classification_id"],
        "clarified_ppp_routing_classification_hash": classification["artifact_hash"],
        "clarification_history": deepcopy(routed["clarification_history"]),
        "clarification_history_hash": routed["clarification_history_hash"],
        "selected_interpretation": routed["selected_interpretation"],
        "confidence": routed["confidence"],
        "domain_reference": routed["ppp_input_contract"]["domain_id"],
        "source_lineage_preserved": True,
        "evidence_status": evidence_status,
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


def _bridge_classification_artifact(
    *,
    bridge_id: str,
    provider_id: str,
    bridge_evidence: dict[str, Any],
    routed: dict[str, Any],
    created_at: str,
    classification_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    contract = routed["ppp_input_contract"]
    artifact = {
        "artifact_type": CLARIFIED_PROVIDER_PROPOSAL_BRIDGE_CLASSIFICATION_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_PROVIDER_PROPOSAL_BRIDGE_VERSION,
        "bridge_classification_id": f"{_require_string(bridge_id, 'bridge_id')}:BRIDGE-CLASSIFICATION",
        "bridge_reference": bridge_id,
        "bridge_evidence_reference": bridge_evidence["bridge_evidence_id"],
        "bridge_evidence_hash": bridge_evidence["artifact_hash"],
        "provider_id": provider_id,
        "canonical_chain_id": routed["canonical_chain_id"],
        "provider_request_packet_type": PROVIDER_REQUEST_PACKET_V1,
        "provider_proposal_input_valid": True,
        "workflow_type": contract["workflow_type"],
        "required_capability": contract["required_capability"],
        "requested_role_type": contract["requested_role_type"],
        "domain_reference": contract["domain_id"],
        "provider_necessity_classification": contract["provider_necessity_classification"],
        "ppp_stage": contract["ppp_stage"],
        "selected_interpretation": routed["selected_interpretation"],
        "confidence": contract["confidence"],
        "classification_status": classification_status,
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


def _provider_request_artifact(
    *,
    bridge_id: str,
    provider_id: str,
    bridge_evidence: dict[str, Any],
    bridge_classification: dict[str, Any],
    routed: dict[str, Any],
    created_at: str,
    request_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    contract = routed["ppp_input_contract"]
    artifact = {
        "artifact_type": CLARIFIED_PROVIDER_PROPOSAL_REQUEST_ARTIFACT_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_PROVIDER_PROPOSAL_BRIDGE_VERSION,
        "provider_proposal_request_id": f"{_require_string(bridge_id, 'bridge_id')}:PROVIDER-PROPOSAL-REQUEST",
        "request_status": request_status,
        "provider_request_packet_type": PROVIDER_REQUEST_PACKET_V1,
        "provider_id": provider_id,
        "canonical_chain_id": routed["canonical_chain_id"],
        "clarified_ppp_routed_intent_reference": routed["clarified_ppp_routed_intent_id"],
        "clarified_ppp_routed_intent_hash": routed["artifact_hash"],
        "source_resource_selection_input_reference": routed["source_resource_selection_input_reference"],
        "source_resource_selection_input_hash": routed["source_resource_selection_input_hash"],
        "bridge_evidence_reference": bridge_evidence["bridge_evidence_id"],
        "bridge_evidence_hash": bridge_evidence["artifact_hash"],
        "bridge_classification_reference": bridge_classification["bridge_classification_id"],
        "bridge_classification_hash": bridge_classification["artifact_hash"],
        "ppp_input_contract": deepcopy(contract),
        "ppp_input_contract_hash": replay_hash(contract),
        "request_instructions": [
            "Prepare one DEVELOPMENT_PROPOSAL_ARTIFACT_V1-compatible proposal payload.",
            "Proposal must remain proposal-only.",
            "Do not authorize, dispatch, execute, mutate governance, mutate replay, create workers, or create domains.",
        ],
        "clarification_history": deepcopy(routed["clarification_history"]),
        "clarification_history_hash": routed["clarification_history_hash"],
        "selected_interpretation": routed["selected_interpretation"],
        "confidence": contract["confidence"],
        "domain_reference": contract["domain_id"],
        "provider_necessity_classification": contract["provider_necessity_classification"],
        "proposal_only": True,
        "provider_invoked": False,
        "provider_authority": False,
        "worker_invoked": False,
        "worker_created": False,
        "domain_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["provider_request_hash"] = replay_hash(
        {
            "provider_id": artifact["provider_id"],
            "canonical_chain_id": artifact["canonical_chain_id"],
            "clarified_ppp_routed_intent_hash": artifact["clarified_ppp_routed_intent_hash"],
            "ppp_input_contract_hash": artifact["ppp_input_contract_hash"],
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_bridge_evidence_artifact(
    *,
    bridge_id: str,
    provider_id: str,
    clarified_ppp_routed_intent_artifact: dict[str, Any],
    clarified_ppp_routing_evidence_artifact: dict[str, Any],
    clarified_ppp_routing_classification_artifact: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    routed = clarified_ppp_routed_intent_artifact if isinstance(clarified_ppp_routed_intent_artifact, dict) else {}
    evidence = clarified_ppp_routing_evidence_artifact if isinstance(clarified_ppp_routing_evidence_artifact, dict) else {}
    classification = (
        clarified_ppp_routing_classification_artifact
        if isinstance(clarified_ppp_routing_classification_artifact, dict)
        else {}
    )
    artifact = {
        "artifact_type": CLARIFIED_PROVIDER_PROPOSAL_BRIDGE_EVIDENCE_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_PROVIDER_PROPOSAL_BRIDGE_VERSION,
        "bridge_evidence_id": f"{bridge_id}:BRIDGE-EVIDENCE" if isinstance(bridge_id, str) else "INVALID:BRIDGE-EVIDENCE",
        "bridge_reference": bridge_id if isinstance(bridge_id, str) else "INVALID",
        "provider_id": provider_id if isinstance(provider_id, str) else None,
        "canonical_chain_id": routed.get("canonical_chain_id"),
        "clarified_ppp_routed_intent_reference": routed.get("clarified_ppp_routed_intent_id"),
        "clarified_ppp_routed_intent_hash": routed.get("artifact_hash"),
        "clarified_ppp_routing_evidence_reference": evidence.get("routing_evidence_id"),
        "clarified_ppp_routing_evidence_hash": evidence.get("artifact_hash"),
        "clarified_ppp_routing_classification_reference": classification.get("routing_classification_id"),
        "clarified_ppp_routing_classification_hash": classification.get("artifact_hash"),
        "clarification_history": [],
        "clarification_history_hash": replay_hash([]),
        "selected_interpretation": routed.get("selected_interpretation"),
        "confidence": routed.get("confidence"),
        "domain_reference": None,
        "source_lineage_preserved": False,
        "evidence_status": FAILED_CLOSED,
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


def _failed_bridge_classification_artifact(
    *,
    bridge_id: str,
    bridge_evidence: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CLARIFIED_PROVIDER_PROPOSAL_BRIDGE_CLASSIFICATION_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_PROVIDER_PROPOSAL_BRIDGE_VERSION,
        "bridge_classification_id": f"{bridge_id}:BRIDGE-CLASSIFICATION"
        if isinstance(bridge_id, str)
        else "INVALID:BRIDGE-CLASSIFICATION",
        "bridge_reference": bridge_id if isinstance(bridge_id, str) else "INVALID",
        "bridge_evidence_reference": bridge_evidence["bridge_evidence_id"],
        "bridge_evidence_hash": bridge_evidence["artifact_hash"],
        "provider_id": bridge_evidence["provider_id"],
        "canonical_chain_id": bridge_evidence["canonical_chain_id"],
        "provider_request_packet_type": None,
        "provider_proposal_input_valid": False,
        "workflow_type": None,
        "required_capability": None,
        "requested_role_type": None,
        "domain_reference": bridge_evidence["domain_reference"],
        "provider_necessity_classification": None,
        "ppp_stage": None,
        "selected_interpretation": bridge_evidence["selected_interpretation"],
        "confidence": bridge_evidence["confidence"],
        "classification_status": FAILED_CLOSED,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": created_at,
        "replay_visible": True,
        "failure_reason": bridge_evidence["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_provider_request_artifact(
    *,
    bridge_id: str,
    provider_id: str,
    bridge_evidence: dict[str, Any],
    bridge_classification: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CLARIFIED_PROVIDER_PROPOSAL_REQUEST_ARTIFACT_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_PROVIDER_PROPOSAL_BRIDGE_VERSION,
        "provider_proposal_request_id": f"{bridge_id}:PROVIDER-PROPOSAL-REQUEST"
        if isinstance(bridge_id, str)
        else "INVALID:PROVIDER-PROPOSAL-REQUEST",
        "request_status": FAILED_CLOSED,
        "provider_request_packet_type": PROVIDER_REQUEST_PACKET_V1,
        "provider_id": provider_id if isinstance(provider_id, str) else None,
        "canonical_chain_id": bridge_evidence["canonical_chain_id"],
        "clarified_ppp_routed_intent_reference": bridge_evidence["clarified_ppp_routed_intent_reference"],
        "clarified_ppp_routed_intent_hash": bridge_evidence["clarified_ppp_routed_intent_hash"],
        "source_resource_selection_input_reference": None,
        "source_resource_selection_input_hash": None,
        "bridge_evidence_reference": bridge_evidence["bridge_evidence_id"],
        "bridge_evidence_hash": bridge_evidence["artifact_hash"],
        "bridge_classification_reference": bridge_classification["bridge_classification_id"],
        "bridge_classification_hash": bridge_classification["artifact_hash"],
        "ppp_input_contract": None,
        "ppp_input_contract_hash": None,
        "request_instructions": [],
        "clarification_history": [],
        "clarification_history_hash": replay_hash([]),
        "selected_interpretation": bridge_evidence["selected_interpretation"],
        "confidence": bridge_evidence["confidence"],
        "domain_reference": bridge_evidence["domain_reference"],
        "provider_necessity_classification": None,
        "proposal_only": True,
        "provider_invoked": False,
        "provider_authority": False,
        "worker_invoked": False,
        "worker_created": False,
        "domain_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": created_at,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["provider_request_hash"] = replay_hash(
        {
            "provider_id": artifact["provider_id"],
            "canonical_chain_id": artifact["canonical_chain_id"],
            "clarified_ppp_routed_intent_hash": artifact["clarified_ppp_routed_intent_hash"],
            "ppp_input_contract_hash": artifact["ppp_input_contract_hash"],
        }
    )
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(request: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(request, "clarified provider proposal bridge artifact")
    returned = {
        "event_type": "CLARIFIED_PROVIDER_PROPOSAL_BRIDGE_RETURNED",
        "provider_proposal_request_reference": request["provider_proposal_request_id"],
        "provider_proposal_request_hash": request["artifact_hash"],
        "request_status": request["request_status"],
        "provider_id": request["provider_id"],
        "canonical_chain_id": request["canonical_chain_id"],
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": request["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(
    evidence: dict[str, Any],
    classification: dict[str, Any],
    request: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "clarified_provider_proposal_bridge_evidence_artifact": deepcopy(evidence),
        "clarified_provider_proposal_bridge_classification_artifact": deepcopy(classification),
        "clarified_provider_proposal_request_artifact": deepcopy(request),
        "clarified_provider_proposal_bridge_replay": deepcopy(returned),
        "clarified_provider_proposal_bridge_replay_reference": str(replay_path),
        "request_status": request["request_status"],
        "provider_request_packet_type": request["provider_request_packet_type"],
        "provider_id": request["provider_id"],
        "canonical_chain_id": request["canonical_chain_id"],
        "selected_interpretation": request["selected_interpretation"],
        "domain_reference": request["domain_reference"],
        "provider_necessity_classification": request["provider_necessity_classification"],
        "fail_closed": request["request_status"] == FAILED_CLOSED,
        "failure_reason": request["failure_reason"],
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["clarified_intent_provider_proposal_bridge_capture_hash"] = replay_hash(capture)
    return capture


def _validate_artifact(artifact: dict[str, Any], expected_type: str, label: str) -> None:
    if not isinstance(artifact, dict) or artifact.get("artifact_type") != expected_type:
        raise FailClosedRuntimeError(f"clarified provider proposal bridge failed closed: {label} missing")
    _verify_artifact_hash(artifact, f"clarified provider proposal bridge {label}")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{label} is required")
    return value.strip()


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("clarified provider proposal bridge replay step ordering mismatch")
    _verify_artifact_hash(artifact, "clarified provider proposal bridge artifact")
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
        raise FailClosedRuntimeError("clarified provider proposal bridge replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("clarified provider proposal bridge replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "clarified provider proposal bridge failed closed"
