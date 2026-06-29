"""Deterministic Product 1 decision packet runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.product1_workflow_foundation import (
    PRODUCT1_IDENTITY,
    PRODUCT1_WORKFLOW_FOUNDATION_ARTIFACT_V1,
    WORKFLOW_READY_FOR_DECISION_PACKET,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PRODUCT1_DECISION_PACKET_RUNTIME_VERSION = "G3_03_IMPLEMENTATION_PHASE_2_DECISION_PACKET_RUNTIME_V1"
PRODUCT1_DECISION_PACKET_ARTIFACT_V1 = "PRODUCT1_DECISION_PACKET_ARTIFACT_V1"

PACKET_CREATED = "PACKET_CREATED"
FAILED_CLOSED = "FAILED_CLOSED"

EVENT_DECISION_PACKET_CREATED = "product1_decision_packet_created"

GOVERNANCE_ALLOWED = {
    "GOVERNANCE_PASSED",
}

NON_AUTHORITY_FLAGS = (
    "provider_invoked",
    "worker_invoked",
    "approval_created",
    "authorization_created",
    "execution_requested",
    "repository_mutated",
    "deployment_requested",
    "external_integration_invoked",
)


def create_product1_decision_packet(
    *,
    packet_id: str,
    workflow_artifact: dict[str, Any],
    evidence_references: list[dict[str, Any]],
    assumptions: list[dict[str, Any]],
    risks: list[dict[str, Any]],
    uncertainties: list[dict[str, Any]],
    recommendation_summary: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create a deterministic non-authoritative Product 1 decision packet."""

    workflow = _validated_workflow_artifact(workflow_artifact)
    if workflow["workflow_status"] != WORKFLOW_READY_FOR_DECISION_PACKET:
        raise FailClosedRuntimeError("Product 1 decision packet failed closed: workflow is not packet-ready")
    if workflow["governance_checkpoint_status"] not in GOVERNANCE_ALLOWED:
        raise FailClosedRuntimeError("Product 1 decision packet failed closed: governance status is not passed")
    evidence = _normalize_evidence_references(evidence_references)
    normalized_assumptions = _normalize_named_items(assumptions, "assumption")
    normalized_risks = _normalize_named_items(risks, "risk")
    normalized_uncertainties = _normalize_named_items(uncertainties, "uncertainty")
    recommendation = _normalize_recommendation_summary(recommendation_summary)
    event = _event(
        event_index=0,
        event_type=EVENT_DECISION_PACKET_CREATED,
        occurred_at=created_at,
        previous_event_hash="",
        event_payload={
            "packet_id": _require_string(packet_id, "packet_id"),
            "workflow_id": workflow["workflow_id"],
            "acli_session_id": workflow["acli_session_id"],
            "originating_turn_id": workflow["originating_turn_id"],
            "canonical_semantic_artifact_hash": workflow["canonical_semantic_artifact_hash"],
            "evidence_reference_count": len(evidence),
        },
    )
    artifact = {
        "artifact_type": PRODUCT1_DECISION_PACKET_ARTIFACT_V1,
        "runtime_version": PRODUCT1_DECISION_PACKET_RUNTIME_VERSION,
        "migration_batch_id": "G3_03_IMPLEMENTATION_PHASE_2_DECISION_PACKET_RUNTIME_V1",
        "product_identity": PRODUCT1_IDENTITY,
        "packet_id": _require_string(packet_id, "packet_id"),
        "packet_status": PACKET_CREATED,
        "workflow_id": workflow["workflow_id"],
        "workflow_hash": workflow["artifact_hash"],
        "acli_session_id": workflow["acli_session_id"],
        "originating_conversation_id": workflow["originating_conversation_id"],
        "originating_turn_id": workflow["originating_turn_id"],
        "originating_turn_hash": workflow["originating_turn_hash"],
        "canonical_semantic_artifact_reference": workflow["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": workflow["canonical_semantic_artifact_hash"],
        "evidence_references": evidence,
        "evidence_reference_count": len(evidence),
        "evidence_aggregation_hash": replay_hash(evidence),
        "assumptions": normalized_assumptions,
        "assumption_count": len(normalized_assumptions),
        "assumptions_hash": replay_hash(normalized_assumptions),
        "risks": normalized_risks,
        "risk_count": len(normalized_risks),
        "risks_hash": replay_hash(normalized_risks),
        "uncertainties": normalized_uncertainties,
        "uncertainty_count": len(normalized_uncertainties),
        "uncertainties_hash": replay_hash(normalized_uncertainties),
        "recommendation_summary": recommendation,
        "recommendation_summary_hash": replay_hash(recommendation),
        "governance_status": workflow["governance_checkpoint_status"],
        "operator_review_status": workflow["operator_review_status"],
        "replay_lineage": _packet_replay_lineage(workflow, evidence),
        "rollback_reference": workflow["rollback_reference"],
        "source_workflow": deepcopy(workflow),
        "decision_packet_identity_created": True,
        "csa_bound": True,
        "evidence_aggregated": True,
        "assumptions_recorded": True,
        "risks_recorded": True,
        "uncertainties_recorded": True,
        "recommendation_aggregated": True,
        "non_authoritative": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "external_integration_invoked": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
        "event": event,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _persist_step(Path(replay_dir), 0, EVENT_DECISION_PACKET_CREATED, artifact)
    return _capture(artifact, Path(replay_dir))


def reconstruct_product1_decision_packet_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate Product 1 decision packet replay."""

    replay_path = Path(replay_dir)
    wrappers = [_load_verified_wrapper(path) for path in sorted(replay_path.glob("*.json"))]
    if not wrappers:
        raise FailClosedRuntimeError("Product 1 decision packet failed closed: replay is empty")
    for index, wrapper in enumerate(wrappers):
        if wrapper.get("replay_index") != index:
            raise FailClosedRuntimeError("Product 1 decision packet replay ordering mismatch")
    artifact = _validated_decision_packet_artifact(wrappers[-1]["artifact"])
    event = artifact.get("event")
    if not isinstance(event, dict) or event.get("event_index") != 0:
        raise FailClosedRuntimeError("Product 1 decision packet event mismatch")
    _verify_hash_field(event, "event_hash", "Product 1 decision packet event hash mismatch")
    return {
        "packet_id": artifact["packet_id"],
        "packet_status": artifact["packet_status"],
        "product_identity": artifact["product_identity"],
        "workflow_id": artifact["workflow_id"],
        "acli_session_id": artifact["acli_session_id"],
        "originating_turn_id": artifact["originating_turn_id"],
        "canonical_semantic_artifact_reference": artifact["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": artifact["canonical_semantic_artifact_hash"],
        "evidence_reference_count": artifact["evidence_reference_count"],
        "assumption_count": artifact["assumption_count"],
        "risk_count": artifact["risk_count"],
        "uncertainty_count": artifact["uncertainty_count"],
        "recommendation_summary_hash": artifact["recommendation_summary_hash"],
        "governance_status": artifact["governance_status"],
        "replay_lineage_count": len(artifact["replay_lineage"]),
        "rollback_reference": artifact["rollback_reference"],
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "external_integration_invoked": False,
        "replay_visible": True,
        "artifact_hash": artifact["artifact_hash"],
        "replay_hash": replay_hash(wrappers),
    }


def _validated_workflow_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("Product 1 decision packet failed closed: workflow artifact must be object")
    if artifact.get("artifact_type") != PRODUCT1_WORKFLOW_FOUNDATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("Product 1 decision packet failed closed: invalid workflow artifact")
    _verify_hash_field(artifact, "artifact_hash", "Product 1 decision packet workflow hash mismatch")
    for flag in NON_AUTHORITY_FLAGS:
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"Product 1 decision packet failed closed: {flag} must be false")
    _require_hash(artifact.get("canonical_semantic_artifact_hash"), "canonical_semantic_artifact_hash")
    _normalize_replay_lineage(artifact.get("replay_lineage"))
    return deepcopy(artifact)


def _validated_decision_packet_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("Product 1 decision packet failed closed: artifact must be object")
    if artifact.get("artifact_type") != PRODUCT1_DECISION_PACKET_ARTIFACT_V1:
        raise FailClosedRuntimeError("Product 1 decision packet failed closed: invalid artifact type")
    _verify_hash_field(artifact, "artifact_hash", "Product 1 decision packet artifact hash mismatch")
    for flag in NON_AUTHORITY_FLAGS:
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"Product 1 decision packet failed closed: {flag} must be false")
    _require_hash(artifact.get("canonical_semantic_artifact_hash"), "canonical_semantic_artifact_hash")
    _normalize_replay_lineage(artifact.get("replay_lineage"))
    return deepcopy(artifact)


def _normalize_evidence_references(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError("Product 1 decision packet failed closed: evidence references are required")
    evidence = []
    seen_ids: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("Product 1 decision packet failed closed: evidence item must be object")
        evidence_id = _require_string(item.get("evidence_id"), "evidence_id")
        if evidence_id in seen_ids:
            raise FailClosedRuntimeError("Product 1 decision packet failed closed: duplicate evidence id")
        seen_ids.add(evidence_id)
        reference = {
            "evidence_index": index,
            "evidence_id": evidence_id,
            "evidence_type": _require_string(item.get("evidence_type"), "evidence_type"),
            "evidence_reference": _require_string(item.get("evidence_reference"), "evidence_reference"),
            "evidence_hash": _require_hash(item.get("evidence_hash"), "evidence_hash"),
            "evidence_role": _require_string(item.get("evidence_role"), "evidence_role"),
        }
        reference["evidence_reference_hash"] = replay_hash(reference)
        evidence.append(reference)
    return evidence


def _normalize_named_items(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"Product 1 decision packet failed closed: {label}s must be list")
    normalized = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise FailClosedRuntimeError(f"Product 1 decision packet failed closed: {label} item must be object")
        normalized_item = {
            f"{label}_index": index,
            f"{label}_id": _require_string(item.get(f"{label}_id"), f"{label}_id"),
            "statement": _require_string(item.get("statement"), "statement"),
            "source_reference": _require_string(item.get("source_reference"), "source_reference"),
            "severity": _optional_string(item.get("severity")),
        }
        normalized_item[f"{label}_hash"] = replay_hash(normalized_item)
        normalized.append(normalized_item)
    return normalized


def _normalize_recommendation_summary(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("Product 1 decision packet failed closed: recommendation summary must be object")
    summary = {
        "recommendation_id": _require_string(value.get("recommendation_id"), "recommendation_id"),
        "recommendation_status": _require_string(value.get("recommendation_status"), "recommendation_status"),
        "summary": _require_string(value.get("summary"), "summary"),
        "recommended_next_action": _require_string(value.get("recommended_next_action"), "recommended_next_action"),
        "confidence": _require_string(value.get("confidence"), "confidence"),
        "non_authoritative": True,
    }
    summary["recommendation_hash"] = replay_hash(summary)
    return summary


def _packet_replay_lineage(workflow: dict[str, Any], evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lineage = deepcopy(workflow["replay_lineage"])
    lineage.append({"replay_reference": f"workflow:{workflow['workflow_id']}", "replay_hash": workflow["artifact_hash"]})
    for item in evidence:
        lineage.append({"replay_reference": f"evidence:{item['evidence_id']}", "replay_hash": item["evidence_hash"]})
    return _normalize_replay_lineage(lineage)


def _event(
    *,
    event_index: int,
    event_type: str,
    occurred_at: str,
    previous_event_hash: str,
    event_payload: dict[str, Any],
) -> dict[str, Any]:
    event = {
        "event_index": event_index,
        "event_type": event_type,
        "occurred_at": _require_string(occurred_at, "occurred_at"),
        "previous_event_hash": previous_event_hash,
        "event_payload": deepcopy(event_payload),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
    }
    event["event_hash"] = replay_hash(event)
    return event


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if (replay_path / f"{index:03d}_{step}.json").exists():
        raise FailClosedRuntimeError("Product 1 decision packet failed closed: replay already exists")
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", _wrapper(index, step, artifact))


def _wrapper(index: int, step: str, artifact: dict[str, Any]) -> dict[str, Any]:
    wrapper = {
        "event_type": step.upper(),
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _load_verified_wrapper(path: Path) -> dict[str, Any]:
    wrapper = load_json(path)
    _verify_hash_field(wrapper, "replay_hash", "Product 1 decision packet replay hash mismatch")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("Product 1 decision packet replay artifact must be object")
    _verify_hash_field(artifact, "artifact_hash", "Product 1 decision packet artifact hash mismatch")
    return wrapper


def _verify_hash_field(value: dict[str, Any], field_name: str, message: str) -> None:
    actual = value.get(field_name)
    if not isinstance(actual, str):
        raise FailClosedRuntimeError(message)
    expected = deepcopy(value)
    expected.pop(field_name)
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError(message)


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": PRODUCT1_DECISION_PACKET_RUNTIME_VERSION,
        "decision_packet_artifact": deepcopy(artifact),
        "packet_id": artifact["packet_id"],
        "packet_status": artifact["packet_status"],
        "workflow_id": artifact["workflow_id"],
        "acli_session_id": artifact["acli_session_id"],
        "originating_turn_id": artifact["originating_turn_id"],
        "canonical_semantic_artifact_reference": artifact["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": artifact["canonical_semantic_artifact_hash"],
        "evidence_reference_count": artifact["evidence_reference_count"],
        "governance_status": artifact["governance_status"],
        "rollback_reference": artifact["rollback_reference"],
        "replay_reference": str(replay_path),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "external_integration_invoked": False,
        "replay_visible": True,
        "failure_reason": artifact["failure_reason"],
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _normalize_replay_lineage(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError("Product 1 decision packet failed closed: replay lineage is required")
    lineage = []
    for item in value:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("Product 1 decision packet failed closed: replay lineage item must be object")
        lineage.append(
            {
                "replay_reference": _require_string(item.get("replay_reference"), "replay_reference"),
                "replay_hash": _require_hash(item.get("replay_hash"), "replay_hash"),
            }
        )
    return lineage


def _optional_string(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"Product 1 decision packet failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"Product 1 decision packet failed closed: {field_name} must be replay hash")
    return text
