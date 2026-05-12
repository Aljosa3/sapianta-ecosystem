from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.observability.runtime_status import runtime_status
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


def test_runtime_status_snapshot_deterministic(tmp_path: Path) -> None:
    config = _config(tmp_path)
    (config.tasks_dir / "task.json").write_text("{}", encoding="utf-8")
    (config.processing_dir / ".bridge.lock").write_text("locked", encoding="utf-8")
    quarantine_record = config.quarantine_root / "malformed" / "QUARANTINE-001"
    quarantine_record.mkdir(parents=True)
    (quarantine_record / "quarantine.json").write_text(
        json.dumps({"quarantine_id": "QUARANTINE-001"}),
        encoding="utf-8",
    )
    append_replay_log(
        config.replay_log_path,
        replay_entry(
            task_id="TASK-001",
            execution_timestamp="2026-05-12T00:00:00+00:00",
            codex_exit_code=0,
            task_hash="a" * 64,
            result_hash="b" * 64,
            processing_duration_seconds=1.0,
            final_state="COMPLETED",
        ),
    )

    first = runtime_status(config)
    second = runtime_status(config)

    assert first == second
    assert first == {
        "active_lock_present": True,
        "completed_tasks": 0,
        "failed_tasks": 0,
        "last_execution_timestamp": "2026-05-12T00:00:00+00:00",
        "processing_tasks": 0,
        "quarantined_artifacts": 1,
        "queue_depth": 1,
        "replay_log_present": True,
        "transport_active": True,
    }
