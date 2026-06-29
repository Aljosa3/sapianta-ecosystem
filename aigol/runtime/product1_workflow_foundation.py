"""Product 1 workflow foundation for certified ACLI conversational sessions."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.acli_conversational_development_session import (
    ACLI_CONVERSATIONAL_DEVELOPMENT_SESSION_ARTIFACT_V1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


PRODUCT1_WORKFLOW_FOUNDATION_RUNTIME_VERSION = "G3_03_IMPLEMENTATION_PHASE_1_PRODUCT_WORKFLOW_FOUNDATION_RUNTIME_V1"
PRODUCT1_WORKFLOW_FOUNDATION_ARTIFACT_V1 = "PRODUCT1_WORKFLOW_FOUNDATION_ARTIFACT_V1"

PRODUCT1_IDENTITY = "AI Decision Validator"

WORKFLOW_CREATED = "WORKFLOW_CREATED"
WORKFLOW_ACTIVE = "WORKFLOW_ACTIVE"
GOVERNANCE_REVIEW_REQUIRED = "GOVERNANCE_REVIEW_REQUIRED"
OPERATOR_REVIEW_REQUIRED = "OPERATOR_REVIEW_REQUIRED"
WORKFLOW_READY_FOR_DECISION_PACKET = "WORKFLOW_READY_FOR_DECISION_PACKET"
FAILED_CLOSED = "FAILED_CLOSED"

GOVERNANCE_PENDING = "GOVERNANCE_PENDING"
GOVERNANCE_PASSED = "GOVERNANCE_PASSED"
GOVERNANCE_BLOCKED = "GOVERNANCE_BLOCKED"

OPERATOR_REVIEW_PENDING = "OPERATOR_REVIEW_PENDING"
OPERATOR_REVIEW_RECORDED = "OPERATOR_REVIEW_RECORDED"
OPERATOR_REVIEW_REJECTED = "OPERATOR_REVIEW_REJECTED"

EVENT_WORKFLOW_CREATED = "product1_workflow_created"
EVENT_GOVERNANCE_CHECKPOINT_RECORDED = "product1_governance_checkpoint_recorded"
EVENT_OPERATOR_REVIEW_CHECKPOINT_RECORDED = "product1_operator_review_checkpoint_recorded"
EVENT_WORKFLOW_STATE_TRANSITIONED = "product1_workflow_state_transitioned"

WORKFLOW_STATUSES = {
    WORKFLOW_CREATED,
    WORKFLOW_ACTIVE,
    GOVERNANCE_REVIEW_REQUIRED,
    OPERATOR_REVIEW_REQUIRED,
    WORKFLOW_READY_FOR_DECISION_PACKET,
    FAILED_CLOSED,
}

GOVERNANCE_STATUSES = {
    GOVERNANCE_PENDING,
    GOVERNANCE_PASSED,
    GOVERNANCE_BLOCKED,
    FAILED_CLOSED,
}

OPERATOR_REVIEW_STATUSES = {
    OPERATOR_REVIEW_PENDING,
    OPERATOR_REVIEW_RECORDED,
    OPERATOR_REVIEW_REJECTED,
    FAILED_CLOSED,
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


def create_product1_workflow(
    *,
    workflow_id: str,
    conversation_artifact: dict[str, Any],
    originating_turn_id: str,
    rollback_reference: str,
    created_at: str,
    replay_dir: str | Path,
    workflow_status: str = WORKFLOW_CREATED,
) -> dict[str, Any]:
    """Create deterministic Product 1 workflow identity from an ACLI turn."""

    conversation = _validated_conversation_artifact(conversation_artifact)
    turn = _find_turn(conversation, originating_turn_id)
    if workflow_status not in WORKFLOW_STATUSES:
        raise FailClosedRuntimeError("Product 1 workflow foundation failed closed: invalid workflow status")
    event = _event(
        event_index=0,
        event_type=EVENT_WORKFLOW_CREATED,
        occurred_at=created_at,
        previous_event_hash="",
        event_payload={
            "workflow_id": _require_string(workflow_id, "workflow_id"),
            "acli_session_id": conversation["session_id"],
            "originating_turn_id": turn["turn_id"],
            "canonical_semantic_artifact_hash": turn["canonical_semantic_artifact_hash"],
        },
    )
    artifact = _workflow_artifact(
        workflow_id=workflow_id,
        conversation=conversation,
        turn=turn,
        workflow_status=workflow_status,
        governance_checkpoint_status=GOVERNANCE_PENDING,
        operator_review_status=OPERATOR_REVIEW_PENDING,
        governance_checkpoints=[],
        operator_review_checkpoints=[],
        workflow_events=[event],
        replay_lineage=_workflow_replay_lineage(conversation, turn),
        rollback_reference=rollback_reference,
        created_at=created_at,
        updated_at=created_at,
        failure_reason=None,
    )
    _persist_step(Path(replay_dir), 0, EVENT_WORKFLOW_CREATED, artifact)
    return _capture(artifact, Path(replay_dir))


def record_product1_governance_checkpoint(
    *,
    workflow_artifact: dict[str, Any],
    checkpoint_id: str,
    checkpoint_status: str,
    checkpoint_scope: str,
    checkpoint_evidence_hash: str,
    recorded_at: str,
    replay_dir: str | Path,
    failure_reason: str | None = None,
) -> dict[str, Any]:
    """Record a Product 1 governance checkpoint without granting authority."""

    workflow = _validated_workflow_artifact(workflow_artifact)
    if checkpoint_status not in GOVERNANCE_STATUSES:
        raise FailClosedRuntimeError("Product 1 workflow foundation failed closed: invalid governance status")
    checkpoint = {
        "checkpoint_id": _require_string(checkpoint_id, "checkpoint_id"),
        "checkpoint_status": checkpoint_status,
        "checkpoint_scope": _require_string(checkpoint_scope, "checkpoint_scope"),
        "checkpoint_evidence_hash": _require_hash(checkpoint_evidence_hash, "checkpoint_evidence_hash"),
        "recorded_at": _require_string(recorded_at, "recorded_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "repository_mutated": False,
    }
    checkpoint["checkpoint_hash"] = replay_hash(checkpoint)
    status = GOVERNANCE_REVIEW_REQUIRED if checkpoint_status == GOVERNANCE_PENDING else WORKFLOW_ACTIVE
    if checkpoint_status in {GOVERNANCE_BLOCKED, FAILED_CLOSED}:
        status = FAILED_CLOSED
    event = _event(
        event_index=len(workflow["workflow_events"]),
        event_type=EVENT_GOVERNANCE_CHECKPOINT_RECORDED,
        occurred_at=recorded_at,
        previous_event_hash=workflow["workflow_events"][-1]["event_hash"],
        event_payload={
            "workflow_id": workflow["workflow_id"],
            "checkpoint_id": checkpoint["checkpoint_id"],
            "checkpoint_status": checkpoint_status,
            "checkpoint_hash": checkpoint["checkpoint_hash"],
        },
    )
    artifact = _workflow_artifact_from_existing(
        workflow,
        workflow_status=status,
        governance_checkpoint_status=checkpoint_status,
        operator_review_status=workflow["operator_review_status"],
        governance_checkpoints=workflow["governance_checkpoints"] + [checkpoint],
        operator_review_checkpoints=workflow["operator_review_checkpoints"],
        workflow_events=workflow["workflow_events"] + [event],
        updated_at=recorded_at,
        failure_reason=failure_reason if status == FAILED_CLOSED else workflow["failure_reason"],
    )
    _persist_step(Path(replay_dir), event["event_index"], EVENT_GOVERNANCE_CHECKPOINT_RECORDED, artifact)
    return _capture(artifact, Path(replay_dir))


def record_product1_operator_review_checkpoint(
    *,
    workflow_artifact: dict[str, Any],
    review_id: str,
    review_status: str,
    review_evidence_hash: str,
    reviewed_at: str,
    required_next_action: str,
    replay_dir: str | Path,
    failure_reason: str | None = None,
) -> dict[str, Any]:
    """Record operator review checkpoint evidence without approval or authorization."""

    workflow = _validated_workflow_artifact(workflow_artifact)
    if review_status not in OPERATOR_REVIEW_STATUSES:
        raise FailClosedRuntimeError("Product 1 workflow foundation failed closed: invalid operator review status")
    review = {
        "review_id": _require_string(review_id, "review_id"),
        "review_status": review_status,
        "review_evidence_hash": _require_hash(review_evidence_hash, "review_evidence_hash"),
        "required_next_action": _require_string(required_next_action, "required_next_action"),
        "reviewed_at": _require_string(reviewed_at, "reviewed_at"),
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
    }
    review["review_hash"] = replay_hash(review)
    status = OPERATOR_REVIEW_REQUIRED if review_status == OPERATOR_REVIEW_PENDING else WORKFLOW_ACTIVE
    if review_status in {OPERATOR_REVIEW_REJECTED, FAILED_CLOSED}:
        status = FAILED_CLOSED
    event = _event(
        event_index=len(workflow["workflow_events"]),
        event_type=EVENT_OPERATOR_REVIEW_CHECKPOINT_RECORDED,
        occurred_at=reviewed_at,
        previous_event_hash=workflow["workflow_events"][-1]["event_hash"],
        event_payload={
            "workflow_id": workflow["workflow_id"],
            "review_id": review["review_id"],
            "review_status": review_status,
            "review_hash": review["review_hash"],
        },
    )
    artifact = _workflow_artifact_from_existing(
        workflow,
        workflow_status=status,
        governance_checkpoint_status=workflow["governance_checkpoint_status"],
        operator_review_status=review_status,
        governance_checkpoints=workflow["governance_checkpoints"],
        operator_review_checkpoints=workflow["operator_review_checkpoints"] + [review],
        workflow_events=workflow["workflow_events"] + [event],
        updated_at=reviewed_at,
        failure_reason=failure_reason if status == FAILED_CLOSED else workflow["failure_reason"],
    )
    _persist_step(Path(replay_dir), event["event_index"], EVENT_OPERATOR_REVIEW_CHECKPOINT_RECORDED, artifact)
    return _capture(artifact, Path(replay_dir))


def transition_product1_workflow_state(
    *,
    workflow_artifact: dict[str, Any],
    workflow_status: str,
    transition_reason_hash: str,
    transitioned_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Record deterministic workflow state transition evidence."""

    workflow = _validated_workflow_artifact(workflow_artifact)
    if workflow_status not in WORKFLOW_STATUSES:
        raise FailClosedRuntimeError("Product 1 workflow foundation failed closed: invalid transition status")
    _validate_transition(workflow, workflow_status)
    event = _event(
        event_index=len(workflow["workflow_events"]),
        event_type=EVENT_WORKFLOW_STATE_TRANSITIONED,
        occurred_at=transitioned_at,
        previous_event_hash=workflow["workflow_events"][-1]["event_hash"],
        event_payload={
            "workflow_id": workflow["workflow_id"],
            "previous_workflow_status": workflow["workflow_status"],
            "workflow_status": workflow_status,
            "transition_reason_hash": _require_hash(transition_reason_hash, "transition_reason_hash"),
        },
    )
    artifact = _workflow_artifact_from_existing(
        workflow,
        workflow_status=workflow_status,
        governance_checkpoint_status=workflow["governance_checkpoint_status"],
        operator_review_status=workflow["operator_review_status"],
        governance_checkpoints=workflow["governance_checkpoints"],
        operator_review_checkpoints=workflow["operator_review_checkpoints"],
        workflow_events=workflow["workflow_events"] + [event],
        updated_at=transitioned_at,
        failure_reason=workflow["failure_reason"],
    )
    _persist_step(Path(replay_dir), event["event_index"], EVENT_WORKFLOW_STATE_TRANSITIONED, artifact)
    return _capture(artifact, Path(replay_dir))


def reconstruct_product1_workflow_foundation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate Product 1 workflow foundation replay."""

    replay_path = Path(replay_dir)
    wrappers = [_load_verified_wrapper(path) for path in sorted(replay_path.glob("*.json"))]
    if not wrappers:
        raise FailClosedRuntimeError("Product 1 workflow foundation failed closed: replay is empty")
    for index, wrapper in enumerate(wrappers):
        if wrapper.get("replay_index") != index:
            raise FailClosedRuntimeError("Product 1 workflow foundation replay ordering mismatch")
    artifact = _validated_workflow_artifact(wrappers[-1]["artifact"])
    events = artifact["workflow_events"]
    if len(events) != len(wrappers):
        raise FailClosedRuntimeError("Product 1 workflow foundation event count mismatch")
    for index, event in enumerate(events):
        if event["event_index"] != index:
            raise FailClosedRuntimeError("Product 1 workflow foundation event order mismatch")
        expected_previous = "" if index == 0 else events[index - 1]["event_hash"]
        if event["previous_event_hash"] != expected_previous:
            raise FailClosedRuntimeError("Product 1 workflow foundation event lineage mismatch")
        _verify_hash_field(event, "event_hash", "Product 1 workflow foundation event hash mismatch")
    return {
        "workflow_id": artifact["workflow_id"],
        "product_identity": artifact["product_identity"],
        "acli_session_id": artifact["acli_session_id"],
        "originating_conversation_id": artifact["originating_conversation_id"],
        "originating_turn_id": artifact["originating_turn_id"],
        "canonical_semantic_artifact_reference": artifact["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": artifact["canonical_semantic_artifact_hash"],
        "workflow_status": artifact["workflow_status"],
        "governance_checkpoint_status": artifact["governance_checkpoint_status"],
        "operator_review_status": artifact["operator_review_status"],
        "governance_checkpoint_count": len(artifact["governance_checkpoints"]),
        "operator_review_checkpoint_count": len(artifact["operator_review_checkpoints"]),
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
        "external_integration_invoked": False,
        "replay_visible": True,
        "artifact_hash": artifact["artifact_hash"],
        "replay_hash": replay_hash(wrappers),
    }


def _workflow_artifact_from_existing(
    workflow: dict[str, Any],
    *,
    workflow_status: str,
    governance_checkpoint_status: str,
    operator_review_status: str,
    governance_checkpoints: list[dict[str, Any]],
    operator_review_checkpoints: list[dict[str, Any]],
    workflow_events: list[dict[str, Any]],
    updated_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    return _workflow_artifact(
        workflow_id=workflow["workflow_id"],
        conversation=workflow["source_conversation"],
        turn=workflow["source_turn"],
        workflow_status=workflow_status,
        governance_checkpoint_status=governance_checkpoint_status,
        operator_review_status=operator_review_status,
        governance_checkpoints=governance_checkpoints,
        operator_review_checkpoints=operator_review_checkpoints,
        workflow_events=workflow_events,
        replay_lineage=workflow["replay_lineage"],
        rollback_reference=workflow["rollback_reference"],
        created_at=workflow["created_at"],
        updated_at=updated_at,
        failure_reason=failure_reason,
    )


def _workflow_artifact(
    *,
    workflow_id: str,
    conversation: dict[str, Any],
    turn: dict[str, Any],
    workflow_status: str,
    governance_checkpoint_status: str,
    operator_review_status: str,
    governance_checkpoints: list[dict[str, Any]],
    operator_review_checkpoints: list[dict[str, Any]],
    workflow_events: list[dict[str, Any]],
    replay_lineage: list[dict[str, Any]],
    rollback_reference: str,
    created_at: str,
    updated_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": PRODUCT1_WORKFLOW_FOUNDATION_ARTIFACT_V1,
        "runtime_version": PRODUCT1_WORKFLOW_FOUNDATION_RUNTIME_VERSION,
        "migration_batch_id": "G3_03_IMPLEMENTATION_PHASE_1_PRODUCT_WORKFLOW_FOUNDATION_V1",
        "product_identity": PRODUCT1_IDENTITY,
        "workflow_id": _require_string(workflow_id, "workflow_id"),
        "acli_session_id": conversation["session_id"],
        "originating_conversation_id": conversation["conversation_id"],
        "originating_conversation_hash": conversation["artifact_hash"],
        "originating_turn_id": turn["turn_id"],
        "originating_turn_hash": turn["turn_hash"],
        "canonical_semantic_artifact_reference": turn["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": turn["canonical_semantic_artifact_hash"],
        "workflow_status": _require_status(workflow_status, WORKFLOW_STATUSES, "workflow_status"),
        "governance_checkpoint_status": _require_status(
            governance_checkpoint_status,
            GOVERNANCE_STATUSES,
            "governance_checkpoint_status",
        ),
        "operator_review_status": _require_status(
            operator_review_status,
            OPERATOR_REVIEW_STATUSES,
            "operator_review_status",
        ),
        "governance_checkpoints": deepcopy(governance_checkpoints),
        "operator_review_checkpoints": deepcopy(operator_review_checkpoints),
        "workflow_events": deepcopy(workflow_events),
        "replay_lineage": _normalize_replay_lineage(replay_lineage),
        "rollback_reference": _require_string(rollback_reference, "rollback_reference"),
        "source_conversation": deepcopy(conversation),
        "source_turn": deepcopy(turn),
        "workflow_identity_created": True,
        "product_session_associated": True,
        "csa_associated": True,
        "replay_lineage_visible": True,
        "governance_checkpoints_visible": True,
        "operator_review_checkpoints_visible": True,
        "deterministic_state_transitions": True,
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
        "updated_at": _require_string(updated_at, "updated_at"),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _workflow_replay_lineage(conversation: dict[str, Any], turn: dict[str, Any]) -> list[dict[str, Any]]:
    lineage = deepcopy(turn["replay_lineage"])
    lineage.append({"replay_reference": f"conversation:{conversation['conversation_id']}", "replay_hash": conversation["artifact_hash"]})
    lineage.append({"replay_reference": f"turn:{turn['turn_id']}", "replay_hash": turn["turn_hash"]})
    return _normalize_replay_lineage(lineage)


def _validated_conversation_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("Product 1 workflow foundation failed closed: conversation artifact must be object")
    if artifact.get("artifact_type") != ACLI_CONVERSATIONAL_DEVELOPMENT_SESSION_ARTIFACT_V1:
        raise FailClosedRuntimeError("Product 1 workflow foundation failed closed: invalid conversation artifact")
    _verify_hash_field(artifact, "artifact_hash", "Product 1 workflow foundation conversation hash mismatch")
    for flag in NON_AUTHORITY_FLAGS:
        if flag in artifact and artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"Product 1 workflow foundation failed closed: {flag} must be false")
    if not isinstance(artifact.get("turns"), list) or not artifact["turns"]:
        raise FailClosedRuntimeError("Product 1 workflow foundation failed closed: originating turn is required")
    return deepcopy(artifact)


def _validated_workflow_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("Product 1 workflow foundation failed closed: artifact must be object")
    if artifact.get("artifact_type") != PRODUCT1_WORKFLOW_FOUNDATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("Product 1 workflow foundation failed closed: invalid artifact type")
    _verify_hash_field(artifact, "artifact_hash", "Product 1 workflow foundation artifact hash mismatch")
    for flag in NON_AUTHORITY_FLAGS:
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"Product 1 workflow foundation failed closed: {flag} must be false")
    _require_hash(artifact.get("canonical_semantic_artifact_hash"), "canonical_semantic_artifact_hash")
    _normalize_replay_lineage(artifact.get("replay_lineage"))
    return deepcopy(artifact)


def _find_turn(conversation: dict[str, Any], turn_id: str) -> dict[str, Any]:
    target = _require_string(turn_id, "originating_turn_id")
    for turn in conversation["turns"]:
        if turn.get("turn_id") == target:
            _verify_hash_field(turn, "turn_hash", "Product 1 workflow foundation turn hash mismatch")
            for flag in (
                "provider_invoked",
                "worker_invoked",
                "approval_created",
                "authorization_created",
                "execution_requested",
                "repository_mutated",
                "deployment_requested",
            ):
                if turn.get(flag) is not False:
                    raise FailClosedRuntimeError(f"Product 1 workflow foundation failed closed: {flag} must be false")
            return deepcopy(turn)
    raise FailClosedRuntimeError("Product 1 workflow foundation failed closed: originating turn not found")


def _validate_transition(workflow: dict[str, Any], next_status: str) -> None:
    if workflow["workflow_status"] == FAILED_CLOSED and next_status != FAILED_CLOSED:
        raise FailClosedRuntimeError("Product 1 workflow foundation failed closed: terminal workflow cannot transition")
    if next_status == WORKFLOW_READY_FOR_DECISION_PACKET:
        if workflow["governance_checkpoint_status"] != GOVERNANCE_PASSED:
            raise FailClosedRuntimeError("Product 1 workflow foundation failed closed: governance checkpoint must pass")
        if workflow["operator_review_status"] != OPERATOR_REVIEW_RECORDED:
            raise FailClosedRuntimeError("Product 1 workflow foundation failed closed: operator review must be recorded")


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
        "execution_requested": False,
        "repository_mutated": False,
    }
    event["event_hash"] = replay_hash(event)
    return event


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if (replay_path / f"{index:03d}_{step}.json").exists():
        raise FailClosedRuntimeError("Product 1 workflow foundation failed closed: replay already exists")
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
    _verify_hash_field(wrapper, "replay_hash", "Product 1 workflow foundation replay hash mismatch")
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("Product 1 workflow foundation replay artifact must be object")
    _verify_hash_field(artifact, "artifact_hash", "Product 1 workflow foundation artifact hash mismatch")
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
        "runtime_version": PRODUCT1_WORKFLOW_FOUNDATION_RUNTIME_VERSION,
        "workflow_artifact": deepcopy(artifact),
        "workflow_id": artifact["workflow_id"],
        "product_identity": artifact["product_identity"],
        "acli_session_id": artifact["acli_session_id"],
        "originating_turn_id": artifact["originating_turn_id"],
        "canonical_semantic_artifact_reference": artifact["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": artifact["canonical_semantic_artifact_hash"],
        "workflow_status": artifact["workflow_status"],
        "governance_checkpoint_status": artifact["governance_checkpoint_status"],
        "operator_review_status": artifact["operator_review_status"],
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
        raise FailClosedRuntimeError("Product 1 workflow foundation failed closed: replay lineage is required")
    lineage = []
    for item in value:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("Product 1 workflow foundation failed closed: replay lineage item must be object")
        lineage.append(
            {
                "replay_reference": _require_string(item.get("replay_reference"), "replay_reference"),
                "replay_hash": _require_hash(item.get("replay_hash"), "replay_hash"),
            }
        )
    return lineage


def _require_status(value: str, allowed: set[str], field_name: str) -> str:
    text = _require_string(value, field_name)
    if text not in allowed:
        raise FailClosedRuntimeError(f"Product 1 workflow foundation failed closed: invalid {field_name}")
    return text


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"Product 1 workflow foundation failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"Product 1 workflow foundation failed closed: {field_name} must be replay hash")
    return text
