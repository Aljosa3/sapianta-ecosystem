"""Canonical Platform Core Conversation Boundary V1.

This module is an additive exposure layer over certified Platform Core
services.  It validates canonical conversation events, delegates semantic
work to the existing owners, projects their results, and records immutable
reference-only lineage.  It does not own Project Services, planning,
governance, approval, authorization, Replay, Worker, or Provider semantics.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Callable

from aigol.runtime.human_interface_runtime_entry_service import (
    CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND,
    run_human_interface_runtime_entry,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    latest_platform_core_workspace_state,
    prepare_unified_human_interface_project_context,
    record_unified_human_interface_workspace_state,
)
from aigol.runtime.transport.serialization import (
    canonical_serialize,
    load_json,
    replay_hash,
    write_json_immutable,
)


PLATFORM_CORE_CONVERSATION_BOUNDARY_VERSION = (
    "PLATFORM_CORE_CONVERSATION_BOUNDARY_V1"
)
CANONICAL_CONVERSATION_EVENT_ARTIFACT_V1 = (
    "CANONICAL_PLATFORM_CORE_CONVERSATION_EVENT_ARTIFACT_V1"
)
CONVERSATION_PROJECTION_ARTIFACT_V1 = (
    "PLATFORM_CORE_CONVERSATION_PROJECTION_ARTIFACT_V1"
)
TURN_EVIDENCE_MANIFEST_ARTIFACT_V1 = (
    "PLATFORM_CORE_CONVERSATION_TURN_EVIDENCE_MANIFEST_ARTIFACT_V1"
)
SESSION_CHECKPOINT_ARTIFACT_V1 = (
    "PLATFORM_CORE_CONVERSATION_SESSION_CHECKPOINT_ARTIFACT_V1"
)

BOUNDARY_COMPLETED = "PLATFORM_CORE_CONVERSATION_BOUNDARY_COMPLETED"
BOUNDARY_FAILED_CLOSED = "PLATFORM_CORE_CONVERSATION_BOUNDARY_FAILED_CLOSED"

HUMAN_REQUEST_SUBMITTED = "HUMAN_REQUEST_SUBMITTED"
CLARIFICATION_REPLY_SUBMITTED = "CLARIFICATION_REPLY_SUBMITTED"
HUMAN_APPROVAL_SUBMITTED = "HUMAN_APPROVAL_SUBMITTED"
HUMAN_REJECTION_SUBMITTED = "HUMAN_REJECTION_SUBMITTED"
HUMAN_CANCEL_SUBMITTED = "HUMAN_CANCEL_SUBMITTED"
HUMAN_EXIT_REQUESTED = "HUMAN_EXIT_REQUESTED"
INPUT_EOF_OBSERVED = "INPUT_EOF_OBSERVED"
INPUT_INTERRUPT_OBSERVED = "INPUT_INTERRUPT_OBSERVED"
RUNTIME_RESULT_RETURNED = "RUNTIME_RESULT_RETURNED"
REPLAY_STATE_RESTORED = "REPLAY_STATE_RESTORED"

CANONICAL_EVENTS = (
    HUMAN_REQUEST_SUBMITTED,
    CLARIFICATION_REPLY_SUBMITTED,
    HUMAN_APPROVAL_SUBMITTED,
    HUMAN_REJECTION_SUBMITTED,
    HUMAN_CANCEL_SUBMITTED,
    HUMAN_EXIT_REQUESTED,
    INPUT_EOF_OBSERVED,
    INPUT_INTERRUPT_OBSERVED,
    RUNTIME_RESULT_RETURNED,
    REPLAY_STATE_RESTORED,
)
HUMAN_EVENTS = frozenset(
    {
        HUMAN_REQUEST_SUBMITTED,
        CLARIFICATION_REPLY_SUBMITTED,
        HUMAN_APPROVAL_SUBMITTED,
        HUMAN_REJECTION_SUBMITTED,
        HUMAN_CANCEL_SUBMITTED,
        HUMAN_EXIT_REQUESTED,
        INPUT_EOF_OBSERVED,
        INPUT_INTERRUPT_OBSERVED,
    }
)
PLATFORM_EVENTS = frozenset({RUNTIME_RESULT_RETURNED, REPLAY_STATE_RESTORED})

CONVERSATION_IDLE = "CONVERSATION_IDLE"
CLARIFICATION_AWAITING_REPLY = "CLARIFICATION_AWAITING_REPLY"
APPROVAL_AWAITING_HUMAN = "APPROVAL_AWAITING_HUMAN"
RUNTIME_RUNNING = "RUNTIME_RUNNING"
RESULT_DELIVERED = "RESULT_DELIVERED"
CONVERSATION_COMPLETED = "CONVERSATION_COMPLETED"
CONVERSATION_CANCELED = "CONVERSATION_CANCELED"
CONVERSATION_FAILED_CLOSED = "CONVERSATION_FAILED_CLOSED"

CONVERSATION_STATES = frozenset(
    {
        CONVERSATION_IDLE,
        CLARIFICATION_AWAITING_REPLY,
        APPROVAL_AWAITING_HUMAN,
        RUNTIME_RUNNING,
        RESULT_DELIVERED,
        CONVERSATION_COMPLETED,
        CONVERSATION_CANCELED,
        CONVERSATION_FAILED_CLOSED,
    }
)

COLLECT_REQUEST = "COLLECT_REQUEST"
COLLECT_CLARIFICATION_REPLY = "COLLECT_CLARIFICATION_REPLY"
COLLECT_APPROVAL_DECISION = "COLLECT_APPROVAL_DECISION"
DISPLAY_NON_DEVELOPMENT_RESPONSE = "DISPLAY_NON_DEVELOPMENT_RESPONSE"
DISPLAY_RUNTIME_PROGRESS = "DISPLAY_RUNTIME_PROGRESS"
DISPLAY_RUNTIME_RESULT = "DISPLAY_RUNTIME_RESULT"
DISPLAY_COMPLETION = "DISPLAY_COMPLETION"
WAIT_FOR_HUMAN = "WAIT_FOR_HUMAN"
CLOSE_INTERFACE_SESSION = "CLOSE_INTERFACE_SESSION"

CANONICAL_ACTIONS = frozenset(
    {
        COLLECT_REQUEST,
        COLLECT_CLARIFICATION_REPLY,
        COLLECT_APPROVAL_DECISION,
        DISPLAY_NON_DEVELOPMENT_RESPONSE,
        DISPLAY_RUNTIME_PROGRESS,
        DISPLAY_RUNTIME_RESULT,
        DISPLAY_COMPLETION,
        WAIT_FOR_HUMAN,
        CLOSE_INTERFACE_SESSION,
    }
)

NO_CLARIFICATION = "NO_CLARIFICATION"
CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
CLARIFICATION_FAILED_CLOSED = "CLARIFICATION_FAILED_CLOSED"

NO_APPROVAL_REQUIRED = "NO_APPROVAL_REQUIRED"
PENDING_HUMAN_APPROVAL = "PENDING_HUMAN_APPROVAL"
APPROVAL_FAILED_CLOSED = "APPROVAL_FAILED_CLOSED"

NOT_COMPLETED = "NOT_COMPLETED"
AWAITING_HUMAN_INPUT = "AWAITING_HUMAN_INPUT"
RUNTIME_COMPLETED = "RUNTIME_COMPLETED"
COMPLETION_RESULT_DELIVERED = "RESULT_DELIVERED"
COMPLETION_CANCELED = "CONVERSATION_CANCELED"
COMPLETION_FAILED_CLOSED = "FAILED_CLOSED"

EVIDENCE_ROLE_ORDER = (
    "EVENT",
    "PRIOR_SESSION_CHECKPOINT",
    "PRIOR_PLATFORM_WORKSPACE_STATE",
    "PROJECT_SERVICES_CONTEXT",
    "OPERATIONAL_TURN_BINDING",
    "CLARIFICATION_CONTINUITY",
    "DEVELOPMENT_GOVERNANCE",
    "IMPLEMENTATION_TURN_BINDING",
    "PLATFORM_WORKSPACE_STATE",
    "RUNTIME_RESULT",
)

OWNERSHIP_FLAGS = {
    "platform_core_owns_conversation": True,
    "human_interface_owns_rendering": True,
    "human_interface_owns_transport": True,
    "human_interface_owns_input_collection": True,
    "human_interface_owns_workflow": False,
    "human_interface_owns_governance": False,
    "human_interface_owns_replay": False,
}

BOUNDARY_FLAGS = {
    "project_services_modified": False,
    "objective_inference_modified": False,
    "development_governance_modified": False,
    "planner_modified": False,
    "durable_work_modified": False,
    "approval_modified": False,
    "authorization_modified": False,
    "replay_protocol_modified": False,
    "worker_modified": False,
    "provider_modified": False,
    "aicli_modified": False,
    "provider_authority": False,
    "worker_invocation_authority": False,
    "authorization_authority": False,
    "replay_authority": False,
}

GovernedRuntimeRunner = Callable[..., dict[str, Any]]


def create_platform_core_conversation_event(
    *,
    event_type: str,
    session_id: str,
    payload: dict[str, Any],
    created_at: str,
    runtime_root: str | Path,
    source_interface: str,
    conversation_id: str | None = None,
) -> dict[str, Any]:
    """Create one canonical event bound to the latest immutable checkpoint."""

    session = _require_string(session_id, "session_id")
    conversation = (
        _require_string(conversation_id, "conversation_id")
        if conversation_id is not None
        else session
    )
    root = Path(runtime_root)
    prior = _latest_checkpoint(root=root, session_id=session)
    turn_id = int(prior["turn_id"]) + 1 if prior is not None else 1
    payload_copy = deepcopy(payload)
    payload_hash = replay_hash(payload_copy)
    event = {
        "artifact_type": CANONICAL_CONVERSATION_EVENT_ARTIFACT_V1,
        "event_version": PLATFORM_CORE_CONVERSATION_BOUNDARY_VERSION,
        "event_id": _event_identity(
            conversation_id=conversation,
            turn_id=turn_id,
            event_type=event_type,
            payload_hash=payload_hash,
        ),
        "event_type": event_type,
        "event_source": (
            "HUMAN_INTERFACE" if event_type in HUMAN_EVENTS else "PLATFORM_CORE"
        ),
        "source_interface": _require_string(
            source_interface, "source_interface"
        ),
        "session_id": session,
        "conversation_id": conversation,
        "turn_id": turn_id,
        "created_at": _require_string(created_at, "created_at"),
        "payload": payload_copy,
        "payload_hash": payload_hash,
        "prior_checkpoint_reference": (
            prior["checkpoint_reference"] if prior is not None else None
        ),
        "prior_checkpoint_hash": (
            prior["artifact_hash"] if prior is not None else None
        ),
        "event_handled_by": "PLATFORM_CORE",
        "human_interface_decides_semantic_effect": False,
    }
    event["artifact_hash"] = replay_hash(event)
    return validate_platform_core_conversation_event(event)


def validate_platform_core_conversation_event(
    event: dict[str, Any],
) -> dict[str, Any]:
    """Validate canonical event identity, payload, ownership, and hash."""

    candidate = _require_dict(event, "conversation event")
    if candidate.get("artifact_type") != CANONICAL_CONVERSATION_EVENT_ARTIFACT_V1:
        raise FailClosedRuntimeError("conversation event artifact type is invalid")
    if candidate.get("event_version") != PLATFORM_CORE_CONVERSATION_BOUNDARY_VERSION:
        raise FailClosedRuntimeError("conversation event version is invalid")
    event_type = candidate.get("event_type")
    if event_type not in CANONICAL_EVENTS:
        raise FailClosedRuntimeError("conversation event type is unsupported")
    expected_source = (
        "HUMAN_INTERFACE" if event_type in HUMAN_EVENTS else "PLATFORM_CORE"
    )
    if candidate.get("event_source") != expected_source:
        raise FailClosedRuntimeError("conversation event source is invalid")
    source_interface = _require_string(
        candidate.get("source_interface"), "source_interface"
    )
    if event_type in PLATFORM_EVENTS and source_interface != "PLATFORM_CORE":
        raise FailClosedRuntimeError(
            "Platform Core event source interface is invalid"
        )
    session_id = _require_string(candidate.get("session_id"), "session_id")
    conversation_id = _require_string(
        candidate.get("conversation_id"), "conversation_id"
    )
    if conversation_id != session_id:
        raise FailClosedRuntimeError(
            "conversation_id must equal session_id for boundary V1"
        )
    turn_id = candidate.get("turn_id")
    if not isinstance(turn_id, int) or isinstance(turn_id, bool) or turn_id < 1:
        raise FailClosedRuntimeError("conversation event turn_id is invalid")
    _require_string(candidate.get("created_at"), "created_at")
    payload = _require_dict(candidate.get("payload"), "conversation event payload")
    _validate_event_payload(event_type, payload)
    expected_payload_hash = replay_hash(payload)
    if candidate.get("payload_hash") != expected_payload_hash:
        raise FailClosedRuntimeError("conversation event payload hash mismatch")
    expected_identity = _event_identity(
        conversation_id=conversation_id,
        turn_id=turn_id,
        event_type=event_type,
        payload_hash=expected_payload_hash,
    )
    if candidate.get("event_id") != expected_identity:
        raise FailClosedRuntimeError("conversation event identity mismatch")
    _validate_optional_reference_pair(
        candidate.get("prior_checkpoint_reference"),
        candidate.get("prior_checkpoint_hash"),
        "prior checkpoint",
    )
    if candidate.get("event_handled_by") != "PLATFORM_CORE":
        raise FailClosedRuntimeError("conversation event handler ownership is invalid")
    if candidate.get("human_interface_decides_semantic_effect") is not False:
        raise FailClosedRuntimeError(
            "conversation event grants semantic authority to Human Interface"
        )
    _verify_artifact_hash(candidate, "conversation event")
    return deepcopy(candidate)


def run_platform_core_conversation_boundary(
    *,
    event: dict[str, Any],
    runtime_root: str | Path,
    workspace: str | Path,
    governed_runtime_runner: GovernedRuntimeRunner | None = None,
) -> dict[str, Any]:
    """Accept one event and return the next canonical conversation projection."""

    accepted_event = validate_platform_core_conversation_event(event)
    root = Path(runtime_root)
    workspace_path = str(Path(workspace))
    session_id = accepted_event["session_id"]
    session_root = root / session_id
    prior_capture = _latest_reconstruction(root=root, session_id=session_id)
    prior_projection = (
        prior_capture["conversation_projection"]
        if prior_capture is not None
        else None
    )
    prior_checkpoint = (
        prior_capture["session_checkpoint"]
        if prior_capture is not None
        else None
    )
    _validate_event_sequence(
        event=accepted_event,
        prior_projection=prior_projection,
        prior_checkpoint=prior_checkpoint,
    )

    turn_root = _turn_root(
        root=root,
        session_id=session_id,
        turn_id=accepted_event["turn_id"],
    )
    if turn_root.exists():
        raise FailClosedRuntimeError(
            "conversation boundary turn already exists"
        )
    event_path = turn_root / "000_event.json"
    write_json_immutable(event_path, accepted_event)

    prior_workspace = latest_platform_core_workspace_state(session_root)
    prior_workspace_reference = None
    if prior_workspace is not None:
        _verify_artifact_hash(prior_workspace, "Platform Core workspace state")
        prior_workspace_reference = _find_artifact_reference(
            session_root=session_root,
            artifact_hash=prior_workspace["artifact_hash"],
        )

    owner_result: dict[str, Any] | None = None
    workspace_state: dict[str, Any] | None = None
    failure_reason: str | None = None
    try:
        owner_result, workspace_state = _handle_event(
            event=accepted_event,
            root=root,
            workspace=workspace_path,
            prior_projection=prior_projection,
            prior_checkpoint=prior_checkpoint,
            prior_workspace=prior_workspace,
            governed_runtime_runner=governed_runtime_runner,
            event_reference=str(event_path),
        )
    except Exception as exc:  # Fail closed after the event acceptance boundary.
        failure_reason = _failure_reason(exc)

    evidence = _collect_evidence_references(
        event=accepted_event,
        event_path=event_path,
        session_root=session_root,
        prior_checkpoint=prior_checkpoint,
        prior_workspace=prior_workspace,
        prior_workspace_reference=prior_workspace_reference,
        owner_result=owner_result,
        workspace_state=workspace_state,
    )
    manifest_path = turn_root / "001_turn_evidence_manifest.json"
    manifest = _turn_evidence_manifest(
        event=accepted_event,
        event_reference=str(event_path),
        evidence_references=evidence,
        owner_result=owner_result,
        owner_failure_reason=failure_reason,
    )
    write_json_immutable(manifest_path, manifest)

    if failure_reason is None:
        projection = _projection_for_event_result(
            event=accepted_event,
            owner_result=owner_result,
            prior_projection=prior_projection,
            manifest_reference=str(manifest_path),
            manifest_hash=manifest["artifact_hash"],
        )
        boundary_status = BOUNDARY_COMPLETED
    else:
        projection = _failed_closed_projection(
            event=accepted_event,
            prior_projection=prior_projection,
            manifest_reference=str(manifest_path),
            manifest_hash=manifest["artifact_hash"],
            failure_reason=failure_reason,
        )
        boundary_status = BOUNDARY_FAILED_CLOSED

    projection_path = turn_root / "002_conversation_projection.json"
    write_json_immutable(projection_path, projection)
    checkpoint_path = turn_root / "003_session_checkpoint.json"
    checkpoint = _session_checkpoint(
        event=accepted_event,
        projection=projection,
        projection_reference=str(projection_path),
        manifest=manifest,
        manifest_reference=str(manifest_path),
        checkpoint_reference=str(checkpoint_path),
        prior_checkpoint=prior_checkpoint,
    )
    write_json_immutable(checkpoint_path, checkpoint)

    return {
        "boundary_version": PLATFORM_CORE_CONVERSATION_BOUNDARY_VERSION,
        "boundary_status": boundary_status,
        "conversation_projection": deepcopy(projection),
        "conversation_projection_reference": str(projection_path),
        "conversation_projection_hash": projection["artifact_hash"],
        "turn_evidence_manifest_reference": str(manifest_path),
        "turn_evidence_manifest_hash": manifest["artifact_hash"],
        "session_checkpoint": deepcopy(checkpoint),
        "session_checkpoint_reference": str(checkpoint_path),
        "session_checkpoint_hash": checkpoint["artifact_hash"],
        "replay_reference": str(turn_root),
        "platform_core_project_services_reused": (
            accepted_event["event_type"]
            in {HUMAN_REQUEST_SUBMITTED, CLARIFICATION_REPLY_SUBMITTED}
        ),
        "canonical_runtime_entry_reused": (
            accepted_event["event_type"] == HUMAN_APPROVAL_SUBMITTED
            and failure_reason is None
        ),
        "ownership": deepcopy(OWNERSHIP_FLAGS),
        "boundary_flags": deepcopy(BOUNDARY_FLAGS),
    }


def validate_platform_core_conversation_projection(
    projection: dict[str, Any],
) -> dict[str, Any]:
    """Validate the presentation-neutral canonical projection."""

    candidate = _require_dict(projection, "conversation projection")
    if candidate.get("artifact_type") != CONVERSATION_PROJECTION_ARTIFACT_V1:
        raise FailClosedRuntimeError(
            "conversation projection artifact type is invalid"
        )
    if candidate.get("projection_version") != PLATFORM_CORE_CONVERSATION_BOUNDARY_VERSION:
        raise FailClosedRuntimeError("conversation projection version is invalid")
    _validate_identity_fields(candidate, "conversation projection")
    state = candidate.get("conversation_state")
    if state not in CONVERSATION_STATES:
        raise FailClosedRuntimeError("conversation projection state is invalid")
    events = candidate.get("admissible_events")
    if (
        not isinstance(events, list)
        or len(events) != len(set(events))
        or any(event not in CANONICAL_EVENTS for event in events)
    ):
        raise FailClosedRuntimeError(
            "conversation projection admissible events are invalid"
        )
    expected_event = candidate.get("expected_event")
    if expected_event is not None and expected_event not in events:
        raise FailClosedRuntimeError(
            "conversation projection expected event is not admissible"
        )
    if candidate.get("next_action") not in CANONICAL_ACTIONS:
        raise FailClosedRuntimeError("conversation projection next action is invalid")
    clarification = _require_dict(
        candidate.get("clarification_state"), "clarification_state"
    )
    approval = _require_dict(candidate.get("approval_state"), "approval_state")
    completion = _require_dict(
        candidate.get("completion_state"), "completion_state"
    )
    if clarification.get("clarification_status") not in {
        NO_CLARIFICATION,
        CLARIFICATION_REQUIRED,
        CLARIFICATION_FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("clarification status is invalid")
    if approval.get("approval_status") not in {
        NO_APPROVAL_REQUIRED,
        PENDING_HUMAN_APPROVAL,
        APPROVAL_FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("approval status is invalid")
    if completion.get("completion_status") not in {
        NOT_COMPLETED,
        AWAITING_HUMAN_INPUT,
        RUNTIME_COMPLETED,
        COMPLETION_RESULT_DELIVERED,
        COMPLETION_CANCELED,
        COMPLETION_FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("completion status is invalid")
    if candidate.get("ownership") != OWNERSHIP_FLAGS:
        raise FailClosedRuntimeError("conversation projection ownership drift")
    if candidate.get("boundary_flags") != BOUNDARY_FLAGS:
        raise FailClosedRuntimeError("conversation projection boundary drift")
    _require_string(
        candidate.get("turn_evidence_manifest_reference"),
        "turn_evidence_manifest_reference",
    )
    _require_hash(
        candidate.get("turn_evidence_manifest_hash"),
        "turn_evidence_manifest_hash",
    )
    _validate_projection_state_contract(candidate)
    _verify_artifact_hash(candidate, "conversation projection")
    return deepcopy(candidate)


def validate_platform_core_conversation_turn_evidence_manifest(
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """Validate deterministic reference-only turn evidence."""

    candidate = _require_dict(manifest, "turn evidence manifest")
    if candidate.get("artifact_type") != TURN_EVIDENCE_MANIFEST_ARTIFACT_V1:
        raise FailClosedRuntimeError("turn evidence manifest type is invalid")
    if candidate.get("manifest_version") != PLATFORM_CORE_CONVERSATION_BOUNDARY_VERSION:
        raise FailClosedRuntimeError("turn evidence manifest version is invalid")
    _validate_identity_fields(candidate, "turn evidence manifest")
    _require_string(candidate.get("event_reference"), "event_reference")
    _require_hash(candidate.get("event_hash"), "event_hash")
    evidence = candidate.get("evidence_references")
    if not isinstance(evidence, list) or not evidence:
        raise FailClosedRuntimeError("turn evidence references are required")
    roles: list[str] = []
    identities: set[tuple[str, str]] = set()
    for item in evidence:
        reference = _require_dict(item, "turn evidence reference")
        if "artifact" in reference:
            raise FailClosedRuntimeError(
                "turn evidence manifest must not embed artifacts"
            )
        role = _require_string(reference.get("role"), "evidence role")
        if role not in EVIDENCE_ROLE_ORDER:
            raise FailClosedRuntimeError("turn evidence role is unsupported")
        path = _require_string(reference.get("reference"), "evidence reference")
        artifact_hash = _require_hash(
            reference.get("artifact_hash"), "evidence artifact_hash"
        )
        _require_string(reference.get("owner"), "evidence owner")
        identity = (path, artifact_hash)
        if identity in identities:
            raise FailClosedRuntimeError("duplicate turn evidence reference")
        identities.add(identity)
        roles.append(role)
    expected_roles = sorted(roles, key=EVIDENCE_ROLE_ORDER.index)
    if roles != expected_roles:
        raise FailClosedRuntimeError("turn evidence ordering is invalid")
    if candidate.get("artifacts_embedded") is not False:
        raise FailClosedRuntimeError("turn evidence artifact duplication detected")
    if candidate.get("replay_protocol_modified") is not False:
        raise FailClosedRuntimeError("turn evidence claims Replay protocol mutation")
    _verify_artifact_hash(candidate, "turn evidence manifest")
    return deepcopy(candidate)


def validate_platform_core_conversation_session_checkpoint(
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    """Validate the immutable session head and projection linkage."""

    candidate = _require_dict(checkpoint, "conversation session checkpoint")
    if candidate.get("artifact_type") != SESSION_CHECKPOINT_ARTIFACT_V1:
        raise FailClosedRuntimeError("conversation checkpoint type is invalid")
    if candidate.get("checkpoint_version") != PLATFORM_CORE_CONVERSATION_BOUNDARY_VERSION:
        raise FailClosedRuntimeError("conversation checkpoint version is invalid")
    _validate_identity_fields(candidate, "conversation session checkpoint")
    _require_string(
        candidate.get("projection_reference"), "projection_reference"
    )
    _require_hash(candidate.get("projection_hash"), "projection_hash")
    _require_string(candidate.get("manifest_reference"), "manifest_reference")
    _require_hash(candidate.get("manifest_hash"), "manifest_hash")
    _validate_optional_reference_pair(
        candidate.get("prior_checkpoint_reference"),
        candidate.get("prior_checkpoint_hash"),
        "prior checkpoint",
    )
    if candidate.get("conversation_state") not in CONVERSATION_STATES:
        raise FailClosedRuntimeError("checkpoint conversation state is invalid")
    if not isinstance(candidate.get("admissible_events"), list):
        raise FailClosedRuntimeError("checkpoint admissible events are invalid")
    if not isinstance(candidate.get("terminal"), bool):
        raise FailClosedRuntimeError("checkpoint terminal flag is invalid")
    if not isinstance(candidate.get("session_close_allowed"), bool):
        raise FailClosedRuntimeError(
            "checkpoint session_close_allowed is invalid"
        )
    if candidate.get("session_owner") != "PLATFORM_CORE":
        raise FailClosedRuntimeError("checkpoint session ownership drift")
    _require_string(
        candidate.get("checkpoint_reference"), "checkpoint_reference"
    )
    _verify_artifact_hash(candidate, "conversation session checkpoint")
    return deepcopy(candidate)


def reconstruct_platform_core_conversation_projection(
    *,
    runtime_root: str | Path,
    session_id: str,
    turn_id: int | None = None,
) -> dict[str, Any]:
    """Reconstruct and verify one projection from immutable boundary evidence."""

    root = Path(runtime_root)
    session = _require_string(session_id, "session_id")
    turns = _turn_directories(root=root, session_id=session)
    if not turns:
        raise FailClosedRuntimeError("conversation boundary replay is missing")
    target_turn = (
        turn_id
        if turn_id is not None
        else int(turns[-1].name.split("_", 1)[0])
    )
    if (
        not isinstance(target_turn, int)
        or isinstance(target_turn, bool)
        or target_turn < 1
    ):
        raise FailClosedRuntimeError("conversation reconstruction turn_id is invalid")

    prior_checkpoint: dict[str, Any] | None = None
    final_capture: dict[str, Any] | None = None
    for expected_turn in range(1, target_turn + 1):
        turn_root = _turn_root(
            root=root, session_id=session, turn_id=expected_turn
        )
        if not turn_root.is_dir():
            raise FailClosedRuntimeError("conversation replay turn is missing")
        event_path = turn_root / "000_event.json"
        manifest_path = turn_root / "001_turn_evidence_manifest.json"
        projection_path = turn_root / "002_conversation_projection.json"
        checkpoint_path = turn_root / "003_session_checkpoint.json"
        event = validate_platform_core_conversation_event(load_json(event_path))
        manifest = validate_platform_core_conversation_turn_evidence_manifest(
            load_json(manifest_path)
        )
        projection = validate_platform_core_conversation_projection(
            load_json(projection_path)
        )
        checkpoint = validate_platform_core_conversation_session_checkpoint(
            load_json(checkpoint_path)
        )
        _verify_reconstructed_turn(
            session_id=session,
            turn_id=expected_turn,
            event=event,
            event_path=event_path,
            manifest=manifest,
            manifest_path=manifest_path,
            projection=projection,
            projection_path=projection_path,
            checkpoint=checkpoint,
            checkpoint_path=checkpoint_path,
            prior_checkpoint=prior_checkpoint,
        )
        for evidence in manifest["evidence_references"]:
            _verify_evidence_reference(evidence)
        final_capture = {
            "conversation_projection": projection,
            "turn_evidence_manifest": manifest,
            "session_checkpoint": checkpoint,
            "event": event,
        }
        prior_checkpoint = checkpoint

    if final_capture is None:
        raise FailClosedRuntimeError("conversation reconstruction produced no result")
    lineage = {
        "event_hash": final_capture["event"]["artifact_hash"],
        "manifest_hash": final_capture["turn_evidence_manifest"]["artifact_hash"],
        "projection_hash": final_capture["conversation_projection"]["artifact_hash"],
        "checkpoint_hash": final_capture["session_checkpoint"]["artifact_hash"],
    }
    return {
        **deepcopy(final_capture),
        "reconstruction_verified": True,
        "reconstruction_turn_count": target_turn,
        "reconstruction_hash": replay_hash(lineage),
        "interface_state_required": False,
        "replay_protocol_modified": False,
    }


def _handle_event(
    *,
    event: dict[str, Any],
    root: Path,
    workspace: str,
    prior_projection: dict[str, Any] | None,
    prior_checkpoint: dict[str, Any] | None,
    prior_workspace: dict[str, Any] | None,
    governed_runtime_runner: GovernedRuntimeRunner | None,
    event_reference: str,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    event_type = event["event_type"]
    if event_type in {
        HUMAN_REQUEST_SUBMITTED,
        CLARIFICATION_REPLY_SUBMITTED,
    }:
        context = prepare_unified_human_interface_project_context(
            interface_name=event["source_interface"],
            session_id=event["session_id"],
            message=event["payload"]["message"],
            runtime_root=root,
            workspace=workspace,
            created_at=event["created_at"],
            explicit_canonical_artifact_references=tuple(
                event["payload"].get(
                    "explicit_canonical_artifact_references", ()
                )
            ),
        )
        conversation = _require_dict(
            context.get("human_conversation_experience"),
            "Platform Core human conversation experience",
        )
        pending_clarification = _pending_clarification(
            message=event["payload"]["message"],
            conversation=conversation,
        )
        pending_summary = _pending_summary(conversation)
        completion = {
            "replay_reference": event_reference,
            "artifact_hash": event["artifact_hash"],
            "development_intent_resolution": deepcopy(
                context.get("development_intent_resolution")
            ),
            "conversation_boundary_event": event_type,
        }
        workspace_state = record_unified_human_interface_workspace_state(
            interface_name=event["source_interface"],
            session_id=event["session_id"],
            runtime_root=root,
            workspace=workspace,
            created_at=event["created_at"],
            completion=completion,
            turn_results=[],
            pending_clarification=pending_clarification,
            pending_summary=pending_summary,
        )
        return {
            "owner": "PLATFORM_CORE_PROJECT_SERVICES",
            "project_context": context,
            "workspace_state": workspace_state,
        }, workspace_state

    if event_type == HUMAN_APPROVAL_SUBMITTED:
        if governed_runtime_runner is None:
            raise FailClosedRuntimeError(
                "governed_runtime_runner is required for approved continuation"
            )
        pending_runtime = _pending_runtime_application_state(prior_projection)
        if pending_runtime is not None:
            accepted_actions = _pending_runtime_actions(pending_runtime)
            if "APPROVE" not in accepted_actions:
                raise FailClosedRuntimeError(
                    "active Runtime Entry state does not accept approval"
                )
            runtime_result = run_human_interface_runtime_entry(
                interface_name=event["source_interface"],
                session_id=event["session_id"],
                human_requests=[],
                created_at=event["created_at"],
                runtime_root=root,
                workspace=workspace,
                governed_runtime_runner=governed_runtime_runner,
                operator_context="PLATFORM_CORE_CONVERSATION_BOUNDARY",
                g31_application_state=pending_runtime,
                g31_human_action="APPROVE",
                g31_human_actor_id=event["payload"]["human_actor_id"],
            )
        else:
            summary = _authoritative_pending_summary(
                prior_projection=prior_projection,
                prior_workspace=prior_workspace,
            )
            runtime_result = run_human_interface_runtime_entry(
                interface_name=event["source_interface"],
                session_id=event["session_id"],
                human_requests=[
                    _require_string(
                        summary.get("canonical_runtime_prompt"),
                        "canonical_runtime_prompt",
                    )
                ],
                created_at=event["created_at"],
                runtime_root=root,
                workspace=workspace,
                governed_runtime_runner=governed_runtime_runner,
                operator_context="PLATFORM_CORE_CONVERSATION_BOUNDARY",
                approved_implementation_turn_binding=_require_dict(
                    summary.get("canonical_implementation_turn_binding"),
                    "canonical implementation turn binding",
                ),
                approved_development_composition_plan_hash=_require_hash(
                    summary.get("development_composition_plan_hash"),
                    "development_composition_plan_hash",
                ),
                approved_durable_governed_work_hash=_require_hash(
                    summary.get("durable_governed_work_hash"),
                    "durable_governed_work_hash",
                ),
                approved_proposal_preview_hash=_require_hash(
                    summary.get("proposal_preview_hash"),
                    "proposal_preview_hash",
                ),
                approved_approval_request_hash=_require_hash(
                    summary.get("approval_request_hash"),
                    "approval_request_hash",
                ),
                g31_human_actor_id=event["payload"]["human_actor_id"],
            )
        workspace_state = latest_platform_core_workspace_state(
            root / event["session_id"]
        )
        if workspace_state is None:
            raise FailClosedRuntimeError(
                "Runtime Entry did not record Platform Core workspace state"
            )
        _verify_artifact_hash(workspace_state, "Runtime Entry workspace state")
        return {
            "owner": "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
            "runtime_result": runtime_result,
            "workspace_state": workspace_state,
        }, workspace_state

    if event_type in {HUMAN_REJECTION_SUBMITTED, HUMAN_CANCEL_SUBMITTED}:
        runtime_result = None
        pending_runtime = _pending_runtime_application_state(prior_projection)
        if event_type == HUMAN_REJECTION_SUBMITTED and pending_runtime is not None:
            if governed_runtime_runner is None:
                raise FailClosedRuntimeError(
                    "governed_runtime_runner is required for rejected continuation"
                )
            accepted_actions = _pending_runtime_actions(pending_runtime)
            if "REJECT" not in accepted_actions:
                raise FailClosedRuntimeError(
                    "active Runtime Entry state does not accept rejection"
                )
            runtime_result = run_human_interface_runtime_entry(
                interface_name=event["source_interface"],
                session_id=event["session_id"],
                human_requests=[],
                created_at=event["created_at"],
                runtime_root=root,
                workspace=workspace,
                governed_runtime_runner=governed_runtime_runner,
                operator_context="PLATFORM_CORE_CONVERSATION_BOUNDARY",
                g31_application_state=pending_runtime,
                g31_human_action="REJECT",
                g31_human_actor_id=event["payload"]["human_actor_id"],
            )
        completion = {
            "replay_reference": event_reference,
            "artifact_hash": event["artifact_hash"],
            "development_intent_resolution": {},
            "conversation_boundary_event": event_type,
        }
        workspace_state = record_unified_human_interface_workspace_state(
            interface_name=event["source_interface"],
            session_id=event["session_id"],
            runtime_root=root,
            workspace=workspace,
            created_at=event["created_at"],
            completion=completion,
            turn_results=[runtime_result] if isinstance(runtime_result, dict) else [],
            pending_clarification=None,
            pending_summary=None,
        )
        return {
            "owner": "PLATFORM_CORE_CONVERSATION_BOUNDARY",
            "terminal_event": event_type,
            "runtime_result": runtime_result,
            "workspace_state": workspace_state,
        }, workspace_state

    if event_type in {
        HUMAN_EXIT_REQUESTED,
        INPUT_EOF_OBSERVED,
        INPUT_INTERRUPT_OBSERVED,
    }:
        return {
            "owner": "PLATFORM_CORE_CONVERSATION_BOUNDARY",
            "transport_event": event_type,
            "pending_state_preserved": (
                prior_projection is not None
                and prior_projection["conversation_state"]
                in {CLARIFICATION_AWAITING_REPLY, APPROVAL_AWAITING_HUMAN}
            ),
        }, prior_workspace

    if event_type == REPLAY_STATE_RESTORED:
        checkpoint_reference = event["payload"]["checkpoint_reference"]
        checkpoint = validate_platform_core_conversation_session_checkpoint(
            load_json(Path(checkpoint_reference))
        )
        if checkpoint["artifact_hash"] != event["payload"]["checkpoint_hash"]:
            raise FailClosedRuntimeError("restored checkpoint hash mismatch")
        if prior_checkpoint is None or (
            checkpoint["artifact_hash"] != prior_checkpoint["artifact_hash"]
        ):
            raise FailClosedRuntimeError(
                "restored checkpoint is not the active session checkpoint"
            )
        return {
            "owner": "PLATFORM_CORE_REPLAY_RECONSTRUCTION",
            "restored_checkpoint": checkpoint,
        }, prior_workspace

    if event_type == RUNTIME_RESULT_RETURNED:
        result_reference = event["payload"]["runtime_result_reference"]
        result = load_json(Path(result_reference))
        _verify_artifact_hash(result, "runtime result")
        if result["artifact_hash"] != event["payload"]["runtime_result_hash"]:
            raise FailClosedRuntimeError("runtime result hash mismatch")
        return {
            "owner": "CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
            "runtime_result": result,
        }, prior_workspace

    raise FailClosedRuntimeError("conversation event has no canonical handler")


def _projection_for_event_result(
    *,
    event: dict[str, Any],
    owner_result: dict[str, Any] | None,
    prior_projection: dict[str, Any] | None,
    manifest_reference: str,
    manifest_hash: str,
) -> dict[str, Any]:
    result = _require_dict(owner_result, "conversation owner result")
    event_type = event["event_type"]
    if event_type in {
        HUMAN_REQUEST_SUBMITTED,
        CLARIFICATION_REPLY_SUBMITTED,
    }:
        return _project_project_services_result(
            event=event,
            context=_require_dict(
                result.get("project_context"), "project services context"
            ),
            manifest_reference=manifest_reference,
            manifest_hash=manifest_hash,
        )
    if event_type in {HUMAN_REJECTION_SUBMITTED, HUMAN_CANCEL_SUBMITTED}:
        return _terminal_projection(
            event=event,
            state=CONVERSATION_CANCELED,
            headline="The pending conversation request was canceled.",
            explanation=(
                "Platform Core recorded the human decision and did not invoke "
                "Runtime Entry, a Worker, or a Provider."
            ),
            completion_status=COMPLETION_CANCELED,
            manifest_reference=manifest_reference,
            manifest_hash=manifest_hash,
        )
    if event_type in {
        HUMAN_EXIT_REQUESTED,
        INPUT_EOF_OBSERVED,
        INPUT_INTERRUPT_OBSERVED,
    }:
        if result.get("pending_state_preserved") is True:
            return _preserved_pending_projection(
                event=event,
                prior_projection=_require_dict(
                    prior_projection, "prior conversation projection"
                ),
                manifest_reference=manifest_reference,
                manifest_hash=manifest_hash,
            )
        return _terminal_projection(
            event=event,
            state=CONVERSATION_COMPLETED,
            headline="The conversation session may close.",
            explanation=(
                "Platform Core found no pending clarification or approval state."
            ),
            completion_status=COMPLETION_RESULT_DELIVERED,
            manifest_reference=manifest_reference,
            manifest_hash=manifest_hash,
        )
    if event_type == REPLAY_STATE_RESTORED:
        return _restored_projection(
            event=event,
            prior_projection=_require_dict(
                prior_projection, "prior conversation projection"
            ),
            manifest_reference=manifest_reference,
            manifest_hash=manifest_hash,
        )
    if event_type in {HUMAN_APPROVAL_SUBMITTED, RUNTIME_RESULT_RETURNED}:
        return _project_runtime_result(
            event=event,
            runtime_result=_require_dict(
                result.get("runtime_result"), "runtime result"
            ),
            manifest_reference=manifest_reference,
            manifest_hash=manifest_hash,
        )
    raise FailClosedRuntimeError("conversation result cannot be projected")


def _project_project_services_result(
    *,
    event: dict[str, Any],
    context: dict[str, Any],
    manifest_reference: str,
    manifest_hash: str,
) -> dict[str, Any]:
    conversation = _require_dict(
        context.get("human_conversation_experience"),
        "human conversation experience",
    )
    intent = _require_dict(
        context.get("development_intent_resolution"),
        "development intent resolution",
    )
    mode = conversation.get("response_mode")
    questions = _string_list(
        conversation.get("clarification_questions"), "clarification_questions"
    )
    approval_summary = conversation.get("approval_summary")
    if mode == "CLARIFICATION" or questions:
        state = CLARIFICATION_AWAITING_REPLY
        expected_event = CLARIFICATION_REPLY_SUBMITTED
        admissible_events = [
            CLARIFICATION_REPLY_SUBMITTED,
            HUMAN_CANCEL_SUBMITTED,
            HUMAN_EXIT_REQUESTED,
            INPUT_EOF_OBSERVED,
            INPUT_INTERRUPT_OBSERVED,
            REPLAY_STATE_RESTORED,
        ]
        next_action = COLLECT_CLARIFICATION_REPLY
        clarification_state = {
            "clarification_status": CLARIFICATION_REQUIRED,
            "clarification_required": True,
            "clarification_questions": questions,
            "clarification_question_bindings": deepcopy(
                intent.get("clarification_question_bindings") or []
            ),
            "clarification_reply_bound": (
                intent.get("clarification_reply_bound") is True
            ),
            "clarification_satisfied": (
                intent.get("clarification_resolved") is True
            ),
            "pending_semantic_slots": deepcopy(
                intent.get("remaining_missing_semantic_slots") or []
            ),
            "clarification_continuity_replay_reference": intent.get(
                "clarification_continuity_replay_reference"
            ),
        }
        approval_state = _no_approval_state()
        completion_state = _completion_state(
            status=AWAITING_HUMAN_INPUT,
            reason="CLARIFICATION_REQUIRED",
            result_delivered=False,
            session_close_allowed=False,
        )
        terminal = False
        session_close_allowed = False
    elif (
        mode == "APPROVAL_PREPARATION"
        and isinstance(approval_summary, dict)
        and approval_summary.get("approval_state") == PENDING_HUMAN_APPROVAL
        and intent.get("summary_admissible") is True
    ):
        state = APPROVAL_AWAITING_HUMAN
        expected_event = HUMAN_APPROVAL_SUBMITTED
        admissible_events = [
            HUMAN_APPROVAL_SUBMITTED,
            HUMAN_REJECTION_SUBMITTED,
            HUMAN_CANCEL_SUBMITTED,
            HUMAN_EXIT_REQUESTED,
            INPUT_EOF_OBSERVED,
            INPUT_INTERRUPT_OBSERVED,
            REPLAY_STATE_RESTORED,
        ]
        next_action = COLLECT_APPROVAL_DECISION
        clarification_state = _no_clarification_state()
        approval_state = {
            "approval_status": PENDING_HUMAN_APPROVAL,
            "approval_required": True,
            "approval_summary": deepcopy(approval_summary),
            "approval_hash": replay_hash(approval_summary),
            "approval_is_execution_authorization": False,
        }
        completion_state = _completion_state(
            status=AWAITING_HUMAN_INPUT,
            reason="HUMAN_APPROVAL_REQUIRED",
            result_delivered=False,
            session_close_allowed=False,
        )
        terminal = False
        session_close_allowed = False
    else:
        state = RESULT_DELIVERED
        expected_event = HUMAN_REQUEST_SUBMITTED
        admissible_events = [
            HUMAN_REQUEST_SUBMITTED,
            HUMAN_EXIT_REQUESTED,
            INPUT_EOF_OBSERVED,
            INPUT_INTERRUPT_OBSERVED,
            REPLAY_STATE_RESTORED,
        ]
        next_action = DISPLAY_NON_DEVELOPMENT_RESPONSE
        clarification_state = _no_clarification_state()
        approval_state = _no_approval_state()
        completion_state = _completion_state(
            status=COMPLETION_RESULT_DELIVERED,
            reason=str(mode or "INFORMATIONAL"),
            result_delivered=True,
            session_close_allowed=True,
        )
        terminal = False
        session_close_allowed = True

    projection = _projection_base(
        event=event,
        state=state,
        expected_event=expected_event,
        admissible_events=admissible_events,
        next_action=next_action,
        terminal=terminal,
        session_close_allowed=session_close_allowed,
        clarification_state=clarification_state,
        approval_state=approval_state,
        completion_state=completion_state,
        manifest_reference=manifest_reference,
        manifest_hash=manifest_hash,
    )
    projection.update(
        {
            "user_headline": conversation.get("user_headline"),
            "user_explanation": conversation.get("user_explanation"),
            "question_set": questions,
            "approval_summary": (
                deepcopy(approval_summary)
                if isinstance(approval_summary, dict)
                else None
            ),
            "runtime_progress": deepcopy(
                conversation.get("progress_messages") or []
            ),
            "runtime_result": deepcopy(
                context.get("governed_read_only_work_result")
            ),
            "completion_summary": (
                "Platform Core delivered a governed read-only result."
                if state == RESULT_DELIVERED
                else None
            ),
            "fail_closed_response": deepcopy(
                conversation.get("fail_closed_response")
            ),
            "project_services_context_hash": context.get("artifact_hash"),
        }
    )
    return _finalize_projection(projection)


def _project_runtime_result(
    *,
    event: dict[str, Any],
    runtime_result: dict[str, Any],
    manifest_reference: str,
    manifest_hash: str,
) -> dict[str, Any]:
    pending_action = runtime_result.get("g31_pending_action")
    if isinstance(pending_action, dict):
        accepted = _string_list(
            pending_action.get("valid_values"), "valid_values"
        )
        if not {"APPROVE", "REJECT"}.intersection(accepted):
            raise FailClosedRuntimeError(
                "Runtime Entry requires an event not defined by Conversation Boundary V1"
            )
        projection = _projection_base(
            event=event,
            state=APPROVAL_AWAITING_HUMAN,
            expected_event=HUMAN_APPROVAL_SUBMITTED,
            admissible_events=[
                HUMAN_APPROVAL_SUBMITTED,
                HUMAN_REJECTION_SUBMITTED,
                HUMAN_CANCEL_SUBMITTED,
                HUMAN_EXIT_REQUESTED,
                INPUT_EOF_OBSERVED,
                INPUT_INTERRUPT_OBSERVED,
                REPLAY_STATE_RESTORED,
            ],
            next_action=COLLECT_APPROVAL_DECISION,
            terminal=False,
            session_close_allowed=False,
            clarification_state=_no_clarification_state(),
            approval_state={
                "approval_status": PENDING_HUMAN_APPROVAL,
                "approval_required": True,
                "approval_summary": deepcopy(pending_action),
                "approval_hash": replay_hash(pending_action),
                "approval_is_execution_authorization": (
                    pending_action.get("action_type") == "EXECUTION_DECISION"
                ),
            },
            completion_state=_completion_state(
                status=AWAITING_HUMAN_INPUT,
                reason="RUNTIME_ENTRY_REQUIRES_HUMAN_DECISION",
                result_delivered=True,
                session_close_allowed=False,
            ),
            manifest_reference=manifest_reference,
            manifest_hash=manifest_hash,
        )
        projection.update(
            {
                "user_headline": "Platform Core requires another human decision.",
                "user_explanation": (
                    "Runtime Entry returned a governed pending action. "
                    "No downstream action is implied by the prior approval."
                ),
                "question_set": [],
                "approval_summary": deepcopy(pending_action),
                "runtime_progress": deepcopy(
                    runtime_result.get("conversation_output_tail") or []
                ),
                "runtime_result": deepcopy(runtime_result),
                "completion_summary": None,
                "fail_closed_response": None,
            }
        )
        return _finalize_projection(projection)

    runtime_completed = (
        runtime_result.get("canonical_runtime_entry_status")
        == CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_BOUND
    )
    projection = _projection_base(
        event=event,
        state=RESULT_DELIVERED if runtime_completed else CONVERSATION_FAILED_CLOSED,
        expected_event=HUMAN_REQUEST_SUBMITTED if runtime_completed else None,
        admissible_events=(
            [
                HUMAN_REQUEST_SUBMITTED,
                HUMAN_EXIT_REQUESTED,
                INPUT_EOF_OBSERVED,
                INPUT_INTERRUPT_OBSERVED,
                REPLAY_STATE_RESTORED,
            ]
            if runtime_completed
            else [HUMAN_REQUEST_SUBMITTED]
        ),
        next_action=(
            DISPLAY_RUNTIME_RESULT
            if runtime_completed
            else DISPLAY_NON_DEVELOPMENT_RESPONSE
        ),
        terminal=False if runtime_completed else True,
        session_close_allowed=True,
        clarification_state=_no_clarification_state(),
        approval_state=_no_approval_state(),
        completion_state=_completion_state(
            status=RUNTIME_COMPLETED if runtime_completed else COMPLETION_FAILED_CLOSED,
            reason=(
                "CANONICAL_RUNTIME_ENTRY_COMPLETED"
                if runtime_completed
                else "CANONICAL_RUNTIME_ENTRY_NOT_FULLY_BOUND"
            ),
            result_delivered=True,
            session_close_allowed=True,
        ),
        manifest_reference=manifest_reference,
        manifest_hash=manifest_hash,
    )
    projection.update(
        {
            "user_headline": (
                "Platform Core runtime returned a governed result."
                if runtime_completed
                else "Platform Core runtime failed closed."
            ),
            "user_explanation": (
                "The result is projected from the existing Runtime Entry."
            ),
            "question_set": [],
            "approval_summary": None,
            "runtime_progress": deepcopy(
                runtime_result.get("conversation_output_tail") or []
            ),
            "runtime_result": deepcopy(runtime_result),
            "completion_summary": (
                "Certified Runtime Entry completed."
                if runtime_completed
                else "Runtime Entry did not prove complete binding."
            ),
            "fail_closed_response": (
                None
                if runtime_completed
                else {
                    "response_authority": "PLATFORM_CORE",
                    "failure_reason": "CANONICAL_RUNTIME_ENTRY_NOT_FULLY_BOUND",
                }
            ),
        }
    )
    return _finalize_projection(projection)


def _preserved_pending_projection(
    *,
    event: dict[str, Any],
    prior_projection: dict[str, Any],
    manifest_reference: str,
    manifest_hash: str,
) -> dict[str, Any]:
    projection = deepcopy(
        validate_platform_core_conversation_projection(prior_projection)
    )
    projection.pop("artifact_hash", None)
    projection.update(
        {
            "session_id": event["session_id"],
            "conversation_id": event["conversation_id"],
            "turn_id": event["turn_id"],
            "source_event_id": event["event_id"],
            "source_event_hash": event["artifact_hash"],
            "turn_evidence_manifest_reference": manifest_reference,
            "turn_evidence_manifest_hash": manifest_hash,
            "next_action": WAIT_FOR_HUMAN,
            "user_explanation": (
                "Platform Core preserved the pending human-input state after "
                f"{event['event_type']}."
            ),
            "replay_reference": manifest_reference,
            "replay_hash": manifest_hash,
        }
    )
    return _finalize_projection(projection)


def _restored_projection(
    *,
    event: dict[str, Any],
    prior_projection: dict[str, Any],
    manifest_reference: str,
    manifest_hash: str,
) -> dict[str, Any]:
    projection = deepcopy(
        validate_platform_core_conversation_projection(prior_projection)
    )
    projection.pop("artifact_hash", None)
    projection.update(
        {
            "turn_id": event["turn_id"],
            "source_event_id": event["event_id"],
            "source_event_hash": event["artifact_hash"],
            "turn_evidence_manifest_reference": manifest_reference,
            "turn_evidence_manifest_hash": manifest_hash,
            "user_explanation": (
                "Platform Core restored the prior state from verified immutable "
                "conversation evidence."
            ),
            "replay_reference": manifest_reference,
            "replay_hash": manifest_hash,
        }
    )
    return _finalize_projection(projection)


def _terminal_projection(
    *,
    event: dict[str, Any],
    state: str,
    headline: str,
    explanation: str,
    completion_status: str,
    manifest_reference: str,
    manifest_hash: str,
) -> dict[str, Any]:
    projection = _projection_base(
        event=event,
        state=state,
        expected_event=HUMAN_REQUEST_SUBMITTED,
        admissible_events=[HUMAN_REQUEST_SUBMITTED, REPLAY_STATE_RESTORED],
        next_action=CLOSE_INTERFACE_SESSION,
        terminal=True,
        session_close_allowed=True,
        clarification_state=_no_clarification_state(),
        approval_state=_no_approval_state(),
        completion_state=_completion_state(
            status=completion_status,
            reason=event["event_type"],
            result_delivered=False,
            session_close_allowed=True,
        ),
        manifest_reference=manifest_reference,
        manifest_hash=manifest_hash,
    )
    projection.update(
        {
            "user_headline": headline,
            "user_explanation": explanation,
            "question_set": [],
            "approval_summary": None,
            "runtime_progress": [],
            "runtime_result": None,
            "completion_summary": headline,
            "fail_closed_response": None,
        }
    )
    return _finalize_projection(projection)


def _failed_closed_projection(
    *,
    event: dict[str, Any],
    prior_projection: dict[str, Any] | None,
    manifest_reference: str,
    manifest_hash: str,
    failure_reason: str,
) -> dict[str, Any]:
    projection = _projection_base(
        event=event,
        state=CONVERSATION_FAILED_CLOSED,
        expected_event=HUMAN_REQUEST_SUBMITTED,
        admissible_events=[HUMAN_REQUEST_SUBMITTED, REPLAY_STATE_RESTORED],
        next_action=DISPLAY_NON_DEVELOPMENT_RESPONSE,
        terminal=True,
        session_close_allowed=True,
        clarification_state={
            "clarification_status": CLARIFICATION_FAILED_CLOSED,
            "clarification_required": False,
            "clarification_questions": [],
        },
        approval_state={
            "approval_status": APPROVAL_FAILED_CLOSED,
            "approval_required": False,
            "approval_summary": None,
            "approval_hash": None,
            "approval_is_execution_authorization": False,
        },
        completion_state=_completion_state(
            status=COMPLETION_FAILED_CLOSED,
            reason=failure_reason,
            result_delivered=False,
            session_close_allowed=True,
        ),
        manifest_reference=manifest_reference,
        manifest_hash=manifest_hash,
    )
    projection.update(
        {
            "user_headline": "Platform Core conversation failed closed.",
            "user_explanation": failure_reason,
            "question_set": [],
            "approval_summary": None,
            "runtime_progress": [],
            "runtime_result": None,
            "completion_summary": "No workflow continuation was authorized.",
            "fail_closed_response": {
                "response_authority": "PLATFORM_CORE",
                "failure_reason": failure_reason,
            },
            "prior_projection_hash": (
                prior_projection.get("artifact_hash")
                if isinstance(prior_projection, dict)
                else None
            ),
        }
    )
    return _finalize_projection(projection)


def _projection_base(
    *,
    event: dict[str, Any],
    state: str,
    expected_event: str | None,
    admissible_events: list[str],
    next_action: str,
    terminal: bool,
    session_close_allowed: bool,
    clarification_state: dict[str, Any],
    approval_state: dict[str, Any],
    completion_state: dict[str, Any],
    manifest_reference: str,
    manifest_hash: str,
) -> dict[str, Any]:
    return {
        "artifact_type": CONVERSATION_PROJECTION_ARTIFACT_V1,
        "projection_version": PLATFORM_CORE_CONVERSATION_BOUNDARY_VERSION,
        "session_id": event["session_id"],
        "conversation_id": event["conversation_id"],
        "turn_id": event["turn_id"],
        "source_event_id": event["event_id"],
        "source_event_hash": event["artifact_hash"],
        "conversation_state": state,
        "lifecycle_status": state,
        "terminal": terminal,
        "session_close_allowed": session_close_allowed,
        "expected_event": expected_event,
        "admissible_events": admissible_events,
        "next_action": next_action,
        "clarification_state": clarification_state,
        "approval_state": approval_state,
        "completion_state": completion_state,
        "turn_evidence_manifest_reference": manifest_reference,
        "turn_evidence_manifest_hash": manifest_hash,
        "replay_reference": manifest_reference,
        "replay_hash": manifest_hash,
        "ownership": deepcopy(OWNERSHIP_FLAGS),
        "boundary_flags": deepcopy(BOUNDARY_FLAGS),
    }


def _finalize_projection(projection: dict[str, Any]) -> dict[str, Any]:
    artifact = json.loads(canonical_serialize(projection))
    artifact["artifact_hash"] = replay_hash(artifact)
    return validate_platform_core_conversation_projection(artifact)


def _turn_evidence_manifest(
    *,
    event: dict[str, Any],
    event_reference: str,
    evidence_references: list[dict[str, str]],
    owner_result: dict[str, Any] | None,
    owner_failure_reason: str | None,
) -> dict[str, Any]:
    manifest = {
        "artifact_type": TURN_EVIDENCE_MANIFEST_ARTIFACT_V1,
        "manifest_version": PLATFORM_CORE_CONVERSATION_BOUNDARY_VERSION,
        "session_id": event["session_id"],
        "conversation_id": event["conversation_id"],
        "turn_id": event["turn_id"],
        "event_reference": event_reference,
        "event_hash": event["artifact_hash"],
        "owner_invoked": (
            owner_result.get("owner")
            if isinstance(owner_result, dict)
            else "PLATFORM_CORE_CONVERSATION_BOUNDARY"
        ),
        "owner_failure_reason": owner_failure_reason,
        "evidence_references": evidence_references,
        "artifacts_embedded": False,
        "project_services_api_modified": False,
        "runtime_entry_api_modified": False,
        "replay_protocol_modified": False,
    }
    manifest["artifact_hash"] = replay_hash(manifest)
    return validate_platform_core_conversation_turn_evidence_manifest(manifest)


def _session_checkpoint(
    *,
    event: dict[str, Any],
    projection: dict[str, Any],
    projection_reference: str,
    manifest: dict[str, Any],
    manifest_reference: str,
    checkpoint_reference: str,
    prior_checkpoint: dict[str, Any] | None,
) -> dict[str, Any]:
    checkpoint = {
        "artifact_type": SESSION_CHECKPOINT_ARTIFACT_V1,
        "checkpoint_version": PLATFORM_CORE_CONVERSATION_BOUNDARY_VERSION,
        "session_id": event["session_id"],
        "conversation_id": event["conversation_id"],
        "turn_id": event["turn_id"],
        "checkpoint_reference": checkpoint_reference,
        "projection_reference": projection_reference,
        "projection_hash": projection["artifact_hash"],
        "manifest_reference": manifest_reference,
        "manifest_hash": manifest["artifact_hash"],
        "prior_checkpoint_reference": (
            prior_checkpoint["checkpoint_reference"]
            if prior_checkpoint is not None
            else None
        ),
        "prior_checkpoint_hash": (
            prior_checkpoint["artifact_hash"]
            if prior_checkpoint is not None
            else None
        ),
        "conversation_state": projection["conversation_state"],
        "expected_event": projection["expected_event"],
        "admissible_events": deepcopy(projection["admissible_events"]),
        "next_action": projection["next_action"],
        "terminal": projection["terminal"],
        "session_close_allowed": projection["session_close_allowed"],
        "session_owner": "PLATFORM_CORE",
        "interface_state_required_for_reconstruction": False,
    }
    checkpoint["artifact_hash"] = replay_hash(checkpoint)
    return validate_platform_core_conversation_session_checkpoint(checkpoint)


def _collect_evidence_references(
    *,
    event: dict[str, Any],
    event_path: Path,
    session_root: Path,
    prior_checkpoint: dict[str, Any] | None,
    prior_workspace: dict[str, Any] | None,
    prior_workspace_reference: str | None,
    owner_result: dict[str, Any] | None,
    workspace_state: dict[str, Any] | None,
) -> list[dict[str, str]]:
    candidates: list[tuple[str, str, str, str]] = [
        (
            "EVENT",
            str(event_path),
            event["artifact_hash"],
            "PLATFORM_CORE_CONVERSATION_BOUNDARY",
        )
    ]
    if prior_checkpoint is not None:
        candidates.append(
            (
                "PRIOR_SESSION_CHECKPOINT",
                prior_checkpoint["checkpoint_reference"],
                prior_checkpoint["artifact_hash"],
                "PLATFORM_CORE_CONVERSATION_BOUNDARY",
            )
        )
    if prior_workspace is not None and prior_workspace_reference is not None:
        candidates.append(
            (
                "PRIOR_PLATFORM_WORKSPACE_STATE",
                prior_workspace_reference,
                prior_workspace["artifact_hash"],
                "PLATFORM_CORE_PROJECT_SERVICES",
            )
        )

    if isinstance(owner_result, dict):
        context = owner_result.get("project_context")
        if isinstance(context, dict):
            _append_hash_reference(
                candidates,
                role="PROJECT_SERVICES_CONTEXT",
                artifact=context,
                session_root=session_root,
                owner="PLATFORM_CORE_PROJECT_SERVICES",
            )
            _append_exact_reference(
                candidates,
                role="OPERATIONAL_TURN_BINDING",
                reference=context.get("operational_turn_binding_reference"),
                artifact_hash=context.get("operational_turn_binding_hash"),
                owner="PLATFORM_CORE_PROJECT_SERVICES",
            )
            _append_hash_reference(
                candidates,
                role="CLARIFICATION_CONTINUITY",
                artifact=context.get("clarification_continuity"),
                session_root=session_root,
                owner="PLATFORM_CORE_PROJECT_SERVICES",
            )
            _append_hash_reference(
                candidates,
                role="DEVELOPMENT_GOVERNANCE",
                artifact=context.get("constitutional_development_governance"),
                session_root=session_root,
                owner="DEVELOPMENT_GOVERNANCE",
            )
            _append_hash_reference(
                candidates,
                role="IMPLEMENTATION_TURN_BINDING",
                artifact=context.get("canonical_implementation_turn_binding"),
                session_root=session_root,
                owner="PLATFORM_CORE_DURABLE_WORK_BINDING",
            )
        runtime_result = owner_result.get("runtime_result")
        if isinstance(runtime_result, dict):
            runtime_hash = runtime_result.get("artifact_hash")
            if isinstance(runtime_hash, str) and runtime_hash.startswith("sha256:"):
                _append_hash_reference(
                    candidates,
                    role="RUNTIME_RESULT",
                    artifact=runtime_result,
                    session_root=session_root,
                    owner="CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY",
                )

    if isinstance(workspace_state, dict):
        _append_hash_reference(
            candidates,
            role="PLATFORM_WORKSPACE_STATE",
            artifact=workspace_state,
            session_root=session_root,
            owner="PLATFORM_CORE_PROJECT_SERVICES",
        )

    unique: dict[tuple[str, str], tuple[str, str, str, str]] = {}
    for candidate in candidates:
        identity = (candidate[1], candidate[2])
        if identity not in unique:
            unique[identity] = candidate
    ordered = sorted(
        unique.values(), key=lambda item: EVIDENCE_ROLE_ORDER.index(item[0])
    )
    references = [
        {
            "role": role,
            "reference": reference,
            "artifact_hash": artifact_hash,
            "owner": owner,
        }
        for role, reference, artifact_hash, owner in ordered
    ]
    for reference in references:
        _verify_evidence_reference(reference)
    return references


def _append_hash_reference(
    candidates: list[tuple[str, str, str, str]],
    *,
    role: str,
    artifact: Any,
    session_root: Path,
    owner: str,
) -> None:
    if not isinstance(artifact, dict):
        return
    artifact_hash = artifact.get("artifact_hash")
    if not isinstance(artifact_hash, str) or not artifact_hash.startswith("sha256:"):
        return
    reference = _find_artifact_reference(
        session_root=session_root, artifact_hash=artifact_hash
    )
    candidates.append((role, reference, artifact_hash, owner))


def _append_exact_reference(
    candidates: list[tuple[str, str, str, str]],
    *,
    role: str,
    reference: Any,
    artifact_hash: Any,
    owner: str,
) -> None:
    if (
        isinstance(reference, str)
        and reference.strip()
        and isinstance(artifact_hash, str)
        and artifact_hash.startswith("sha256:")
    ):
        candidates.append((role, reference, artifact_hash, owner))


def _find_artifact_reference(
    *, session_root: Path, artifact_hash: str
) -> str:
    _require_hash(artifact_hash, "artifact_hash")
    matches: list[Path] = []
    if session_root.exists():
        for path in sorted(session_root.rglob("*.json")):
            try:
                stored = load_json(path)
            except FailClosedRuntimeError:
                continue
            artifact = _stored_artifact_for_hash(
                stored=stored, artifact_hash=artifact_hash
            )
            if artifact is not None:
                matches.append(path)
    if len(matches) != 1:
        raise FailClosedRuntimeError(
            "authoritative artifact reference is missing or ambiguous"
        )
    _verify_stored_reference(
        stored=load_json(matches[0]), artifact_hash=artifact_hash
    )
    return str(matches[0])


def _verify_evidence_reference(reference: dict[str, Any]) -> None:
    path = Path(_require_string(reference.get("reference"), "evidence reference"))
    artifact_hash = _require_hash(
        reference.get("artifact_hash"), "evidence artifact_hash"
    )
    _verify_stored_reference(stored=load_json(path), artifact_hash=artifact_hash)


def _stored_artifact_for_hash(
    *, stored: dict[str, Any], artifact_hash: str
) -> dict[str, Any] | None:
    if stored.get("artifact_hash") == artifact_hash:
        return stored
    nested = stored.get("artifact")
    if isinstance(nested, dict) and nested.get("artifact_hash") == artifact_hash:
        return nested
    return None


def _verify_stored_reference(
    *, stored: dict[str, Any], artifact_hash: str
) -> None:
    artifact = _stored_artifact_for_hash(
        stored=stored, artifact_hash=artifact_hash
    )
    if artifact is None:
        raise FailClosedRuntimeError("referenced evidence hash mismatch")
    _verify_artifact_hash(artifact, "referenced evidence")
    if artifact is not stored:
        wrapper_hash = stored.get("replay_hash")
        if not isinstance(wrapper_hash, str):
            raise FailClosedRuntimeError(
                "referenced evidence wrapper replay hash is required"
            )
        body = deepcopy(stored)
        body.pop("replay_hash")
        if replay_hash(body) != wrapper_hash:
            raise FailClosedRuntimeError(
                "referenced evidence wrapper replay hash mismatch"
            )


def _pending_clarification(
    *, message: str, conversation: dict[str, Any]
) -> dict[str, Any] | None:
    questions = conversation.get("clarification_questions")
    if conversation.get("response_mode") != "CLARIFICATION" and not questions:
        return None
    question_set = _string_list(questions, "clarification_questions")
    if not question_set:
        raise FailClosedRuntimeError(
            "Platform Core clarification lacks canonical questions"
        )
    return {
        "original_message": _require_string(message, "message"),
        "clarification_required": True,
        "clarification_authority": "PLATFORM_CORE",
        "conversation_response_mode": conversation.get("response_mode"),
        "user_headline": conversation.get("user_headline"),
        "user_explanation": conversation.get("user_explanation"),
        "requested_work_type": conversation.get("requested_work_type"),
        "work_type": conversation.get("work_type"),
        "prepared_work_type": conversation.get("prepared_work_type"),
        "work_type_source": conversation.get("work_type_source"),
        "work_type_source_text": conversation.get("work_type_source_text"),
        "mutation_allowed": conversation.get("mutation_allowed"),
        "runtime_implementation": conversation.get("runtime_implementation"),
        "work_type_change_allowed": conversation.get("work_type_change_allowed"),
        "work_type_conflict_detected": conversation.get(
            "work_type_conflict_detected"
        ),
        "work_type_conflict_reason": conversation.get("work_type_conflict_reason"),
        "clarification_questions": question_set,
        "operational_clarification_envelope": deepcopy(
            conversation.get("operational_clarification_envelope")
        )
        if isinstance(
            conversation.get("operational_clarification_envelope"), dict
        )
        else None,
        "artifact_attachment_retry_state": deepcopy(
            conversation.get("artifact_attachment_retry_state")
        )
        if isinstance(conversation.get("artifact_attachment_retry_state"), dict)
        else None,
    }


def _pending_summary(conversation: dict[str, Any]) -> dict[str, Any] | None:
    summary = conversation.get("approval_summary")
    if (
        conversation.get("response_mode") != "APPROVAL_PREPARATION"
        or not isinstance(summary, dict)
        or summary.get("approval_state") != PENDING_HUMAN_APPROVAL
    ):
        return None
    if summary.get("summary_authority") != "PLATFORM_CORE":
        raise FailClosedRuntimeError("approval summary authority is invalid")
    return deepcopy(summary)


def _authoritative_pending_summary(
    *,
    prior_projection: dict[str, Any] | None,
    prior_workspace: dict[str, Any] | None,
) -> dict[str, Any]:
    projection = validate_platform_core_conversation_projection(
        _require_dict(prior_projection, "prior conversation projection")
    )
    workspace = _require_dict(
        prior_workspace, "prior Platform Core workspace state"
    )
    _verify_artifact_hash(workspace, "prior Platform Core workspace state")
    if workspace.get("pending_approval") is not True:
        raise FailClosedRuntimeError("Platform Core has no pending approval")
    summary = _require_dict(
        workspace.get("pending_implementation_summary"),
        "pending implementation summary",
    )
    projected_summary = _require_dict(
        projection.get("approval_summary"), "projected approval summary"
    )
    if replay_hash(summary) != replay_hash(projected_summary):
        raise FailClosedRuntimeError(
            "pending approval projection does not match Platform Core workspace"
        )
    if summary.get("summary_authority") != "PLATFORM_CORE":
        raise FailClosedRuntimeError("pending approval authority is invalid")
    if summary.get("approval_is_execution_authorization") is not False:
        raise FailClosedRuntimeError(
            "proposal approval cannot imply execution authorization"
        )
    return deepcopy(summary)


def _pending_runtime_application_state(
    prior_projection: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not isinstance(prior_projection, dict):
        return None
    runtime_result = prior_projection.get("runtime_result")
    if not isinstance(runtime_result, dict):
        return None
    if not isinstance(runtime_result.get("g31_pending_action"), dict):
        return None
    return deepcopy(runtime_result)


def _pending_runtime_actions(runtime_state: dict[str, Any]) -> list[str]:
    pending = _require_dict(
        runtime_state.get("g31_pending_action"), "g31_pending_action"
    )
    return _string_list(pending.get("valid_values"), "valid_values")


def _validate_event_sequence(
    *,
    event: dict[str, Any],
    prior_projection: dict[str, Any] | None,
    prior_checkpoint: dict[str, Any] | None,
) -> None:
    expected_turn = int(prior_checkpoint["turn_id"]) + 1 if prior_checkpoint else 1
    if event["turn_id"] != expected_turn:
        raise FailClosedRuntimeError("conversation event turn sequence mismatch")
    expected_reference = (
        prior_checkpoint["checkpoint_reference"] if prior_checkpoint else None
    )
    expected_hash = prior_checkpoint["artifact_hash"] if prior_checkpoint else None
    if event.get("prior_checkpoint_reference") != expected_reference:
        raise FailClosedRuntimeError(
            "conversation event prior checkpoint reference mismatch"
        )
    if event.get("prior_checkpoint_hash") != expected_hash:
        raise FailClosedRuntimeError(
            "conversation event prior checkpoint hash mismatch"
        )
    event_type = event["event_type"]
    if prior_projection is None:
        if event_type != HUMAN_REQUEST_SUBMITTED:
            raise FailClosedRuntimeError(
                "first conversation event must submit a human request"
            )
        return
    projection = validate_platform_core_conversation_projection(prior_projection)
    if event_type not in projection["admissible_events"]:
        raise FailClosedRuntimeError(
            "conversation event is not admissible in the active state"
        )


def _validate_event_payload(event_type: str, payload: dict[str, Any]) -> None:
    if event_type in {HUMAN_REQUEST_SUBMITTED, CLARIFICATION_REPLY_SUBMITTED}:
        allowed = {"message", "explicit_canonical_artifact_references"}
        _reject_unexpected_fields(payload, allowed, "conversation request payload")
        _require_string(payload.get("message"), "message")
        references = payload.get("explicit_canonical_artifact_references", [])
        if not isinstance(references, list):
            raise FailClosedRuntimeError(
                "explicit canonical artifact references must be a list"
            )
        replay_hash(references)
        return
    if event_type in {HUMAN_APPROVAL_SUBMITTED, HUMAN_REJECTION_SUBMITTED}:
        _reject_unexpected_fields(
            payload, {"human_actor_id"}, "human decision payload"
        )
        _require_string(payload.get("human_actor_id"), "human_actor_id")
        return
    if event_type in {
        HUMAN_CANCEL_SUBMITTED,
        HUMAN_EXIT_REQUESTED,
        INPUT_EOF_OBSERVED,
        INPUT_INTERRUPT_OBSERVED,
    }:
        _reject_unexpected_fields(payload, {"reason"}, "transport event payload")
        if "reason" in payload:
            _require_string(payload.get("reason"), "reason")
        return
    if event_type == RUNTIME_RESULT_RETURNED:
        _reject_unexpected_fields(
            payload,
            {"runtime_result_reference", "runtime_result_hash"},
            "runtime result payload",
        )
        _require_string(
            payload.get("runtime_result_reference"), "runtime_result_reference"
        )
        _require_hash(payload.get("runtime_result_hash"), "runtime_result_hash")
        return
    if event_type == REPLAY_STATE_RESTORED:
        _reject_unexpected_fields(
            payload,
            {"checkpoint_reference", "checkpoint_hash"},
            "replay restoration payload",
        )
        _require_string(
            payload.get("checkpoint_reference"), "checkpoint_reference"
        )
        _require_hash(payload.get("checkpoint_hash"), "checkpoint_hash")
        return
    raise FailClosedRuntimeError("conversation event payload contract is missing")


def _validate_projection_state_contract(projection: dict[str, Any]) -> None:
    state = projection["conversation_state"]
    if state == CLARIFICATION_AWAITING_REPLY:
        if (
            projection.get("expected_event") != CLARIFICATION_REPLY_SUBMITTED
            or projection.get("next_action") not in {
                COLLECT_CLARIFICATION_REPLY,
                WAIT_FOR_HUMAN,
            }
            or projection["clarification_state"].get("clarification_required")
            is not True
            or projection.get("session_close_allowed") is not False
        ):
            raise FailClosedRuntimeError(
                "clarification projection state contract mismatch"
            )
    if state == APPROVAL_AWAITING_HUMAN:
        if (
            projection.get("expected_event") != HUMAN_APPROVAL_SUBMITTED
            or projection.get("next_action")
            not in {COLLECT_APPROVAL_DECISION, WAIT_FOR_HUMAN}
            or projection["approval_state"].get("approval_required") is not True
            or projection.get("session_close_allowed") is not False
        ):
            raise FailClosedRuntimeError(
                "approval projection state contract mismatch"
            )
    if state in {
        CONVERSATION_COMPLETED,
        CONVERSATION_CANCELED,
        CONVERSATION_FAILED_CLOSED,
    } and projection.get("terminal") is not True:
        raise FailClosedRuntimeError("terminal projection state is not terminal")


def _verify_reconstructed_turn(
    *,
    session_id: str,
    turn_id: int,
    event: dict[str, Any],
    event_path: Path,
    manifest: dict[str, Any],
    manifest_path: Path,
    projection: dict[str, Any],
    projection_path: Path,
    checkpoint: dict[str, Any],
    checkpoint_path: Path,
    prior_checkpoint: dict[str, Any] | None,
) -> None:
    for artifact in (event, manifest, projection, checkpoint):
        if artifact["session_id"] != session_id or artifact["turn_id"] != turn_id:
            raise FailClosedRuntimeError(
                "conversation replay identity continuity mismatch"
            )
    if manifest["event_reference"] != str(event_path):
        raise FailClosedRuntimeError("conversation replay event reference mismatch")
    if manifest["event_hash"] != event["artifact_hash"]:
        raise FailClosedRuntimeError("conversation replay event hash mismatch")
    if projection["turn_evidence_manifest_reference"] != str(manifest_path):
        raise FailClosedRuntimeError(
            "conversation projection manifest reference mismatch"
        )
    if projection["turn_evidence_manifest_hash"] != manifest["artifact_hash"]:
        raise FailClosedRuntimeError("conversation projection manifest hash mismatch")
    if checkpoint["projection_reference"] != str(projection_path):
        raise FailClosedRuntimeError(
            "conversation checkpoint projection reference mismatch"
        )
    if checkpoint["projection_hash"] != projection["artifact_hash"]:
        raise FailClosedRuntimeError(
            "conversation checkpoint projection hash mismatch"
        )
    if checkpoint["manifest_reference"] != str(manifest_path):
        raise FailClosedRuntimeError(
            "conversation checkpoint manifest reference mismatch"
        )
    if checkpoint["manifest_hash"] != manifest["artifact_hash"]:
        raise FailClosedRuntimeError(
            "conversation checkpoint manifest hash mismatch"
        )
    if checkpoint["checkpoint_reference"] != str(checkpoint_path):
        raise FailClosedRuntimeError(
            "conversation checkpoint self reference mismatch"
        )
    expected_prior_reference = (
        prior_checkpoint["checkpoint_reference"] if prior_checkpoint else None
    )
    expected_prior_hash = (
        prior_checkpoint["artifact_hash"] if prior_checkpoint else None
    )
    if checkpoint["prior_checkpoint_reference"] != expected_prior_reference:
        raise FailClosedRuntimeError(
            "conversation checkpoint prior reference mismatch"
        )
    if checkpoint["prior_checkpoint_hash"] != expected_prior_hash:
        raise FailClosedRuntimeError("conversation checkpoint prior hash mismatch")
    if checkpoint["conversation_state"] != projection["conversation_state"]:
        raise FailClosedRuntimeError(
            "conversation checkpoint state projection mismatch"
        )


def _latest_reconstruction(
    *, root: Path, session_id: str
) -> dict[str, Any] | None:
    if not _turn_directories(root=root, session_id=session_id):
        return None
    return reconstruct_platform_core_conversation_projection(
        runtime_root=root, session_id=session_id
    )


def _latest_checkpoint(
    *, root: Path, session_id: str
) -> dict[str, Any] | None:
    reconstruction = _latest_reconstruction(root=root, session_id=session_id)
    if reconstruction is None:
        return None
    checkpoint = reconstruction["session_checkpoint"]
    return deepcopy(checkpoint)


def _turn_directories(*, root: Path, session_id: str) -> list[Path]:
    boundary_root = root / session_id / "conversation_boundary" / "turns"
    if not boundary_root.exists():
        return []
    turns = sorted(path for path in boundary_root.glob("*_turn") if path.is_dir())
    for expected, path in enumerate(turns, start=1):
        if path.name != f"{expected:06d}_turn":
            raise FailClosedRuntimeError("conversation replay turn ordering mismatch")
    return turns


def _turn_root(*, root: Path, session_id: str, turn_id: int) -> Path:
    return (
        root
        / session_id
        / "conversation_boundary"
        / "turns"
        / f"{turn_id:06d}_turn"
    )


def _event_identity(
    *, conversation_id: str, turn_id: int, event_type: str, payload_hash: str
) -> str:
    return (
        f"{conversation_id}:TURN:{turn_id:06d}:{event_type}:"
        f"{payload_hash.removeprefix('sha256:')[:16]}"
    )


def _completion_state(
    *,
    status: str,
    reason: str,
    result_delivered: bool,
    session_close_allowed: bool,
) -> dict[str, Any]:
    return {
        "completion_status": status,
        "completion_reason": reason,
        "result_delivered": result_delivered,
        "session_close_allowed": session_close_allowed,
    }


def _no_clarification_state() -> dict[str, Any]:
    return {
        "clarification_status": NO_CLARIFICATION,
        "clarification_required": False,
        "clarification_questions": [],
    }


def _no_approval_state() -> dict[str, Any]:
    return {
        "approval_status": NO_APPROVAL_REQUIRED,
        "approval_required": False,
        "approval_summary": None,
        "approval_hash": None,
        "approval_is_execution_authorization": False,
    }


def _validate_identity_fields(candidate: dict[str, Any], label: str) -> None:
    session_id = _require_string(candidate.get("session_id"), "session_id")
    conversation_id = _require_string(
        candidate.get("conversation_id"), "conversation_id"
    )
    if session_id != conversation_id:
        raise FailClosedRuntimeError(f"{label} conversation identity mismatch")
    turn_id = candidate.get("turn_id")
    if not isinstance(turn_id, int) or isinstance(turn_id, bool) or turn_id < 1:
        raise FailClosedRuntimeError(f"{label} turn identity is invalid")


def _validate_optional_reference_pair(
    reference: Any, artifact_hash: Any, label: str
) -> None:
    if reference is None and artifact_hash is None:
        return
    if reference is None or artifact_hash is None:
        raise FailClosedRuntimeError(f"{label} reference/hash pair is incomplete")
    _require_string(reference, f"{label}_reference")
    _require_hash(artifact_hash, f"{label}_hash")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    candidate = _require_dict(artifact, label)
    actual = _require_hash(candidate.get("artifact_hash"), "artifact_hash")
    body = deepcopy(candidate)
    body.pop("artifact_hash")
    if replay_hash(body) != actual:
        raise FailClosedRuntimeError(f"{label} artifact hash mismatch")


def _require_hash(value: Any, name: str) -> str:
    text = _require_string(value, name)
    if not text.startswith("sha256:") or len(text) != 71:
        raise FailClosedRuntimeError(f"{name} must be a sha256 replay hash")
    return text


def _require_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{name} is required")
    return value


def _require_dict(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{name} must be an object")
    return value


def _string_list(value: Any, name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, (list, tuple)):
        raise FailClosedRuntimeError(f"{name} must be a list")
    result: list[str] = []
    for item in value:
        result.append(_require_string(item, name))
    return result


def _reject_unexpected_fields(
    payload: dict[str, Any], allowed: set[str], label: str
) -> None:
    unexpected = sorted(set(payload) - allowed)
    if unexpected:
        raise FailClosedRuntimeError(
            f"{label} contains unsupported fields: {unexpected}"
        )


def _failure_reason(exc: Exception) -> str:
    text = " ".join(str(exc).split())
    return text or exc.__class__.__name__


__all__ = [
    "APPROVAL_AWAITING_HUMAN",
    "BOUNDARY_COMPLETED",
    "BOUNDARY_FAILED_CLOSED",
    "CANONICAL_CONVERSATION_EVENT_ARTIFACT_V1",
    "CLARIFICATION_AWAITING_REPLY",
    "CLARIFICATION_REPLY_SUBMITTED",
    "CONVERSATION_CANCELED",
    "CONVERSATION_COMPLETED",
    "CONVERSATION_FAILED_CLOSED",
    "CONVERSATION_PROJECTION_ARTIFACT_V1",
    "HUMAN_APPROVAL_SUBMITTED",
    "HUMAN_CANCEL_SUBMITTED",
    "HUMAN_EXIT_REQUESTED",
    "HUMAN_REJECTION_SUBMITTED",
    "HUMAN_REQUEST_SUBMITTED",
    "INPUT_EOF_OBSERVED",
    "INPUT_INTERRUPT_OBSERVED",
    "PLATFORM_CORE_CONVERSATION_BOUNDARY_VERSION",
    "REPLAY_STATE_RESTORED",
    "RESULT_DELIVERED",
    "RUNTIME_RESULT_RETURNED",
    "SESSION_CHECKPOINT_ARTIFACT_V1",
    "TURN_EVIDENCE_MANIFEST_ARTIFACT_V1",
    "create_platform_core_conversation_event",
    "reconstruct_platform_core_conversation_projection",
    "run_platform_core_conversation_boundary",
    "validate_platform_core_conversation_event",
    "validate_platform_core_conversation_projection",
    "validate_platform_core_conversation_session_checkpoint",
    "validate_platform_core_conversation_turn_evidence_manifest",
]
