"""Proposal and approval-request bridge for conversational ACLI sessions."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.acli_conversational_development_session import (
    ACLI_CONVERSATIONAL_DEVELOPMENT_SESSION_ARTIFACT_V1,
)
from aigol.runtime.approval.approval_request import ApprovalRequest
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


ACLI_PROPOSAL_APPROVAL_BRIDGE_RUNTIME_VERSION = (
    "G3_02_IMPLEMENTATION_PHASE_4_PROPOSAL_APPROVAL_BRIDGE_RUNTIME_V1"
)
ACLI_PROPOSAL_APPROVAL_BRIDGE_ARTIFACT_V1 = "ACLI_PROPOSAL_APPROVAL_BRIDGE_ARTIFACT_V1"

PROPOSAL_DRAFTED = "PROPOSAL_DRAFTED"
PROPOSAL_REVISED = "PROPOSAL_REVISED"
APPROVAL_REQUESTED = "APPROVAL_REQUESTED"
APPROVAL_RECORDED = "APPROVAL_RECORDED"
PROPOSAL_REJECTED = "PROPOSAL_REJECTED"
CLARIFICATION_RETURNED = "CLARIFICATION_RETURNED"
FAILED_CLOSED = "FAILED_CLOSED"

APPROVAL_NOT_REQUESTED = "APPROVAL_NOT_REQUESTED"
APPROVAL_REJECTED = "REJECTED"
APPROVAL_CLARIFICATION_REQUESTED = "CLARIFICATION_REQUESTED"

APPROVAL_DECISIONS = {
    "APPROVED",
    "REJECTED",
    "CLARIFICATION_REQUESTED",
}

EVENT_PROPOSAL_CREATED = "acli_proposal_created"
EVENT_PROPOSAL_REVISED = "acli_proposal_revised"
EVENT_APPROVAL_REQUEST_GENERATED = "acli_approval_request_generated"
EVENT_APPROVAL_DECISION_RECORDED = "acli_approval_decision_recorded"

NON_AUTHORITY_FLAGS = (
    "provider_invoked",
    "worker_invoked",
    "approval_created",
    "authorization_created",
    "execution_requested",
    "repository_mutated",
    "deployment_requested",
    "product1_workflow_started",
)


def create_conversational_development_proposal(
    *,
    proposal_id: str,
    conversation_artifact: dict[str, Any],
    originating_turn_id: str,
    proposal_version: int,
    proposal_summary: str,
    rollback_reference: str,
    created_at: str,
    replay_dir: str | Path,
    proposal_scope: str = "CONVERSATIONAL_DEVELOPMENT_PROPOSAL",
) -> dict[str, Any]:
    """Create a replay-visible proposal artifact from a conversational ACLI turn."""

    conversation = _validated_conversation_artifact(conversation_artifact)
    turn = _find_turn(conversation, originating_turn_id)
    if proposal_version < 1:
        raise FailClosedRuntimeError("ACLI proposal approval bridge failed closed: proposal version must be positive")
    replay_path = Path(replay_dir)
    _ensure_step_available(replay_path, 0, EVENT_PROPOSAL_CREATED)
    version = _proposal_version(
        proposal_version=proposal_version,
        proposal_summary=proposal_summary,
        rollback_reference=rollback_reference,
        recorded_at=created_at,
        previous_version_hash="",
    )
    event = _event(
        event_index=0,
        event_type=EVENT_PROPOSAL_CREATED,
        occurred_at=created_at,
        previous_event_hash="",
        event_payload={
            "proposal_id": _require_string(proposal_id, "proposal_id"),
            "originating_session_id": conversation["session_id"],
            "originating_turn_id": turn["turn_id"],
            "canonical_semantic_artifact_hash": turn["canonical_semantic_artifact_hash"],
            "proposal_version_hash": version["proposal_version_hash"],
        },
    )
    artifact = _proposal_artifact(
        proposal_id=proposal_id,
        originating_session_id=conversation["session_id"],
        originating_conversation_id=conversation["conversation_id"],
        originating_turn_id=turn["turn_id"],
        originating_turn_hash=turn["turn_hash"],
        conversation_hash=conversation["artifact_hash"],
        canonical_semantic_artifact_reference=turn["canonical_semantic_artifact_reference"],
        canonical_semantic_artifact_hash=turn["canonical_semantic_artifact_hash"],
        proposal_scope=proposal_scope,
        proposal_version=proposal_version,
        proposal_status=PROPOSAL_DRAFTED,
        approval_status=APPROVAL_NOT_REQUESTED,
        rollback_reference=rollback_reference,
        proposal_versions=[version],
        approval_requests=[],
        approval_decisions=[],
        bridge_events=[event],
        replay_lineage=_bridge_replay_lineage(conversation, turn),
        created_at=created_at,
        updated_at=created_at,
        clarification_return_reference=None,
        rejection_reference=None,
        failure_reason=None,
    )
    _persist_step(replay_path, 0, EVENT_PROPOSAL_CREATED, artifact)
    return _capture(artifact, replay_path)


def revise_conversational_development_proposal(
    *,
    proposal_artifact: dict[str, Any],
    proposal_version: int,
    proposal_summary: str,
    rollback_reference: str,
    revised_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Record a new non-authoritative proposal version."""

    proposal = _validated_bridge_artifact(proposal_artifact)
    if proposal["proposal_status"] in {APPROVAL_RECORDED, PROPOSAL_REJECTED, FAILED_CLOSED}:
        raise FailClosedRuntimeError("ACLI proposal approval bridge failed closed: terminal proposal cannot be revised")
    if proposal_version <= proposal["proposal_version"]:
        raise FailClosedRuntimeError("ACLI proposal approval bridge failed closed: proposal version must increase")
    event_index = len(proposal["bridge_events"])
    previous_version_hash = proposal["proposal_versions"][-1]["proposal_version_hash"]
    version = _proposal_version(
        proposal_version=proposal_version,
        proposal_summary=proposal_summary,
        rollback_reference=rollback_reference,
        recorded_at=revised_at,
        previous_version_hash=previous_version_hash,
    )
    event = _event(
        event_index=event_index,
        event_type=EVENT_PROPOSAL_REVISED,
        occurred_at=revised_at,
        previous_event_hash=proposal["bridge_events"][-1]["event_hash"],
        event_payload={
            "proposal_id": proposal["proposal_id"],
            "proposal_version": proposal_version,
            "proposal_version_hash": version["proposal_version_hash"],
            "previous_version_hash": previous_version_hash,
        },
    )
    artifact = _proposal_artifact_from_existing(
        proposal,
        proposal_version=proposal_version,
        proposal_status=PROPOSAL_REVISED,
        approval_status=APPROVAL_NOT_REQUESTED,
        rollback_reference=rollback_reference,
        proposal_versions=proposal["proposal_versions"] + [version],
        approval_requests=proposal["approval_requests"],
        approval_decisions=proposal["approval_decisions"],
        bridge_events=proposal["bridge_events"] + [event],
        updated_at=revised_at,
        clarification_return_reference=None,
        rejection_reference=None,
        failure_reason=proposal["failure_reason"],
    )
    _persist_step(Path(replay_dir), event_index, EVENT_PROPOSAL_REVISED, artifact)
    return _capture(artifact, Path(replay_dir))


def generate_conversational_approval_request(
    *,
    proposal_artifact: dict[str, Any],
    approval_request_id: str,
    requested_at: str,
    replay_dir: str | Path,
    risk_class: str = "HUMAN_CONFIRMATION_REQUIRED",
) -> dict[str, Any]:
    """Generate approval-request evidence without granting approval or authorization."""

    proposal = _validated_bridge_artifact(proposal_artifact)
    if proposal["approval_status"] not in {APPROVAL_NOT_REQUESTED, APPROVAL_CLARIFICATION_REQUESTED}:
        raise FailClosedRuntimeError("ACLI proposal approval bridge failed closed: approval request state mismatch")
    event_index = len(proposal["bridge_events"])
    approval_request = ApprovalRequest(
        approval_request_id=_require_string(approval_request_id, "approval_request_id"),
        runtime_id=ACLI_PROPOSAL_APPROVAL_BRIDGE_RUNTIME_VERSION,
        requested_action=f"review_proposal:{proposal['proposal_id']}:v{proposal['proposal_version']}",
        risk_class=_require_string(risk_class, "risk_class"),
        approval_required=True,
        requested_by="acli_conversational_development_session",
        created_at=_require_string(requested_at, "requested_at"),
    ).to_dict()
    request = {
        "approval_request": approval_request,
        "approval_request_id": approval_request["approval_request_id"],
        "proposal_id": proposal["proposal_id"],
        "proposal_version": proposal["proposal_version"],
        "proposal_hash": proposal["artifact_hash"],
        "canonical_semantic_artifact_reference": proposal["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": proposal["canonical_semantic_artifact_hash"],
        "approval_required": True,
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "requested_at": requested_at,
    }
    request["approval_request_hash"] = replay_hash(request)
    event = _event(
        event_index=event_index,
        event_type=EVENT_APPROVAL_REQUEST_GENERATED,
        occurred_at=requested_at,
        previous_event_hash=proposal["bridge_events"][-1]["event_hash"],
        event_payload={
            "proposal_id": proposal["proposal_id"],
            "approval_request_id": approval_request["approval_request_id"],
            "approval_request_hash": request["approval_request_hash"],
        },
    )
    artifact = _proposal_artifact_from_existing(
        proposal,
        proposal_version=proposal["proposal_version"],
        proposal_status=APPROVAL_REQUESTED,
        approval_status=APPROVAL_REQUESTED,
        rollback_reference=proposal["rollback_reference"],
        proposal_versions=proposal["proposal_versions"],
        approval_requests=proposal["approval_requests"] + [request],
        approval_decisions=proposal["approval_decisions"],
        bridge_events=proposal["bridge_events"] + [event],
        updated_at=requested_at,
        clarification_return_reference=None,
        rejection_reference=None,
        failure_reason=proposal["failure_reason"],
    )
    _persist_step(Path(replay_dir), event_index, EVENT_APPROVAL_REQUEST_GENERATED, artifact)
    return _capture(artifact, Path(replay_dir))


def record_conversational_approval_decision(
    *,
    proposal_artifact: dict[str, Any],
    approval_decision_id: str,
    decision: str,
    decided_at: str,
    replay_dir: str | Path,
    decision_rationale_hash: str,
    clarification_return_reference: str | None = None,
    rejection_reference: str | None = None,
) -> dict[str, Any]:
    """Record approval state without authorizing execution."""

    proposal = _validated_bridge_artifact(proposal_artifact)
    if proposal["approval_status"] != APPROVAL_REQUESTED or not proposal["approval_requests"]:
        raise FailClosedRuntimeError("ACLI proposal approval bridge failed closed: approval request is required")
    normalized_decision = _require_string(decision, "decision").upper()
    if normalized_decision not in APPROVAL_DECISIONS:
        raise FailClosedRuntimeError("ACLI proposal approval bridge failed closed: unsupported approval decision")
    latest_request = proposal["approval_requests"][-1]
    proposal_status, approval_status = _status_for_decision(normalized_decision)
    clarification_reference = _optional_string(clarification_return_reference)
    rejection_ref = _optional_string(rejection_reference)
    if normalized_decision == "CLARIFICATION_REQUESTED" and clarification_reference is None:
        raise FailClosedRuntimeError("ACLI proposal approval bridge failed closed: clarification return reference required")
    if normalized_decision == "REJECTED" and rejection_ref is None:
        raise FailClosedRuntimeError("ACLI proposal approval bridge failed closed: rejection reference required")
    event_index = len(proposal["bridge_events"])
    decision_artifact = {
        "approval_decision_id": _require_string(approval_decision_id, "approval_decision_id"),
        "approval_request_id": latest_request["approval_request_id"],
        "approval_request_hash": latest_request["approval_request_hash"],
        "proposal_id": proposal["proposal_id"],
        "proposal_version": proposal["proposal_version"],
        "decision": normalized_decision,
        "approval_status": approval_status,
        "decision_rationale_hash": _require_hash(decision_rationale_hash, "decision_rationale_hash"),
        "clarification_return_reference": clarification_reference,
        "rejection_reference": rejection_ref,
        "decided_at": _require_string(decided_at, "decided_at"),
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
    }
    decision_artifact["approval_decision_hash"] = replay_hash(decision_artifact)
    event = _event(
        event_index=event_index,
        event_type=EVENT_APPROVAL_DECISION_RECORDED,
        occurred_at=decided_at,
        previous_event_hash=proposal["bridge_events"][-1]["event_hash"],
        event_payload={
            "proposal_id": proposal["proposal_id"],
            "approval_decision_id": decision_artifact["approval_decision_id"],
            "approval_decision_hash": decision_artifact["approval_decision_hash"],
            "approval_status": approval_status,
        },
    )
    artifact = _proposal_artifact_from_existing(
        proposal,
        proposal_version=proposal["proposal_version"],
        proposal_status=proposal_status,
        approval_status=approval_status,
        rollback_reference=proposal["rollback_reference"],
        proposal_versions=proposal["proposal_versions"],
        approval_requests=proposal["approval_requests"],
        approval_decisions=proposal["approval_decisions"] + [decision_artifact],
        bridge_events=proposal["bridge_events"] + [event],
        updated_at=decided_at,
        clarification_return_reference=clarification_reference,
        rejection_reference=rejection_ref,
        failure_reason=proposal["failure_reason"],
    )
    _persist_step(Path(replay_dir), event_index, EVENT_APPROVAL_DECISION_RECORDED, artifact)
    return _capture(artifact, Path(replay_dir))


def reconstruct_acli_proposal_approval_bridge_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate conversational proposal/approval bridge replay."""

    replay_path = Path(replay_dir)
    wrappers = [_load_verified_wrapper(path) for path in sorted(replay_path.glob("*.json"))]
    if not wrappers:
        raise FailClosedRuntimeError("ACLI proposal approval bridge failed closed: replay is empty")
    for index, wrapper in enumerate(wrappers):
        if wrapper.get("replay_index") != index:
            raise FailClosedRuntimeError("ACLI proposal approval bridge replay ordering mismatch")
    artifact = _validated_bridge_artifact(wrappers[-1]["artifact"])
    events = artifact["bridge_events"]
    if len(events) != len(wrappers):
        raise FailClosedRuntimeError("ACLI proposal approval bridge event count mismatch")
    for index, event in enumerate(events):
        if event["event_index"] != index:
            raise FailClosedRuntimeError("ACLI proposal approval bridge event order mismatch")
        expected_previous = "" if index == 0 else events[index - 1]["event_hash"]
        if event["previous_event_hash"] != expected_previous:
            raise FailClosedRuntimeError("ACLI proposal approval bridge event lineage mismatch")
        _verify_hash_field(event, "event_hash", "ACLI proposal approval bridge event hash mismatch")
    for index, version in enumerate(artifact["proposal_versions"]):
        if version["proposal_version_index"] != index:
            raise FailClosedRuntimeError("ACLI proposal approval bridge proposal version order mismatch")
        expected_previous = "" if index == 0 else artifact["proposal_versions"][index - 1]["proposal_version_hash"]
        if version["previous_version_hash"] != expected_previous:
            raise FailClosedRuntimeError("ACLI proposal approval bridge proposal version lineage mismatch")
        _verify_hash_field(
            version,
            "proposal_version_hash",
            "ACLI proposal approval bridge proposal version hash mismatch",
        )
    return {
        "proposal_id": artifact["proposal_id"],
        "originating_session_id": artifact["originating_session_id"],
        "originating_turn_id": artifact["originating_turn_id"],
        "canonical_semantic_artifact_reference": artifact["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": artifact["canonical_semantic_artifact_hash"],
        "proposal_version": artifact["proposal_version"],
        "proposal_status": artifact["proposal_status"],
        "approval_status": artifact["approval_status"],
        "proposal_version_count": len(artifact["proposal_versions"]),
        "approval_request_count": len(artifact["approval_requests"]),
        "approval_decision_count": len(artifact["approval_decisions"]),
        "event_count": len(events),
        "event_hash_chain": [event["event_hash"] for event in events],
        "rollback_reference": artifact["rollback_reference"],
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "product1_workflow_started": False,
        "replay_visible": True,
        "artifact_hash": artifact["artifact_hash"],
        "replay_hash": replay_hash(wrappers),
    }


def _proposal_artifact_from_existing(
    proposal: dict[str, Any],
    *,
    proposal_version: int,
    proposal_status: str,
    approval_status: str,
    rollback_reference: str,
    proposal_versions: list[dict[str, Any]],
    approval_requests: list[dict[str, Any]],
    approval_decisions: list[dict[str, Any]],
    bridge_events: list[dict[str, Any]],
    updated_at: str,
    clarification_return_reference: str | None,
    rejection_reference: str | None,
    failure_reason: str | None,
) -> dict[str, Any]:
    return _proposal_artifact(
        proposal_id=proposal["proposal_id"],
        originating_session_id=proposal["originating_session_id"],
        originating_conversation_id=proposal["originating_conversation_id"],
        originating_turn_id=proposal["originating_turn_id"],
        originating_turn_hash=proposal["originating_turn_hash"],
        conversation_hash=proposal["conversation_hash"],
        canonical_semantic_artifact_reference=proposal["canonical_semantic_artifact_reference"],
        canonical_semantic_artifact_hash=proposal["canonical_semantic_artifact_hash"],
        proposal_scope=proposal["proposal_scope"],
        proposal_version=proposal_version,
        proposal_status=proposal_status,
        approval_status=approval_status,
        rollback_reference=rollback_reference,
        proposal_versions=proposal_versions,
        approval_requests=approval_requests,
        approval_decisions=approval_decisions,
        bridge_events=bridge_events,
        replay_lineage=proposal["replay_lineage"],
        created_at=proposal["created_at"],
        updated_at=updated_at,
        clarification_return_reference=clarification_return_reference,
        rejection_reference=rejection_reference,
        failure_reason=failure_reason,
    )


def _proposal_artifact(
    *,
    proposal_id: str,
    originating_session_id: str,
    originating_conversation_id: str,
    originating_turn_id: str,
    originating_turn_hash: str,
    conversation_hash: str,
    canonical_semantic_artifact_reference: str,
    canonical_semantic_artifact_hash: str,
    proposal_scope: str,
    proposal_version: int,
    proposal_status: str,
    approval_status: str,
    rollback_reference: str,
    proposal_versions: list[dict[str, Any]],
    approval_requests: list[dict[str, Any]],
    approval_decisions: list[dict[str, Any]],
    bridge_events: list[dict[str, Any]],
    replay_lineage: list[dict[str, Any]],
    created_at: str,
    updated_at: str,
    clarification_return_reference: str | None,
    rejection_reference: str | None,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": ACLI_PROPOSAL_APPROVAL_BRIDGE_ARTIFACT_V1,
        "runtime_version": ACLI_PROPOSAL_APPROVAL_BRIDGE_RUNTIME_VERSION,
        "migration_batch_id": "G3_02_IMPLEMENTATION_PHASE_4_PROPOSAL_APPROVAL_BRIDGE_V1",
        "proposal_id": _require_string(proposal_id, "proposal_id"),
        "originating_session_id": _require_string(originating_session_id, "originating_session_id"),
        "originating_conversation_id": _require_string(
            originating_conversation_id,
            "originating_conversation_id",
        ),
        "originating_turn_id": _require_string(originating_turn_id, "originating_turn_id"),
        "originating_turn_hash": _require_hash(originating_turn_hash, "originating_turn_hash"),
        "conversation_hash": _require_hash(conversation_hash, "conversation_hash"),
        "canonical_semantic_artifact_reference": _require_string(
            canonical_semantic_artifact_reference,
            "canonical_semantic_artifact_reference",
        ),
        "canonical_semantic_artifact_hash": _require_hash(
            canonical_semantic_artifact_hash,
            "canonical_semantic_artifact_hash",
        ),
        "proposal_scope": _require_string(proposal_scope, "proposal_scope"),
        "proposal_version": proposal_version,
        "proposal_status": _require_string(proposal_status, "proposal_status"),
        "approval_status": _require_string(approval_status, "approval_status"),
        "rollback_reference": _require_string(rollback_reference, "rollback_reference"),
        "proposal_versions": deepcopy(proposal_versions),
        "approval_requests": deepcopy(approval_requests),
        "approval_decisions": deepcopy(approval_decisions),
        "bridge_events": deepcopy(bridge_events),
        "replay_lineage": _normalize_replay_lineage(replay_lineage),
        "created_at": _require_string(created_at, "created_at"),
        "updated_at": _require_string(updated_at, "updated_at"),
        "clarification_return_reference": clarification_return_reference,
        "rejection_reference": rejection_reference,
        "proposal_object_created": True,
        "proposal_lifecycle_visible": True,
        "proposal_versioning_visible": True,
        "approval_request_generated": bool(approval_requests),
        "approval_state_tracking_visible": True,
        "rejection_handling_visible": rejection_reference is not None,
        "clarification_return_path_visible": clarification_return_reference is not None,
        "replay_lineage_visible": True,
        "non_authoritative_until_approval": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "product1_workflow_started": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _proposal_version(
    *,
    proposal_version: int,
    proposal_summary: str,
    rollback_reference: str,
    recorded_at: str,
    previous_version_hash: str,
) -> dict[str, Any]:
    version = {
        "proposal_version_index": proposal_version - 1,
        "proposal_version": proposal_version,
        "proposal_summary": _require_string(proposal_summary, "proposal_summary"),
        "proposal_summary_hash": replay_hash({"proposal_summary": proposal_summary}),
        "rollback_reference": _require_string(rollback_reference, "rollback_reference"),
        "recorded_at": _require_string(recorded_at, "recorded_at"),
        "previous_version_hash": previous_version_hash,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "execution_requested": False,
        "repository_mutated": False,
    }
    version["proposal_version_hash"] = replay_hash(version)
    return version


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


def _bridge_replay_lineage(conversation: dict[str, Any], turn: dict[str, Any]) -> list[dict[str, Any]]:
    lineage = deepcopy(turn["replay_lineage"])
    lineage.append(
        {
            "replay_reference": f"conversation:{conversation['conversation_id']}",
            "replay_hash": conversation["artifact_hash"],
        }
    )
    lineage.append(
        {
            "replay_reference": f"turn:{turn['turn_id']}",
            "replay_hash": turn["turn_hash"],
        }
    )
    return _normalize_replay_lineage(lineage)


def _validated_conversation_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("ACLI proposal approval bridge failed closed: conversation artifact must be object")
    if artifact.get("artifact_type") != ACLI_CONVERSATIONAL_DEVELOPMENT_SESSION_ARTIFACT_V1:
        raise FailClosedRuntimeError("ACLI proposal approval bridge failed closed: invalid conversation artifact type")
    _verify_hash_field(artifact, "artifact_hash", "ACLI proposal approval bridge conversation hash mismatch")
    for flag in NON_AUTHORITY_FLAGS:
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"ACLI proposal approval bridge failed closed: {flag} must be false")
    if not isinstance(artifact.get("turns"), list):
        raise FailClosedRuntimeError("ACLI proposal approval bridge failed closed: conversation turns are required")
    return deepcopy(artifact)


def _validated_bridge_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("ACLI proposal approval bridge failed closed: artifact must be object")
    if artifact.get("artifact_type") != ACLI_PROPOSAL_APPROVAL_BRIDGE_ARTIFACT_V1:
        raise FailClosedRuntimeError("ACLI proposal approval bridge failed closed: invalid artifact type")
    _verify_hash_field(artifact, "artifact_hash", "ACLI proposal approval bridge artifact hash mismatch")
    for flag in NON_AUTHORITY_FLAGS:
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"ACLI proposal approval bridge failed closed: {flag} must be false")
    _require_hash(artifact.get("canonical_semantic_artifact_hash"), "canonical_semantic_artifact_hash")
    _normalize_replay_lineage(artifact.get("replay_lineage"))
    return deepcopy(artifact)


def _find_turn(conversation: dict[str, Any], turn_id: str) -> dict[str, Any]:
    target = _require_string(turn_id, "originating_turn_id")
    for turn in conversation["turns"]:
        if turn.get("turn_id") == target:
            _verify_hash_field(turn, "turn_hash", "ACLI proposal approval bridge turn hash mismatch")
            for flag in NON_AUTHORITY_FLAGS:
                if turn.get(flag) is not False:
                    raise FailClosedRuntimeError(f"ACLI proposal approval bridge failed closed: {flag} must be false")
            return deepcopy(turn)
    raise FailClosedRuntimeError("ACLI proposal approval bridge failed closed: originating turn not found")


def _status_for_decision(decision: str) -> tuple[str, str]:
    if decision == "APPROVED":
        return APPROVAL_RECORDED, APPROVAL_RECORDED
    if decision == "REJECTED":
        return PROPOSAL_REJECTED, APPROVAL_REJECTED
    return CLARIFICATION_RETURNED, APPROVAL_CLARIFICATION_REQUESTED


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    _ensure_step_available(replay_path, index, step)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", _wrapper(index, step, artifact))


def _ensure_step_available(replay_path: Path, index: int, step: str) -> None:
    if (replay_path / f"{index:03d}_{step}.json").exists():
        raise FailClosedRuntimeError("ACLI proposal approval bridge failed closed: replay already exists")


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
    _verify_hash_field(wrapper, "replay_hash", "ACLI proposal approval bridge replay hash mismatch")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("ACLI proposal approval bridge replay artifact must be object")
    _verify_hash_field(artifact, "artifact_hash", "ACLI proposal approval bridge artifact hash mismatch")
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
        "runtime_version": ACLI_PROPOSAL_APPROVAL_BRIDGE_RUNTIME_VERSION,
        "proposal_artifact": deepcopy(artifact),
        "proposal_id": artifact["proposal_id"],
        "originating_session_id": artifact["originating_session_id"],
        "originating_turn_id": artifact["originating_turn_id"],
        "canonical_semantic_artifact_reference": artifact["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": artifact["canonical_semantic_artifact_hash"],
        "proposal_version": artifact["proposal_version"],
        "proposal_status": artifact["proposal_status"],
        "approval_status": artifact["approval_status"],
        "rollback_reference": artifact["rollback_reference"],
        "replay_reference": str(replay_path),
        "approval_request_generated": artifact["approval_request_generated"],
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "provider_invoked": False,
        "worker_invoked": False,
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
        raise FailClosedRuntimeError("ACLI proposal approval bridge failed closed: replay lineage is required")
    lineage = []
    for item in value:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("ACLI proposal approval bridge failed closed: replay lineage item must be object")
        lineage.append(
            {
                "replay_reference": _require_string(item.get("replay_reference"), "replay_reference"),
                "replay_hash": _require_hash(item.get("replay_hash"), "replay_hash"),
            }
        )
    return lineage


def _optional_string(value: str | None) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"ACLI proposal approval bridge failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"ACLI proposal approval bridge failed closed: {field_name} must be replay hash")
    return text
