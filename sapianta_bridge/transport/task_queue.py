"""Deterministic single-task queue operations for bridge transport."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from sapianta_bridge.protocol.enforcement import enforce_artifact_path

from .transport_config import TransportConfig


def queued_tasks(config: TransportConfig) -> list[Path]:
    config.ensure_directories()
    return sorted(config.tasks_dir.glob("*.json"), key=lambda path: path.name)


def load_task(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def next_valid_task(config: TransportConfig) -> Path | None:
    for path in queued_tasks(config):
        result = enforce_artifact_path(path, current_state="CREATED", next_state="VALIDATED")
        if result.allowed_to_continue:
            return path
    return None


def move_to_processing(task_path: Path, config: TransportConfig) -> Path:
    config.ensure_directories()
    destination = config.processing_dir / task_path.name
    return Path(shutil.move(str(task_path), str(destination)))


def move_to_completed(path: Path, config: TransportConfig) -> Path:
    config.ensure_directories()
    destination = config.completed_dir / path.name
    return Path(shutil.move(str(path), str(destination)))


def move_to_failed(path: Path, config: TransportConfig) -> Path:
    config.ensure_directories()
    destination = config.failed_dir / path.name
    return Path(shutil.move(str(path), str(destination)))

