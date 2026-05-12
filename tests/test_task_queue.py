from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from protocol_fixtures import valid_task

from sapianta_bridge.transport.task_queue import (
    move_to_processing,
    next_valid_task,
    queued_tasks,
)
from sapianta_bridge.transport.transport_config import TransportConfig


def _config(tmp_path: Path) -> TransportConfig:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    config = TransportConfig(
        runtime_root=tmp_path / "runtime",
        workspace=workspace,
        quarantine_root=tmp_path / "quarantine",
    )
    config.ensure_directories()
    return config


def test_valid_task_enters_processing(tmp_path: Path) -> None:
    config = _config(tmp_path)
    task_path = config.tasks_dir / "task.json"
    task_path.write_text(json.dumps(valid_task(), sort_keys=True), encoding="utf-8")

    selected = next_valid_task(config)
    assert selected == task_path
    processing = move_to_processing(selected, config)
    assert processing.parent == config.processing_dir
    assert not task_path.exists()


def test_task_queue_processes_one_task_only(tmp_path: Path) -> None:
    config = _config(tmp_path)
    for name in ("001-task.json", "002-task.json"):
        task = valid_task()
        task["task_id"] = f"TASK-{name[:3]}"
        (config.tasks_dir / name).write_text(json.dumps(task, sort_keys=True), encoding="utf-8")

    queued = queued_tasks(config)
    selected = next_valid_task(config)

    assert len(queued) == 2
    assert selected == config.tasks_dir / "001-task.json"

