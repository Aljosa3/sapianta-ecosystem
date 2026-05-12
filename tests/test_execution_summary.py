from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.observability.execution_summary import execution_summary
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


def test_execution_summary_deterministic(tmp_path: Path) -> None:
    config = _config(tmp_path)
    append_replay_log(
        config.replay_log_path,
        replay_entry(
            task_id="TASK-001",
            execution_timestamp="2026-05-12T00:00:00+00:00",
            codex_exit_code=0,
            task_hash="a" * 64,
            result_hash="b" * 64,
            processing_duration_seconds=2.0,
            final_state="COMPLETED",
        ),
    )
    append_replay_log(
        config.replay_log_path,
        replay_entry(
            task_id="TASK-002",
            execution_timestamp="2026-05-12T00:00:01+00:00",
            codex_exit_code=1,
            task_hash="c" * 64,
            result_hash="d" * 64,
            processing_duration_seconds=4.0,
            final_state="FAILED",
        ),
    )

    first = execution_summary(config)
    second = execution_summary(config)

    assert first == second
    assert first == {
        "average_duration_seconds": 3.0,
        "failed_executions": 1,
        "last_result_state": "FAILED",
        "quarantined_results": 0,
        "successful_executions": 1,
        "total_executions": 2,
    }
