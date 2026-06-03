"""Route replay-derived improvement intent into cognition-compatible input."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_to_improvement_intent_runtime import (
    IMPROVEMENT_INTENT_ARTIFACT_V1,
    IMPROVEMENT_INTENT_CLASSIFICATION_V1,
    IMPROVEMENT_INTENT_CREATED,
    IMPROVEMENT_INTENT_EVIDENCE_V1,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_IMPROVEMENT_INTENT_COGNITION_ROUTING_RUNTIME_VERSION = (
    "AIGOL_IMPROVEMENT_INTENT_COGNITION_ROUTING_RUNTIME_V1"
)
COGNITION_ROUTED_INTENT_ARTIFACT_V1 = "COGNITION_ROUTED_INTENT_ARTIFACT_V1"
COGNITION_ROUTING_EVIDENCE_V1 = "COGNITION_ROUTING_EVIDENCE_V1"
COGNITION_ROUTING_CLASSIFICATION_V1 = "COGNITION_ROUTING_CLASSIFICATION_V1"
COGNITION_INTENT_ROUTED = "COGNITION_INTENT_ROUTED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "cognition_routing_evidence_recorded",
    "cognition_routing_classification_recorded",
    "cognition_routed_intent_recorded",
    "cognition_routing_returned",
)


def route_improvement_intent_to_cognition(
    *,
    routing_id: str,
    improvement_intent_artifact: dict[str, Any],
    improvement_intent_evidence_artifact: dict[str, Any],
    improvement_intent_classification_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create source-agnostic cognition input from replay-derived improvement intent."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        intent = deepcopy(improvement_intent_artifact)
        evidence = deepcopy(improvement_intent_evidence_artifact)
        classification = deepcopy(improvement_intent_classification_artifact)
        _validate_inputs(intent=intent, evidence=evidence, classification=classification)
        routing_evidence = _routing_evidence_artifact(
            routing_id=routing_id,
            intent=intent,
            evidence=evidence,
            classification=classification,
            created_at=created_at,
            evidence_status="COGNITION_ROUTING_EVIDENCE_ACCEPTED",
            failure_reason=None,
        )
        routing_classification = _routing_classification_artifact(
            routing_id=routing_id,
            routing_evidence=routing_evidence,
            intent=intent,
            created_at=created_at,
            classification_status="COGNITION_ROUTING_CLASSIFIED",
            failure_reason=None,
        )
        routed = _routed_intent_artifact(
            routing_id=routing_id,
            routing_evidence=routing_evidence,
            routing_classification=routing_classification,
            intent=intent,
            created_at=created_at,
            routing_status=COGNITION_INTENT_ROUTED,
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
            improvement_intent_artifact=improvement_intent_artifact,
            improvement_intent_evidence_artifact=improvement_intent_evidence_artifact,
            improvement_intent_classification_artifact=improvement_intent_classification_artifact,
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


def reconstruct_improvement_intent_cognition_routing_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct improvement-intent cognition routing replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("improvement intent cognition routing replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("improvement intent cognition routing replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "improvement intent cognition routing artifact")
        wrappers.append(wrapper)
    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    routed = wrappers[2]["artifact"]
    returned = wrappers[3]["artifact"]
    if classification.get("routing_evidence_reference") != evidence["routing_evidence_id"]:
        raise FailClosedRuntimeError("improvement intent cognition routing evidence reference mismatch")
    if classification.get("routing_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("improvement intent cognition routing evidence hash mismatch")
    if routed.get("routing_classification_reference") != classification["routing_classification_id"]:
        raise FailClosedRuntimeError("improvement intent cognition routing classification reference mismatch")
    if routed.get("routing_classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("improvement intent cognition routing classification hash mismatch")
    if returned.get("routed_intent_reference") != routed["routed_intent_id"]:
        raise FailClosedRuntimeError("improvement intent cognition routing returned reference mismatch")
    if returned.get("routed_intent_hash") != routed["artifact_hash"]:
        raise FailClosedRuntimeError("improvement intent cognition routing returned hash mismatch")
    return {
        "routed_intent_id": routed["routed_intent_id"],
        "routing_status": routed["routing_status"],
        "canonical_chain_id": routed["canonical_chain_id"],
        "cognition_input_type": routed["cognition_input_type"],
        "normalized_intent": routed["normalized_intent"],
        "intent_source_visible_to_ppp": routed["intent_source_visible_to_ppp"],
        "source_lineage_preserved": routed["source_lineage_preserved"],
        "confidence": routed["confidence"],
        "affected_domain": routed["affected_domain"],
        "failure_reason": routed["failure_reason"],
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


def _validate_inputs(*, intent: dict[str, Any], evidence: dict[str, Any], classification: dict[str, Any]) -> None:
    _validate_artifact(intent, IMPROVEMENT_INTENT_ARTIFACT_V1, "improvement intent")
    _validate_artifact(evidence, IMPROVEMENT_INTENT_EVIDENCE_V1, "improvement intent evidence")
    _validate_artifact(classification, IMPROVEMENT_INTENT_CLASSIFICATION_V1, "improvement intent classification")
    if intent.get("intent_status") != IMPROVEMENT_INTENT_CREATED:
        raise FailClosedRuntimeError("improvement intent cognition routing failed closed: improvement intent not created")
    if intent.get("ppp_eligible") is not True:
        raise FailClosedRuntimeError("improvement intent cognition routing failed closed: improvement intent not ppp eligible")
    if intent.get("intent_evidence_reference") != evidence.get("intent_evidence_id"):
        raise FailClosedRuntimeError("improvement intent cognition routing failed closed: replay lineage broken")
    if intent.get("intent_evidence_hash") != evidence.get("artifact_hash"):
        raise FailClosedRuntimeError("improvement intent cognition routing failed closed: replay lineage broken")
    if intent.get("intent_classification_reference") != classification.get("intent_classification_id"):
        raise FailClosedRuntimeError("improvement intent cognition routing failed closed: replay lineage broken")
    if intent.get("intent_classification_hash") != classification.get("artifact_hash"):
        raise FailClosedRuntimeError("improvement intent cognition routing failed closed: replay lineage broken")
    if classification.get("intent_evidence_reference") != evidence.get("intent_evidence_id"):
        raise FailClosedRuntimeError("improvement intent cognition routing failed closed: replay lineage broken")
    if classification.get("intent_evidence_hash") != evidence.get("artifact_hash"):
        raise FailClosedRuntimeError("improvement intent cognition routing failed closed: replay lineage broken")
    if intent.get("canonical_chain_id") != evidence.get("canonical_chain_id"):
        raise FailClosedRuntimeError("improvement intent cognition routing failed closed: chain continuity failed")
    if intent.get("canonical_chain_id") != classification.get("canonical_chain_id"):
        raise FailClosedRuntimeError("improvement intent cognition routing failed closed: chain continuity failed")
    _require_string(intent.get("confidence"), "confidence")
    _require_string(intent.get("affected_domain"), "affected_domain")
    _require_string(intent.get("intent_summary"), "intent_summary")


def _routing_evidence_artifact(
    *,
    routing_id: str,
    intent: dict[str, Any],
    evidence: dict[str, Any],
    classification: dict[str, Any],
    created_at: str,
    evidence_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": COGNITION_ROUTING_EVIDENCE_V1,
        "runtime_version": AIGOL_IMPROVEMENT_INTENT_COGNITION_ROUTING_RUNTIME_VERSION,
        "routing_evidence_id": f"{_require_string(routing_id, 'routing_id')}:COGNITION-ROUTING-EVIDENCE",
        "routing_reference": routing_id,
        "canonical_chain_id": intent["canonical_chain_id"],
        "improvement_intent_reference": intent["improvement_intent_id"],
        "improvement_intent_hash": intent["artifact_hash"],
        "improvement_intent_evidence_reference": evidence["intent_evidence_id"],
        "improvement_intent_evidence_hash": evidence["artifact_hash"],
        "improvement_intent_classification_reference": classification["intent_classification_id"],
        "improvement_intent_classification_hash": classification["artifact_hash"],
        "source_replay_reference": deepcopy(intent["source_replay_reference"]),
        "source_replay_hash": deepcopy(intent["source_replay_hash"]),
        "source_lineage_preserved": True,
        "confidence": intent["confidence"],
        "affected_domain": intent["affected_domain"],
        "evidence_status": evidence_status,
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
    intent: dict[str, Any],
    created_at: str,
    classification_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": COGNITION_ROUTING_CLASSIFICATION_V1,
        "runtime_version": AIGOL_IMPROVEMENT_INTENT_COGNITION_ROUTING_RUNTIME_VERSION,
        "routing_classification_id": f"{_require_string(routing_id, 'routing_id')}:COGNITION-ROUTING-CLASSIFICATION",
        "routing_reference": routing_id,
        "routing_evidence_reference": routing_evidence["routing_evidence_id"],
        "routing_evidence_hash": routing_evidence["artifact_hash"],
        "canonical_chain_id": intent["canonical_chain_id"],
        "cognition_input_type": "STRUCTURED_INTENT",
        "intent_source_class": "REPLAY_DERIVED_INTENT",
        "source_normalized_for_cognition": True,
        "intent_source_visible_to_ppp": False,
        "normalized_intent": intent["intent_summary"],
        "normalized_intent_class": intent["improvement_class"],
        "affected_domain": intent["affected_domain"],
        "affected_layer": intent["affected_layer"],
        "confidence": intent["confidence"],
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


def _routed_intent_artifact(
    *,
    routing_id: str,
    routing_evidence: dict[str, Any],
    routing_classification: dict[str, Any],
    intent: dict[str, Any],
    created_at: str,
    routing_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": COGNITION_ROUTED_INTENT_ARTIFACT_V1,
        "runtime_version": AIGOL_IMPROVEMENT_INTENT_COGNITION_ROUTING_RUNTIME_VERSION,
        "routed_intent_id": f"{_require_string(routing_id, 'routing_id')}:COGNITION-ROUTED-INTENT",
        "routing_id": routing_id,
        "routing_status": routing_status,
        "canonical_chain_id": intent["canonical_chain_id"],
        "cognition_input_type": routing_classification["cognition_input_type"],
        "normalized_intent": routing_classification["normalized_intent"],
        "normalized_intent_class": routing_classification["normalized_intent_class"],
        "affected_domain": routing_classification["affected_domain"],
        "affected_layer": routing_classification["affected_layer"],
        "confidence": routing_classification["confidence"],
        "human_review_required": intent["human_review_required"],
        "high_risk_domain": intent["high_risk_domain"],
        "source_lineage_preserved": True,
        "intent_source": intent["intent_source"],
        "intent_source_visible_to_ppp": False,
        "ppp_input_contract": {
            "intent_reference": f"{routing_id}:COGNITION-ROUTED-INTENT",
            "normalized_intent": routing_classification["normalized_intent"],
            "normalized_intent_class": routing_classification["normalized_intent_class"],
            "affected_domain": routing_classification["affected_domain"],
            "confidence": routing_classification["confidence"],
            "intent_source_visible_to_ppp": False,
        },
        "routing_evidence_reference": routing_evidence["routing_evidence_id"],
        "routing_evidence_hash": routing_evidence["artifact_hash"],
        "routing_classification_reference": routing_classification["routing_classification_id"],
        "routing_classification_hash": routing_classification["artifact_hash"],
        "source_improvement_intent_reference": intent["improvement_intent_id"],
        "source_improvement_intent_hash": intent["artifact_hash"],
        "source_replay_reference": deepcopy(intent["source_replay_reference"]),
        "source_replay_hash": deepcopy(intent["source_replay_hash"]),
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
    improvement_intent_artifact: dict[str, Any],
    improvement_intent_evidence_artifact: dict[str, Any],
    improvement_intent_classification_artifact: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": COGNITION_ROUTING_EVIDENCE_V1,
        "runtime_version": AIGOL_IMPROVEMENT_INTENT_COGNITION_ROUTING_RUNTIME_VERSION,
        "routing_evidence_id": f"{routing_id}:COGNITION-ROUTING-EVIDENCE" if isinstance(routing_id, str) else "INVALID_ROUTING:COGNITION-ROUTING-EVIDENCE",
        "routing_reference": routing_id if isinstance(routing_id, str) else "INVALID_ROUTING",
        "canonical_chain_id": improvement_intent_artifact.get("canonical_chain_id")
        if isinstance(improvement_intent_artifact, dict)
        else None,
        "improvement_intent_reference": improvement_intent_artifact.get("improvement_intent_id")
        if isinstance(improvement_intent_artifact, dict)
        else None,
        "improvement_intent_hash": improvement_intent_artifact.get("artifact_hash")
        if isinstance(improvement_intent_artifact, dict)
        else None,
        "improvement_intent_evidence_reference": improvement_intent_evidence_artifact.get("intent_evidence_id")
        if isinstance(improvement_intent_evidence_artifact, dict)
        else None,
        "improvement_intent_evidence_hash": improvement_intent_evidence_artifact.get("artifact_hash")
        if isinstance(improvement_intent_evidence_artifact, dict)
        else None,
        "improvement_intent_classification_reference": improvement_intent_classification_artifact.get(
            "intent_classification_id"
        )
        if isinstance(improvement_intent_classification_artifact, dict)
        else None,
        "improvement_intent_classification_hash": improvement_intent_classification_artifact.get("artifact_hash")
        if isinstance(improvement_intent_classification_artifact, dict)
        else None,
        "source_replay_reference": [],
        "source_replay_hash": [],
        "source_lineage_preserved": False,
        "confidence": improvement_intent_artifact.get("confidence") if isinstance(improvement_intent_artifact, dict) else None,
        "affected_domain": improvement_intent_artifact.get("affected_domain") if isinstance(improvement_intent_artifact, dict) else None,
        "evidence_status": FAILED_CLOSED,
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
        "artifact_type": COGNITION_ROUTING_CLASSIFICATION_V1,
        "runtime_version": AIGOL_IMPROVEMENT_INTENT_COGNITION_ROUTING_RUNTIME_VERSION,
        "routing_classification_id": f"{routing_id}:COGNITION-ROUTING-CLASSIFICATION"
        if isinstance(routing_id, str)
        else "INVALID_ROUTING:COGNITION-ROUTING-CLASSIFICATION",
        "routing_reference": routing_id if isinstance(routing_id, str) else "INVALID_ROUTING",
        "routing_evidence_reference": routing_evidence["routing_evidence_id"],
        "routing_evidence_hash": routing_evidence["artifact_hash"],
        "canonical_chain_id": routing_evidence["canonical_chain_id"],
        "cognition_input_type": None,
        "intent_source_class": "REPLAY_DERIVED_INTENT",
        "source_normalized_for_cognition": False,
        "intent_source_visible_to_ppp": False,
        "normalized_intent": None,
        "normalized_intent_class": None,
        "affected_domain": routing_evidence["affected_domain"],
        "affected_layer": None,
        "confidence": routing_evidence["confidence"],
        "classification_status": FAILED_CLOSED,
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


def _failed_routed_intent_artifact(
    *,
    routing_id: str,
    routing_evidence: dict[str, Any],
    routing_classification: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": COGNITION_ROUTED_INTENT_ARTIFACT_V1,
        "runtime_version": AIGOL_IMPROVEMENT_INTENT_COGNITION_ROUTING_RUNTIME_VERSION,
        "routed_intent_id": f"{routing_id}:COGNITION-ROUTED-INTENT" if isinstance(routing_id, str) else "INVALID_ROUTING:COGNITION-ROUTED-INTENT",
        "routing_id": routing_id if isinstance(routing_id, str) else "INVALID_ROUTING",
        "routing_status": FAILED_CLOSED,
        "canonical_chain_id": routing_evidence["canonical_chain_id"],
        "cognition_input_type": None,
        "normalized_intent": None,
        "normalized_intent_class": None,
        "affected_domain": routing_evidence["affected_domain"],
        "affected_layer": None,
        "confidence": routing_evidence["confidence"],
        "human_review_required": True,
        "high_risk_domain": False,
        "source_lineage_preserved": False,
        "intent_source": "REPLAY_GAP_DETECTION",
        "intent_source_visible_to_ppp": False,
        "ppp_input_contract": None,
        "routing_evidence_reference": routing_evidence["routing_evidence_id"],
        "routing_evidence_hash": routing_evidence["artifact_hash"],
        "routing_classification_reference": routing_classification["routing_classification_id"],
        "routing_classification_hash": routing_classification["artifact_hash"],
        "source_improvement_intent_reference": routing_evidence["improvement_intent_reference"],
        "source_improvement_intent_hash": routing_evidence["improvement_intent_hash"],
        "source_replay_reference": [],
        "source_replay_hash": [],
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
    _verify_artifact_hash(routed, "improvement intent cognition routing artifact")
    artifact = {
        "event_type": "IMPROVEMENT_INTENT_COGNITION_ROUTING_RETURNED",
        "routed_intent_reference": routed["routed_intent_id"],
        "routed_intent_hash": routed["artifact_hash"],
        "routing_status": routed["routing_status"],
        "canonical_chain_id": routed["canonical_chain_id"],
        "cognition_input_type": routed["cognition_input_type"],
        "normalized_intent": routed["normalized_intent"],
        "intent_source_visible_to_ppp": routed["intent_source_visible_to_ppp"],
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
        "cognition_routing_evidence_artifact": deepcopy(evidence),
        "cognition_routing_classification_artifact": deepcopy(classification),
        "cognition_routed_intent_artifact": deepcopy(routed),
        "cognition_routing_replay": deepcopy(returned),
        "cognition_routing_replay_reference": str(replay_path),
        "routing_status": routed["routing_status"],
        "canonical_chain_id": routed["canonical_chain_id"],
        "cognition_input_type": routed["cognition_input_type"],
        "normalized_intent": routed["normalized_intent"],
        "intent_source_visible_to_ppp": routed["intent_source_visible_to_ppp"],
        "source_lineage_preserved": routed["source_lineage_preserved"],
        "fail_closed": routed["routing_status"] == FAILED_CLOSED,
        "failure_reason": routed["failure_reason"],
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["improvement_intent_cognition_routing_capture_hash"] = replay_hash(capture)
    return capture


def _validate_artifact(artifact: dict[str, Any], expected_type: str, label: str) -> None:
    if not isinstance(artifact, dict) or artifact.get("artifact_type") != expected_type:
        raise FailClosedRuntimeError(f"improvement intent cognition routing failed closed: {label} missing")
    _verify_artifact_hash(artifact, f"improvement intent cognition routing {label}")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"improvement intent cognition routing failed closed: {label} missing")
    return value


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("improvement intent cognition routing replay step ordering mismatch")
    _verify_artifact_hash(artifact, "improvement intent cognition routing artifact")
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
        raise FailClosedRuntimeError("improvement intent cognition routing replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("improvement intent cognition routing replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "improvement intent cognition routing failed closed"
