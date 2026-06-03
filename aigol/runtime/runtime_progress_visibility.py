"""Deterministic runtime progress visibility for AiGOL CLI workflows."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from pathlib import Path
import time
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_RUNTIME_PROGRESS_VISIBILITY_VERSION = "AIGOL_RUNTIME_PROGRESS_VISIBILITY_V1"
RUNTIME_PROGRESS_VISIBILITY_ARTIFACT_V1 = "RUNTIME_PROGRESS_VISIBILITY_ARTIFACT_V1"
RUNTIME_DURATION_HISTORY_V1 = "RUNTIME_DURATION_HISTORY_V1"
RUNTIME_VISIBILITY_SNAPSHOT_RECORDED = "RUNTIME_VISIBILITY_SNAPSHOT_RECORDED"
RUNTIME_PROGRESS_REPLAY_RECONSTRUCTED = "RUNTIME_PROGRESS_REPLAY_RECONSTRUCTED"

PENDING = "PENDING"
RUNNING = "RUNNING"
WAITING_FOR_PROVIDER = "WAITING_FOR_PROVIDER"
WAITING_FOR_HUMAN_CLARIFICATION = "WAITING_FOR_HUMAN_CLARIFICATION"
WAITING_FOR_HUMAN_APPROVAL = "WAITING_FOR_HUMAN_APPROVAL"
COMPLETED = "COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"

VALID_RUNTIME_STATUSES = (
    PENDING,
    RUNNING,
    WAITING_FOR_PROVIDER,
    WAITING_FOR_HUMAN_CLARIFICATION,
    WAITING_FOR_HUMAN_APPROVAL,
    COMPLETED,
    FAILED_CLOSED,
)

DEFAULT_STAGE_MODEL = (
    "CONVERSATION",
    "CLARIFICATION",
    "COGNITION",
    "RESOURCE_SELECTION",
    "PPP",
    "PROVIDER_PROPOSAL_PRODUCTION",
    "PROPOSAL_VALIDATION",
    "APPROVAL",
    "HANDOFF",
    "REPLAY_IMPROVEMENT",
)

CONVERSATION = DEFAULT_STAGE_MODEL[0]
CLARIFICATION = DEFAULT_STAGE_MODEL[1]
COGNITION = DEFAULT_STAGE_MODEL[2]
RESOURCE_SELECTION = DEFAULT_STAGE_MODEL[3]
PPP = DEFAULT_STAGE_MODEL[4]
PROVIDER_PROPOSAL_PRODUCTION = DEFAULT_STAGE_MODEL[5]
PROPOSAL_VALIDATION = DEFAULT_STAGE_MODEL[6]
APPROVAL = DEFAULT_STAGE_MODEL[7]
HANDOFF = DEFAULT_STAGE_MODEL[8]
REPLAY_IMPROVEMENT = DEFAULT_STAGE_MODEL[9]

TERMINAL_STATUSES = frozenset({COMPLETED, FAILED_CLOSED})
SNAPSHOT_SUFFIX = "runtime_progress_visibility_snapshot"

VALID_STATUS_TRANSITIONS = {
    PENDING: frozenset({PENDING, RUNNING, FAILED_CLOSED}),
    RUNNING: frozenset(
        {
            RUNNING,
            WAITING_FOR_PROVIDER,
            WAITING_FOR_HUMAN_CLARIFICATION,
            WAITING_FOR_HUMAN_APPROVAL,
            COMPLETED,
            FAILED_CLOSED,
        }
    ),
    WAITING_FOR_PROVIDER: frozenset({WAITING_FOR_PROVIDER, RUNNING, COMPLETED, FAILED_CLOSED}),
    WAITING_FOR_HUMAN_CLARIFICATION: frozenset(
        {WAITING_FOR_HUMAN_CLARIFICATION, RUNNING, FAILED_CLOSED}
    ),
    WAITING_FOR_HUMAN_APPROVAL: frozenset(
        {WAITING_FOR_HUMAN_APPROVAL, RUNNING, COMPLETED, FAILED_CLOSED}
    ),
    COMPLETED: frozenset({COMPLETED}),
    FAILED_CLOSED: frozenset({FAILED_CLOSED}),
}


def record_runtime_progress_snapshot(
    *,
    runtime_id: str,
    runtime_status: str,
    current_stage: str,
    started_at: str,
    snapshot_at: str,
    replay_dir: str | Path,
    current_activity: str = "",
    stage_model: list[str] | tuple[str, ...] | None = None,
    completed_stages: list[str] | tuple[str, ...] | None = None,
    duration_history: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Record an append-only visibility snapshot without changing runtime behavior."""

    replay_path = Path(replay_dir)
    try:
        stages = _validated_stage_model(stage_model)
        completed = _validated_completed_stages(completed_stages or (), stages)
        status = _require_status(runtime_status)
        stage = _require_stage(current_stage, stages)
        _validate_completed_stage_order(completed, stages, stage, status)
        started = _parse_timestamp(started_at, "started_at")
        snapshot = _parse_timestamp(snapshot_at, "snapshot_at")
        if snapshot < started:
            raise FailClosedRuntimeError("runtime progress visibility failed closed: timestamp ordering mismatch")
        index = _next_replay_index(replay_path)
        previous_hash = _latest_snapshot_hash(replay_path)
        history = _duration_history_artifact(duration_history or {}, stages)
        elapsed_seconds = int((snapshot - started).total_seconds())
        progress_percent = _progress_percent(status, completed, stages)
        eta = _eta_artifact(
            runtime_status=status,
            current_stage=stage,
            stage_model=stages,
            completed_stages=completed,
            duration_history=history,
        )
        artifact = {
            "artifact_type": RUNTIME_PROGRESS_VISIBILITY_ARTIFACT_V1,
            "runtime_version": AIGOL_RUNTIME_PROGRESS_VISIBILITY_VERSION,
            "runtime_id": _require_string(runtime_id, "runtime_id"),
            "visibility_status": RUNTIME_VISIBILITY_SNAPSHOT_RECORDED,
            "runtime_status": status,
            "stage_model": stages,
            "stage_count": len(stages),
            "completed_stages": completed,
            "completed_stage_count": len(completed),
            "current_stage": stage,
            "progress_percent": progress_percent,
            "started_at": started_at,
            "snapshot_at": snapshot_at,
            "elapsed_seconds": elapsed_seconds,
            "elapsed_display": format_duration(elapsed_seconds),
            "eta": eta,
            "duration_history": history,
            "current_activity": str(current_activity or ""),
            "previous_snapshot_hash": previous_hash,
            "replay_visible": True,
            "stage_ordering_verified": True,
            "timestamp_ordering_verified": True,
            "status_continuity_verified": True,
            "visibility_only": True,
            "governance_mutated": False,
            "ppp_mutated": False,
            "provider_invoked": False,
            "worker_invoked": False,
            "authorization_created": False,
            "dispatch_requested": False,
            "execution_requested": False,
        }
        artifact["artifact_hash"] = replay_hash(artifact)
        wrapper = _replay_wrapper(index, artifact)
        write_json_immutable(replay_path / f"{index:03d}_{SNAPSHOT_SUFFIX}.json", wrapper)
        return _capture(artifact, wrapper, replay_path)
    except Exception as exc:
        failure = _failed_snapshot_artifact(
            runtime_id=runtime_id,
            runtime_status=runtime_status,
            current_stage=current_stage,
            started_at=started_at,
            snapshot_at=snapshot_at,
            failure_reason=_failure_reason(exc),
        )
        failure_index = _next_replay_index_if_possible(replay_path)
        if failure_index is not None:
            try:
                wrapper = _replay_wrapper(failure_index, failure)
                write_json_immutable(replay_path / f"{failure_index:03d}_{SNAPSHOT_SUFFIX}.json", wrapper)
                return _capture(failure, wrapper, replay_path)
            except Exception:
                pass
        return {
            "command": "aigol runtime-progress",
            "runtime_progress_artifact": failure,
            "runtime_id": failure["runtime_id"],
            "runtime_status": FAILED_CLOSED,
            "current_stage": failure["current_stage"],
            "progress_percent": 0,
            "fail_closed": True,
            "failure_reason": failure["failure_reason"],
            "replay_reference": str(replay_path),
            "replay_visible": True,
            "visibility_only": True,
            "provider_invoked": False,
            "worker_invoked": False,
            "authorization_created": False,
            "dispatch_requested": False,
            "execution_requested": False,
        }


def reconstruct_runtime_progress_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct visibility replay and verify ordering, status continuity, and hashes."""

    replay_path = Path(replay_dir)
    wrappers = _load_snapshot_wrappers(replay_path)
    if not wrappers:
        raise FailClosedRuntimeError("runtime progress visibility replay is missing")

    previous_status: str | None = None
    previous_stage_index = -1
    previous_completed_count = -1
    previous_snapshot: datetime | None = None
    runtime_id: str | None = None
    artifacts: list[dict[str, Any]] = []
    for expected_index, wrapper in enumerate(wrappers):
        if wrapper.get("replay_index") != expected_index:
            raise FailClosedRuntimeError("runtime progress visibility replay ordering mismatch")
        if wrapper.get("replay_step") != SNAPSHOT_SUFFIX:
            raise FailClosedRuntimeError("runtime progress visibility replay step mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("runtime progress visibility artifact must be a JSON object")
        _verify_artifact_hash(artifact, "runtime progress visibility artifact")
        artifact_runtime_id = _require_string(artifact.get("runtime_id"), "runtime_id")
        if runtime_id is None:
            runtime_id = artifact_runtime_id
        elif runtime_id != artifact_runtime_id:
            raise FailClosedRuntimeError("runtime progress visibility runtime id mismatch")
        status = _require_status(artifact.get("runtime_status"))
        stages = _validated_stage_model(artifact.get("stage_model"))
        stage = _require_stage(artifact.get("current_stage"), stages)
        completed = _validated_completed_stages(artifact.get("completed_stages") or (), stages)
        _validate_completed_stage_order(completed, stages, stage, status)
        snapshot_at = _parse_timestamp(artifact.get("snapshot_at"), "snapshot_at")
        if previous_snapshot is not None and snapshot_at < previous_snapshot:
            raise FailClosedRuntimeError("runtime progress visibility timestamp ordering mismatch")
        if previous_status is not None and status not in VALID_STATUS_TRANSITIONS[previous_status]:
            raise FailClosedRuntimeError("runtime progress visibility status continuity mismatch")
        stage_index = stages.index(stage)
        if previous_stage_index > stage_index and status not in TERMINAL_STATUSES:
            raise FailClosedRuntimeError("runtime progress visibility stage ordering mismatch")
        if len(completed) < previous_completed_count:
            raise FailClosedRuntimeError("runtime progress visibility completed stage continuity mismatch")
        previous_status = status
        previous_stage_index = stage_index
        previous_completed_count = len(completed)
        previous_snapshot = snapshot_at
        artifacts.append(artifact)

    latest = artifacts[-1]
    return {
        "command": "aigol runtime-progress",
        "reconstruction_status": RUNTIME_PROGRESS_REPLAY_RECONSTRUCTED,
        "runtime_id": latest["runtime_id"],
        "runtime_status": latest["runtime_status"],
        "current_stage": latest["current_stage"],
        "progress_percent": latest["progress_percent"],
        "elapsed_seconds": latest["elapsed_seconds"],
        "elapsed_display": latest["elapsed_display"],
        "estimated_remaining": latest["eta"]["estimated_remaining_display"],
        "eta_status": latest["eta"]["eta_status"],
        "current_activity": latest["current_activity"],
        "runtime_progress_artifact": deepcopy(latest),
        "replay_artifact_count": len(wrappers),
        "replay_reference": str(replay_path),
        "replay_hash": replay_hash(wrappers),
        "replay_visible": True,
        "stage_ordering_verified": True,
        "timestamp_ordering_verified": True,
        "status_continuity_verified": True,
        "visibility_only": True,
        "governance_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "dispatch_requested": False,
        "execution_requested": False,
        "fail_closed": latest["runtime_status"] == FAILED_CLOSED,
        "failure_reason": latest.get("failure_reason", ""),
    }


def load_runtime_progress(runtime_id: str, replay_root: str | Path = ".aigol_runtime_progress") -> dict[str, Any]:
    """Load the latest replay-visible progress for a runtime id."""

    runtime_path = Path(replay_root) / _require_string(runtime_id, "runtime_id")
    return reconstruct_runtime_progress_replay(runtime_path)


def format_runtime_status(progress: dict[str, Any]) -> str:
    artifact = _progress_artifact(progress)
    return "\n".join(
        [
            f"[{artifact.get('runtime_status')}]",
            "",
            f"Runtime ID: {artifact.get('runtime_id')}",
            f"Current Stage: {artifact.get('current_stage')}",
            f"Progress: {artifact.get('progress_percent')}%",
            f"Elapsed: {artifact.get('elapsed_display')}",
            f"Estimated Remaining: {artifact.get('eta', {}).get('estimated_remaining_display')}",
            f"Current Activity: {artifact.get('current_activity')}",
        ]
    )


def format_runtime_progress(progress: dict[str, Any]) -> str:
    artifact = _progress_artifact(progress)
    percent = int(artifact.get("progress_percent", 0))
    return "\n".join(
        [
            f"[{artifact.get('runtime_status')}]",
            "",
            "Runtime ID:",
            str(artifact.get("runtime_id")),
            "",
            "Current Stage:",
            str(artifact.get("current_stage")),
            "",
            "Progress:",
            f"{progress_bar(percent)} {percent}%",
            "",
            "Elapsed:",
            str(artifact.get("elapsed_display")),
            "",
            "Estimated Remaining:",
            str(artifact.get("eta", {}).get("estimated_remaining_display")),
            "",
            "Current Activity:",
            str(artifact.get("current_activity")),
        ]
    )


def watch_runtime_progress(
    *,
    runtime_id: str,
    replay_root: str | Path = ".aigol_runtime_progress",
    interval_seconds: float = 2.0,
    max_iterations: int | None = None,
) -> list[str]:
    """Return live progress renderings; callers decide whether to print them."""

    if interval_seconds < 0:
        raise FailClosedRuntimeError("runtime progress visibility interval must be non-negative")
    outputs: list[str] = []
    iterations = 0
    while True:
        progress = load_runtime_progress(runtime_id, replay_root)
        outputs.append(format_runtime_progress(progress))
        status = progress.get("runtime_status")
        iterations += 1
        if status in TERMINAL_STATUSES:
            break
        if max_iterations is not None and iterations >= max_iterations:
            break
        time.sleep(interval_seconds)
    return outputs


def progress_bar(percent: int, width: int = 10) -> str:
    if width <= 0:
        raise FailClosedRuntimeError("runtime progress visibility bar width must be positive")
    bounded = max(0, min(100, int(percent)))
    filled = min(width, (bounded * width) // 100)
    return "█" * filled + "░" * (width - filled)


def format_duration(total_seconds: int | None) -> str:
    if total_seconds is None:
        return "unknown"
    seconds = max(0, int(total_seconds))
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{remaining:02d}"


def _duration_history_artifact(duration_history: dict[str, Any], stages: list[str]) -> dict[str, Any]:
    stage_durations = duration_history.get("stage_durations", {})
    if stage_durations is None:
        stage_durations = {}
    if not isinstance(stage_durations, dict):
        raise FailClosedRuntimeError("runtime duration history stage_durations must be a JSON object")
    normalized_durations: dict[str, dict[str, int | None]] = {}
    for stage, value in stage_durations.items():
        if stage not in stages:
            raise FailClosedRuntimeError("runtime duration history stage is not in stage model")
        if not isinstance(value, dict):
            raise FailClosedRuntimeError("runtime duration history stage entry must be a JSON object")
        normalized_durations[stage] = {
            "average_duration_seconds": _optional_nonnegative_int(value.get("average_duration_seconds")),
            "last_duration_seconds": _optional_nonnegative_int(value.get("last_duration_seconds")),
            "sample_count": _optional_nonnegative_int(value.get("sample_count")) or 0,
        }
    history = {
        "artifact_type": RUNTIME_DURATION_HISTORY_V1,
        "stage_durations": normalized_durations,
        "runtime_duration_seconds": _optional_nonnegative_int(duration_history.get("runtime_duration_seconds")),
        "history_source": str(duration_history.get("history_source") or "REPLAY_VISIBLE_HISTORY"),
    }
    history["history_hash"] = replay_hash(history)
    return history


def _eta_artifact(
    *,
    runtime_status: str,
    current_stage: str,
    stage_model: list[str],
    completed_stages: list[str],
    duration_history: dict[str, Any],
) -> dict[str, Any]:
    if runtime_status == COMPLETED:
        return _eta_with_hash("estimated", 0, "completed")
    if runtime_status == FAILED_CLOSED:
        return _eta_with_hash("unknown", None, "failed closed")
    remaining = [stage for stage in stage_model if stage not in completed_stages]
    if current_stage in remaining:
        remaining = remaining[remaining.index(current_stage) :]
    stage_durations = duration_history.get("stage_durations", {})
    total = 0
    for stage in remaining:
        entry = stage_durations.get(stage)
        if not isinstance(entry, dict) or entry.get("average_duration_seconds") is None:
            return _eta_with_hash("unknown", None, "duration history incomplete")
        total += int(entry["average_duration_seconds"])
    return _eta_with_hash("estimated", total, "stage averages")


def _eta_with_hash(status: str, remaining_seconds: int | None, reason: str) -> dict[str, Any]:
    eta = {
        "eta_status": status,
        "estimated_remaining_seconds": remaining_seconds,
        "estimated_remaining_display": format_duration(remaining_seconds),
        "eta_reason": reason,
    }
    eta["eta_inputs_hash"] = replay_hash(eta)
    return eta


def _progress_percent(status: str, completed_stages: list[str], stage_model: list[str]) -> int:
    if status == COMPLETED:
        return 100
    if not stage_model:
        return 0
    return int((len(completed_stages) * 100) // len(stage_model))


def _replay_wrapper(index: int, artifact: dict[str, Any]) -> dict[str, Any]:
    wrapper = {
        "replay_index": index,
        "replay_step": SNAPSHOT_SUFFIX,
        "event_type": RUNTIME_VISIBILITY_SNAPSHOT_RECORDED,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _capture(artifact: dict[str, Any], wrapper: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    return {
        "command": "aigol runtime-progress",
        "runtime_progress_artifact": deepcopy(artifact),
        "runtime_id": artifact["runtime_id"],
        "runtime_status": artifact["runtime_status"],
        "current_stage": artifact["current_stage"],
        "progress_percent": artifact["progress_percent"],
        "elapsed_seconds": artifact["elapsed_seconds"],
        "elapsed_display": artifact["elapsed_display"],
        "estimated_remaining": artifact["eta"]["estimated_remaining_display"],
        "eta_status": artifact["eta"]["eta_status"],
        "current_activity": artifact["current_activity"],
        "snapshot_hash": artifact["artifact_hash"],
        "replay_hash": wrapper["replay_hash"],
        "replay_reference": str(replay_path),
        "replay_visible": True,
        "visibility_only": True,
        "fail_closed": artifact["runtime_status"] == FAILED_CLOSED,
        "failure_reason": artifact.get("failure_reason", ""),
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "dispatch_requested": False,
        "execution_requested": False,
    }


def _load_snapshot_wrappers(replay_path: Path) -> list[dict[str, Any]]:
    paths = sorted(replay_path.glob(f"[0-9][0-9][0-9]_{SNAPSHOT_SUFFIX}.json"))
    return [load_json(path) for path in paths]


def _next_replay_index(replay_path: Path) -> int:
    wrappers = _load_snapshot_wrappers(replay_path) if replay_path.exists() else []
    return len(wrappers)


def _next_replay_index_if_possible(replay_path: Path) -> int | None:
    try:
        return _next_replay_index(replay_path)
    except Exception:
        return None


def _latest_snapshot_hash(replay_path: Path) -> str | None:
    if not replay_path.exists():
        return None
    paths = sorted(replay_path.glob(f"[0-9][0-9][0-9]_{SNAPSHOT_SUFFIX}.json"))
    if not paths:
        return None
    latest = load_json(paths[-1])
    artifact = latest.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("runtime progress visibility previous snapshot is invalid")
    _verify_artifact_hash(artifact, "runtime progress visibility previous snapshot")
    return artifact["artifact_hash"]


def _validated_stage_model(stage_model: Any) -> list[str]:
    stages = list(DEFAULT_STAGE_MODEL if stage_model is None else stage_model)
    if not stages:
        raise FailClosedRuntimeError("runtime progress visibility stage model is required")
    normalized: list[str] = []
    for stage in stages:
        normalized.append(_require_string(stage, "stage"))
    if len(set(normalized)) != len(normalized):
        raise FailClosedRuntimeError("runtime progress visibility stage model contains duplicates")
    return normalized


def _validated_completed_stages(completed_stages: Any, stage_model: list[str]) -> list[str]:
    if not isinstance(completed_stages, (list, tuple)):
        raise FailClosedRuntimeError("runtime progress visibility completed stages must be a list")
    completed = [_require_string(stage, "completed_stage") for stage in completed_stages]
    for stage in completed:
        if stage not in stage_model:
            raise FailClosedRuntimeError("runtime progress visibility completed stage is not in stage model")
    if len(set(completed)) != len(completed):
        raise FailClosedRuntimeError("runtime progress visibility completed stages contain duplicates")
    indexes = [stage_model.index(stage) for stage in completed]
    if indexes != sorted(indexes):
        raise FailClosedRuntimeError("runtime progress visibility completed stages are out of order")
    return completed


def _validate_completed_stage_order(
    completed_stages: list[str],
    stage_model: list[str],
    current_stage: str,
    runtime_status: str,
) -> None:
    current_index = stage_model.index(current_stage)
    for stage in completed_stages:
        if runtime_status != COMPLETED and stage_model.index(stage) > current_index:
            raise FailClosedRuntimeError("runtime progress visibility stage ordering mismatch")


def _require_stage(value: Any, stage_model: list[str]) -> str:
    stage = _require_string(value, "current_stage")
    if stage not in stage_model:
        raise FailClosedRuntimeError("runtime progress visibility current stage is not in stage model")
    return stage


def _require_status(value: Any) -> str:
    status = _require_string(value, "runtime_status")
    if status not in VALID_RUNTIME_STATUSES:
        raise FailClosedRuntimeError("runtime progress visibility runtime status is invalid")
    return status


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"runtime progress visibility {field_name} is required")
    return value.strip()


def _optional_nonnegative_int(value: Any) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or value < 0:
        raise FailClosedRuntimeError("runtime progress visibility duration must be a non-negative integer")
    return value


def _parse_timestamp(value: Any, field_name: str) -> datetime:
    text = _require_string(value, field_name)
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise FailClosedRuntimeError(f"runtime progress visibility {field_name} must be an ISO timestamp") from exc


def _progress_artifact(progress: dict[str, Any]) -> dict[str, Any]:
    artifact = progress.get("runtime_progress_artifact")
    if isinstance(artifact, dict):
        return artifact
    if progress.get("artifact_type") == RUNTIME_PROGRESS_VISIBILITY_ARTIFACT_V1:
        return progress
    raise FailClosedRuntimeError("runtime progress visibility artifact is required")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("runtime progress visibility replay hash is required")
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("runtime progress visibility replay hash mismatch")


def _failed_snapshot_artifact(
    *,
    runtime_id: Any,
    runtime_status: Any,
    current_stage: Any,
    started_at: Any,
    snapshot_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": RUNTIME_PROGRESS_VISIBILITY_ARTIFACT_V1,
        "runtime_version": AIGOL_RUNTIME_PROGRESS_VISIBILITY_VERSION,
        "runtime_id": str(runtime_id or "INVALID_RUNTIME_ID"),
        "visibility_status": FAILED_CLOSED,
        "runtime_status": FAILED_CLOSED,
        "stage_model": list(DEFAULT_STAGE_MODEL),
        "stage_count": len(DEFAULT_STAGE_MODEL),
        "completed_stages": [],
        "completed_stage_count": 0,
        "current_stage": str(current_stage or "UNKNOWN_STAGE"),
        "progress_percent": 0,
        "started_at": str(started_at or ""),
        "snapshot_at": str(snapshot_at or ""),
        "elapsed_seconds": 0,
        "elapsed_display": "00:00:00",
        "eta": _eta_with_hash("unknown", None, "failed closed"),
        "duration_history": _duration_history_artifact({}, list(DEFAULT_STAGE_MODEL)),
        "current_activity": "Failed closed while recording runtime progress visibility.",
        "previous_snapshot_hash": None,
        "failure_reason": failure_reason,
        "replay_visible": True,
        "visibility_only": True,
        "governance_mutated": False,
        "ppp_mutated": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "authorization_created": False,
        "dispatch_requested": False,
        "execution_requested": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_reason(exc: Exception) -> str:
    text = str(exc).strip()
    return text or "runtime progress visibility failed closed"
