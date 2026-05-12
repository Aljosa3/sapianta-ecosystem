"""Read-only replay log inspection."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sapianta_bridge.transport.transport_config import TransportConfig


REQUIRED_REPLAY_FIELDS = (
    "task_id",
    "execution_timestamp",
    "codex_exit_code",
    "task_hash",
    "result_hash",
    "processing_duration_seconds",
    "final_state",
)


@dataclass(frozen=True)
class ReplayEvidenceError(Exception):
    field: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"field": self.field, "reason": self.reason}


def _validate_entry(entry: Any, line_number: int) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise ReplayEvidenceError(f"line_{line_number}", "replay entry must be an object")
    for field in REQUIRED_REPLAY_FIELDS:
        if field not in entry:
            raise ReplayEvidenceError(field, "missing replay field")
    if not isinstance(entry["task_id"], str) or not entry["task_id"].strip():
        raise ReplayEvidenceError("task_id", "task_id must be non-empty")
    if entry["final_state"] not in {"COMPLETED", "FAILED"}:
        raise ReplayEvidenceError("final_state", "unknown execution state")
    if not isinstance(entry["codex_exit_code"], int):
        raise ReplayEvidenceError("codex_exit_code", "exit code must be integer")
    if not isinstance(entry["processing_duration_seconds"], (int, float)):
        raise ReplayEvidenceError("processing_duration_seconds", "duration must be numeric")
    return entry


def read_replay_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            parsed = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise ReplayEvidenceError(f"line_{line_number}", f"malformed replay JSON: {exc.msg}") from exc
        entries.append(_validate_entry(parsed, line_number))
    return entries


def execution_history(config: TransportConfig | None = None) -> list[dict[str, Any]]:
    active_config = config or TransportConfig()
    return read_replay_entries(active_config.replay_log_path)


def latest_execution(config: TransportConfig | None = None) -> dict[str, Any] | None:
    entries = execution_history(config)
    return entries[-1] if entries else None


def find_by_task_id(task_id: str, config: TransportConfig | None = None) -> list[dict[str, Any]]:
    return [entry for entry in execution_history(config) if entry["task_id"] == task_id]


def replay_summary(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": entry["task_id"],
        "timestamp": entry["execution_timestamp"],
        "exit_code": entry["codex_exit_code"],
        "final_state": entry["final_state"],
        "duration_seconds": entry["processing_duration_seconds"],
    }

