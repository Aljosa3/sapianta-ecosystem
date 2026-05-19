"""Append-only replay logging for AGOL Bridge transport transitions."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

DEFAULT_TIMESTAMP = "1970-01-01T00:00:00Z"
REPLAY_LOG_NAME = "agol_bridge_replay.jsonl"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def replay_log_path(bridge_root: Path) -> Path:
    path = bridge_root / "replay_log" / REPLAY_LOG_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def append_replay_event(
    *,
    bridge_root: Path,
    task_id: str,
    event_type: str,
    previous_state: str,
    next_state: str,
    package: dict,
    actor: str,
    reason: str,
    timestamp: str = DEFAULT_TIMESTAMP,
) -> dict:
    record_without_id = {
        "task_id": task_id,
        "event_type": event_type,
        "previous_state": previous_state,
        "next_state": next_state,
        "package_hash": sha256_digest(package),
        "timestamp": timestamp,
        "actor": actor,
        "reason": reason,
    }
    record = {
        "event_id": f"AGOL-REPLAY-{sha256_digest(record_without_id)[:24]}",
        **record_without_id,
    }
    with replay_log_path(bridge_root).open("a", encoding="utf-8") as handle:
        handle.write(canonical_json(record) + "\n")
    return record
