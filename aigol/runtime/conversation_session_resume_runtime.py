"""Conversation session resume runtime for AiGOL native development V1."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CONVERSATION_SESSION_RESUME_RUNTIME_VERSION = "CONVERSATION_SESSION_RESUME_RUNTIME_V1"
CONVERSATION_SESSION_RESUME_STATUS = "SESSION_RESUME_READY"
TURN_ID_PATTERN = re.compile(r"^TURN-(\d{6})$")


def resume_conversation_session(
    *,
    session_id: str,
    runtime_root: str | Path,
    created_at: str,
) -> dict[str, Any]:
    """Inspect an existing conversation session and allocate the next safe turn id."""

    session = _require_string(session_id, "session_id")
    root = Path(runtime_root)
    session_root = root / session
    existing_turns = _discover_turns(session_root)
    next_turn_number = _next_turn_number(existing_turns)
    next_turn_id = _turn_id(next_turn_number)
    next_turn_root = session_root / next_turn_id
    _ensure_turn_available(next_turn_root)
    artifact = {
        "runtime_version": CONVERSATION_SESSION_RESUME_RUNTIME_VERSION,
        "session_id": session,
        "runtime_root": str(root),
        "session_root": str(session_root),
        "session_existed": session_root.exists(),
        "session_resumed": bool(existing_turns),
        "existing_turn_ids": list(existing_turns),
        "existing_turn_count": len(existing_turns),
        "next_turn_number": next_turn_number,
        "next_turn_id": next_turn_id,
        "next_turn_root": str(next_turn_root),
        "resume_status": CONVERSATION_SESSION_RESUME_STATUS,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "append_only_semantics_preserved": True,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "invocation_requested": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def allocate_conversation_turn(
    *,
    session_id: str,
    runtime_root: str | Path,
    created_at: str,
) -> dict[str, Any]:
    """Return the next unused turn allocation for a session."""

    return resume_conversation_session(session_id=session_id, runtime_root=runtime_root, created_at=created_at)


def _discover_turns(session_root: Path) -> list[str]:
    if not session_root.exists():
        return []
    if not session_root.is_dir():
        raise FailClosedRuntimeError("conversation session resume failed closed: session root is not a directory")
    turn_numbers: list[int] = []
    for child in session_root.iterdir():
        if not child.is_dir():
            continue
        match = TURN_ID_PATTERN.match(child.name)
        if match:
            turn_numbers.append(int(match.group(1)))
    return [_turn_id(number) for number in sorted(set(turn_numbers))]


def _next_turn_number(existing_turns: list[str]) -> int:
    if not existing_turns:
        return 1
    numbers = []
    for turn_id in existing_turns:
        match = TURN_ID_PATTERN.match(turn_id)
        if not match:
            raise FailClosedRuntimeError("conversation session resume failed closed: invalid turn id")
        numbers.append(int(match.group(1)))
    return max(numbers) + 1


def _ensure_turn_available(turn_root: Path) -> None:
    if turn_root.exists():
        raise FailClosedRuntimeError("conversation session resume failed closed: next turn already exists")
    router_root = turn_root / "source_router"
    for name in ("000_source_of_truth_router_selected.json", "001_source_of_truth_router_returned.json"):
        if (router_root / name).exists():
            raise FailClosedRuntimeError("conversation session resume failed closed: replay path collision would occur")


def _turn_id(number: int) -> str:
    if number < 1 or number > 999999:
        raise FailClosedRuntimeError("conversation session resume failed closed: turn id exhausted")
    return f"TURN-{number:06d}"


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()

