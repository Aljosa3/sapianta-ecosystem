from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.reflection.reflection_engine import generate_reflection
from sapianta_bridge.reflection.reflection_reader import (
    latest_reflection,
    reflection_history,
    reflections_for_task,
)
from sapianta_bridge.transport.replay_log import append_replay_log, replay_entry
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


def _append_completed(config: TransportConfig, task_id: str) -> None:
    append_replay_log(
        config.replay_log_path,
        replay_entry(
            task_id=task_id,
            execution_timestamp=f"2026-05-12T00:00:0{task_id[-1]}+00:00",
            codex_exit_code=0,
            task_hash="a" * 64,
            result_hash="b" * 64,
            processing_duration_seconds=1.0,
            final_state="COMPLETED",
        ),
    )


def _snapshot(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): path.read_text(encoding="utf-8")
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_reflection_reader_immutable(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _append_completed(config, "TASK-001")
    generate_reflection("TASK-001", config, timestamp="2026-05-12T00:00:01+00:00")
    before = _snapshot(config.runtime_root / "reflections")

    history = reflection_history(config)
    latest = latest_reflection(config)
    after = _snapshot(config.runtime_root / "reflections")

    assert len(history) == 1
    assert latest is not None
    assert after == before


def test_reflection_task_lookup_works(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _append_completed(config, "TASK-001")
    _append_completed(config, "TASK-002")
    generate_reflection("TASK-001", config, timestamp="2026-05-12T00:00:01+00:00")
    generate_reflection("TASK-002", config, timestamp="2026-05-12T00:00:02+00:00")

    matches = reflections_for_task("TASK-002", config)

    assert len(matches) == 1
    assert matches[0]["source_task_id"] == "TASK-002"


def test_reflection_artifacts_append_only(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _append_completed(config, "TASK-001")
    generate_reflection("TASK-001", config, timestamp="2026-05-12T00:00:01+00:00")
    generate_reflection("TASK-001", config, timestamp="2026-05-12T00:00:02+00:00")

    assert len(reflection_history(config)) == 2
