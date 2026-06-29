"""Advisory-only OCS integration for Product 1 decision packets."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.product1_decision_packet import (
    PACKET_CREATED,
    PRODUCT1_DECISION_PACKET_ARTIFACT_V1,
)
from aigol.runtime.product1_workflow_foundation import PRODUCT1_IDENTITY
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PRODUCT1_OCS_ADVISORY_RUNTIME_VERSION = "G3_03_IMPLEMENTATION_PHASE_3_OCS_ADVISORY_INTEGRATION_RUNTIME_V1"
PRODUCT1_OCS_ADVISORY_ARTIFACT_V1 = "PRODUCT1_OCS_ADVISORY_ARTIFACT_V1"

OCS_ADVISORY_ATTACHED = "OCS_ADVISORY_ATTACHED"
FAILED_CLOSED = "FAILED_CLOSED"

EVENT_OCS_ADVISORY_ATTACHED = "product1_ocs_advisory_attached"

DECISION_AUTHORITY = "GOVERNANCE_AND_HUMAN_APPROVAL"

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


def attach_product1_ocs_advisory(
    *,
    advisory_id: str,
    decision_packet_artifact: dict[str, Any],
    ocs_cognition_reference: str,
    ocs_cognition_hash: str,
    provider_provenance: list[dict[str, Any]],
    confidence: dict[str, Any],
    assumptions: list[dict[str, Any]],
    risks: list[dict[str, Any]],
    uncertainties: list[dict[str, Any]],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Attach non-authoritative OCS advisory evidence to a Product 1 packet."""

    packet = _validated_decision_packet(decision_packet_artifact)
    provenance = _normalize_provider_provenance(provider_provenance)
    confidence_record = _normalize_confidence(confidence)
    normalized_assumptions = _normalize_named_items(assumptions, "assumption")
    normalized_risks = _normalize_named_items(risks, "risk")
    normalized_uncertainties = _normalize_named_items(uncertainties, "uncertainty")
    event = _event(
        event_index=0,
        event_type=EVENT_OCS_ADVISORY_ATTACHED,
        occurred_at=created_at,
        previous_event_hash="",
        event_payload={
            "advisory_id": _require_string(advisory_id, "advisory_id"),
            "decision_packet_id": packet["packet_id"],
            "canonical_semantic_artifact_hash": packet["canonical_semantic_artifact_hash"],
            "ocs_cognition_hash": _require_hash(ocs_cognition_hash, "ocs_cognition_hash"),
            "provider_provenance_count": len(provenance),
        },
    )
    artifact = {
        "artifact_type": PRODUCT1_OCS_ADVISORY_ARTIFACT_V1,
        "runtime_version": PRODUCT1_OCS_ADVISORY_RUNTIME_VERSION,
        "migration_batch_id": "G3_03_IMPLEMENTATION_PHASE_3_OCS_ADVISORY_INTEGRATION_V1",
        "product_identity": PRODUCT1_IDENTITY,
        "advisory_id": _require_string(advisory_id, "advisory_id"),
        "advisory_status": OCS_ADVISORY_ATTACHED,
        "decision_packet_id": packet["packet_id"],
        "decision_packet_hash": packet["artifact_hash"],
        "workflow_id": packet["workflow_id"],
        "acli_session_id": packet["acli_session_id"],
        "originating_turn_id": packet["originating_turn_id"],
        "canonical_semantic_artifact_reference": packet["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": packet["canonical_semantic_artifact_hash"],
        "ocs_cognition_reference": _require_string(ocs_cognition_reference, "ocs_cognition_reference"),
        "ocs_cognition_hash": _require_hash(ocs_cognition_hash, "ocs_cognition_hash"),
        "provider_provenance": provenance,
        "provider_provenance_count": len(provenance),
        "provider_provenance_hash": replay_hash(provenance),
        "confidence": confidence_record,
        "confidence_hash": confidence_record["confidence_hash"],
        "assumptions": normalized_assumptions,
        "assumption_count": len(normalized_assumptions),
        "assumptions_hash": replay_hash(normalized_assumptions),
        "risks": normalized_risks,
        "risk_count": len(normalized_risks),
        "risks_hash": replay_hash(normalized_risks),
        "uncertainties": normalized_uncertainties,
        "uncertainty_count": len(normalized_uncertainties),
        "uncertainties_hash": replay_hash(normalized_uncertainties),
        "replay_lineage": _advisory_replay_lineage(packet, provenance, ocs_cognition_hash),
        "rollback_reference": packet["rollback_reference"],
        "source_decision_packet": deepcopy(packet),
        "decision_authority": DECISION_AUTHORITY,
        "ocs_advisory_attached": True,
        "advisory_identity_created": True,
        "cognition_lineage_recorded": True,
        "provider_provenance_recorded": True,
        "confidence_recorded": True,
        "uncertainties_recorded": True,
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
    _persist_step(Path(replay_dir), 0, EVENT_OCS_ADVISORY_ATTACHED, artifact)
    return _capture(artifact, Path(replay_dir))


def reconstruct_product1_ocs_advisory_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate Product 1 OCS advisory replay evidence."""

    replay_path = Path(replay_dir)
    wrappers = [_load_verified_wrapper(path) for path in sorted(replay_path.glob("*.json"))]
    if not wrappers:
        raise FailClosedRuntimeError("Product 1 OCS advisory failed closed: replay is empty")
    for index, wrapper in enumerate(wrappers):
        if wrapper.get("replay_index") != index:
            raise FailClosedRuntimeError("Product 1 OCS advisory replay ordering mismatch")
    artifact = _validated_ocs_advisory_artifact(wrappers[-1]["artifact"])
    event = artifact.get("event")
    if not isinstance(event, dict) or event.get("event_index") != 0:
        raise FailClosedRuntimeError("Product 1 OCS advisory event mismatch")
    _verify_hash_field(event, "event_hash", "Product 1 OCS advisory event hash mismatch")
    return {
        "advisory_id": artifact["advisory_id"],
        "advisory_status": artifact["advisory_status"],
        "decision_packet_id": artifact["decision_packet_id"],
        "workflow_id": artifact["workflow_id"],
        "acli_session_id": artifact["acli_session_id"],
        "originating_turn_id": artifact["originating_turn_id"],
        "canonical_semantic_artifact_reference": artifact["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": artifact["canonical_semantic_artifact_hash"],
        "ocs_cognition_reference": artifact["ocs_cognition_reference"],
        "ocs_cognition_hash": artifact["ocs_cognition_hash"],
        "provider_provenance_count": artifact["provider_provenance_count"],
        "confidence_hash": artifact["confidence_hash"],
        "assumption_count": artifact["assumption_count"],
        "risk_count": artifact["risk_count"],
        "uncertainty_count": artifact["uncertainty_count"],
        "decision_authority": artifact["decision_authority"],
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


def _validated_decision_packet(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("Product 1 OCS advisory failed closed: decision packet must be object")
    if artifact.get("artifact_type") != PRODUCT1_DECISION_PACKET_ARTIFACT_V1:
        raise FailClosedRuntimeError("Product 1 OCS advisory failed closed: invalid decision packet artifact")
    _verify_hash_field(artifact, "artifact_hash", "Product 1 OCS advisory decision packet hash mismatch")
    if artifact.get("packet_status") != PACKET_CREATED:
        raise FailClosedRuntimeError("Product 1 OCS advisory failed closed: decision packet is not created")
    for flag in NON_AUTHORITY_FLAGS:
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"Product 1 OCS advisory failed closed: {flag} must be false")
    _require_hash(artifact.get("canonical_semantic_artifact_hash"), "canonical_semantic_artifact_hash")
    _normalize_replay_lineage(artifact.get("replay_lineage"))
    return deepcopy(artifact)


def _validated_ocs_advisory_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("Product 1 OCS advisory failed closed: artifact must be object")
    if artifact.get("artifact_type") != PRODUCT1_OCS_ADVISORY_ARTIFACT_V1:
        raise FailClosedRuntimeError("Product 1 OCS advisory failed closed: invalid artifact type")
    _verify_hash_field(artifact, "artifact_hash", "Product 1 OCS advisory artifact hash mismatch")
    if artifact.get("advisory_status") != OCS_ADVISORY_ATTACHED:
        raise FailClosedRuntimeError("Product 1 OCS advisory failed closed: advisory is not attached")
    if artifact.get("decision_authority") != DECISION_AUTHORITY:
        raise FailClosedRuntimeError("Product 1 OCS advisory failed closed: invalid decision authority")
    for flag in NON_AUTHORITY_FLAGS:
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"Product 1 OCS advisory failed closed: {flag} must be false")
    _require_hash(artifact.get("canonical_semantic_artifact_hash"), "canonical_semantic_artifact_hash")
    _require_hash(artifact.get("ocs_cognition_hash"), "ocs_cognition_hash")
    _normalize_replay_lineage(artifact.get("replay_lineage"))
    return deepcopy(artifact)


def _normalize_provider_provenance(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError("Product 1 OCS advisory failed closed: provider provenance is required")
    provenance = []
    seen_ids: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("Product 1 OCS advisory failed closed: provider provenance item must be object")
        provenance_id = _require_string(item.get("provider_provenance_id"), "provider_provenance_id")
        if provenance_id in seen_ids:
            raise FailClosedRuntimeError("Product 1 OCS advisory failed closed: duplicate provider provenance id")
        seen_ids.add(provenance_id)
        if item.get("provider_invoked") is not False:
            raise FailClosedRuntimeError("Product 1 OCS advisory failed closed: provider provenance must not invoke provider")
        if item.get("provider_authority") is not False:
            raise FailClosedRuntimeError("Product 1 OCS advisory failed closed: provider provenance must not be authoritative")
        if item.get("advisory_only") is not True:
            raise FailClosedRuntimeError("Product 1 OCS advisory failed closed: provider provenance must be advisory only")
        record = {
            "provider_provenance_index": index,
            "provider_provenance_id": provenance_id,
            "provider_id": _require_string(item.get("provider_id"), "provider_id"),
            "provider_reference": _require_string(item.get("provider_reference"), "provider_reference"),
            "provider_response_hash": _require_hash(item.get("provider_response_hash"), "provider_response_hash"),
            "provider_role": _require_string(item.get("provider_role"), "provider_role"),
            "provider_invoked": False,
            "provider_authority": False,
            "advisory_only": True,
        }
        record["provider_provenance_hash"] = replay_hash(record)
        provenance.append(record)
    return provenance


def _normalize_confidence(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("Product 1 OCS advisory failed closed: confidence must be object")
    record = {
        "confidence_id": _require_string(value.get("confidence_id"), "confidence_id"),
        "confidence_level": _require_string(value.get("confidence_level"), "confidence_level"),
        "confidence_score": _require_string(value.get("confidence_score"), "confidence_score"),
        "confidence_rationale": _require_string(value.get("confidence_rationale"), "confidence_rationale"),
        "confidence_source_reference": _require_string(
            value.get("confidence_source_reference"),
            "confidence_source_reference",
        ),
        "non_authoritative": True,
    }
    record["confidence_hash"] = replay_hash(record)
    return record


def _normalize_named_items(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"Product 1 OCS advisory failed closed: {label}s must be list")
    normalized = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise FailClosedRuntimeError(f"Product 1 OCS advisory failed closed: {label} item must be object")
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


def _advisory_replay_lineage(
    packet: dict[str, Any],
    provenance: list[dict[str, Any]],
    ocs_cognition_hash: str,
) -> list[dict[str, Any]]:
    lineage = deepcopy(packet["replay_lineage"])
    lineage.append({"replay_reference": f"decision_packet:{packet['packet_id']}", "replay_hash": packet["artifact_hash"]})
    lineage.append(
        {
            "replay_reference": "ocs_cognition:" + packet["canonical_semantic_artifact_reference"],
            "replay_hash": _require_hash(ocs_cognition_hash, "ocs_cognition_hash"),
        }
    )
    for item in provenance:
        lineage.append(
            {
                "replay_reference": f"provider_provenance:{item['provider_provenance_id']}",
                "replay_hash": item["provider_provenance_hash"],
            }
        )
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
        raise FailClosedRuntimeError("Product 1 OCS advisory failed closed: replay already exists")
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
    _verify_hash_field(wrapper, "replay_hash", "Product 1 OCS advisory replay hash mismatch")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("Product 1 OCS advisory replay artifact must be object")
    _verify_hash_field(artifact, "artifact_hash", "Product 1 OCS advisory artifact hash mismatch")
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
        "runtime_version": PRODUCT1_OCS_ADVISORY_RUNTIME_VERSION,
        "ocs_advisory_artifact": deepcopy(artifact),
        "advisory_id": artifact["advisory_id"],
        "advisory_status": artifact["advisory_status"],
        "decision_packet_id": artifact["decision_packet_id"],
        "workflow_id": artifact["workflow_id"],
        "acli_session_id": artifact["acli_session_id"],
        "originating_turn_id": artifact["originating_turn_id"],
        "canonical_semantic_artifact_reference": artifact["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": artifact["canonical_semantic_artifact_hash"],
        "ocs_cognition_reference": artifact["ocs_cognition_reference"],
        "ocs_cognition_hash": artifact["ocs_cognition_hash"],
        "provider_provenance_count": artifact["provider_provenance_count"],
        "decision_authority": artifact["decision_authority"],
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
        raise FailClosedRuntimeError("Product 1 OCS advisory failed closed: replay lineage is required")
    lineage = []
    for item in value:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("Product 1 OCS advisory failed closed: replay lineage item must be object")
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
        raise FailClosedRuntimeError(f"Product 1 OCS advisory failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"Product 1 OCS advisory failed closed: {field_name} must be replay hash")
    return text
