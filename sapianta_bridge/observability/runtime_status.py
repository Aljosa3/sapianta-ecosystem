"""Deterministic runtime status snapshots for bridge transport."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sapianta_bridge.transport.transport_config import TransportConfig

from .queue_inspector import inspect_queue
from .replay_reader import latest_execution


def _count_quarantine_records(quarantine_root: Path) -> int:
    if not quarantine_root.exists():
        return 0
    return len(sorted(quarantine_root.glob("*/QUARANTINE-*/quarantine.json")))


def runtime_status(config: TransportConfig | None = None) -> dict[str, Any]:
    active_config = config or TransportConfig()
    queue = inspect_queue(active_config)
    latest = latest_execution(active_config)
    return {
        "transport_active": active_config.runtime_root.exists(),
        "active_lock_present": active_config.lock_path.exists(),
        "queue_depth": len(queue["tasks"]),
        "processing_tasks": len(queue["processing"]),
        "completed_tasks": len(queue["completed"]),
        "failed_tasks": len(queue["failed"]),
        "quarantined_artifacts": _count_quarantine_records(active_config.quarantine_root),
        "last_execution_timestamp": latest["execution_timestamp"] if latest else None,
        "replay_log_present": active_config.replay_log_path.exists(),
    }

