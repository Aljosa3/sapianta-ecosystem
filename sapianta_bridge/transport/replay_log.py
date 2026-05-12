"""Append-only replay ledger for bridge transport executions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def replay_entry(
    *,
    task_id: str,
    execution_timestamp: str,
    codex_exit_code: int,
    task_hash: str,
    result_hash: str,
    processing_duration_seconds: float,
    final_state: str,
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "execution_timestamp": execution_timestamp,
        "codex_exit_code": codex_exit_code,
        "task_hash": task_hash,
        "result_hash": result_hash,
        "processing_duration_seconds": round(processing_duration_seconds, 6),
        "final_state": final_state,
    }


def append_replay_log(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True, separators=(",", ":")))
        handle.write("\n")

