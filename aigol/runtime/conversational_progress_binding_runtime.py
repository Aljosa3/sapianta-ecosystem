"""Conversational CLI binding for existing runtime progress visibility."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.runtime_progress_visibility import (
    COMPLETED,
    FAILED_CLOSED,
    RUNNING,
    record_runtime_progress_snapshot,
    reconstruct_runtime_progress_replay,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_CONVERSATIONAL_PROGRESS_BINDING_V1"
FINAL_CLASSIFICATION = "CERTIFIED_CONVERSATIONAL_PROGRESS_BINDING"

CONVERSATIONAL_PROGRESS_BINDING_ARTIFACT_V1 = "CONVERSATIONAL_PROGRESS_BINDING_ARTIFACT_V1"
CONVERSATIONAL_PROGRESS_BINDING_REPLAY_STEP = "conversational_progress_binding_recorded"

ROUTING = "Routing"
COGNITION = "Cognition"
PROVIDER_INVOCATION = "Provider Invocation"
COMPARISON = "Comparison"
CONTINUITY = "Continuity"
CLARIFICATION = "Clarification"
RESULT_ASSEMBLY = "Result Assembly"
REPLAY = "Replay"

CONVERSATIONAL_PROGRESS_STAGE_MODEL = (
    ROUTING,
    COGNITION,
    PROVIDER_INVOCATION,
    COMPARISON,
    CONTINUITY,
    CLARIFICATION,
    RESULT_ASSEMBLY,
    REPLAY,
)


def create_conversational_progress_binding(
    *,
    binding_id: str,
    session_id: str,
    turn_id: str,
    prompt_id: str,
    created_at: str,
    replay_dir: str | Path,
    workflow_id: str = "UNRESOLVED",
) -> dict[str, Any]:
    """Create a replay-visible binding from a conversation turn to progress snapshots."""

    replay_path = Path(replay_dir)
    binding_artifact = {
        "artifact_type": CONVERSATIONAL_PROGRESS_BINDING_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "binding_id": _require_string(binding_id, "binding_id"),
        "runtime_id": f"{_require_string(binding_id, 'binding_id')}:RUNTIME-PROGRESS",
        "session_id": _require_string(session_id, "session_id"),
        "turn_id": _require_string(turn_id, "turn_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "workflow_id": _require_string(workflow_id, "workflow_id"),
        "stage_model": list(CONVERSATIONAL_PROGRESS_STAGE_MODEL),
        "stage_count": len(CONVERSATIONAL_PROGRESS_STAGE_MODEL),
        "started_at": _require_string(created_at, "created_at"),
        "created_at": _require_string(created_at, "created_at"),
        "runtime_progress_replay_reference": str(replay_path / "runtime_progress"),
        "replay_reference": str(replay_path),
        "replay_visible": True,
        "uses_existing_runtime_progress_visibility": True,
        "visibility_only": True,
        "provider_authority": False,
        "approval_authority": False,
        "execution_authority": False,
        "worker_authority": False,
        "governance_authority": False,
        "replay_authority": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "dispatch_requested": False,
        "execution_requested": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }
    binding_artifact["artifact_hash"] = replay_hash(binding_artifact)
    wrapper = {
        "replay_index": 0,
        "replay_step": CONVERSATIONAL_PROGRESS_BINDING_REPLAY_STEP,
        "event_type": CONVERSATIONAL_PROGRESS_BINDING_REPLAY_STEP.upper(),
        "artifact": deepcopy(binding_artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / "000_conversational_progress_binding.json", wrapper)
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "conversational_progress_binding_artifact": binding_artifact,
        "conversational_progress_binding_replay_reference": str(replay_path),
        "runtime_progress_replay_reference": binding_artifact["runtime_progress_replay_reference"],
        "replay_visible": True,
        "visibility_only": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "dispatch_requested": False,
        "execution_requested": False,
    }


def record_conversational_progress_checkpoint(
    *,
    binding_artifact: dict[str, Any],
    stage: str,
    activity: str,
    snapshot_at: str,
    runtime_status: str = RUNNING,
) -> dict[str, Any]:
    """Record and render one conversational progress checkpoint."""

    binding = _validate_binding(binding_artifact)
    normalized_stage = _require_stage(stage)
    normalized_status = _require_status(runtime_status)
    completed = _completed_stages_for(normalized_stage, normalized_status)
    progress = record_runtime_progress_snapshot(
        runtime_id=binding["runtime_id"],
        runtime_status=normalized_status,
        current_stage=normalized_stage,
        completed_stages=completed,
        started_at=binding["started_at"],
        snapshot_at=_require_string(snapshot_at, "snapshot_at"),
        current_activity=_require_string(activity, "activity"),
        stage_model=CONVERSATIONAL_PROGRESS_STAGE_MODEL,
        duration_history=_duration_history(),
        replay_dir=binding["runtime_progress_replay_reference"],
    )
    progress["conversational_progress_binding_id"] = binding["binding_id"]
    progress["conversational_progress_binding_hash"] = binding["artifact_hash"]
    progress["operator_progress_line"] = render_conversational_progress_line(progress)
    progress["final_classification"] = FINAL_CLASSIFICATION
    return progress


def reconstruct_conversational_progress_binding(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct a conversation progress binding and its progress replay."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / "000_conversational_progress_binding.json")
    if wrapper.get("replay_index") != 0:
        raise FailClosedRuntimeError("conversational progress binding replay ordering mismatch")
    if wrapper.get("replay_step") != CONVERSATIONAL_PROGRESS_BINDING_REPLAY_STEP:
        raise FailClosedRuntimeError("conversational progress binding replay step mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("conversational progress binding artifact must be a JSON object")
    binding = _validate_binding(artifact)
    progress = reconstruct_runtime_progress_replay(binding["runtime_progress_replay_reference"])
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "binding_id": binding["binding_id"],
        "runtime_id": binding["runtime_id"],
        "session_id": binding["session_id"],
        "turn_id": binding["turn_id"],
        "prompt_id": binding["prompt_id"],
        "latest_runtime_status": progress["runtime_status"],
        "latest_stage": progress["current_stage"],
        "progress_percent": progress["progress_percent"],
        "replay_visible": True,
        "visibility_only": True,
        "runtime_progress_replay_reference": binding["runtime_progress_replay_reference"],
        "replay_hash": replay_hash([wrapper, progress["replay_hash"]]),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "dispatch_requested": False,
        "execution_requested": False,
    }


def render_conversational_progress_line(progress_capture: dict[str, Any]) -> str:
    artifact = progress_capture.get("runtime_progress_artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("conversational progress artifact is required")
    stage = _require_stage(artifact.get("current_stage"))
    index = CONVERSATIONAL_PROGRESS_STAGE_MODEL.index(stage) + 1
    return f"[{index}/{len(CONVERSATIONAL_PROGRESS_STAGE_MODEL)}] {stage}"


def _completed_stages_for(stage: str, runtime_status: str) -> list[str]:
    if runtime_status == COMPLETED:
        return list(CONVERSATIONAL_PROGRESS_STAGE_MODEL)
    index = CONVERSATIONAL_PROGRESS_STAGE_MODEL.index(stage)
    return list(CONVERSATIONAL_PROGRESS_STAGE_MODEL[:index])


def _duration_history() -> dict[str, Any]:
    return {
        "history_source": "CONVERSATIONAL_PROGRESS_BINDING_V1",
        "runtime_duration_seconds": len(CONVERSATIONAL_PROGRESS_STAGE_MODEL),
        "stage_durations": {
            stage: {
                "average_duration_seconds": 1,
                "last_duration_seconds": 1,
                "sample_count": 1,
            }
            for stage in CONVERSATIONAL_PROGRESS_STAGE_MODEL
        },
    }


def _validate_binding(binding_artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(binding_artifact, dict):
        raise FailClosedRuntimeError("conversational progress binding artifact must be a JSON object")
    candidate = deepcopy(binding_artifact)
    artifact_hash = candidate.pop("artifact_hash", None)
    if artifact_hash != replay_hash(candidate):
        raise FailClosedRuntimeError("conversational progress binding hash mismatch")
    if binding_artifact.get("artifact_type") != CONVERSATIONAL_PROGRESS_BINDING_ARTIFACT_V1:
        raise FailClosedRuntimeError("conversational progress binding artifact type mismatch")
    if binding_artifact.get("stage_model") != list(CONVERSATIONAL_PROGRESS_STAGE_MODEL):
        raise FailClosedRuntimeError("conversational progress binding stage model mismatch")
    return binding_artifact


def _require_stage(value: Any) -> str:
    stage = _require_string(value, "stage")
    if stage not in CONVERSATIONAL_PROGRESS_STAGE_MODEL:
        raise FailClosedRuntimeError("conversational progress stage is not allowed")
    return stage


def _require_status(value: Any) -> str:
    status = _require_string(value, "runtime_status")
    if status not in {RUNNING, COMPLETED, FAILED_CLOSED}:
        raise FailClosedRuntimeError("conversational progress runtime status is not allowed")
    return status


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"conversational progress {field_name} is required")
    return value.strip()


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("conversational progress binding replay hash mismatch")
