"""Read-only queue inspection for bridge runtime directories."""

from __future__ import annotations

from pathlib import Path

from sapianta_bridge.transport.transport_config import TransportConfig


def _names(directory: Path) -> list[str]:
    if not directory.exists():
        return []
    return sorted(path.name for path in directory.glob("*.json"))


def inspect_queue(config: TransportConfig | None = None) -> dict[str, list[str]]:
    active_config = config or TransportConfig()
    return {
        "tasks": _names(active_config.tasks_dir),
        "processing": _names(active_config.processing_dir),
        "completed": _names(active_config.completed_dir),
        "failed": _names(active_config.failed_dir),
    }

