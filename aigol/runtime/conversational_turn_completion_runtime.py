"""Replay-visible conversational turn completion evidence."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_CONVERSATIONAL_TURN_COMPLETION_RUNTIME_V1"
FINAL_CLASSIFICATION = "CERTIFIED_CONVERSATIONAL_TURN_COMPLETION_RUNTIME"

TURN_COMPLETED_ARTIFACT_V1 = "TURN_COMPLETED_ARTIFACT_V1"
RESULT_DELIVERED_ARTIFACT_V1 = "RESULT_DELIVERED_ARTIFACT_V1"

TURN_COMPLETED = "TURN_COMPLETED"
RESULT_DELIVERED = "RESULT_DELIVERED"

STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED_CLOSED = "FAILED_CLOSED"

TRANSITION_DEFINITIONS = (
    {
        "transition": TURN_COMPLETED,
        "from_state": "REPLAY_PROGRESS_RECORDED",
        "to_state": TURN_COMPLETED,
        "meaning": "The turn branch has completed and replay progress is recorded.",
        "authority_created": False,
    },
    {
        "transition": RESULT_DELIVERED,
        "from_state": TURN_COMPLETED,
        "to_state": RESULT_DELIVERED,
        "meaning": "The human-facing result and completion boundary have been delivered to the operator.",
        "authority_created": False,
    },
)

REPLAY_STEPS = (
    "turn_completed",
    "result_delivered",
)


def record_conversational_turn_completed(
    *,
    session_id: str,
    turn_id: str,
    prompt_id: str,
    providers: list[str],
    status: str,
    result_delivered: bool,
    elapsed_seconds: int,
    progress_replay_reference: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Persist immutable turn completion evidence."""

    replay_path = Path(replay_dir)
    artifact = {
        "artifact_type": TURN_COMPLETED_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "turn_completion_id": f"{_require_string(prompt_id, 'prompt_id')}:TURN_COMPLETED",
        "session_id": _require_string(session_id, "session_id"),
        "turn_id": _require_string(turn_id, "turn_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "transition": TURN_COMPLETED,
        "lifecycle_state": TURN_COMPLETED,
        "status": _require_status(status),
        "providers": _providers(providers),
        "result_delivered": bool(result_delivered),
        "elapsed_seconds": _require_nonnegative_int(elapsed_seconds, "elapsed_seconds"),
        "progress_replay_reference": _require_string(progress_replay_reference, "progress_replay_reference"),
        "transition_definitions": deepcopy(TRANSITION_DEFINITIONS),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": str(replay_path),
        "replay_visible": True,
        "visibility_only": True,
        "provider_authority": False,
        "approval_authority": False,
        "execution_authority": False,
        "worker_authority": False,
        "governance_authority": False,
        "replay_authority": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _persist_step(replay_path, 0, REPLAY_STEPS[0], artifact)
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "turn_completed_artifact": deepcopy(artifact),
        "turn_completion_replay_reference": str(replay_path),
        "replay_visible": True,
    }


def record_conversational_result_delivered(
    *,
    turn_completed_artifact: dict[str, Any],
    delivered_at: str,
    delivered_output_line_count: int,
) -> dict[str, Any]:
    """Persist immutable result delivery evidence for a completed turn."""

    turn_completed = _validate_turn_completed(turn_completed_artifact)
    replay_path = Path(turn_completed["replay_reference"])
    artifact = {
        "artifact_type": RESULT_DELIVERED_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "result_delivery_id": f"{turn_completed['prompt_id']}:RESULT_DELIVERED",
        "turn_completion_reference": turn_completed["turn_completion_id"],
        "turn_completion_hash": turn_completed["artifact_hash"],
        "session_id": turn_completed["session_id"],
        "turn_id": turn_completed["turn_id"],
        "prompt_id": turn_completed["prompt_id"],
        "transition": RESULT_DELIVERED,
        "lifecycle_state": RESULT_DELIVERED,
        "status": turn_completed["status"],
        "providers": deepcopy(turn_completed["providers"]),
        "result_delivered": True,
        "elapsed_seconds": turn_completed["elapsed_seconds"],
        "delivered_output_line_count": _require_nonnegative_int(
            delivered_output_line_count, "delivered_output_line_count"
        ),
        "transition_definitions": deepcopy(TRANSITION_DEFINITIONS),
        "delivered_at": _require_string(delivered_at, "delivered_at"),
        "replay_reference": str(replay_path),
        "replay_visible": True,
        "visibility_only": True,
        "provider_authority": False,
        "approval_authority": False,
        "execution_authority": False,
        "worker_authority": False,
        "governance_authority": False,
        "replay_authority": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], artifact)
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "turn_completed_artifact": deepcopy(turn_completed),
        "result_delivered_artifact": deepcopy(artifact),
        "turn_completion_replay_reference": str(replay_path),
        "operator_completion_summary": render_conversational_turn_completion_summary(
            {
                "turn_id": artifact["turn_id"],
                "providers": artifact["providers"],
                "status": artifact["status"],
                "result_delivered": artifact["result_delivered"],
                "elapsed_seconds": artifact["elapsed_seconds"],
            }
        ),
        "replay_visible": True,
    }


def reconstruct_conversational_turn_completion_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct turn completion and result delivery evidence."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("conversational turn completion replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("conversational turn completion replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "conversational turn completion artifact")
        wrappers.append(wrapper)

    turn_completed = _validate_turn_completed(wrappers[0]["artifact"])
    result_delivered = wrappers[1]["artifact"]
    if result_delivered.get("artifact_type") != RESULT_DELIVERED_ARTIFACT_V1:
        raise FailClosedRuntimeError("conversational result delivered artifact type mismatch")
    if result_delivered.get("turn_completion_reference") != turn_completed["turn_completion_id"]:
        raise FailClosedRuntimeError("conversational result delivery reference mismatch")
    if result_delivered.get("turn_completion_hash") != turn_completed["artifact_hash"]:
        raise FailClosedRuntimeError("conversational result delivery hash mismatch")
    if result_delivered.get("result_delivered") is not True:
        raise FailClosedRuntimeError("conversational result delivery must be explicit")

    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "session_id": turn_completed["session_id"],
        "turn_id": turn_completed["turn_id"],
        "prompt_id": turn_completed["prompt_id"],
        "status": result_delivered["status"],
        "providers": deepcopy(result_delivered["providers"]),
        "turn_completed": True,
        "result_delivered": True,
        "elapsed_seconds": result_delivered["elapsed_seconds"],
        "transition_definitions": deepcopy(TRANSITION_DEFINITIONS),
        "replay_visible": True,
        "visibility_only": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def render_conversational_turn_completion_summary(capture: dict[str, Any]) -> str:
    """Render the operator-facing turn completion boundary."""

    providers = capture.get("providers")
    if not isinstance(providers, list):
        providers = []
    provider_text = ", ".join(str(provider) for provider in providers) if providers else "NONE"
    delivered = "TRUE" if capture.get("result_delivered") is True else "FALSE"
    elapsed = _require_nonnegative_int(capture.get("elapsed_seconds"), "elapsed_seconds")
    return "\n".join(
        [
            "================================",
            "TURN COMPLETED",
            f"turn_id: {_require_string(capture.get('turn_id'), 'turn_id')}",
            f"providers: {provider_text}",
            f"status: {_require_status(capture.get('status'))}",
            f"result_delivered: {delivered}",
            f"elapsed: {elapsed}s",
            "============",
        ]
    )


def _persist_step(replay_path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": step.upper(),
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"{index:03d}_{step}.json", wrapper)


def _validate_turn_completed(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("conversational turn completed artifact must be a JSON object")
    _verify_artifact_hash(artifact, "conversational turn completed artifact")
    if artifact.get("artifact_type") != TURN_COMPLETED_ARTIFACT_V1:
        raise FailClosedRuntimeError("conversational turn completed artifact type mismatch")
    if artifact.get("transition") != TURN_COMPLETED:
        raise FailClosedRuntimeError("conversational turn completion transition mismatch")
    return artifact


def _providers(values: list[str]) -> list[str]:
    if not isinstance(values, list):
        raise FailClosedRuntimeError("conversational turn completion providers must be a list")
    normalized = [_require_string(value, "provider") for value in values]
    if len(normalized) != len(set(normalized)):
        raise FailClosedRuntimeError("conversational turn completion providers must be unique")
    return normalized


def _require_status(value: Any) -> str:
    status = _require_string(value, "status")
    if status not in {STATUS_COMPLETED, STATUS_FAILED_CLOSED}:
        raise FailClosedRuntimeError("conversational turn completion status is not allowed")
    return status


def _require_nonnegative_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or value < 0:
        raise FailClosedRuntimeError(f"conversational turn completion {field_name} must be non-negative")
    return value


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"conversational turn completion {field_name} is required")
    return value.strip()


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("conversational turn completion replay hash mismatch")
