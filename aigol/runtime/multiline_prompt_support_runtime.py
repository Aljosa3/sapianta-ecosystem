"""Replay-visible multiline prompt capture for the interactive conversation CLI."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_MULTILINE_PROMPT_SUPPORT_RUNTIME_V1"
FINAL_CLASSIFICATION = "CERTIFIED_MULTILINE_PROMPT_SUPPORT_RUNTIME"

MULTILINE_PROMPT_CAPTURED_ARTIFACT_V1 = "MULTILINE_PROMPT_CAPTURED_ARTIFACT_V1"
MULTILINE_PROMPT_CAPTURED = "MULTILINE_PROMPT_CAPTURED"
TURN_STARTED = "TURN_STARTED"

REPLAY_STEP = "multiline_prompt_captured"


def record_multiline_prompt_capture(
    *,
    session_id: str,
    turn_id: str,
    prompt_id: str,
    prompt_lines: list[str],
    assembled_prompt: str,
    terminator: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Persist prompt assembly evidence before routing."""

    replay_path = Path(replay_dir)
    lines = _prompt_lines(prompt_lines)
    prompt = _require_string(assembled_prompt, "assembled_prompt")
    artifact = {
        "artifact_type": MULTILINE_PROMPT_CAPTURED_ARTIFACT_V1,
        "milestone_id": MILESTONE_ID,
        "capture_id": f"{_require_string(prompt_id, 'prompt_id')}:MULTILINE_PROMPT_CAPTURED",
        "session_id": _require_string(session_id, "session_id"),
        "turn_id": _require_string(turn_id, "turn_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "event_type": MULTILINE_PROMPT_CAPTURED,
        "turn_boundary_event": TURN_STARTED,
        "input_mode": "MULTILINE_SENTINEL" if len(lines) > 1 else "SINGLE_LINE",
        "line_count": len(lines),
        "character_count": len(prompt),
        "assembled_prompt_hash": replay_hash(prompt),
        "blank_line_count": sum(1 for line in lines if line == ""),
        "terminator": _require_string(terminator, "terminator"),
        "terminator_included": False,
        "ordering_preserved": True,
        "single_turn_guarantee": True,
        "fragment_turns_created": False,
        "partial_routing_allowed": False,
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
    wrapper = {
        "replay_index": 0,
        "replay_step": REPLAY_STEP,
        "event_type": MULTILINE_PROMPT_CAPTURED,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_path / f"000_{REPLAY_STEP}.json", wrapper)
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "multiline_prompt_capture_artifact": deepcopy(artifact),
        "multiline_prompt_capture_replay_reference": str(replay_path),
        "turn_started": True,
        "line_count": artifact["line_count"],
        "character_count": artifact["character_count"],
        "assembled_prompt_hash": artifact["assembled_prompt_hash"],
        "replay_visible": True,
    }


def reconstruct_multiline_prompt_capture_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct multiline prompt capture evidence."""

    replay_path = Path(replay_dir)
    wrapper = load_json(replay_path / f"000_{REPLAY_STEP}.json")
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != REPLAY_STEP:
        raise FailClosedRuntimeError("multiline prompt capture replay ordering mismatch")
    _verify_wrapper_hash(wrapper)
    artifact = wrapper.get("artifact")
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("multiline prompt capture artifact must be a JSON object")
    _verify_artifact_hash(artifact, "multiline prompt capture artifact")
    if artifact.get("artifact_type") != MULTILINE_PROMPT_CAPTURED_ARTIFACT_V1:
        raise FailClosedRuntimeError("multiline prompt capture artifact type mismatch")
    if artifact.get("event_type") != MULTILINE_PROMPT_CAPTURED:
        raise FailClosedRuntimeError("multiline prompt capture event type mismatch")
    if artifact.get("turn_boundary_event") != TURN_STARTED:
        raise FailClosedRuntimeError("multiline prompt capture turn boundary mismatch")
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "session_id": artifact["session_id"],
        "turn_id": artifact["turn_id"],
        "prompt_id": artifact["prompt_id"],
        "event_type": artifact["event_type"],
        "turn_boundary_event": artifact["turn_boundary_event"],
        "input_mode": artifact["input_mode"],
        "line_count": artifact["line_count"],
        "character_count": artifact["character_count"],
        "assembled_prompt_hash": artifact["assembled_prompt_hash"],
        "terminator_included": artifact["terminator_included"],
        "ordering_preserved": artifact["ordering_preserved"],
        "single_turn_guarantee": artifact["single_turn_guarantee"],
        "fragment_turns_created": artifact["fragment_turns_created"],
        "partial_routing_allowed": artifact["partial_routing_allowed"],
        "replay_visible": True,
        "visibility_only": True,
        "replay_artifact_count": 1,
        "replay_hash": replay_hash(wrapper),
    }


def _prompt_lines(values: list[str]) -> list[str]:
    if not isinstance(values, list) or not values:
        raise FailClosedRuntimeError("multiline prompt capture prompt_lines must be a non-empty list")
    lines: list[str] = []
    for value in values:
        if not isinstance(value, str):
            raise FailClosedRuntimeError("multiline prompt capture prompt line must be a string")
        lines.append(value)
    return lines


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"multiline prompt capture {field_name} is required")
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
        raise FailClosedRuntimeError("multiline prompt capture replay hash mismatch")
