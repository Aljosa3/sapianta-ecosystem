"""Deterministic Product 1 audit packet assembly runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.product1_decision_packet import (
    PACKET_CREATED,
    PRODUCT1_DECISION_PACKET_ARTIFACT_V1,
)
from aigol.runtime.product1_ocs_advisory import (
    OCS_ADVISORY_ATTACHED,
    PRODUCT1_OCS_ADVISORY_ARTIFACT_V1,
)
from aigol.runtime.product1_workflow_foundation import PRODUCT1_IDENTITY
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PRODUCT1_AUDIT_PACKET_RUNTIME_VERSION = "G3_03_IMPLEMENTATION_PHASE_4_AUDIT_PACKET_ASSEMBLY_RUNTIME_V1"
PRODUCT1_AUDIT_PACKET_ARTIFACT_V1 = "PRODUCT1_AUDIT_PACKET_ARTIFACT_V1"

AUDIT_PACKET_ASSEMBLED = "AUDIT_PACKET_ASSEMBLED"
FAILED_CLOSED = "FAILED_CLOSED"

EVENT_AUDIT_PACKET_ASSEMBLED = "product1_audit_packet_assembled"

AUDIT_PACKET_AUTHORITY = "READ_ONLY_AUDIT_EVIDENCE"

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


def assemble_product1_audit_packet(
    *,
    audit_packet_id: str,
    decision_packet_artifact: dict[str, Any],
    ocs_advisory_artifact: dict[str, Any],
    governance_evidence: list[dict[str, Any]],
    replay_evidence: list[dict[str, Any]],
    certification_evidence: list[dict[str, Any]],
    audit_summary: dict[str, Any],
    assembled_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Assemble read-only Product 1 audit evidence from packet and advisory artifacts."""

    packet = _validated_decision_packet(decision_packet_artifact)
    advisory = _validated_ocs_advisory(ocs_advisory_artifact)
    _validate_packet_advisory_binding(packet, advisory)
    governance = _normalize_governance_evidence(governance_evidence)
    replay = _normalize_replay_evidence(replay_evidence)
    certification = _normalize_certification_evidence(certification_evidence)
    summary = _normalize_audit_summary(audit_summary)
    event = _event(
        event_index=0,
        event_type=EVENT_AUDIT_PACKET_ASSEMBLED,
        occurred_at=assembled_at,
        previous_event_hash="",
        event_payload={
            "audit_packet_id": _require_string(audit_packet_id, "audit_packet_id"),
            "workflow_id": packet["workflow_id"],
            "decision_packet_id": packet["packet_id"],
            "ocs_advisory_id": advisory["advisory_id"],
            "canonical_semantic_artifact_hash": packet["canonical_semantic_artifact_hash"],
            "governance_evidence_count": len(governance),
            "replay_evidence_count": len(replay),
            "certification_evidence_count": len(certification),
        },
    )
    artifact = {
        "artifact_type": PRODUCT1_AUDIT_PACKET_ARTIFACT_V1,
        "runtime_version": PRODUCT1_AUDIT_PACKET_RUNTIME_VERSION,
        "migration_batch_id": "G3_03_IMPLEMENTATION_PHASE_4_AUDIT_PACKET_ASSEMBLY_V1",
        "product_identity": PRODUCT1_IDENTITY,
        "audit_packet_id": _require_string(audit_packet_id, "audit_packet_id"),
        "audit_packet_status": AUDIT_PACKET_ASSEMBLED,
        "workflow_id": packet["workflow_id"],
        "acli_session_id": packet["acli_session_id"],
        "originating_turn_id": packet["originating_turn_id"],
        "decision_packet_id": packet["packet_id"],
        "decision_packet_hash": packet["artifact_hash"],
        "ocs_advisory_id": advisory["advisory_id"],
        "ocs_advisory_hash": advisory["artifact_hash"],
        "canonical_semantic_artifact_reference": packet["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": packet["canonical_semantic_artifact_hash"],
        "governance_evidence": governance,
        "governance_evidence_count": len(governance),
        "governance_evidence_hash": replay_hash(governance),
        "replay_evidence": replay,
        "replay_evidence_count": len(replay),
        "replay_evidence_hash": replay_hash(replay),
        "certification_evidence": certification,
        "certification_evidence_count": len(certification),
        "certification_evidence_hash": replay_hash(certification),
        "audit_summary": summary,
        "audit_summary_hash": summary["audit_summary_hash"],
        "replay_lineage": _audit_replay_lineage(packet, advisory, governance, replay, certification),
        "rollback_reference": packet["rollback_reference"],
        "source_decision_packet": deepcopy(packet),
        "source_ocs_advisory": deepcopy(advisory),
        "audit_packet_identity_created": True,
        "decision_packet_aggregated": True,
        "ocs_advisory_aggregated": True,
        "governance_evidence_aggregated": True,
        "replay_evidence_aggregated": True,
        "certification_evidence_aggregated": True,
        "read_only": True,
        "non_authoritative": True,
        "audit_packet_authority": AUDIT_PACKET_AUTHORITY,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "external_integration_invoked": False,
        "replay_visible": True,
        "assembled_at": _require_string(assembled_at, "assembled_at"),
        "event": event,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _persist_step(Path(replay_dir), 0, EVENT_AUDIT_PACKET_ASSEMBLED, artifact)
    return _capture(artifact, Path(replay_dir))


def reconstruct_product1_audit_packet_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate Product 1 audit packet replay evidence."""

    replay_path = Path(replay_dir)
    wrappers = [_load_verified_wrapper(path) for path in sorted(replay_path.glob("*.json"))]
    if not wrappers:
        raise FailClosedRuntimeError("Product 1 audit packet failed closed: replay is empty")
    for index, wrapper in enumerate(wrappers):
        if wrapper.get("replay_index") != index:
            raise FailClosedRuntimeError("Product 1 audit packet replay ordering mismatch")
    artifact = _validated_audit_packet_artifact(wrappers[-1]["artifact"])
    event = artifact.get("event")
    if not isinstance(event, dict) or event.get("event_index") != 0:
        raise FailClosedRuntimeError("Product 1 audit packet event mismatch")
    _verify_hash_field(event, "event_hash", "Product 1 audit packet event hash mismatch")
    return {
        "audit_packet_id": artifact["audit_packet_id"],
        "audit_packet_status": artifact["audit_packet_status"],
        "workflow_id": artifact["workflow_id"],
        "acli_session_id": artifact["acli_session_id"],
        "originating_turn_id": artifact["originating_turn_id"],
        "decision_packet_id": artifact["decision_packet_id"],
        "ocs_advisory_id": artifact["ocs_advisory_id"],
        "canonical_semantic_artifact_reference": artifact["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": artifact["canonical_semantic_artifact_hash"],
        "governance_evidence_count": artifact["governance_evidence_count"],
        "replay_evidence_count": artifact["replay_evidence_count"],
        "certification_evidence_count": artifact["certification_evidence_count"],
        "audit_summary_hash": artifact["audit_summary_hash"],
        "replay_lineage_count": len(artifact["replay_lineage"]),
        "rollback_reference": artifact["rollback_reference"],
        "read_only": True,
        "non_authoritative": True,
        "audit_packet_authority": artifact["audit_packet_authority"],
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
        raise FailClosedRuntimeError("Product 1 audit packet failed closed: decision packet must be object")
    if artifact.get("artifact_type") != PRODUCT1_DECISION_PACKET_ARTIFACT_V1:
        raise FailClosedRuntimeError("Product 1 audit packet failed closed: invalid decision packet artifact")
    _verify_hash_field(artifact, "artifact_hash", "Product 1 audit packet decision packet hash mismatch")
    if artifact.get("packet_status") != PACKET_CREATED:
        raise FailClosedRuntimeError("Product 1 audit packet failed closed: decision packet is not created")
    for flag in NON_AUTHORITY_FLAGS:
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"Product 1 audit packet failed closed: {flag} must be false")
    _require_hash(artifact.get("canonical_semantic_artifact_hash"), "canonical_semantic_artifact_hash")
    _normalize_replay_lineage(artifact.get("replay_lineage"))
    return deepcopy(artifact)


def _validated_ocs_advisory(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("Product 1 audit packet failed closed: OCS advisory must be object")
    if artifact.get("artifact_type") != PRODUCT1_OCS_ADVISORY_ARTIFACT_V1:
        raise FailClosedRuntimeError("Product 1 audit packet failed closed: invalid OCS advisory artifact")
    _verify_hash_field(artifact, "artifact_hash", "Product 1 audit packet OCS advisory hash mismatch")
    if artifact.get("advisory_status") != OCS_ADVISORY_ATTACHED:
        raise FailClosedRuntimeError("Product 1 audit packet failed closed: OCS advisory is not attached")
    for flag in NON_AUTHORITY_FLAGS:
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"Product 1 audit packet failed closed: {flag} must be false")
    _require_hash(artifact.get("canonical_semantic_artifact_hash"), "canonical_semantic_artifact_hash")
    _require_hash(artifact.get("ocs_cognition_hash"), "ocs_cognition_hash")
    _normalize_replay_lineage(artifact.get("replay_lineage"))
    return deepcopy(artifact)


def _validated_audit_packet_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("Product 1 audit packet failed closed: artifact must be object")
    if artifact.get("artifact_type") != PRODUCT1_AUDIT_PACKET_ARTIFACT_V1:
        raise FailClosedRuntimeError("Product 1 audit packet failed closed: invalid artifact type")
    _verify_hash_field(artifact, "artifact_hash", "Product 1 audit packet artifact hash mismatch")
    if artifact.get("audit_packet_status") != AUDIT_PACKET_ASSEMBLED:
        raise FailClosedRuntimeError("Product 1 audit packet failed closed: audit packet is not assembled")
    if artifact.get("audit_packet_authority") != AUDIT_PACKET_AUTHORITY:
        raise FailClosedRuntimeError("Product 1 audit packet failed closed: invalid audit authority")
    if artifact.get("read_only") is not True or artifact.get("non_authoritative") is not True:
        raise FailClosedRuntimeError("Product 1 audit packet failed closed: audit packet must be read-only")
    for flag in NON_AUTHORITY_FLAGS:
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"Product 1 audit packet failed closed: {flag} must be false")
    _require_hash(artifact.get("canonical_semantic_artifact_hash"), "canonical_semantic_artifact_hash")
    _normalize_replay_lineage(artifact.get("replay_lineage"))
    return deepcopy(artifact)


def _validate_packet_advisory_binding(packet: dict[str, Any], advisory: dict[str, Any]) -> None:
    required_pairs = (
        ("packet_id", "decision_packet_id"),
        ("artifact_hash", "decision_packet_hash"),
        ("workflow_id", "workflow_id"),
        ("acli_session_id", "acli_session_id"),
        ("originating_turn_id", "originating_turn_id"),
        ("canonical_semantic_artifact_reference", "canonical_semantic_artifact_reference"),
        ("canonical_semantic_artifact_hash", "canonical_semantic_artifact_hash"),
        ("rollback_reference", "rollback_reference"),
    )
    for packet_field, advisory_field in required_pairs:
        if packet.get(packet_field) != advisory.get(advisory_field):
            raise FailClosedRuntimeError("Product 1 audit packet failed closed: advisory does not match decision packet")


def _normalize_governance_evidence(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError("Product 1 audit packet failed closed: governance evidence is required")
    evidence = []
    seen_ids: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("Product 1 audit packet failed closed: governance evidence item must be object")
        evidence_id = _require_string(item.get("governance_evidence_id"), "governance_evidence_id")
        if evidence_id in seen_ids:
            raise FailClosedRuntimeError("Product 1 audit packet failed closed: duplicate governance evidence id")
        seen_ids.add(evidence_id)
        record = {
            "governance_evidence_index": index,
            "governance_evidence_id": evidence_id,
            "governance_scope": _require_string(item.get("governance_scope"), "governance_scope"),
            "governance_status": _require_string(item.get("governance_status"), "governance_status"),
            "governance_reference": _require_string(item.get("governance_reference"), "governance_reference"),
            "governance_hash": _require_hash(item.get("governance_hash"), "governance_hash"),
        }
        record["governance_evidence_hash"] = replay_hash(record)
        evidence.append(record)
    return evidence


def _normalize_replay_evidence(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError("Product 1 audit packet failed closed: replay evidence is required")
    evidence = []
    seen_ids: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("Product 1 audit packet failed closed: replay evidence item must be object")
        evidence_id = _require_string(item.get("replay_evidence_id"), "replay_evidence_id")
        if evidence_id in seen_ids:
            raise FailClosedRuntimeError("Product 1 audit packet failed closed: duplicate replay evidence id")
        seen_ids.add(evidence_id)
        record = {
            "replay_evidence_index": index,
            "replay_evidence_id": evidence_id,
            "replay_reference": _require_string(item.get("replay_reference"), "replay_reference"),
            "replay_hash": _require_hash(item.get("replay_hash"), "replay_hash"),
            "replay_role": _require_string(item.get("replay_role"), "replay_role"),
        }
        record["replay_evidence_hash"] = replay_hash(record)
        evidence.append(record)
    return evidence


def _normalize_certification_evidence(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError("Product 1 audit packet failed closed: certification evidence is required")
    evidence = []
    seen_ids: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("Product 1 audit packet failed closed: certification evidence item must be object")
        evidence_id = _require_string(item.get("certification_evidence_id"), "certification_evidence_id")
        if evidence_id in seen_ids:
            raise FailClosedRuntimeError("Product 1 audit packet failed closed: duplicate certification evidence id")
        seen_ids.add(evidence_id)
        record = {
            "certification_evidence_index": index,
            "certification_evidence_id": evidence_id,
            "certification_scope": _require_string(item.get("certification_scope"), "certification_scope"),
            "certification_status": _require_string(item.get("certification_status"), "certification_status"),
            "certification_reference": _require_string(item.get("certification_reference"), "certification_reference"),
            "certification_hash": _require_hash(item.get("certification_hash"), "certification_hash"),
        }
        record["certification_evidence_hash"] = replay_hash(record)
        evidence.append(record)
    return evidence


def _normalize_audit_summary(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("Product 1 audit packet failed closed: audit summary must be object")
    summary = {
        "audit_summary_id": _require_string(value.get("audit_summary_id"), "audit_summary_id"),
        "summary": _require_string(value.get("summary"), "summary"),
        "readiness_status": _require_string(value.get("readiness_status"), "readiness_status"),
        "required_next_action": _require_string(value.get("required_next_action"), "required_next_action"),
        "non_authoritative": True,
        "read_only": True,
    }
    summary["audit_summary_hash"] = replay_hash(summary)
    return summary


def _audit_replay_lineage(
    packet: dict[str, Any],
    advisory: dict[str, Any],
    governance: list[dict[str, Any]],
    replay: list[dict[str, Any]],
    certification: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    lineage = deepcopy(advisory["replay_lineage"])
    lineage.append({"replay_reference": f"decision_packet:{packet['packet_id']}", "replay_hash": packet["artifact_hash"]})
    lineage.append({"replay_reference": f"ocs_advisory:{advisory['advisory_id']}", "replay_hash": advisory["artifact_hash"]})
    for item in governance:
        lineage.append(
            {
                "replay_reference": f"governance_evidence:{item['governance_evidence_id']}",
                "replay_hash": item["governance_evidence_hash"],
            }
        )
    for item in replay:
        lineage.append(
            {
                "replay_reference": f"replay_evidence:{item['replay_evidence_id']}",
                "replay_hash": item["replay_evidence_hash"],
            }
        )
    for item in certification:
        lineage.append(
            {
                "replay_reference": f"certification_evidence:{item['certification_evidence_id']}",
                "replay_hash": item["certification_evidence_hash"],
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
        raise FailClosedRuntimeError("Product 1 audit packet failed closed: replay already exists")
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
    _verify_hash_field(wrapper, "replay_hash", "Product 1 audit packet replay hash mismatch")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("Product 1 audit packet replay artifact must be object")
    _verify_hash_field(artifact, "artifact_hash", "Product 1 audit packet artifact hash mismatch")
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
        "runtime_version": PRODUCT1_AUDIT_PACKET_RUNTIME_VERSION,
        "audit_packet_artifact": deepcopy(artifact),
        "audit_packet_id": artifact["audit_packet_id"],
        "audit_packet_status": artifact["audit_packet_status"],
        "workflow_id": artifact["workflow_id"],
        "decision_packet_id": artifact["decision_packet_id"],
        "ocs_advisory_id": artifact["ocs_advisory_id"],
        "canonical_semantic_artifact_reference": artifact["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": artifact["canonical_semantic_artifact_hash"],
        "governance_evidence_count": artifact["governance_evidence_count"],
        "replay_evidence_count": artifact["replay_evidence_count"],
        "certification_evidence_count": artifact["certification_evidence_count"],
        "rollback_reference": artifact["rollback_reference"],
        "read_only": True,
        "non_authoritative": True,
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
        raise FailClosedRuntimeError("Product 1 audit packet failed closed: replay lineage is required")
    lineage = []
    for item in value:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("Product 1 audit packet failed closed: replay lineage item must be object")
        lineage.append(
            {
                "replay_reference": _require_string(item.get("replay_reference"), "replay_reference"),
                "replay_hash": _require_hash(item.get("replay_hash"), "replay_hash"),
            }
        )
    return lineage


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"Product 1 audit packet failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"Product 1 audit packet failed closed: {field_name} must be replay hash")
    return text
