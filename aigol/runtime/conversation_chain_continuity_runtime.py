"""Conversation-to-chain continuity runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


CONVERSATION_CHAIN_CONTINUITY_RUNTIME_VERSION = "CONVERSATION_CHAIN_CONTINUITY_RUNTIME_V1"
CONVERSATION_CHAIN_CONTINUITY_RECORD_V1 = "CONVERSATION_CHAIN_CONTINUITY_RECORD_V1"
CONVERSATION_CHAIN_CONTINUITY_RECORDED = "CONVERSATION_CHAIN_CONTINUITY_RECORDED"
CONVERSATION_CHAIN_CONTINUITY_RETURNED = "CONVERSATION_CHAIN_CONTINUITY_RETURNED"

CONTINUITY_PRESERVED = "CONTINUITY_PRESERVED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "conversation_chain_continuity_recorded",
    "conversation_chain_continuity_returned",
)


def attach_conversation_chain_continuity(
    *,
    prompt_id: str,
    conversation_capture: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    session_id: str | None = None,
    current_chain_id: str | None = None,
    latest_chain_id: str | None = None,
    related_chain_id: str | None = None,
) -> dict[str, Any]:
    """Attach read-only canonical chain continuity metadata to a conversation turn."""

    replay_path = Path(replay_dir)
    _ensure_replay_available(replay_path)
    prompt = _require_string(prompt_id, "prompt_id")
    capture = _validate_conversation_capture(conversation_capture)
    chain_id = _canonical_chain_id(
        prompt_id=prompt,
        session_id=session_id,
        current_chain_id=current_chain_id,
        capture=capture,
    )
    latest = _optional_chain_id(latest_chain_id) or chain_id
    related = _optional_chain_id(related_chain_id)
    record = _continuity_record(
        prompt_id=prompt,
        conversation_capture=capture,
        canonical_chain_id=chain_id,
        latest_chain_id=latest,
        current_chain_id=chain_id,
        related_chain_id=related,
        created_at=created_at,
        replay_reference=str(replay_path),
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], CONVERSATION_CHAIN_CONTINUITY_RECORDED, record)
    returned = _continuity_returned(record)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], CONVERSATION_CHAIN_CONTINUITY_RETURNED, returned)
    return _capture(record, returned)


def reconstruct_conversation_chain_continuity_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct conversation chain continuity evidence deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("conversation chain continuity replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("conversation chain continuity replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "conversation chain continuity artifact")
        wrappers.append(wrapper)

    record = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("continuity_reference") != record["continuity_id"]:
        raise FailClosedRuntimeError("conversation chain continuity replay reference mismatch")
    if returned.get("continuity_hash") != record["artifact_hash"]:
        raise FailClosedRuntimeError("conversation chain continuity replay hash mismatch")
    if returned.get("canonical_chain_id") != record["canonical_chain_id"]:
        raise FailClosedRuntimeError("conversation chain continuity replay chain mismatch")
    return {
        "continuity_id": record["continuity_id"],
        "prompt_id": record["prompt_id"],
        "canonical_chain_id": record["canonical_chain_id"],
        "current_chain_id": record["current_chain_id"],
        "latest_chain_id": record["latest_chain_id"],
        "related_chain_id": record["related_chain_id"],
        "continuity_status": record["continuity_status"],
        "suggested_inspection_commands": deepcopy(record["suggested_inspection_commands"]),
        "read_only": True,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "invocation_requested": False,
        "execution_performed": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _continuity_record(
    *,
    prompt_id: str,
    conversation_capture: dict[str, Any],
    canonical_chain_id: str,
    latest_chain_id: str,
    current_chain_id: str,
    related_chain_id: str | None,
    created_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    response_status = conversation_capture.get("response_status")
    fail_closed = conversation_capture.get("fail_closed") is True
    record = {
        "artifact_type": CONVERSATION_CHAIN_CONTINUITY_RECORD_V1,
        "conversation_chain_continuity_runtime_version": CONVERSATION_CHAIN_CONTINUITY_RUNTIME_VERSION,
        "continuity_id": f"{prompt_id}:CHAIN_CONTINUITY",
        "prompt_id": prompt_id,
        "canonical_chain_id": canonical_chain_id,
        "current_chain_id": current_chain_id,
        "latest_chain_id": latest_chain_id,
        "related_chain_id": related_chain_id,
        "response_status": response_status,
        "conversation_replay_reference": conversation_capture.get("conversation_replay_reference"),
        "prompt_replay_reference": conversation_capture.get("replay_reference"),
        "continuity_status": FAILED_CLOSED if fail_closed else CONTINUITY_PRESERVED,
        "suggested_inspection_commands": _suggested_commands(canonical_chain_id),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "read_only": True,
        "authority": False,
        "provider_authority": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "invocation_requested": False,
        "execution_performed": False,
    }
    record["conversation_capture_hash"] = replay_hash(conversation_capture)
    record["artifact_hash"] = replay_hash(record)
    return record


def _continuity_returned(record: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(record, "conversation chain continuity artifact")
    returned = {
        "event_type": CONVERSATION_CHAIN_CONTINUITY_RETURNED,
        "continuity_reference": record["continuity_id"],
        "continuity_hash": record["artifact_hash"],
        "prompt_id": record["prompt_id"],
        "canonical_chain_id": record["canonical_chain_id"],
        "current_chain_id": record["current_chain_id"],
        "latest_chain_id": record["latest_chain_id"],
        "related_chain_id": record["related_chain_id"],
        "continuity_status": record["continuity_status"],
        "suggested_inspection_commands": deepcopy(record["suggested_inspection_commands"]),
        "read_only": True,
        "authority": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "invocation_requested": False,
        "execution_performed": False,
        "replay_visible": True,
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(record: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "conversation_chain_continuity_record": deepcopy(record),
        "conversation_chain_continuity_replay": deepcopy(returned),
        "canonical_chain_id": record["canonical_chain_id"],
        "current_chain_id": record["current_chain_id"],
        "latest_chain_id": record["latest_chain_id"],
        "related_chain_id": record["related_chain_id"],
        "suggested_inspection_commands": deepcopy(record["suggested_inspection_commands"]),
        "conversation_chain_continuity_replay_reference": record["replay_reference"],
        "read_only": True,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "invocation_requested": False,
        "execution_performed": False,
        "replay_visible": True,
    }
    capture["conversation_chain_continuity_capture_hash"] = replay_hash(capture)
    return capture


def _canonical_chain_id(
    *,
    prompt_id: str,
    session_id: str | None,
    current_chain_id: str | None,
    capture: dict[str, Any],
) -> str:
    existing = _optional_chain_id(capture.get("canonical_chain_id"))
    if existing is not None:
        return existing
    current = _optional_chain_id(current_chain_id)
    if current is not None:
        return current
    session = _optional_chain_id(session_id)
    seed = session or prompt_id
    return "CHAIN-" + replay_hash({"conversation_chain_seed": seed})[7:23].upper()


def _suggested_commands(canonical_chain_id: str) -> list[str]:
    return [
        f"show-chain {canonical_chain_id}",
        f"show-full-lineage {canonical_chain_id}",
        f"show-learning-lifecycle {canonical_chain_id}",
    ]


def _validate_conversation_capture(capture: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(capture, dict):
        raise FailClosedRuntimeError("conversation chain continuity failed closed: conversation capture is required")
    if capture.get("worker_invoked") is True:
        raise FailClosedRuntimeError("conversation chain continuity failed closed: worker invocation detected")
    if capture.get("execution_requested") is True:
        raise FailClosedRuntimeError("conversation chain continuity failed closed: execution request detected")
    return deepcopy(capture)


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, event_type: str, artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "conversation chain continuity artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": event_type,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("conversation chain continuity replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _optional_chain_id(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
