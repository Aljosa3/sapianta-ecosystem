"""Replay-based answer resolution for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.resolution_strategy_runtime import REPLAY, select_resolution_strategy
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


REPLAY_RESOLUTION_STRATEGY_VERSION = "REPLAY_RESOLUTION_STRATEGY_V1"
REPLAY_RESOLUTION_ARTIFACT_V1 = "REPLAY_RESOLUTION_ARTIFACT_V1"
REPLAY_RESOLUTION_CREATED = "REPLAY_RESOLUTION_CREATED"
REPLAY_RESOLUTION_RETURNED = "REPLAY_RESOLUTION_RETURNED"
RESOLVED = "RESOLVED"

REPLAY_STEPS = ("replay_resolution_created", "replay_resolution_returned")

REPLAY_PROMPT_MARKERS = (
    "what happened recently",
    "what changed",
    "show latest proposal",
    "show latest approval",
    "what was the last operation",
    "summarize recent activity",
)


def is_replay_oriented_prompt(human_prompt: str) -> bool:
    """Return whether the prompt asks for replay-backed operational evidence."""

    prompt = _normalize_text(human_prompt, "human_prompt").lower().rstrip("?.! ")
    return any(marker in prompt for marker in REPLAY_PROMPT_MARKERS)


def resolve_replay_question(
    *,
    resolution_id: str,
    strategy_id: str,
    human_prompt_reference: str,
    human_prompt: str,
    replay_source_dir: str | Path,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Resolve a replay-oriented question from replay evidence only."""

    replay_path = Path(replay_dir)
    source_path = Path(replay_source_dir)
    _ensure_resolution_replay_available(replay_path)
    if not is_replay_oriented_prompt(human_prompt):
        raise FailClosedRuntimeError("replay resolution failed closed: prompt is not replay-oriented")

    strategy_capture = select_resolution_strategy(
        strategy_id=strategy_id,
        selected_strategy=REPLAY,
        selection_reason="Prompt asks for replay-backed operational evidence.",
        human_prompt_reference=human_prompt_reference,
        created_at=created_at,
        replay_dir=replay_path / "strategy_selection",
    )
    strategy_artifact = strategy_capture["resolution_strategy_artifact"]
    evidence = _collect_replay_evidence(source_path)
    resolution = _resolution_artifact(
        resolution_id=resolution_id,
        strategy_artifact=strategy_artifact,
        human_prompt_reference=human_prompt_reference,
        human_prompt=human_prompt,
        replay_source_dir=source_path,
        evidence=evidence,
        created_at=created_at,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], resolution)
    returned = _resolution_returned(resolution)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(strategy_artifact, resolution, returned)


def reconstruct_replay_resolution(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct replay resolution evidence deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("replay resolution ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("replay resolution artifact must be a JSON object")
        _verify_artifact_hash(artifact, "replay resolution artifact")
        wrappers.append(wrapper)

    resolution = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("resolution_reference") != resolution["resolution_id"]:
        raise FailClosedRuntimeError("replay resolution reference mismatch")
    if returned.get("resolution_hash") != resolution["artifact_hash"]:
        raise FailClosedRuntimeError("replay resolution hash mismatch")
    _validate_resolution(resolution)
    return {
        "resolution_id": resolution["resolution_id"],
        "selected_strategy": resolution["selected_strategy"],
        "human_prompt_reference": resolution["human_prompt_reference"],
        "answer_text": resolution["answer_text"],
        "latest_event_type": resolution["latest_event"]["event_type"],
        "latest_artifact_type": resolution["latest_event"]["artifact_type"],
        "evidence_count": resolution["evidence_count"],
        "resolution_status": resolution["resolution_status"],
        "provider_used": False,
        "worker_invoked": False,
        "execution_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _collect_replay_evidence(replay_source_dir: Path) -> dict[str, Any]:
    if not replay_source_dir.exists() or not replay_source_dir.is_dir():
        raise FailClosedRuntimeError("replay resolution failed closed: replay unavailable")
    events = []
    for path in sorted(replay_source_dir.rglob("*.json")):
        wrapper = _load_verified_replay_json(path)
        artifact = wrapper.get("artifact") if isinstance(wrapper.get("artifact"), dict) else wrapper
        event = {
            "path": str(path.relative_to(replay_source_dir)),
            "event_type": _event_type(wrapper, artifact),
            "artifact_type": str(artifact.get("artifact_type", "UNKNOWN")),
            "created_at": str(artifact.get("created_at", artifact.get("accepted_on", ""))),
            "proposal_id": artifact.get("proposal_id"),
            "approval_id": artifact.get("approval_id"),
            "status": artifact.get("status", artifact.get("approval_status", artifact.get("proposal_status", "UNAVAILABLE"))),
            "artifact_hash": artifact.get("artifact_hash", wrapper.get("replay_hash", "UNAVAILABLE")),
        }
        events.append(event)
    if not events:
        raise FailClosedRuntimeError("replay resolution failed closed: replay unavailable")
    latest = sorted(events, key=lambda item: (item["created_at"], item["path"]))[-1]
    return {
        "events": events,
        "latest": latest,
        "summary": _summary_text(events, latest),
    }


def _load_verified_replay_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FailClosedRuntimeError("replay resolution failed closed: replay corrupt") from exc
    if not isinstance(value, dict):
        raise FailClosedRuntimeError("replay resolution failed closed: replay corrupt")
    if "replay_hash" in value:
        _verify_wrapper_hash(value)
    artifact = value.get("artifact")
    if isinstance(artifact, dict) and "artifact_hash" in artifact:
        _verify_artifact_hash(artifact, "replay source artifact")
    return value


def _resolution_artifact(
    *,
    resolution_id: str,
    strategy_artifact: dict[str, Any],
    human_prompt_reference: str,
    human_prompt: str,
    replay_source_dir: Path,
    evidence: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": REPLAY_RESOLUTION_ARTIFACT_V1,
        "replay_resolution_version": REPLAY_RESOLUTION_STRATEGY_VERSION,
        "resolution_id": _require_string(resolution_id, "resolution_id"),
        "strategy_id": strategy_artifact["strategy_id"],
        "strategy_hash": strategy_artifact["artifact_hash"],
        "selected_strategy": REPLAY,
        "human_prompt_reference": _require_string(human_prompt_reference, "human_prompt_reference"),
        "human_prompt": _normalize_text(human_prompt, "human_prompt"),
        "replay_source_reference": str(replay_source_dir),
        "evidence_count": len(evidence["events"]),
        "latest_event": evidence["latest"],
        "answer_text": evidence["summary"],
        "resolution_status": RESOLVED,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "authority": False,
        "provider_used": False,
        "worker_invoked": False,
        "execution_requested": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_resolution(artifact)
    return artifact


def _resolution_returned(resolution: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(resolution, "replay resolution artifact")
    returned = {
        "event_type": REPLAY_RESOLUTION_RETURNED,
        "resolution_reference": resolution["resolution_id"],
        "resolution_hash": resolution["artifact_hash"],
        "selected_strategy": REPLAY,
        "resolution_status": resolution["resolution_status"],
        "replay_visible": True,
        "provider_used": False,
        "worker_invoked": False,
        "execution_requested": False,
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _summary_text(events: list[dict[str, Any]], latest: dict[str, Any]) -> str:
    return (
        f"Replay evidence contains {len(events)} event(s). "
        f"Latest event: {latest['event_type']} from {latest['path']} "
        f"with artifact_type={latest['artifact_type']} and status={latest['status']}."
    )


def _event_type(wrapper: dict[str, Any], artifact: dict[str, Any]) -> str:
    return str(wrapper.get("event_type", artifact.get("event_type", "UNKNOWN")))


def _capture(strategy: dict[str, Any], resolution: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "resolution_strategy_artifact": deepcopy(strategy),
        "replay_resolution_artifact": deepcopy(resolution),
        "replay_resolution_replay": deepcopy(returned),
    }
    capture["replay_resolution_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_resolution_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("replay resolution step ordering mismatch")
    _verify_artifact_hash(artifact, "replay resolution artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": REPLAY_RESOLUTION_CREATED if index == 0 else REPLAY_RESOLUTION_RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _validate_resolution(resolution: dict[str, Any]) -> None:
    if resolution.get("artifact_type") != REPLAY_RESOLUTION_ARTIFACT_V1:
        raise FailClosedRuntimeError("replay resolution failed closed: invalid artifact")
    if resolution.get("selected_strategy") != REPLAY:
        raise FailClosedRuntimeError("replay resolution failed closed: invalid strategy")
    if resolution.get("resolution_status") != RESOLVED:
        raise FailClosedRuntimeError("replay resolution failed closed: invalid status")
    if not isinstance(resolution.get("latest_event"), dict):
        raise FailClosedRuntimeError("replay resolution failed closed: invalid references")
    if int(resolution.get("evidence_count", 0)) < 1:
        raise FailClosedRuntimeError("replay resolution failed closed: invalid references")
    if resolution.get("replay_visible") is not True:
        raise FailClosedRuntimeError("replay resolution failed closed: replay visibility missing")
    if resolution.get("authority") is not False:
        raise FailClosedRuntimeError("replay resolution failed closed: authority introduced")
    if resolution.get("provider_used") is not False:
        raise FailClosedRuntimeError("replay resolution failed closed: provider use introduced")
    if resolution.get("worker_invoked") is not False:
        raise FailClosedRuntimeError("replay resolution failed closed: worker invocation detected")
    if resolution.get("execution_requested") is not False:
        raise FailClosedRuntimeError("replay resolution failed closed: execution requested")
    _require_string(resolution.get("resolution_id"), "resolution_id")
    _require_string(resolution.get("strategy_id"), "strategy_id")
    _require_string(resolution.get("strategy_hash"), "strategy_hash")
    _require_string(resolution.get("human_prompt_reference"), "human_prompt_reference")
    _require_string(resolution.get("answer_text"), "answer_text")
    _require_string(resolution.get("created_at"), "created_at")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("replay resolution replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("replay resolution replay hash mismatch")


def _normalize_text(value: Any, field_name: str) -> str:
    raw = _require_string(value, field_name)
    normalized = " ".join(raw.split())
    if not normalized:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return normalized


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
