"""Route replay-derived cognition intent into Resource Selection-compatible input."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.improvement_intent_cognition_routing_runtime import (
    COGNITION_INTENT_ROUTED,
    COGNITION_ROUTED_INTENT_ARTIFACT_V1,
    COGNITION_ROUTING_CLASSIFICATION_V1,
    COGNITION_ROUTING_EVIDENCE_V1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.unified_resource_selection_runtime import PROVIDER_ROLE


AIGOL_REPLAY_DERIVED_INTENT_RESOURCE_SELECTION_ROUTING_RUNTIME_VERSION = (
    "AIGOL_REPLAY_DERIVED_INTENT_RESOURCE_SELECTION_ROUTING_RUNTIME_V1"
)
RESOURCE_SELECTION_ROUTED_INTENT_V1 = "RESOURCE_SELECTION_ROUTED_INTENT_V1"
RESOURCE_SELECTION_ROUTING_EVIDENCE_V1 = "RESOURCE_SELECTION_ROUTING_EVIDENCE_V1"
RESOURCE_SELECTION_ROUTING_CLASSIFICATION_V1 = "RESOURCE_SELECTION_ROUTING_CLASSIFICATION_V1"
RESOURCE_SELECTION_INTENT_ROUTED = "RESOURCE_SELECTION_INTENT_ROUTED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "resource_selection_routing_evidence_recorded",
    "resource_selection_routing_classification_recorded",
    "resource_selection_routed_intent_recorded",
    "resource_selection_routing_returned",
)

CAPABILITY_BY_INTENT_CLASS = {
    "RUNTIME_HARDENING": "PROPOSAL_GENERATION",
    "CONTEXT_ASSEMBLY_HARDENING": "PROPOSAL_GENERATION",
    "RESOURCE_SELECTION_HARDENING": "PROPOSAL_GENERATION",
    "PPP_CONTRACT_HARDENING": "PROPOSAL_GENERATION",
    "GOVERNANCE_REVIEW": "PROPOSAL_GENERATION",
    "WORKER_FOUNDATION": "PROPOSAL_GENERATION",
    "WORKER_RUNTIME": "PROPOSAL_GENERATION",
    "DOMAIN_MODEL": "PROPOSAL_GENERATION",
    "OPERATOR_WORKFLOW": "PROPOSAL_GENERATION",
    "REPLAY_RECONSTRUCTION": "PROPOSAL_GENERATION",
    "TEST_FIXTURE": "PROPOSAL_GENERATION",
    "DOCUMENTATION_OR_CERTIFICATION": "PROPOSAL_GENERATION",
}


def route_replay_derived_intent_to_resource_selection(
    *,
    routing_id: str,
    cognition_routed_intent_artifact: dict[str, Any],
    cognition_routing_evidence_artifact: dict[str, Any],
    cognition_routing_classification_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    requested_role_type: str = PROVIDER_ROLE,
    provider_necessity_classification: str = "PROVIDER_REQUIRED",
) -> dict[str, Any]:
    """Create source-agnostic Resource Selection input without selecting a Resource."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        routed = deepcopy(cognition_routed_intent_artifact)
        evidence = deepcopy(cognition_routing_evidence_artifact)
        classification = deepcopy(cognition_routing_classification_artifact)
        _validate_inputs(routed=routed, evidence=evidence, classification=classification)
        routing_evidence = _routing_evidence_artifact(
            routing_id=routing_id,
            routed=routed,
            evidence=evidence,
            classification=classification,
            created_at=created_at,
            evidence_status="RESOURCE_SELECTION_ROUTING_EVIDENCE_ACCEPTED",
            failure_reason=None,
        )
        routing_classification = _routing_classification_artifact(
            routing_id=routing_id,
            routing_evidence=routing_evidence,
            routed=routed,
            requested_role_type=requested_role_type,
            provider_necessity_classification=provider_necessity_classification,
            created_at=created_at,
            classification_status="RESOURCE_SELECTION_ROUTING_CLASSIFIED",
            failure_reason=None,
        )
        resource_routed = _resource_selection_routed_intent_artifact(
            routing_id=routing_id,
            routing_evidence=routing_evidence,
            routing_classification=routing_classification,
            routed=routed,
            created_at=created_at,
            routing_status=RESOURCE_SELECTION_INTENT_ROUTED,
            failure_reason=None,
        )
        returned = _returned_artifact(resource_routed)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], routing_evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], routing_classification)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], resource_routed)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(routing_evidence, routing_classification, resource_routed, returned, replay_path)
    except Exception as exc:
        routing_evidence = _failed_routing_evidence_artifact(
            routing_id=routing_id,
            cognition_routed_intent_artifact=cognition_routed_intent_artifact,
            cognition_routing_evidence_artifact=cognition_routing_evidence_artifact,
            cognition_routing_classification_artifact=cognition_routing_classification_artifact,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        routing_classification = _failed_routing_classification_artifact(
            routing_id=routing_id,
            routing_evidence=routing_evidence,
            created_at=created_at,
        )
        resource_routed = _failed_resource_selection_routed_intent_artifact(
            routing_id=routing_id,
            routing_evidence=routing_evidence,
            routing_classification=routing_classification,
            created_at=created_at,
            failure_reason=routing_evidence["failure_reason"],
        )
        returned = _returned_artifact(resource_routed)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], routing_evidence)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], routing_classification)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], resource_routed)
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(routing_evidence, routing_classification, resource_routed, returned, replay_path)


def reconstruct_replay_derived_intent_resource_selection_routing_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct replay-derived intent Resource Selection routing replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("replay-derived Resource Selection routing replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("replay-derived Resource Selection routing replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "replay-derived Resource Selection routing artifact")
        wrappers.append(wrapper)
    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    routed = wrappers[2]["artifact"]
    returned = wrappers[3]["artifact"]
    if classification.get("routing_evidence_reference") != evidence["routing_evidence_id"]:
        raise FailClosedRuntimeError("replay-derived Resource Selection routing evidence reference mismatch")
    if classification.get("routing_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("replay-derived Resource Selection routing evidence hash mismatch")
    if routed.get("routing_classification_reference") != classification["routing_classification_id"]:
        raise FailClosedRuntimeError("replay-derived Resource Selection routing classification reference mismatch")
    if routed.get("routing_classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("replay-derived Resource Selection routing classification hash mismatch")
    if returned.get("resource_selection_routed_intent_reference") != routed["resource_selection_routed_intent_id"]:
        raise FailClosedRuntimeError("replay-derived Resource Selection routing returned reference mismatch")
    if returned.get("resource_selection_routed_intent_hash") != routed["artifact_hash"]:
        raise FailClosedRuntimeError("replay-derived Resource Selection routing returned hash mismatch")
    return {
        "resource_selection_routed_intent_id": routed["resource_selection_routed_intent_id"],
        "routing_status": routed["routing_status"],
        "canonical_chain_id": routed["canonical_chain_id"],
        "workflow_type": routed["resource_selection_input_contract"]["workflow_type"],
        "required_capability": routed["resource_selection_input_contract"]["required_capability"],
        "requested_role_type": routed["resource_selection_input_contract"]["requested_role_type"],
        "domain_id": routed["resource_selection_input_contract"]["domain_id"],
        "intent_source_visible_to_resource_selection": routed["intent_source_visible_to_resource_selection"],
        "source_lineage_preserved": routed["source_lineage_preserved"],
        "failure_reason": routed["failure_reason"],
        "resource_selection_invoked": False,
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


def _validate_inputs(*, routed: dict[str, Any], evidence: dict[str, Any], classification: dict[str, Any]) -> None:
    _validate_artifact(routed, COGNITION_ROUTED_INTENT_ARTIFACT_V1, "cognition routed intent")
    _validate_artifact(evidence, COGNITION_ROUTING_EVIDENCE_V1, "cognition routing evidence")
    _validate_artifact(classification, COGNITION_ROUTING_CLASSIFICATION_V1, "cognition routing classification")
    if routed.get("routing_status") != COGNITION_INTENT_ROUTED:
        raise FailClosedRuntimeError("replay-derived Resource Selection routing failed closed: cognition intent not routed")
    if routed.get("intent_source_visible_to_ppp") is not False:
        raise FailClosedRuntimeError("replay-derived Resource Selection routing failed closed: source visibility leak")
    if routed.get("source_lineage_preserved") is not True:
        raise FailClosedRuntimeError("replay-derived Resource Selection routing failed closed: replay lineage broken")
    if routed.get("routing_evidence_reference") != evidence.get("routing_evidence_id"):
        raise FailClosedRuntimeError("replay-derived Resource Selection routing failed closed: replay lineage broken")
    if routed.get("routing_evidence_hash") != evidence.get("artifact_hash"):
        raise FailClosedRuntimeError("replay-derived Resource Selection routing failed closed: replay lineage broken")
    if routed.get("routing_classification_reference") != classification.get("routing_classification_id"):
        raise FailClosedRuntimeError("replay-derived Resource Selection routing failed closed: replay lineage broken")
    if routed.get("routing_classification_hash") != classification.get("artifact_hash"):
        raise FailClosedRuntimeError("replay-derived Resource Selection routing failed closed: replay lineage broken")
    if classification.get("routing_evidence_reference") != evidence.get("routing_evidence_id"):
        raise FailClosedRuntimeError("replay-derived Resource Selection routing failed closed: replay lineage broken")
    if classification.get("routing_evidence_hash") != evidence.get("artifact_hash"):
        raise FailClosedRuntimeError("replay-derived Resource Selection routing failed closed: replay lineage broken")
    if routed.get("canonical_chain_id") != evidence.get("canonical_chain_id"):
        raise FailClosedRuntimeError("replay-derived Resource Selection routing failed closed: chain continuity failed")
    if routed.get("canonical_chain_id") != classification.get("canonical_chain_id"):
        raise FailClosedRuntimeError("replay-derived Resource Selection routing failed closed: chain continuity failed")
    _require_string(routed.get("normalized_intent"), "normalized_intent")
    _require_string(routed.get("normalized_intent_class"), "normalized_intent_class")
    _require_string(routed.get("affected_domain"), "affected_domain")
    _require_string(routed.get("confidence"), "confidence")


def _routing_evidence_artifact(
    *,
    routing_id: str,
    routed: dict[str, Any],
    evidence: dict[str, Any],
    classification: dict[str, Any],
    created_at: str,
    evidence_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": RESOURCE_SELECTION_ROUTING_EVIDENCE_V1,
        "runtime_version": AIGOL_REPLAY_DERIVED_INTENT_RESOURCE_SELECTION_ROUTING_RUNTIME_VERSION,
        "routing_evidence_id": f"{_require_string(routing_id, 'routing_id')}:RESOURCE-SELECTION-ROUTING-EVIDENCE",
        "routing_reference": routing_id,
        "canonical_chain_id": routed["canonical_chain_id"],
        "cognition_routed_intent_reference": routed["routed_intent_id"],
        "cognition_routed_intent_hash": routed["artifact_hash"],
        "cognition_routing_evidence_reference": evidence["routing_evidence_id"],
        "cognition_routing_evidence_hash": evidence["artifact_hash"],
        "cognition_routing_classification_reference": classification["routing_classification_id"],
        "cognition_routing_classification_hash": classification["artifact_hash"],
        "source_replay_reference": deepcopy(routed["source_replay_reference"]),
        "source_replay_hash": deepcopy(routed["source_replay_hash"]),
        "source_lineage_preserved": True,
        "confidence": routed["confidence"],
        "affected_domain": routed["affected_domain"],
        "evidence_status": evidence_status,
        "resource_selection_invoked": False,
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


def _routing_classification_artifact(
    *,
    routing_id: str,
    routing_evidence: dict[str, Any],
    routed: dict[str, Any],
    requested_role_type: str,
    provider_necessity_classification: str,
    created_at: str,
    classification_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    required_capability = _required_capability(routed["normalized_intent_class"])
    artifact = {
        "artifact_type": RESOURCE_SELECTION_ROUTING_CLASSIFICATION_V1,
        "runtime_version": AIGOL_REPLAY_DERIVED_INTENT_RESOURCE_SELECTION_ROUTING_RUNTIME_VERSION,
        "routing_classification_id": f"{_require_string(routing_id, 'routing_id')}:RESOURCE-SELECTION-ROUTING-CLASSIFICATION",
        "routing_reference": routing_id,
        "routing_evidence_reference": routing_evidence["routing_evidence_id"],
        "routing_evidence_hash": routing_evidence["artifact_hash"],
        "canonical_chain_id": routed["canonical_chain_id"],
        "resource_selection_input_type": "STRUCTURED_RESOURCE_SELECTION_REQUIREMENTS",
        "intent_source_class": "REPLAY_DERIVED_INTENT",
        "source_normalized_for_resource_selection": True,
        "intent_source_visible_to_resource_selection": False,
        "workflow_type": "NATIVE_DEVELOPMENT",
        "required_capability": required_capability,
        "requested_role_type": _require_string(requested_role_type, "requested_role_type"),
        "domain_id": routed["affected_domain"],
        "provider_necessity_classification": _require_string(
            provider_necessity_classification,
            "provider_necessity_classification",
        ),
        "normalized_intent": routed["normalized_intent"],
        "normalized_intent_class": routed["normalized_intent_class"],
        "confidence": routed["confidence"],
        "classification_status": classification_status,
        "resource_selection_invoked": False,
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


def _resource_selection_routed_intent_artifact(
    *,
    routing_id: str,
    routing_evidence: dict[str, Any],
    routing_classification: dict[str, Any],
    routed: dict[str, Any],
    created_at: str,
    routing_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": RESOURCE_SELECTION_ROUTED_INTENT_V1,
        "runtime_version": AIGOL_REPLAY_DERIVED_INTENT_RESOURCE_SELECTION_ROUTING_RUNTIME_VERSION,
        "resource_selection_routed_intent_id": f"{_require_string(routing_id, 'routing_id')}:RESOURCE-SELECTION-ROUTED-INTENT",
        "routing_id": routing_id,
        "routing_status": routing_status,
        "canonical_chain_id": routed["canonical_chain_id"],
        "resource_selection_input_type": routing_classification["resource_selection_input_type"],
        "normalized_intent": routing_classification["normalized_intent"],
        "normalized_intent_class": routing_classification["normalized_intent_class"],
        "confidence": routing_classification["confidence"],
        "source_lineage_preserved": True,
        "intent_source": routed["intent_source"],
        "intent_source_visible_to_resource_selection": False,
        "resource_selection_input_contract": {
            "intent_reference": f"{routing_id}:RESOURCE-SELECTION-ROUTED-INTENT",
            "workflow_type": routing_classification["workflow_type"],
            "required_capability": routing_classification["required_capability"],
            "requested_role_type": routing_classification["requested_role_type"],
            "domain_id": routing_classification["domain_id"],
            "provider_necessity_classification": routing_classification["provider_necessity_classification"],
            "confidence": routing_classification["confidence"],
            "intent_source_visible_to_resource_selection": False,
        },
        "routing_evidence_reference": routing_evidence["routing_evidence_id"],
        "routing_evidence_hash": routing_evidence["artifact_hash"],
        "routing_classification_reference": routing_classification["routing_classification_id"],
        "routing_classification_hash": routing_classification["artifact_hash"],
        "source_cognition_routed_intent_reference": routed["routed_intent_id"],
        "source_cognition_routed_intent_hash": routed["artifact_hash"],
        "source_replay_reference": deepcopy(routed["source_replay_reference"]),
        "source_replay_hash": deepcopy(routed["source_replay_hash"]),
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
    cognition_routed_intent_artifact: dict[str, Any],
    cognition_routing_evidence_artifact: dict[str, Any],
    cognition_routing_classification_artifact: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": RESOURCE_SELECTION_ROUTING_EVIDENCE_V1,
        "runtime_version": AIGOL_REPLAY_DERIVED_INTENT_RESOURCE_SELECTION_ROUTING_RUNTIME_VERSION,
        "routing_evidence_id": f"{routing_id}:RESOURCE-SELECTION-ROUTING-EVIDENCE"
        if isinstance(routing_id, str)
        else "INVALID_ROUTING:RESOURCE-SELECTION-ROUTING-EVIDENCE",
        "routing_reference": routing_id if isinstance(routing_id, str) else "INVALID_ROUTING",
        "canonical_chain_id": cognition_routed_intent_artifact.get("canonical_chain_id")
        if isinstance(cognition_routed_intent_artifact, dict)
        else None,
        "cognition_routed_intent_reference": cognition_routed_intent_artifact.get("routed_intent_id")
        if isinstance(cognition_routed_intent_artifact, dict)
        else None,
        "cognition_routed_intent_hash": cognition_routed_intent_artifact.get("artifact_hash")
        if isinstance(cognition_routed_intent_artifact, dict)
        else None,
        "cognition_routing_evidence_reference": cognition_routing_evidence_artifact.get("routing_evidence_id")
        if isinstance(cognition_routing_evidence_artifact, dict)
        else None,
        "cognition_routing_evidence_hash": cognition_routing_evidence_artifact.get("artifact_hash")
        if isinstance(cognition_routing_evidence_artifact, dict)
        else None,
        "cognition_routing_classification_reference": cognition_routing_classification_artifact.get(
            "routing_classification_id"
        )
        if isinstance(cognition_routing_classification_artifact, dict)
        else None,
        "cognition_routing_classification_hash": cognition_routing_classification_artifact.get("artifact_hash")
        if isinstance(cognition_routing_classification_artifact, dict)
        else None,
        "source_replay_reference": [],
        "source_replay_hash": [],
        "source_lineage_preserved": False,
        "confidence": cognition_routed_intent_artifact.get("confidence")
        if isinstance(cognition_routed_intent_artifact, dict)
        else None,
        "affected_domain": cognition_routed_intent_artifact.get("affected_domain")
        if isinstance(cognition_routed_intent_artifact, dict)
        else None,
        "evidence_status": FAILED_CLOSED,
        "resource_selection_invoked": False,
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


def _failed_routing_classification_artifact(
    *,
    routing_id: str,
    routing_evidence: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": RESOURCE_SELECTION_ROUTING_CLASSIFICATION_V1,
        "runtime_version": AIGOL_REPLAY_DERIVED_INTENT_RESOURCE_SELECTION_ROUTING_RUNTIME_VERSION,
        "routing_classification_id": f"{routing_id}:RESOURCE-SELECTION-ROUTING-CLASSIFICATION"
        if isinstance(routing_id, str)
        else "INVALID_ROUTING:RESOURCE-SELECTION-ROUTING-CLASSIFICATION",
        "routing_reference": routing_id if isinstance(routing_id, str) else "INVALID_ROUTING",
        "routing_evidence_reference": routing_evidence["routing_evidence_id"],
        "routing_evidence_hash": routing_evidence["artifact_hash"],
        "canonical_chain_id": routing_evidence["canonical_chain_id"],
        "resource_selection_input_type": None,
        "intent_source_class": "REPLAY_DERIVED_INTENT",
        "source_normalized_for_resource_selection": False,
        "intent_source_visible_to_resource_selection": False,
        "workflow_type": None,
        "required_capability": None,
        "requested_role_type": None,
        "domain_id": routing_evidence["affected_domain"],
        "provider_necessity_classification": None,
        "normalized_intent": None,
        "normalized_intent_class": None,
        "confidence": routing_evidence["confidence"],
        "classification_status": FAILED_CLOSED,
        "resource_selection_invoked": False,
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": created_at,
        "replay_visible": True,
        "failure_reason": routing_evidence["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_resource_selection_routed_intent_artifact(
    *,
    routing_id: str,
    routing_evidence: dict[str, Any],
    routing_classification: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": RESOURCE_SELECTION_ROUTED_INTENT_V1,
        "runtime_version": AIGOL_REPLAY_DERIVED_INTENT_RESOURCE_SELECTION_ROUTING_RUNTIME_VERSION,
        "resource_selection_routed_intent_id": f"{routing_id}:RESOURCE-SELECTION-ROUTED-INTENT"
        if isinstance(routing_id, str)
        else "INVALID_ROUTING:RESOURCE-SELECTION-ROUTED-INTENT",
        "routing_id": routing_id if isinstance(routing_id, str) else "INVALID_ROUTING",
        "routing_status": FAILED_CLOSED,
        "canonical_chain_id": routing_evidence["canonical_chain_id"],
        "resource_selection_input_type": None,
        "normalized_intent": None,
        "normalized_intent_class": None,
        "confidence": routing_evidence["confidence"],
        "source_lineage_preserved": False,
        "intent_source": "REPLAY_GAP_DETECTION",
        "intent_source_visible_to_resource_selection": False,
        "resource_selection_input_contract": None,
        "routing_evidence_reference": routing_evidence["routing_evidence_id"],
        "routing_evidence_hash": routing_evidence["artifact_hash"],
        "routing_classification_reference": routing_classification["routing_classification_id"],
        "routing_classification_hash": routing_classification["artifact_hash"],
        "source_cognition_routed_intent_reference": routing_evidence["cognition_routed_intent_reference"],
        "source_cognition_routed_intent_hash": routing_evidence["cognition_routed_intent_hash"],
        "source_replay_reference": [],
        "source_replay_hash": [],
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
    _verify_artifact_hash(routed, "replay-derived Resource Selection routing artifact")
    artifact = {
        "event_type": "REPLAY_DERIVED_RESOURCE_SELECTION_ROUTING_RETURNED",
        "resource_selection_routed_intent_reference": routed["resource_selection_routed_intent_id"],
        "resource_selection_routed_intent_hash": routed["artifact_hash"],
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
        "resource_selection_routing_evidence_artifact": deepcopy(evidence),
        "resource_selection_routing_classification_artifact": deepcopy(classification),
        "resource_selection_routed_intent_artifact": deepcopy(routed),
        "resource_selection_routing_replay": deepcopy(returned),
        "resource_selection_routing_replay_reference": str(replay_path),
        "routing_status": routed["routing_status"],
        "canonical_chain_id": routed["canonical_chain_id"],
        "resource_selection_input_type": routed["resource_selection_input_type"],
        "resource_selection_input_contract": deepcopy(routed["resource_selection_input_contract"]),
        "intent_source_visible_to_resource_selection": routed["intent_source_visible_to_resource_selection"],
        "source_lineage_preserved": routed["source_lineage_preserved"],
        "fail_closed": routed["routing_status"] == FAILED_CLOSED,
        "failure_reason": routed["failure_reason"],
        "resource_selection_invoked": False,
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["replay_derived_intent_resource_selection_routing_capture_hash"] = replay_hash(capture)
    return capture


def _validate_artifact(artifact: dict[str, Any], expected_type: str, label: str) -> None:
    if not isinstance(artifact, dict) or artifact.get("artifact_type") != expected_type:
        raise FailClosedRuntimeError(f"replay-derived Resource Selection routing failed closed: {label} missing")
    _verify_artifact_hash(artifact, f"replay-derived Resource Selection routing {label}")


def _required_capability(normalized_intent_class: str) -> str:
    key = _require_string(normalized_intent_class, "normalized_intent_class").strip().upper()
    if key not in CAPABILITY_BY_INTENT_CLASS:
        raise FailClosedRuntimeError("replay-derived Resource Selection routing failed closed: classification ambiguous")
    return CAPABILITY_BY_INTENT_CLASS[key]


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"replay-derived Resource Selection routing failed closed: {label} missing")
    return value


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("replay-derived Resource Selection routing replay step ordering mismatch")
    _verify_artifact_hash(artifact, "replay-derived Resource Selection routing artifact")
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
        raise FailClosedRuntimeError("replay-derived Resource Selection routing replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("replay-derived Resource Selection routing replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "replay-derived Resource Selection routing failed closed"
