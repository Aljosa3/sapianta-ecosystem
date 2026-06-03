"""Integrate clarified provider request artifacts with provider proposal production readiness."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.clarified_intent_provider_proposal_bridge import (
    CLARIFIED_PROVIDER_PROPOSAL_BRIDGE_CLASSIFICATION_V1,
    CLARIFIED_PROVIDER_PROPOSAL_BRIDGE_EVIDENCE_V1,
    CLARIFIED_PROVIDER_PROPOSAL_REQUEST_ARTIFACT_V1,
    CLARIFIED_PROVIDER_PROPOSAL_REQUEST_READY,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_proposal_production_runtime import PROVIDER_REQUEST_PACKET_V1
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_CLARIFIED_INTENT_PROVIDER_PROPOSAL_PRODUCTION_INTEGRATION_VERSION = (
    "AIGOL_CLARIFIED_INTENT_PROVIDER_PROPOSAL_PRODUCTION_INTEGRATION_V1"
)
CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_ARTIFACT_V1 = (
    "CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_ARTIFACT_V1"
)
CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_EVIDENCE_V1 = (
    "CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_EVIDENCE_V1"
)
CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_CLASSIFICATION_V1 = (
    "CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_CLASSIFICATION_V1"
)
CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_READY = "CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_READY"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "clarified_provider_proposal_production_evidence_recorded",
    "clarified_provider_proposal_production_classification_recorded",
    "clarified_provider_proposal_production_recorded",
    "clarified_provider_proposal_production_returned",
)


def integrate_clarified_provider_request_with_proposal_production(
    *,
    integration_id: str,
    provider_id: str,
    clarified_provider_proposal_request_artifact: dict[str, Any],
    clarified_provider_proposal_bridge_evidence_artifact: dict[str, Any],
    clarified_provider_proposal_bridge_classification_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    selected_provider_id: str | None = None,
) -> dict[str, Any]:
    """Verify clarified provider request artifacts are ready for governed provider production."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        request = deepcopy(clarified_provider_proposal_request_artifact)
        evidence = deepcopy(clarified_provider_proposal_bridge_evidence_artifact)
        classification = deepcopy(clarified_provider_proposal_bridge_classification_artifact)
        active_provider_id = _require_string(provider_id, "provider_id")
        selected = selected_provider_id if selected_provider_id is not None else active_provider_id
        _validate_inputs(
            request=request,
            evidence=evidence,
            classification=classification,
            provider_id=active_provider_id,
            selected_provider_id=selected,
        )
        production_evidence = _production_evidence_artifact(
            integration_id=integration_id,
            provider_id=active_provider_id,
            request=request,
            evidence=evidence,
            classification=classification,
            created_at=created_at,
            evidence_status="CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_EVIDENCE_ACCEPTED",
            failure_reason=None,
        )
        production_classification = _production_classification_artifact(
            integration_id=integration_id,
            provider_id=active_provider_id,
            production_evidence=production_evidence,
            request=request,
            created_at=created_at,
            classification_status="CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_CLASSIFIED",
            failure_reason=None,
        )
        production = _production_artifact(
            integration_id=integration_id,
            provider_id=active_provider_id,
            production_evidence=production_evidence,
            production_classification=production_classification,
            request=request,
            created_at=created_at,
            production_status=CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_READY,
            failure_reason=None,
        )
        returned = _returned_artifact(production)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], production_evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], production_classification)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], production)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(production_evidence, production_classification, production, returned, replay_path)
    except Exception as exc:
        production_evidence = _failed_production_evidence_artifact(
            integration_id=integration_id,
            provider_id=provider_id,
            request_artifact=clarified_provider_proposal_request_artifact,
            bridge_evidence_artifact=clarified_provider_proposal_bridge_evidence_artifact,
            bridge_classification_artifact=clarified_provider_proposal_bridge_classification_artifact,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        production_classification = _failed_production_classification_artifact(
            integration_id=integration_id,
            production_evidence=production_evidence,
            created_at=created_at,
        )
        production = _failed_production_artifact(
            integration_id=integration_id,
            provider_id=provider_id,
            production_evidence=production_evidence,
            production_classification=production_classification,
            created_at=created_at,
            failure_reason=production_evidence["failure_reason"],
        )
        returned = _returned_artifact(production)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], production_evidence)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], production_classification)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], production)
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(production_evidence, production_classification, production, returned, replay_path)


def reconstruct_clarified_intent_provider_proposal_production_integration_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct clarified provider proposal production integration replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("clarified provider production integration replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError(
                "clarified provider production integration replay artifact must be a JSON object"
            )
        _verify_artifact_hash(artifact, "clarified provider production integration artifact")
        wrappers.append(wrapper)
    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    production = wrappers[2]["artifact"]
    returned = wrappers[3]["artifact"]
    if classification.get("production_evidence_reference") != evidence["production_evidence_id"]:
        raise FailClosedRuntimeError("clarified provider production integration evidence reference mismatch")
    if classification.get("production_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("clarified provider production integration evidence hash mismatch")
    if production.get("production_classification_reference") != classification["production_classification_id"]:
        raise FailClosedRuntimeError("clarified provider production integration classification reference mismatch")
    if production.get("production_classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("clarified provider production integration classification hash mismatch")
    if returned.get("production_reference") != production["production_id"]:
        raise FailClosedRuntimeError("clarified provider production integration returned reference mismatch")
    if returned.get("production_hash") != production["artifact_hash"]:
        raise FailClosedRuntimeError("clarified provider production integration returned hash mismatch")
    return {
        "production_id": production["production_id"],
        "production_status": production["production_status"],
        "provider_id": production["provider_id"],
        "provider_request_packet_type": production["provider_request_packet_type"],
        "provider_proposal_request_reference": production["provider_proposal_request_reference"],
        "canonical_chain_id": production["canonical_chain_id"],
        "selected_interpretation": production["selected_interpretation"],
        "domain_reference": production["domain_reference"],
        "failure_reason": production["failure_reason"],
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
    request: dict[str, Any],
    evidence: dict[str, Any],
    classification: dict[str, Any],
    provider_id: str,
    selected_provider_id: str,
) -> None:
    _validate_artifact(
        request,
        CLARIFIED_PROVIDER_PROPOSAL_REQUEST_ARTIFACT_V1,
        "clarified provider proposal request",
    )
    _validate_artifact(
        evidence,
        CLARIFIED_PROVIDER_PROPOSAL_BRIDGE_EVIDENCE_V1,
        "clarified provider bridge evidence",
    )
    _validate_artifact(
        classification,
        CLARIFIED_PROVIDER_PROPOSAL_BRIDGE_CLASSIFICATION_V1,
        "clarified provider bridge classification",
    )
    if provider_id != _require_string(selected_provider_id, "selected_provider_id"):
        raise FailClosedRuntimeError("clarified provider production integration failed closed: provider mismatch")
    if request.get("provider_id") != provider_id:
        raise FailClosedRuntimeError("clarified provider production integration failed closed: provider mismatch")
    if evidence.get("provider_id") != provider_id or classification.get("provider_id") != provider_id:
        raise FailClosedRuntimeError("clarified provider production integration failed closed: invalid provider lineage")
    if request.get("request_status") != CLARIFIED_PROVIDER_PROPOSAL_REQUEST_READY:
        reason = str(request.get("failure_reason") or "")
        if "unresolved clarification" in reason:
            raise FailClosedRuntimeError("clarified provider production integration failed closed: unresolved clarification")
        raise FailClosedRuntimeError("clarified provider production integration failed closed: invalid provider lineage")
    if request.get("provider_request_packet_type") != PROVIDER_REQUEST_PACKET_V1:
        raise FailClosedRuntimeError("clarified provider production integration failed closed: invalid provider lineage")
    if classification.get("provider_request_packet_type") != PROVIDER_REQUEST_PACKET_V1:
        raise FailClosedRuntimeError("clarified provider production integration failed closed: invalid provider lineage")
    if request.get("bridge_evidence_reference") != evidence.get("bridge_evidence_id"):
        raise FailClosedRuntimeError("clarified provider production integration failed closed: invalid provider lineage")
    if request.get("bridge_evidence_hash") != evidence.get("artifact_hash"):
        raise FailClosedRuntimeError("clarified provider production integration failed closed: invalid provider lineage")
    if request.get("bridge_classification_reference") != classification.get("bridge_classification_id"):
        raise FailClosedRuntimeError("clarified provider production integration failed closed: invalid provider lineage")
    if request.get("bridge_classification_hash") != classification.get("artifact_hash"):
        raise FailClosedRuntimeError("clarified provider production integration failed closed: invalid provider lineage")
    if classification.get("bridge_evidence_reference") != evidence.get("bridge_evidence_id"):
        raise FailClosedRuntimeError("clarified provider production integration failed closed: invalid provider lineage")
    if classification.get("bridge_evidence_hash") != evidence.get("artifact_hash"):
        raise FailClosedRuntimeError("clarified provider production integration failed closed: invalid provider lineage")
    if request.get("canonical_chain_id") != evidence.get("canonical_chain_id"):
        raise FailClosedRuntimeError("clarified provider production integration failed closed: chain continuity failure")
    if request.get("canonical_chain_id") != classification.get("canonical_chain_id"):
        raise FailClosedRuntimeError("clarified provider production integration failed closed: chain continuity failure")
    contract = request.get("ppp_input_contract")
    if not isinstance(contract, dict):
        raise FailClosedRuntimeError("clarified provider production integration failed closed: invalid PPP lineage")
    if contract.get("intent_source_visible_to_ppp") is not False:
        raise FailClosedRuntimeError("clarified provider production integration failed closed: replay corruption")
    if request.get("ppp_input_contract_hash") != replay_hash(contract):
        raise FailClosedRuntimeError("clarified provider production integration failed closed: replay corruption")
    if not isinstance(request.get("clarification_history"), list):
        raise FailClosedRuntimeError("clarified provider production integration failed closed: invalid provider lineage")
    if request.get("clarification_history_hash") != replay_hash(request["clarification_history"]):
        raise FailClosedRuntimeError("clarified provider production integration failed closed: replay corruption")
    if request.get("provider_invoked") is not False or request.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("clarified provider production integration failed closed: replay corruption")
    if request.get("execution_requested") is not False or request.get("dispatch_requested") is not False:
        raise FailClosedRuntimeError("clarified provider production integration failed closed: replay corruption")
    _require_string(request.get("clarified_ppp_routed_intent_reference"), "clarified_ppp_routed_intent_reference")
    _require_string(request.get("clarified_ppp_routed_intent_hash"), "clarified_ppp_routed_intent_hash")
    _require_string(request.get("selected_interpretation"), "selected_interpretation")
    _require_string(request.get("confidence"), "confidence")
    _require_string(request.get("domain_reference"), "domain_reference")
    _require_string(request.get("provider_necessity_classification"), "provider_necessity_classification")


def _production_evidence_artifact(
    *,
    integration_id: str,
    provider_id: str,
    request: dict[str, Any],
    evidence: dict[str, Any],
    classification: dict[str, Any],
    created_at: str,
    evidence_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_EVIDENCE_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_PROVIDER_PROPOSAL_PRODUCTION_INTEGRATION_VERSION,
        "production_evidence_id": f"{_require_string(integration_id, 'integration_id')}:PRODUCTION-EVIDENCE",
        "integration_reference": integration_id,
        "provider_id": provider_id,
        "canonical_chain_id": request["canonical_chain_id"],
        "provider_proposal_request_reference": request["provider_proposal_request_id"],
        "provider_proposal_request_hash": request["artifact_hash"],
        "bridge_evidence_reference": evidence["bridge_evidence_id"],
        "bridge_evidence_hash": evidence["artifact_hash"],
        "bridge_classification_reference": classification["bridge_classification_id"],
        "bridge_classification_hash": classification["artifact_hash"],
        "clarified_ppp_routed_intent_reference": request["clarified_ppp_routed_intent_reference"],
        "clarified_ppp_routed_intent_hash": request["clarified_ppp_routed_intent_hash"],
        "selected_interpretation": request["selected_interpretation"],
        "confidence": request["confidence"],
        "domain_reference": request["domain_reference"],
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


def _production_classification_artifact(
    *,
    integration_id: str,
    provider_id: str,
    production_evidence: dict[str, Any],
    request: dict[str, Any],
    created_at: str,
    classification_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_CLASSIFICATION_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_PROVIDER_PROPOSAL_PRODUCTION_INTEGRATION_VERSION,
        "production_classification_id": f"{_require_string(integration_id, 'integration_id')}:PRODUCTION-CLASSIFICATION",
        "integration_reference": integration_id,
        "production_evidence_reference": production_evidence["production_evidence_id"],
        "production_evidence_hash": production_evidence["artifact_hash"],
        "provider_id": provider_id,
        "canonical_chain_id": request["canonical_chain_id"],
        "provider_request_packet_type": request["provider_request_packet_type"],
        "provider_production_input_valid": True,
        "provider_proposal_request_reference": request["provider_proposal_request_id"],
        "provider_proposal_request_hash": request["artifact_hash"],
        "provider_necessity_classification": request["provider_necessity_classification"],
        "selected_interpretation": request["selected_interpretation"],
        "confidence": request["confidence"],
        "domain_reference": request["domain_reference"],
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


def _production_artifact(
    *,
    integration_id: str,
    provider_id: str,
    production_evidence: dict[str, Any],
    production_classification: dict[str, Any],
    request: dict[str, Any],
    created_at: str,
    production_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_ARTIFACT_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_PROVIDER_PROPOSAL_PRODUCTION_INTEGRATION_VERSION,
        "production_id": f"{_require_string(integration_id, 'integration_id')}:CLARIFIED-PROVIDER-PRODUCTION",
        "integration_id": integration_id,
        "production_status": production_status,
        "provider_id": provider_id,
        "provider_request_packet_type": request["provider_request_packet_type"],
        "provider_proposal_request_reference": request["provider_proposal_request_id"],
        "provider_proposal_request_hash": request["artifact_hash"],
        "provider_request_hash": request["provider_request_hash"],
        "production_evidence_reference": production_evidence["production_evidence_id"],
        "production_evidence_hash": production_evidence["artifact_hash"],
        "production_classification_reference": production_classification["production_classification_id"],
        "production_classification_hash": production_classification["artifact_hash"],
        "canonical_chain_id": request["canonical_chain_id"],
        "clarified_ppp_routed_intent_reference": request["clarified_ppp_routed_intent_reference"],
        "clarified_ppp_routed_intent_hash": request["clarified_ppp_routed_intent_hash"],
        "selected_interpretation": request["selected_interpretation"],
        "clarification_history_hash": request["clarification_history_hash"],
        "confidence": request["confidence"],
        "domain_reference": request["domain_reference"],
        "provider_necessity_classification": request["provider_necessity_classification"],
        "proposal_validation_status": "AWAITING_PROVIDER_RESPONSE",
        "approval_evidence_status": "AWAITING_VALIDATED_PROPOSAL",
        "handoff_preparation_status": "AWAITING_VALIDATED_PROPOSAL",
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
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_production_evidence_artifact(
    *,
    integration_id: str,
    provider_id: str,
    request_artifact: dict[str, Any],
    bridge_evidence_artifact: dict[str, Any],
    bridge_classification_artifact: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    request = request_artifact if isinstance(request_artifact, dict) else {}
    evidence = bridge_evidence_artifact if isinstance(bridge_evidence_artifact, dict) else {}
    classification = bridge_classification_artifact if isinstance(bridge_classification_artifact, dict) else {}
    artifact = {
        "artifact_type": CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_EVIDENCE_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_PROVIDER_PROPOSAL_PRODUCTION_INTEGRATION_VERSION,
        "production_evidence_id": f"{integration_id}:PRODUCTION-EVIDENCE"
        if isinstance(integration_id, str)
        else "INVALID:PRODUCTION-EVIDENCE",
        "integration_reference": integration_id if isinstance(integration_id, str) else "INVALID",
        "provider_id": provider_id if isinstance(provider_id, str) else None,
        "canonical_chain_id": request.get("canonical_chain_id"),
        "provider_proposal_request_reference": request.get("provider_proposal_request_id"),
        "provider_proposal_request_hash": request.get("artifact_hash"),
        "bridge_evidence_reference": evidence.get("bridge_evidence_id"),
        "bridge_evidence_hash": evidence.get("artifact_hash"),
        "bridge_classification_reference": classification.get("bridge_classification_id"),
        "bridge_classification_hash": classification.get("artifact_hash"),
        "clarified_ppp_routed_intent_reference": request.get("clarified_ppp_routed_intent_reference"),
        "clarified_ppp_routed_intent_hash": request.get("clarified_ppp_routed_intent_hash"),
        "selected_interpretation": request.get("selected_interpretation"),
        "confidence": request.get("confidence"),
        "domain_reference": request.get("domain_reference"),
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


def _failed_production_classification_artifact(
    *,
    integration_id: str,
    production_evidence: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_CLASSIFICATION_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_PROVIDER_PROPOSAL_PRODUCTION_INTEGRATION_VERSION,
        "production_classification_id": f"{integration_id}:PRODUCTION-CLASSIFICATION"
        if isinstance(integration_id, str)
        else "INVALID:PRODUCTION-CLASSIFICATION",
        "integration_reference": integration_id if isinstance(integration_id, str) else "INVALID",
        "production_evidence_reference": production_evidence["production_evidence_id"],
        "production_evidence_hash": production_evidence["artifact_hash"],
        "provider_id": production_evidence["provider_id"],
        "canonical_chain_id": production_evidence["canonical_chain_id"],
        "provider_request_packet_type": None,
        "provider_production_input_valid": False,
        "provider_proposal_request_reference": production_evidence["provider_proposal_request_reference"],
        "provider_proposal_request_hash": production_evidence["provider_proposal_request_hash"],
        "provider_necessity_classification": None,
        "selected_interpretation": production_evidence["selected_interpretation"],
        "confidence": production_evidence["confidence"],
        "domain_reference": production_evidence["domain_reference"],
        "classification_status": FAILED_CLOSED,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": created_at,
        "replay_visible": True,
        "failure_reason": production_evidence["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_production_artifact(
    *,
    integration_id: str,
    provider_id: str,
    production_evidence: dict[str, Any],
    production_classification: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_ARTIFACT_V1,
        "runtime_version": AIGOL_CLARIFIED_INTENT_PROVIDER_PROPOSAL_PRODUCTION_INTEGRATION_VERSION,
        "production_id": f"{integration_id}:CLARIFIED-PROVIDER-PRODUCTION"
        if isinstance(integration_id, str)
        else "INVALID:CLARIFIED-PROVIDER-PRODUCTION",
        "integration_id": integration_id if isinstance(integration_id, str) else "INVALID",
        "production_status": FAILED_CLOSED,
        "provider_id": provider_id if isinstance(provider_id, str) else None,
        "provider_request_packet_type": None,
        "provider_proposal_request_reference": production_evidence["provider_proposal_request_reference"],
        "provider_proposal_request_hash": production_evidence["provider_proposal_request_hash"],
        "provider_request_hash": None,
        "production_evidence_reference": production_evidence["production_evidence_id"],
        "production_evidence_hash": production_evidence["artifact_hash"],
        "production_classification_reference": production_classification["production_classification_id"],
        "production_classification_hash": production_classification["artifact_hash"],
        "canonical_chain_id": production_evidence["canonical_chain_id"],
        "clarified_ppp_routed_intent_reference": production_evidence["clarified_ppp_routed_intent_reference"],
        "clarified_ppp_routed_intent_hash": production_evidence["clarified_ppp_routed_intent_hash"],
        "selected_interpretation": production_evidence["selected_interpretation"],
        "clarification_history_hash": None,
        "confidence": production_evidence["confidence"],
        "domain_reference": production_evidence["domain_reference"],
        "provider_necessity_classification": None,
        "proposal_validation_status": None,
        "approval_evidence_status": None,
        "handoff_preparation_status": None,
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
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _returned_artifact(production: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(production, "clarified provider production integration artifact")
    returned = {
        "event_type": "CLARIFIED_PROVIDER_PROPOSAL_PRODUCTION_INTEGRATION_RETURNED",
        "production_reference": production["production_id"],
        "production_hash": production["artifact_hash"],
        "production_status": production["production_status"],
        "provider_id": production["provider_id"],
        "canonical_chain_id": production["canonical_chain_id"],
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": production["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(
    evidence: dict[str, Any],
    classification: dict[str, Any],
    production: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "clarified_provider_proposal_production_evidence_artifact": deepcopy(evidence),
        "clarified_provider_proposal_production_classification_artifact": deepcopy(classification),
        "clarified_provider_proposal_production_artifact": deepcopy(production),
        "clarified_provider_proposal_production_replay": deepcopy(returned),
        "clarified_provider_proposal_production_replay_reference": str(replay_path),
        "production_status": production["production_status"],
        "provider_id": production["provider_id"],
        "provider_request_packet_type": production["provider_request_packet_type"],
        "provider_proposal_request_reference": production["provider_proposal_request_reference"],
        "canonical_chain_id": production["canonical_chain_id"],
        "selected_interpretation": production["selected_interpretation"],
        "domain_reference": production["domain_reference"],
        "proposal_validation_status": production["proposal_validation_status"],
        "approval_evidence_status": production["approval_evidence_status"],
        "handoff_preparation_status": production["handoff_preparation_status"],
        "fail_closed": production["production_status"] == FAILED_CLOSED,
        "failure_reason": production["failure_reason"],
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["clarified_intent_provider_proposal_production_integration_capture_hash"] = replay_hash(capture)
    return capture


def _validate_artifact(artifact: dict[str, Any], expected_type: str, label: str) -> None:
    if not isinstance(artifact, dict) or artifact.get("artifact_type") != expected_type:
        raise FailClosedRuntimeError(f"clarified provider production integration failed closed: {label} missing")
    _verify_artifact_hash(artifact, f"clarified provider production integration {label}")


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
        raise FailClosedRuntimeError("clarified provider production integration replay step ordering mismatch")
    _verify_artifact_hash(artifact, "clarified provider production integration artifact")
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
        raise FailClosedRuntimeError("clarified provider production integration replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("clarified provider production integration replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "clarified provider production integration failed closed"
