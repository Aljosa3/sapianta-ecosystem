"""ACLI governed development session lifecycle for Generation 3."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


ACLI_DEVELOPMENT_SESSION_LIFECYCLE_RUNTIME_VERSION = (
    "G3_02_IMPLEMENTATION_PHASE_1_ACLI_SESSION_LIFECYCLE_RUNTIME_V1"
)
ACLI_DEVELOPMENT_SESSION_LIFECYCLE_ARTIFACT_V1 = "ACLI_DEVELOPMENT_SESSION_LIFECYCLE_ARTIFACT_V1"

SESSION_CREATED = "SESSION_CREATED"
SESSION_ACTIVE = "SESSION_ACTIVE"
CONFIRMATION_REQUIRED = "CONFIRMATION_REQUIRED"
CONFIRMATION_RECORDED = "CONFIRMATION_RECORDED"
RECOVERY_REQUIRED = "RECOVERY_REQUIRED"
SESSION_COMPLETED = "SESSION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"

NO_CONFIRMATION_REQUIRED = "NO_CONFIRMATION_REQUIRED"
NO_RECOVERY_REQUIRED = "NO_RECOVERY_REQUIRED"

EVENT_SESSION_CREATED = "acli_development_session_created"
EVENT_CONFIRMATION_CHECKPOINT_RECORDED = "acli_development_session_confirmation_checkpoint_recorded"
EVENT_RECOVERY_STATE_RECORDED = "acli_development_session_recovery_state_recorded"

CONFIRMATION_CLASSES = {
    "CLARIFICATION_RESPONSE",
    "ADVISORY_CONFIRMATION",
    "PROPOSAL_APPROVAL",
    "RELEASE_APPROVAL",
    "DEPLOYMENT_APPROVAL",
}

CONFIRMATION_STATUSES = {
    CONFIRMATION_REQUIRED,
    CONFIRMATION_RECORDED,
    FAILED_CLOSED,
}

RECOVERY_STATUSES = {
    RECOVERY_REQUIRED,
    FAILED_CLOSED,
    "RECOVERY_RESOLVED",
}

GOVERNANCE_CHECKPOINTS = (
    "semantic_authority_preserved",
    "governance_authority_preserved",
    "approval_boundary_preserved",
    "provider_boundary_preserved",
    "worker_boundary_preserved",
    "replay_boundary_preserved",
    "execution_boundary_preserved",
)

ALLOWED_LIFECYCLE_STATUSES = {
    SESSION_CREATED,
    SESSION_ACTIVE,
    CONFIRMATION_REQUIRED,
    CONFIRMATION_RECORDED,
    RECOVERY_REQUIRED,
    SESSION_COMPLETED,
    FAILED_CLOSED,
}


def create_acli_development_session(
    *,
    session_id: str,
    created_at: str,
    replay_dir: str | Path,
    canonical_semantic_artifact_reference: str,
    canonical_semantic_artifact_hash: str,
    replay_lineage: list[dict[str, Any]],
    governance_checkpoints: dict[str, Any],
    parent_session_id: str | None = None,
) -> dict[str, Any]:
    """Create a non-authoritative ACLI development session lifecycle artifact."""

    replay_path = Path(replay_dir)
    _ensure_next_replay_available(replay_path, 0, EVENT_SESSION_CREATED)
    lineage = _normalize_replay_lineage(replay_lineage)
    checkpoints = _validate_governance_checkpoints(governance_checkpoints)
    event = _event(
        event_index=0,
        event_type=EVENT_SESSION_CREATED,
        occurred_at=created_at,
        previous_event_hash="",
        event_payload={
            "session_id": _require_string(session_id, "session_id"),
            "parent_session_id": parent_session_id if parent_session_id else None,
            "canonical_semantic_artifact_reference": _require_string(
                canonical_semantic_artifact_reference,
                "canonical_semantic_artifact_reference",
            ),
            "canonical_semantic_artifact_hash": _require_hash(
                canonical_semantic_artifact_hash,
                "canonical_semantic_artifact_hash",
            ),
            "replay_lineage_count": len(lineage),
        },
    )
    artifact = _session_artifact(
        session_id=session_id,
        parent_session_id=parent_session_id,
        canonical_semantic_artifact_reference=canonical_semantic_artifact_reference,
        canonical_semantic_artifact_hash=canonical_semantic_artifact_hash,
        replay_lineage=lineage,
        governance_checkpoints=checkpoints,
        confirmation_state=NO_CONFIRMATION_REQUIRED,
        confirmation_checkpoints=[],
        lifecycle_status=SESSION_CREATED,
        recovery_status=NO_RECOVERY_REQUIRED,
        recovery_states=[],
        lifecycle_events=[event],
        created_at=created_at,
        updated_at=created_at,
        failure_reason=None,
    )
    _persist_step(replay_path, 0, EVENT_SESSION_CREATED, artifact)
    return _capture(artifact, replay_path)


def record_human_confirmation_checkpoint(
    *,
    session_artifact: dict[str, Any],
    checkpoint_id: str,
    confirmation_class: str,
    confirmation_status: str,
    active_context_reference: str,
    confirmation_text_hash: str,
    recorded_at: str,
    replay_dir: str | Path,
    proposal_reference: str | None = None,
    approval_scope: str | None = None,
) -> dict[str, Any]:
    """Record a human confirmation checkpoint without approving or authorizing execution."""

    session = _validated_session_artifact(session_artifact)
    if session["lifecycle_status"] in {SESSION_COMPLETED, FAILED_CLOSED}:
        raise FailClosedRuntimeError("ACLI session lifecycle failed closed: terminal session cannot be updated")
    if confirmation_class not in CONFIRMATION_CLASSES:
        raise FailClosedRuntimeError("ACLI session lifecycle failed closed: unsupported confirmation class")
    if confirmation_status not in CONFIRMATION_STATUSES:
        raise FailClosedRuntimeError("ACLI session lifecycle failed closed: unsupported confirmation status")
    checkpoint = {
        "checkpoint_id": _require_string(checkpoint_id, "checkpoint_id"),
        "confirmation_class": confirmation_class,
        "confirmation_status": confirmation_status,
        "active_context_reference": _require_string(active_context_reference, "active_context_reference"),
        "confirmation_text_hash": _require_hash(confirmation_text_hash, "confirmation_text_hash"),
        "proposal_reference": proposal_reference if isinstance(proposal_reference, str) and proposal_reference else None,
        "approval_scope": approval_scope if isinstance(approval_scope, str) and approval_scope else None,
        "recorded_at": _require_string(recorded_at, "recorded_at"),
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
    }
    checkpoint["checkpoint_hash"] = replay_hash(checkpoint)
    status = CONFIRMATION_REQUIRED if confirmation_status == CONFIRMATION_REQUIRED else CONFIRMATION_RECORDED
    if confirmation_status == FAILED_CLOSED:
        status = FAILED_CLOSED
    event = _event(
        event_index=len(session["lifecycle_events"]),
        event_type=EVENT_CONFIRMATION_CHECKPOINT_RECORDED,
        occurred_at=recorded_at,
        previous_event_hash=session["lifecycle_events"][-1]["event_hash"],
        event_payload={
            "checkpoint_id": checkpoint["checkpoint_id"],
            "confirmation_class": confirmation_class,
            "confirmation_status": confirmation_status,
            "checkpoint_hash": checkpoint["checkpoint_hash"],
        },
    )
    artifact = _session_artifact(
        session_id=session["session_id"],
        parent_session_id=session["parent_session_id"],
        canonical_semantic_artifact_reference=session["canonical_semantic_artifact_reference"],
        canonical_semantic_artifact_hash=session["canonical_semantic_artifact_hash"],
        replay_lineage=session["replay_lineage"],
        governance_checkpoints=session["governance_checkpoints"],
        confirmation_state=confirmation_status,
        confirmation_checkpoints=session["confirmation_checkpoints"] + [checkpoint],
        lifecycle_status=status,
        recovery_status=session["recovery_status"],
        recovery_states=session["recovery_states"],
        lifecycle_events=session["lifecycle_events"] + [event],
        created_at=session["created_at"],
        updated_at=recorded_at,
        failure_reason="confirmation checkpoint failed closed" if status == FAILED_CLOSED else session["failure_reason"],
    )
    _persist_step(Path(replay_dir), event["event_index"], EVENT_CONFIRMATION_CHECKPOINT_RECORDED, artifact)
    return _capture(artifact, Path(replay_dir))


def record_acli_session_recovery_state(
    *,
    session_artifact: dict[str, Any],
    recovery_id: str,
    recovery_status: str,
    recovery_reason: str,
    safe_next_action: str,
    recorded_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Record a replay-visible recovery state for an ACLI development session."""

    session = _validated_session_artifact(session_artifact)
    if session["lifecycle_status"] == SESSION_COMPLETED:
        raise FailClosedRuntimeError("ACLI session lifecycle failed closed: completed session cannot recover")
    if recovery_status not in RECOVERY_STATUSES:
        raise FailClosedRuntimeError("ACLI session lifecycle failed closed: unsupported recovery status")
    recovery = {
        "recovery_id": _require_string(recovery_id, "recovery_id"),
        "recovery_status": recovery_status,
        "recovery_reason": _require_string(recovery_reason, "recovery_reason"),
        "safe_next_action": _require_string(safe_next_action, "safe_next_action"),
        "recorded_at": _require_string(recorded_at, "recorded_at"),
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
    }
    recovery["recovery_hash"] = replay_hash(recovery)
    lifecycle_status = RECOVERY_REQUIRED if recovery_status != FAILED_CLOSED else FAILED_CLOSED
    event = _event(
        event_index=len(session["lifecycle_events"]),
        event_type=EVENT_RECOVERY_STATE_RECORDED,
        occurred_at=recorded_at,
        previous_event_hash=session["lifecycle_events"][-1]["event_hash"],
        event_payload={
            "recovery_id": recovery["recovery_id"],
            "recovery_status": recovery_status,
            "recovery_hash": recovery["recovery_hash"],
        },
    )
    artifact = _session_artifact(
        session_id=session["session_id"],
        parent_session_id=session["parent_session_id"],
        canonical_semantic_artifact_reference=session["canonical_semantic_artifact_reference"],
        canonical_semantic_artifact_hash=session["canonical_semantic_artifact_hash"],
        replay_lineage=session["replay_lineage"],
        governance_checkpoints=session["governance_checkpoints"],
        confirmation_state=session["confirmation_state"],
        confirmation_checkpoints=session["confirmation_checkpoints"],
        lifecycle_status=lifecycle_status,
        recovery_status=recovery_status,
        recovery_states=session["recovery_states"] + [recovery],
        lifecycle_events=session["lifecycle_events"] + [event],
        created_at=session["created_at"],
        updated_at=recorded_at,
        failure_reason=recovery_reason if recovery_status == FAILED_CLOSED else session["failure_reason"],
    )
    _persist_step(Path(replay_dir), event["event_index"], EVENT_RECOVERY_STATE_RECORDED, artifact)
    return _capture(artifact, Path(replay_dir))


def reconstruct_acli_development_session_lifecycle_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate ACLI development session lifecycle replay."""

    replay_path = Path(replay_dir)
    wrappers = [_load_verified_wrapper(path) for path in sorted(replay_path.glob("*.json"))]
    if not wrappers:
        raise FailClosedRuntimeError("ACLI session lifecycle failed closed: replay is empty")
    for index, wrapper in enumerate(wrappers):
        if wrapper.get("replay_index") != index:
            raise FailClosedRuntimeError("ACLI session lifecycle replay ordering mismatch")
    final_artifact = wrappers[-1]["artifact"]
    _validated_session_artifact(final_artifact)
    events = final_artifact["lifecycle_events"]
    if len(events) != len(wrappers):
        raise FailClosedRuntimeError("ACLI session lifecycle event count mismatch")
    for index, event in enumerate(events):
        if event["event_index"] != index:
            raise FailClosedRuntimeError("ACLI session lifecycle event order mismatch")
        expected_previous = "" if index == 0 else events[index - 1]["event_hash"]
        if event["previous_event_hash"] != expected_previous:
            raise FailClosedRuntimeError("ACLI session lifecycle event lineage mismatch")
        expected_event = deepcopy(event)
        actual_hash = expected_event.pop("event_hash")
        if actual_hash != replay_hash(expected_event):
            raise FailClosedRuntimeError("ACLI session lifecycle event hash mismatch")
    return {
        "session_id": final_artifact["session_id"],
        "parent_session_id": final_artifact["parent_session_id"],
        "lifecycle_status": final_artifact["lifecycle_status"],
        "confirmation_state": final_artifact["confirmation_state"],
        "recovery_status": final_artifact["recovery_status"],
        "canonical_semantic_artifact_reference": final_artifact["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": final_artifact["canonical_semantic_artifact_hash"],
        "replay_lineage_count": len(final_artifact["replay_lineage"]),
        "governance_checkpoints": deepcopy(final_artifact["governance_checkpoints"]),
        "event_count": len(events),
        "event_hash_chain": [event["event_hash"] for event in events],
        "artifact_hash": final_artifact["artifact_hash"],
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "governance_modified": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "replay_visible": True,
        "replay_hash": replay_hash(wrappers),
    }


def _session_artifact(
    *,
    session_id: str,
    parent_session_id: str | None,
    canonical_semantic_artifact_reference: str,
    canonical_semantic_artifact_hash: str,
    replay_lineage: list[dict[str, Any]],
    governance_checkpoints: dict[str, Any],
    confirmation_state: str,
    confirmation_checkpoints: list[dict[str, Any]],
    lifecycle_status: str,
    recovery_status: str,
    recovery_states: list[dict[str, Any]],
    lifecycle_events: list[dict[str, Any]],
    created_at: str,
    updated_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    if lifecycle_status not in ALLOWED_LIFECYCLE_STATUSES:
        raise FailClosedRuntimeError("ACLI session lifecycle failed closed: unsupported lifecycle status")
    artifact = {
        "artifact_type": ACLI_DEVELOPMENT_SESSION_LIFECYCLE_ARTIFACT_V1,
        "runtime_version": ACLI_DEVELOPMENT_SESSION_LIFECYCLE_RUNTIME_VERSION,
        "migration_batch_id": "G3_02_IMPLEMENTATION_PHASE_1_ACLI_SESSION_LIFECYCLE_V1",
        "session_id": _require_string(session_id, "session_id"),
        "parent_session_id": parent_session_id if isinstance(parent_session_id, str) and parent_session_id else None,
        "canonical_semantic_artifact_reference": _require_string(
            canonical_semantic_artifact_reference,
            "canonical_semantic_artifact_reference",
        ),
        "canonical_semantic_artifact_hash": _require_hash(
            canonical_semantic_artifact_hash,
            "canonical_semantic_artifact_hash",
        ),
        "replay_lineage": deepcopy(replay_lineage),
        "governance_checkpoints": deepcopy(governance_checkpoints),
        "confirmation_state": _require_string(confirmation_state, "confirmation_state"),
        "confirmation_checkpoints": deepcopy(confirmation_checkpoints),
        "lifecycle_status": lifecycle_status,
        "recovery_status": _require_string(recovery_status, "recovery_status"),
        "recovery_states": deepcopy(recovery_states),
        "lifecycle_events": deepcopy(lifecycle_events),
        "created_at": _require_string(created_at, "created_at"),
        "updated_at": _require_string(updated_at, "updated_at"),
        "session_identity_preserved": True,
        "replay_lineage_preserved": True,
        "governance_checkpoints_preserved": True,
        "confirmation_checkpoint_visible": bool(confirmation_checkpoints),
        "recovery_state_visible": bool(recovery_states),
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "authorization_created": False,
        "execution_requested": False,
        "governance_modified": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "product1_workflow_started": False,
        "release_candidate_created": False,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


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
        "governance_modified": False,
    }
    event["event_hash"] = replay_hash(event)
    return event


def _validated_session_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("ACLI session lifecycle failed closed: artifact must be object")
    if artifact.get("artifact_type") != ACLI_DEVELOPMENT_SESSION_LIFECYCLE_ARTIFACT_V1:
        raise FailClosedRuntimeError("ACLI session lifecycle failed closed: invalid artifact type")
    _verify_artifact_hash(artifact)
    if artifact.get("runtime_version") != ACLI_DEVELOPMENT_SESSION_LIFECYCLE_RUNTIME_VERSION:
        raise FailClosedRuntimeError("ACLI session lifecycle failed closed: invalid runtime version")
    if artifact.get("lifecycle_status") not in ALLOWED_LIFECYCLE_STATUSES:
        raise FailClosedRuntimeError("ACLI session lifecycle failed closed: invalid lifecycle status")
    _require_hash(artifact.get("canonical_semantic_artifact_hash"), "canonical_semantic_artifact_hash")
    _normalize_replay_lineage(artifact.get("replay_lineage"))
    _validate_governance_checkpoints(artifact.get("governance_checkpoints"))
    for flag in (
        "provider_invoked",
        "worker_invoked",
        "approval_created",
        "authorization_created",
        "execution_requested",
        "governance_modified",
        "repository_mutated",
        "deployment_requested",
    ):
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"ACLI session lifecycle failed closed: {flag} must be false")
    events = artifact.get("lifecycle_events")
    if not isinstance(events, list) or not events:
        raise FailClosedRuntimeError("ACLI session lifecycle failed closed: lifecycle events required")
    return deepcopy(artifact)


def _validate_governance_checkpoints(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("ACLI session lifecycle failed closed: governance checkpoints must be object")
    checkpoints = {}
    for checkpoint in GOVERNANCE_CHECKPOINTS:
        if value.get(checkpoint) is not True:
            raise FailClosedRuntimeError(
                f"ACLI session lifecycle failed closed: {checkpoint} must be true"
            )
        checkpoints[checkpoint] = True
    checkpoints["checkpoint_count"] = len(GOVERNANCE_CHECKPOINTS)
    return checkpoints


def _normalize_replay_lineage(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError("ACLI session lifecycle failed closed: replay lineage is required")
    lineage = []
    for item in value:
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("ACLI session lifecycle failed closed: replay lineage item must be object")
        lineage.append(
            {
                "replay_reference": _require_string(item.get("replay_reference"), "replay_reference"),
                "replay_hash": _require_hash(item.get("replay_hash"), "replay_hash"),
            }
        )
    return lineage


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    _ensure_next_replay_available(replay_path, index, step)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", _wrapper(index, step, artifact))


def _ensure_next_replay_available(replay_path: Path, index: int, step: str) -> None:
    if (replay_path / f"{index:03d}_{step}.json").exists():
        raise FailClosedRuntimeError("ACLI session lifecycle failed closed: replay already exists")


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
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("ACLI session lifecycle replay artifact must be object")
    _verify_artifact_hash(artifact)
    return wrapper


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("ACLI session lifecycle artifact hash is required")
    expected = deepcopy(artifact)
    expected.pop("artifact_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("ACLI session lifecycle artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("ACLI session lifecycle replay hash is required")
    expected = deepcopy(wrapper)
    expected.pop("replay_hash")
    if actual != replay_hash(expected):
        raise FailClosedRuntimeError("ACLI session lifecycle replay hash mismatch")


def _capture(artifact: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "runtime_version": ACLI_DEVELOPMENT_SESSION_LIFECYCLE_RUNTIME_VERSION,
        "session_artifact": deepcopy(artifact),
        "session_id": artifact["session_id"],
        "lifecycle_status": artifact["lifecycle_status"],
        "confirmation_state": artifact["confirmation_state"],
        "recovery_status": artifact["recovery_status"],
        "canonical_semantic_artifact_reference": artifact["canonical_semantic_artifact_reference"],
        "canonical_semantic_artifact_hash": artifact["canonical_semantic_artifact_hash"],
        "replay_reference": str(replay_path),
        "replay_lineage_preserved": artifact["replay_lineage_preserved"],
        "governance_checkpoints_preserved": artifact["governance_checkpoints_preserved"],
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "governance_modified": False,
        "repository_mutated": False,
        "deployment_requested": False,
        "replay_visible": True,
        "failure_reason": artifact["failure_reason"],
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"ACLI session lifecycle failed closed: {field_name} is required")
    return value.strip()


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"ACLI session lifecycle failed closed: {field_name} must be a replay hash")
    return text
