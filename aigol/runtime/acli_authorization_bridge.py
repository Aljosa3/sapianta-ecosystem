"""Authorization-readiness bridge for conversational ACLI proposal evidence."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.acli_proposal_approval_bridge import (
    ACLI_PROPOSAL_APPROVAL_BRIDGE_ARTIFACT_V1,
    APPROVAL_RECORDED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


ACLI_AUTHORIZATION_BRIDGE_RUNTIME_VERSION = "G3_02_IMPLEMENTATION_PHASE_5_AUTHORIZATION_BRIDGE_RUNTIME_V1"
ACLI_AUTHORIZATION_BRIDGE_ARTIFACT_V1 = "ACLI_AUTHORIZATION_BRIDGE_ARTIFACT_V1"

AUTHORIZATION_READY = "AUTHORIZATION_READY"
AUTHORIZATION_BLOCKED = "AUTHORIZATION_BLOCKED"
PRECONDITIONS_SATISFIED = "PRECONDITIONS_SATISFIED"
PRECONDITIONS_FAILED = "PRECONDITIONS_FAILED"

APPROVAL_REQUEST_MISSING = "APPROVAL_REQUEST_MISSING"
APPROVAL_DECISION_MISSING = "APPROVAL_DECISION_MISSING"

EVENT_AUTHORIZATION_BRIDGE_RECORDED = "acli_authorization_bridge_recorded"

NON_EXECUTING_FLAGS = (
    "provider_invoked",
    "worker_invoked",
    "authorization_created",
    "execution_requested",
    "repository_mutated",
    "deployment_requested",
    "product1_workflow_started",
)


def create_conversational_authorization_bridge(
    *,
    authorization_bridge_id: str,
    proposal_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    rollback_reference: str | None = None,
) -> dict[str, Any]:
    """Create authorization-readiness evidence without authorizing execution."""

    proposal = _validated_proposal_artifact(proposal_artifact)
    latest_request = proposal["approval_requests"][-1] if proposal["approval_requests"] else None
    latest_decision = proposal["approval_decisions"][-1] if proposal["approval_decisions"] else None
    preconditions = _precondition_evidence(proposal, latest_request, latest_decision)
    readiness_status = AUTHORIZATION_READY if preconditions["precondition_status"] == PRECONDITIONS_SATISFIED else AUTHORIZATION_BLOCKED
    approval_request_id = (
        latest_request["approval_request_id"]
        if isinstance(latest_request, dict) and latest_request.get("approval_request_id")
        else APPROVAL_REQUEST_MISSING
    )
    approval_request_hash = (
        latest_request["approval_request_hash"]
        if isinstance(latest_request, dict) and latest_request.get("approval_request_hash")
        else replay_hash({"approval_request_id": APPROVAL_REQUEST_MISSING, "proposal_id": proposal["proposal_id"]})
    )
    approval_decision_reference = (
        latest_decision["approval_decision_id"]
        if isinstance(latest_decision, dict) and latest_decision.get("approval_decision_id")
        else APPROVAL_DECISION_MISSING
    )
    approval_decision_hash = (
        latest_decision["approval_decision_hash"]
        if isinstance(latest_decision, dict) and latest_decision.get("approval_decision_hash")
        else replay_hash({"approval_decision_reference": APPROVAL_DECISION_MISSING, "proposal_id": proposal["proposal_id"]})
    )
    event = _event(
        event_index=0,
        event_type=EVENT_AUTHORIZATION_BRIDGE_RECORDED,
        occurred_at=created_at,
        previous_event_hash="",
        event_payload={
            "authorization_bridge_id": _require_string(authorization_bridge_id, "authorization_bridge_id"),
            "proposal_id": proposal["proposal_id"],
            "approval_request_id": approval_request_id,
            "approval_decision_reference": approval_decision_reference,
            "authorization_readiness_status": readiness_status,
            "precondition_status": preconditions["precondition_status"],
        },
    )
    artifact = _authorization_bridge_artifact(
        authorization_bridge_id=authorization_bridge_id,
        proposal=proposal,
        approval_request_id=approval_request_id,
        approval_request_hash=approval_request_hash,
        approval_decision_reference=approval_decision_reference,
        approval_decision_hash=approval_decision_hash,
        authorization_readiness_status=readiness_status,
        precondition_status=preconditions["precondition_status"],
        precondition_evidence=preconditions["precondition_evidence"],
        replay_lineage=_authorization_replay_lineage(
            proposal=proposal,
            approval_request_id=approval_request_id,
            approval_request_hash=approval_request_hash,
            approval_decision_reference=approval_decision_reference,
            approval_decision_hash=approval_decision_hash,
        ),
        rollback_reference=rollback_reference or proposal["rollback_reference"],
        bridge_events=[event],
        created_at=created_at,
        failure_reason=None if readiness_status == AUTHORIZATION_READY else preconditions["failure_reason"],
    )
    replay_path = Path(replay_dir)
    _persist_step(replay_path, 0, EVENT_AUTHORIZATION_BRIDGE_RECORDED, artifact)
    return _capture(artifact, replay_path)


def reconstruct_acli_authorization_bridge_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate ACLI authorization bridge replay."""

    replay_path = Path(replay_dir)
    wrappers = [_load_verified_wrapper(path) for path in sorted(replay_path.glob("*.json"))]
    if not wrappers:
        raise FailClosedRuntimeError("ACLI authorization bridge failed closed: replay is empty")
    for index, wrapper in enumerate(wrappers):
        if wrapper.get("replay_index") != index:
            raise FailClosedRuntimeError("ACLI authorization bridge replay ordering mismatch")
    artifact = _validated_authorization_bridge_artifact(wrappers[-1]["artifact"])
    events = artifact["bridge_events"]
    if len(events) != len(wrappers):
        raise FailClosedRuntimeError("ACLI authorization bridge event count mismatch")
    for index, event in enumerate(events):
        if event["event_index"] != index:
            raise FailClosedRuntimeError("ACLI authorization bridge event order mismatch")
        expected_previous = "" if index == 0 else events[index - 1]["event_hash"]
        if event["previous_event_hash"] != expected_previous:
            raise FailClosedRuntimeError("ACLI authorization bridge event lineage mismatch")
        _verify_hash_field(event, "event_hash", "ACLI authorization bridge event hash mismatch")
    return {
        "authorization_bridge_id": artifact["authorization_bridge_id"],
        "originating_session_id": artifact["originating_session_id"],
        "originating_turn_id": artifact["originating_turn_id"],
        "proposal_id": artifact["proposal_id"],
        "proposal_hash": artifact["proposal_hash"],
        "approval_request_id": artifact["approval_request_id"],
        "approval_decision_reference": artifact["approval_decision_reference"],
        "canonical_semantic_artifact_reference": artifact["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": artifact["canonical_semantic_artifact_hash"],
        "authorization_readiness_status": artifact["authorization_readiness_status"],
        "precondition_status": artifact["precondition_status"],
        "precondition_evidence_hash": artifact["precondition_evidence_hash"],
        "replay_lineage_count": len(artifact["replay_lineage"]),
        "rollback_reference": artifact["rollback_reference"],
        "event_count": len(events),
        "event_hash_chain": [event["event_hash"] for event in events],
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "product1_workflow_started": False,
        "replay_visible": True,
        "artifact_hash": artifact["artifact_hash"],
        "replay_hash": replay_hash(wrappers),
    }


def _authorization_bridge_artifact(
    *,
    authorization_bridge_id: str,
    proposal: dict[str, Any],
    approval_request_id: str,
    approval_request_hash: str,
    approval_decision_reference: str,
    approval_decision_hash: str,
    authorization_readiness_status: str,
    precondition_status: str,
    precondition_evidence: list[dict[str, Any]],
    replay_lineage: list[dict[str, Any]],
    rollback_reference: str,
    bridge_events: list[dict[str, Any]],
    created_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": ACLI_AUTHORIZATION_BRIDGE_ARTIFACT_V1,
        "runtime_version": ACLI_AUTHORIZATION_BRIDGE_RUNTIME_VERSION,
        "migration_batch_id": "G3_02_IMPLEMENTATION_PHASE_5_AUTHORIZATION_BRIDGE_V1",
        "authorization_bridge_id": _require_string(authorization_bridge_id, "authorization_bridge_id"),
        "originating_session_id": proposal["originating_session_id"],
        "originating_conversation_id": proposal["originating_conversation_id"],
        "originating_turn_id": proposal["originating_turn_id"],
        "originating_turn_hash": proposal["originating_turn_hash"],
        "proposal_id": proposal["proposal_id"],
        "proposal_hash": proposal["artifact_hash"],
        "approval_request_id": _require_string(approval_request_id, "approval_request_id"),
        "approval_request_hash": _require_hash(approval_request_hash, "approval_request_hash"),
        "approval_decision_reference": _require_string(approval_decision_reference, "approval_decision_reference"),
        "approval_decision_hash": _require_hash(approval_decision_hash, "approval_decision_hash"),
        "canonical_semantic_artifact_reference": proposal["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": proposal["canonical_semantic_artifact_hash"],
        "authorization_readiness_status": _require_string(
            authorization_readiness_status,
            "authorization_readiness_status",
        ),
        "precondition_status": _require_string(precondition_status, "precondition_status"),
        "precondition_evidence": deepcopy(precondition_evidence),
        "precondition_evidence_hash": replay_hash(precondition_evidence),
        "replay_lineage": _normalize_replay_lineage(replay_lineage),
        "rollback_reference": _require_string(rollback_reference, "rollback_reference"),
        "bridge_events": deepcopy(bridge_events),
        "authorization_intent_created": True,
        "authorization_readiness_visible": True,
        "approval_to_authorization_lineage_visible": True,
        "precondition_evidence_visible": True,
        "rejection_or_missing_approval_handling_visible": authorization_readiness_status == AUTHORIZATION_BLOCKED,
        "non_executing": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "product1_workflow_started": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _precondition_evidence(
    proposal: dict[str, Any],
    latest_request: dict[str, Any] | None,
    latest_decision: dict[str, Any] | None,
) -> dict[str, Any]:
    checks = [
        _precondition("proposal_artifact_valid", True, proposal["artifact_hash"]),
        _precondition("approval_request_present", isinstance(latest_request, dict), None),
        _precondition("approval_decision_present", isinstance(latest_decision, dict), None),
        _precondition("proposal_status_approved", proposal.get("proposal_status") == APPROVAL_RECORDED, None),
        _precondition("approval_status_approved", proposal.get("approval_status") == APPROVAL_RECORDED, None),
        _precondition(
            "approval_decision_approved",
            isinstance(latest_decision, dict) and latest_decision.get("decision") == "APPROVED",
            latest_decision.get("approval_decision_hash") if isinstance(latest_decision, dict) else None,
        ),
        _precondition(
            "approval_request_bound_to_proposal",
            isinstance(latest_request, dict) and latest_request.get("proposal_id") == proposal["proposal_id"],
            latest_request.get("approval_request_hash") if isinstance(latest_request, dict) else None,
        ),
        _precondition(
            "approval_decision_bound_to_request",
            isinstance(latest_request, dict)
            and isinstance(latest_decision, dict)
            and latest_decision.get("approval_request_id") == latest_request.get("approval_request_id"),
            latest_decision.get("approval_decision_hash") if isinstance(latest_decision, dict) else None,
        ),
        _precondition("csa_bound", bool(proposal.get("canonical_semantic_artifact_hash")), proposal["canonical_semantic_artifact_hash"]),
        _precondition("rollback_reference_present", bool(proposal.get("rollback_reference")), None),
        _precondition("non_executing_boundary_preserved", True, None),
    ]
    failed = [check["precondition_name"] for check in checks if check["precondition_met"] is not True]
    return {
        "precondition_status": PRECONDITIONS_SATISFIED if not failed else PRECONDITIONS_FAILED,
        "precondition_evidence": checks,
        "failure_reason": None if not failed else "authorization bridge blocked: " + ", ".join(failed),
    }


def _precondition(name: str, met: bool, evidence_hash: str | None) -> dict[str, Any]:
    item = {
        "precondition_name": _require_string(name, "precondition_name"),
        "precondition_met": bool(met),
        "evidence_hash": evidence_hash if isinstance(evidence_hash, str) and evidence_hash else None,
    }
    item["precondition_hash"] = replay_hash(item)
    return item


def _authorization_replay_lineage(
    *,
    proposal: dict[str, Any],
    approval_request_id: str,
    approval_request_hash: str,
    approval_decision_reference: str,
    approval_decision_hash: str,
) -> list[dict[str, Any]]:
    lineage = deepcopy(proposal["replay_lineage"])
    lineage.append({"replay_reference": f"proposal:{proposal['proposal_id']}", "replay_hash": proposal["artifact_hash"]})
    lineage.append({"replay_reference": f"approval_request:{approval_request_id}", "replay_hash": approval_request_hash})
    lineage.append({"replay_reference": f"approval_decision:{approval_decision_reference}", "replay_hash": approval_decision_hash})
    return _normalize_replay_lineage(lineage)


def _validated_proposal_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("ACLI authorization bridge failed closed: proposal artifact must be object")
    if artifact.get("artifact_type") != ACLI_PROPOSAL_APPROVAL_BRIDGE_ARTIFACT_V1:
        raise FailClosedRuntimeError("ACLI authorization bridge failed closed: invalid proposal artifact type")
    _verify_hash_field(artifact, "artifact_hash", "ACLI authorization bridge proposal hash mismatch")
    for flag in NON_EXECUTING_FLAGS:
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"ACLI authorization bridge failed closed: {flag} must be false")
    if not isinstance(artifact.get("approval_requests"), list):
        raise FailClosedRuntimeError("ACLI authorization bridge failed closed: approval requests must be list")
    if not isinstance(artifact.get("approval_decisions"), list):
        raise FailClosedRuntimeError("ACLI authorization bridge failed closed: approval decisions must be list")
    _require_hash(artifact.get("canonical_semantic_artifact_hash"), "canonical_semantic_artifact_hash")
    _normalize_replay_lineage(artifact.get("replay_lineage"))
    return deepcopy(artifact)


def _validated_authorization_bridge_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("ACLI authorization bridge failed closed: artifact must be object")
    if artifact.get("artifact_type") != ACLI_AUTHORIZATION_BRIDGE_ARTIFACT_V1:
        raise FailClosedRuntimeError("ACLI authorization bridge failed closed: invalid artifact type")
    _verify_hash_field(artifact, "artifact_hash", "ACLI authorization bridge artifact hash mismatch")
    for flag in NON_EXECUTING_FLAGS:
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"ACLI authorization bridge failed closed: {flag} must be false")
    if artifact.get("non_executing") is not True:
        raise FailClosedRuntimeError("ACLI authorization bridge failed closed: non-executing flag is required")
    _require_hash(artifact.get("canonical_semantic_artifact_hash"), "canonical_semantic_artifact_hash")
    _normalize_replay_lineage(artifact.get("replay_lineage"))
    return deepcopy(artifact)


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
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
    }
    event["event_hash"] = replay_hash(event)
    return event


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if (replay_path / f"{index:03d}_{step}.json").exists():
        raise FailClosedRuntimeError("ACLI authorization bridge failed closed: replay already exists")
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
    _verify_hash_field(wrapper, "replay_hash", "ACLI authorization bridge replay hash mismatch")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("ACLI authorization bridge replay artifact must be object")
    _verify_hash_field(artifact, "artifact_hash", "ACLI authorization bridge artifact hash mismatch")
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
        "runtime_version": ACLI_AUTHORIZATION_BRIDGE_RUNTIME_VERSION,
        "authorization_bridge_artifact": deepcopy(artifact),
        "authorization_bridge_id": artifact["authorization_bridge_id"],
        "originating_session_id": artifact["originating_session_id"],
        "originating_turn_id": artifact["originating_turn_id"],
        "proposal_id": artifact["proposal_id"],
        "approval_request_id": artifact["approval_request_id"],
        "approval_decision_reference": artifact["approval_decision_reference"],
        "canonical_semantic_artifact_reference": artifact["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": artifact["canonical_semantic_artifact_hash"],
        "authorization_readiness_status": artifact["authorization_readiness_status"],
        "precondition_status": artifact["precondition_status"],
        "rollback_reference": artifact["rollback_reference"],
        "replay_reference": str(replay_path),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "product1_workflow_started": False,
        "replay_visible": True,
        "failure_reason": artifact["failure_reason"],
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _normalize_replay_lineage(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError("ACLI authorization bridge failed closed: replay lineage is required")
    lineage = []
    for item in value:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("ACLI authorization bridge failed closed: replay lineage item must be object")
        lineage.append(
            {
                "replay_reference": _require_string(item.get("replay_reference"), "replay_reference"),
                "replay_hash": _require_hash(item.get("replay_hash"), "replay_hash"),
            }
        )
    return lineage


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"ACLI authorization bridge failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"ACLI authorization bridge failed closed: {field_name} must be replay hash")
    return text
