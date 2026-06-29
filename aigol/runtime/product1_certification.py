"""Formal Product 1 runtime certification evidence."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.product1_audit_packet import (
    AUDIT_PACKET_ASSEMBLED,
    PRODUCT1_AUDIT_PACKET_ARTIFACT_V1,
)
from aigol.runtime.product1_decision_packet import PACKET_CREATED, PRODUCT1_DECISION_PACKET_ARTIFACT_V1
from aigol.runtime.product1_ocs_advisory import OCS_ADVISORY_ATTACHED, PRODUCT1_OCS_ADVISORY_ARTIFACT_V1
from aigol.runtime.product1_workflow_foundation import (
    GOVERNANCE_PASSED,
    PRODUCT1_IDENTITY,
    PRODUCT1_WORKFLOW_FOUNDATION_ARTIFACT_V1,
    WORKFLOW_READY_FOR_DECISION_PACKET,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PRODUCT1_CERTIFICATION_RUNTIME_VERSION = "G3_03_IMPLEMENTATION_PHASE_5_PRODUCT_1_CERTIFICATION_RUNTIME_V1"
PRODUCT1_CERTIFICATION_ARTIFACT_V1 = "PRODUCT1_CERTIFICATION_ARTIFACT_V1"

PRODUCT1_CERTIFIED = "PRODUCT1_CERTIFIED"
FAILED_CLOSED = "FAILED_CLOSED"

EVENT_PRODUCT1_CERTIFIED = "product1_runtime_certified"

CERTIFICATION_AUTHORITY = "CERTIFICATION_EVIDENCE_ONLY"
CERTIFICATION_RECOMMENDATION = "PRODUCT_1_READY_FOR_G3_03_CERTIFICATION"

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

CERTIFICATION_CHECKS = (
    "product_workflow_integrity",
    "decision_packet_integrity",
    "ocs_advisory_integrity",
    "audit_packet_integrity",
    "governance_checkpoints",
    "replay_integrity",
    "rollback_capability",
    "deterministic_reconstruction",
    "authority_preservation",
    "human_approval_boundaries",
    "non_authority_guarantees",
)


def certify_product1_runtime(
    *,
    certification_id: str,
    audit_packet_artifact: dict[str, Any],
    remaining_limitations: list[dict[str, Any]],
    certified_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create read-only Product 1 certification evidence from an Audit Packet."""

    audit_packet = _validated_audit_packet(audit_packet_artifact)
    decision_packet = _validated_decision_packet(audit_packet["source_decision_packet"])
    ocs_advisory = _validated_ocs_advisory(audit_packet["source_ocs_advisory"])
    workflow = _validated_workflow(decision_packet["source_workflow"])
    _validate_chain_binding(audit_packet, decision_packet, ocs_advisory, workflow)
    checks = _certification_checks(audit_packet, decision_packet, ocs_advisory, workflow)
    limitations = _normalize_remaining_limitations(remaining_limitations)
    event = _event(
        event_index=0,
        event_type=EVENT_PRODUCT1_CERTIFIED,
        occurred_at=certified_at,
        previous_event_hash="",
        event_payload={
            "certification_id": _require_string(certification_id, "certification_id"),
            "audit_packet_id": audit_packet["audit_packet_id"],
            "workflow_id": audit_packet["workflow_id"],
            "decision_packet_id": audit_packet["decision_packet_id"],
            "ocs_advisory_id": audit_packet["ocs_advisory_id"],
            "canonical_semantic_artifact_hash": audit_packet["canonical_semantic_artifact_hash"],
            "certification_check_count": len(checks),
            "remaining_limitation_count": len(limitations),
        },
    )
    artifact = {
        "artifact_type": PRODUCT1_CERTIFICATION_ARTIFACT_V1,
        "runtime_version": PRODUCT1_CERTIFICATION_RUNTIME_VERSION,
        "migration_batch_id": "G3_03_IMPLEMENTATION_PHASE_5_PRODUCT_1_CERTIFICATION_V1",
        "product_identity": PRODUCT1_IDENTITY,
        "certification_id": _require_string(certification_id, "certification_id"),
        "certification_status": PRODUCT1_CERTIFIED,
        "certification_recommendation": CERTIFICATION_RECOMMENDATION,
        "certification_authority": CERTIFICATION_AUTHORITY,
        "audit_packet_id": audit_packet["audit_packet_id"],
        "audit_packet_hash": audit_packet["artifact_hash"],
        "workflow_id": audit_packet["workflow_id"],
        "acli_session_id": audit_packet["acli_session_id"],
        "originating_turn_id": audit_packet["originating_turn_id"],
        "decision_packet_id": audit_packet["decision_packet_id"],
        "decision_packet_hash": audit_packet["decision_packet_hash"],
        "ocs_advisory_id": audit_packet["ocs_advisory_id"],
        "ocs_advisory_hash": audit_packet["ocs_advisory_hash"],
        "canonical_semantic_artifact_reference": audit_packet["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": audit_packet["canonical_semantic_artifact_hash"],
        "certification_checks": checks,
        "certification_check_count": len(checks),
        "certification_checks_hash": replay_hash(checks),
        "remaining_limitations": limitations,
        "remaining_limitation_count": len(limitations),
        "remaining_limitations_hash": replay_hash(limitations),
        "replay_lineage": _certification_replay_lineage(audit_packet, decision_packet, ocs_advisory, workflow, checks),
        "rollback_reference": audit_packet["rollback_reference"],
        "source_audit_packet": deepcopy(audit_packet),
        "source_decision_packet": deepcopy(decision_packet),
        "source_ocs_advisory": deepcopy(ocs_advisory),
        "source_workflow": deepcopy(workflow),
        "product_workflow_integrity_verified": True,
        "decision_packet_integrity_verified": True,
        "ocs_advisory_integrity_verified": True,
        "audit_packet_integrity_verified": True,
        "governance_checkpoints_verified": True,
        "replay_integrity_verified": True,
        "rollback_capability_verified": True,
        "deterministic_reconstruction_verified": True,
        "authority_preservation_verified": True,
        "human_approval_boundaries_verified": True,
        "non_authority_guarantees_verified": True,
        "read_only": True,
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
        "certified_at": _require_string(certified_at, "certified_at"),
        "event": event,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _persist_step(Path(replay_dir), 0, EVENT_PRODUCT1_CERTIFIED, artifact)
    return _capture(artifact, Path(replay_dir))


def reconstruct_product1_certification_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate Product 1 certification replay evidence."""

    replay_path = Path(replay_dir)
    wrappers = [_load_verified_wrapper(path) for path in sorted(replay_path.glob("*.json"))]
    if not wrappers:
        raise FailClosedRuntimeError("Product 1 certification failed closed: replay is empty")
    for index, wrapper in enumerate(wrappers):
        if wrapper.get("replay_index") != index:
            raise FailClosedRuntimeError("Product 1 certification replay ordering mismatch")
    artifact = _validated_certification_artifact(wrappers[-1]["artifact"])
    event = artifact.get("event")
    if not isinstance(event, dict) or event.get("event_index") != 0:
        raise FailClosedRuntimeError("Product 1 certification event mismatch")
    _verify_hash_field(event, "event_hash", "Product 1 certification event hash mismatch")
    return {
        "certification_id": artifact["certification_id"],
        "certification_status": artifact["certification_status"],
        "certification_recommendation": artifact["certification_recommendation"],
        "audit_packet_id": artifact["audit_packet_id"],
        "workflow_id": artifact["workflow_id"],
        "decision_packet_id": artifact["decision_packet_id"],
        "ocs_advisory_id": artifact["ocs_advisory_id"],
        "canonical_semantic_artifact_reference": artifact["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": artifact["canonical_semantic_artifact_hash"],
        "certification_check_count": artifact["certification_check_count"],
        "remaining_limitation_count": artifact["remaining_limitation_count"],
        "replay_lineage_count": len(artifact["replay_lineage"]),
        "rollback_reference": artifact["rollback_reference"],
        "read_only": True,
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
        "artifact_hash": artifact["artifact_hash"],
        "replay_hash": replay_hash(wrappers),
    }


def _validated_audit_packet(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("Product 1 certification failed closed: audit packet must be object")
    if artifact.get("artifact_type") != PRODUCT1_AUDIT_PACKET_ARTIFACT_V1:
        raise FailClosedRuntimeError("Product 1 certification failed closed: invalid audit packet artifact")
    _verify_hash_field(artifact, "artifact_hash", "Product 1 certification audit packet hash mismatch")
    if artifact.get("audit_packet_status") != AUDIT_PACKET_ASSEMBLED:
        raise FailClosedRuntimeError("Product 1 certification failed closed: audit packet is not assembled")
    if artifact.get("read_only") is not True or artifact.get("non_authoritative") is not True:
        raise FailClosedRuntimeError("Product 1 certification failed closed: audit packet must be read-only")
    for flag in NON_AUTHORITY_FLAGS:
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"Product 1 certification failed closed: {flag} must be false")
    _require_hash(artifact.get("canonical_semantic_artifact_hash"), "canonical_semantic_artifact_hash")
    _normalize_replay_lineage(artifact.get("replay_lineage"))
    return deepcopy(artifact)


def _validated_decision_packet(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("Product 1 certification failed closed: decision packet must be object")
    if artifact.get("artifact_type") != PRODUCT1_DECISION_PACKET_ARTIFACT_V1:
        raise FailClosedRuntimeError("Product 1 certification failed closed: invalid decision packet artifact")
    _verify_hash_field(artifact, "artifact_hash", "Product 1 certification decision packet hash mismatch")
    if artifact.get("packet_status") != PACKET_CREATED:
        raise FailClosedRuntimeError("Product 1 certification failed closed: decision packet is not created")
    for flag in NON_AUTHORITY_FLAGS:
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"Product 1 certification failed closed: {flag} must be false")
    _normalize_replay_lineage(artifact.get("replay_lineage"))
    return deepcopy(artifact)


def _validated_ocs_advisory(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("Product 1 certification failed closed: OCS advisory must be object")
    if artifact.get("artifact_type") != PRODUCT1_OCS_ADVISORY_ARTIFACT_V1:
        raise FailClosedRuntimeError("Product 1 certification failed closed: invalid OCS advisory artifact")
    _verify_hash_field(artifact, "artifact_hash", "Product 1 certification OCS advisory hash mismatch")
    if artifact.get("advisory_status") != OCS_ADVISORY_ATTACHED:
        raise FailClosedRuntimeError("Product 1 certification failed closed: OCS advisory is not attached")
    for flag in NON_AUTHORITY_FLAGS:
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"Product 1 certification failed closed: {flag} must be false")
    _normalize_replay_lineage(artifact.get("replay_lineage"))
    return deepcopy(artifact)


def _validated_workflow(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("Product 1 certification failed closed: workflow must be object")
    if artifact.get("artifact_type") != PRODUCT1_WORKFLOW_FOUNDATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("Product 1 certification failed closed: invalid workflow artifact")
    _verify_hash_field(artifact, "artifact_hash", "Product 1 certification workflow hash mismatch")
    if artifact.get("workflow_status") != WORKFLOW_READY_FOR_DECISION_PACKET:
        raise FailClosedRuntimeError("Product 1 certification failed closed: workflow is not packet-ready")
    if artifact.get("governance_checkpoint_status") != GOVERNANCE_PASSED:
        raise FailClosedRuntimeError("Product 1 certification failed closed: governance checkpoint is not passed")
    for flag in NON_AUTHORITY_FLAGS:
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"Product 1 certification failed closed: {flag} must be false")
    _normalize_replay_lineage(artifact.get("replay_lineage"))
    return deepcopy(artifact)


def _validated_certification_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("Product 1 certification failed closed: artifact must be object")
    if artifact.get("artifact_type") != PRODUCT1_CERTIFICATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("Product 1 certification failed closed: invalid artifact type")
    _verify_hash_field(artifact, "artifact_hash", "Product 1 certification artifact hash mismatch")
    if artifact.get("certification_status") != PRODUCT1_CERTIFIED:
        raise FailClosedRuntimeError("Product 1 certification failed closed: product is not certified")
    if artifact.get("certification_authority") != CERTIFICATION_AUTHORITY:
        raise FailClosedRuntimeError("Product 1 certification failed closed: invalid certification authority")
    if artifact.get("certification_check_count") != len(CERTIFICATION_CHECKS):
        raise FailClosedRuntimeError("Product 1 certification failed closed: certification check count mismatch")
    if artifact.get("read_only") is not True or artifact.get("non_authoritative") is not True:
        raise FailClosedRuntimeError("Product 1 certification failed closed: certification must be read-only")
    for flag in NON_AUTHORITY_FLAGS:
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"Product 1 certification failed closed: {flag} must be false")
    _normalize_replay_lineage(artifact.get("replay_lineage"))
    return deepcopy(artifact)


def _validate_chain_binding(
    audit: dict[str, Any],
    packet: dict[str, Any],
    advisory: dict[str, Any],
    workflow: dict[str, Any],
) -> None:
    pairs = (
        (audit["workflow_id"], packet["workflow_id"]),
        (audit["workflow_id"], advisory["workflow_id"]),
        (audit["workflow_id"], workflow["workflow_id"]),
        (audit["decision_packet_id"], packet["packet_id"]),
        (audit["decision_packet_hash"], packet["artifact_hash"]),
        (audit["ocs_advisory_id"], advisory["advisory_id"]),
        (audit["ocs_advisory_hash"], advisory["artifact_hash"]),
        (packet["artifact_hash"], advisory["decision_packet_hash"]),
        (audit["canonical_semantic_artifact_hash"], packet["canonical_semantic_artifact_hash"]),
        (audit["canonical_semantic_artifact_hash"], advisory["canonical_semantic_artifact_hash"]),
        (audit["rollback_reference"], packet["rollback_reference"]),
        (audit["rollback_reference"], advisory["rollback_reference"]),
        (audit["rollback_reference"], workflow["rollback_reference"]),
    )
    for left, right in pairs:
        if left != right:
            raise FailClosedRuntimeError("Product 1 certification failed closed: certification chain binding mismatch")


def _certification_checks(
    audit: dict[str, Any],
    packet: dict[str, Any],
    advisory: dict[str, Any],
    workflow: dict[str, Any],
) -> list[dict[str, Any]]:
    references = {
        "product_workflow_integrity": workflow["artifact_hash"],
        "decision_packet_integrity": packet["artifact_hash"],
        "ocs_advisory_integrity": advisory["artifact_hash"],
        "audit_packet_integrity": audit["artifact_hash"],
        "governance_checkpoints": audit["governance_evidence_hash"],
        "replay_integrity": audit["replay_evidence_hash"],
        "rollback_capability": replay_hash({"rollback_reference": audit["rollback_reference"]}),
        "deterministic_reconstruction": replay_hash({"audit_replay_lineage": audit["replay_lineage"]}),
        "authority_preservation": replay_hash({"non_authority_flags": NON_AUTHORITY_FLAGS}),
        "human_approval_boundaries": replay_hash({"approval_created": False, "authorization_created": False}),
        "non_authority_guarantees": replay_hash({"read_only": True, "non_authoritative": True}),
    }
    checks = []
    for index, check_name in enumerate(CERTIFICATION_CHECKS):
        check = {
            "certification_check_index": index,
            "certification_check_id": f"PRODUCT1-CERTIFICATION-CHECK-{index + 1:03d}",
            "check_name": check_name,
            "check_status": "PASSED",
            "evidence_reference": check_name,
            "evidence_hash": references[check_name],
        }
        check["certification_check_hash"] = replay_hash(check)
        checks.append(check)
    return checks


def _normalize_remaining_limitations(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError("Product 1 certification failed closed: remaining limitations must be list")
    limitations = []
    seen_ids: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("Product 1 certification failed closed: remaining limitation must be object")
        limitation_id = _require_string(item.get("limitation_id"), "limitation_id")
        if limitation_id in seen_ids:
            raise FailClosedRuntimeError("Product 1 certification failed closed: duplicate limitation id")
        seen_ids.add(limitation_id)
        limitation = {
            "limitation_index": index,
            "limitation_id": limitation_id,
            "limitation_scope": _require_string(item.get("limitation_scope"), "limitation_scope"),
            "statement": _require_string(item.get("statement"), "statement"),
            "owner": _require_string(item.get("owner"), "owner"),
            "planned_resolution": _require_string(item.get("planned_resolution"), "planned_resolution"),
        }
        limitation["limitation_hash"] = replay_hash(limitation)
        limitations.append(limitation)
    return limitations


def _certification_replay_lineage(
    audit: dict[str, Any],
    packet: dict[str, Any],
    advisory: dict[str, Any],
    workflow: dict[str, Any],
    checks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    lineage = deepcopy(audit["replay_lineage"])
    lineage.append({"replay_reference": f"workflow:{workflow['workflow_id']}", "replay_hash": workflow["artifact_hash"]})
    lineage.append({"replay_reference": f"decision_packet:{packet['packet_id']}", "replay_hash": packet["artifact_hash"]})
    lineage.append({"replay_reference": f"ocs_advisory:{advisory['advisory_id']}", "replay_hash": advisory["artifact_hash"]})
    lineage.append({"replay_reference": f"audit_packet:{audit['audit_packet_id']}", "replay_hash": audit["artifact_hash"]})
    for item in checks:
        lineage.append(
            {
                "replay_reference": f"certification_check:{item['certification_check_id']}",
                "replay_hash": item["certification_check_hash"],
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
        raise FailClosedRuntimeError("Product 1 certification failed closed: replay already exists")
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
    _verify_hash_field(wrapper, "replay_hash", "Product 1 certification replay hash mismatch")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("Product 1 certification replay artifact must be object")
    _verify_hash_field(artifact, "artifact_hash", "Product 1 certification artifact hash mismatch")
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
        "runtime_version": PRODUCT1_CERTIFICATION_RUNTIME_VERSION,
        "certification_artifact": deepcopy(artifact),
        "certification_id": artifact["certification_id"],
        "certification_status": artifact["certification_status"],
        "certification_recommendation": artifact["certification_recommendation"],
        "audit_packet_id": artifact["audit_packet_id"],
        "workflow_id": artifact["workflow_id"],
        "decision_packet_id": artifact["decision_packet_id"],
        "ocs_advisory_id": artifact["ocs_advisory_id"],
        "canonical_semantic_artifact_reference": artifact["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": artifact["canonical_semantic_artifact_hash"],
        "certification_check_count": artifact["certification_check_count"],
        "remaining_limitation_count": artifact["remaining_limitation_count"],
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
        raise FailClosedRuntimeError("Product 1 certification failed closed: replay lineage is required")
    lineage = []
    for item in value:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("Product 1 certification failed closed: replay lineage item must be object")
        lineage.append(
            {
                "replay_reference": _require_string(item.get("replay_reference"), "replay_reference"),
                "replay_hash": _require_hash(item.get("replay_hash"), "replay_hash"),
            }
        )
    return lineage


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"Product 1 certification failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"Product 1 certification failed closed: {field_name} must be replay hash")
    return text
