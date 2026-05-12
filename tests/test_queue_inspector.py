from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.observability.queue_inspector import inspect_queue
from sapianta_bridge.transport.transport_config import TransportConfig


def _config(tmp_path: Path) -> TransportConfig:
    config = TransportConfig(
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path / "workspace",
        quarantine_root=tmp_path / "quarantine",
    )
    config.ensure_directories()
    config.workspace.mkdir()
    return config


def _snapshot(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): path.read_text(encoding="utf-8")
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_queue_inspection_read_only(tmp_path: Path) -> None:
    config = _config(tmp_path)
    (config.tasks_dir / "001-task.json").write_text("queued", encoding="utf-8")
    (config.processing_dir / "002-task.json").write_text("processing", encoding="utf-8")
    (config.completed_dir / "003-result.json").write_text("completed", encoding="utf-8")
    (config.failed_dir / "004-result.json").write_text("failed", encoding="utf-8")
    before = _snapshot(config.runtime_root)

    result = inspect_queue(config)
    after = _snapshot(config.runtime_root)

    assert result == {
        "completed": ["003-result.json"],
        "failed": ["004-result.json"],
        "processing": ["002-task.json"],
        "tasks": ["001-task.json"],
    }
    assert after == before
