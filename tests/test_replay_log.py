from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.transport.replay_log import append_replay_log, replay_entry


def test_replay_log_append_succeeds(tmp_path: Path) -> None:
    log_path = tmp_path / "replay_log.jsonl"
    entry = replay_entry(
        task_id="TASK-001",
        execution_timestamp="2026-05-12T00:00:00+00:00",
        codex_exit_code=0,
        task_hash="a" * 64,
        result_hash="b" * 64,
        processing_duration_seconds=1.2345678,
        final_state="COMPLETED",
    )

    append_replay_log(log_path, entry)
    assert log_path.read_text(encoding="utf-8").count("\n") == 1


def test_replay_log_deterministic_across_runs() -> None:
    first = replay_entry(
        task_id="TASK-001",
        execution_timestamp="2026-05-12T00:00:00+00:00",
        codex_exit_code=0,
        task_hash="a" * 64,
        result_hash="b" * 64,
        processing_duration_seconds=1.2345678,
        final_state="COMPLETED",
    )
    second = replay_entry(
        task_id="TASK-001",
        execution_timestamp="2026-05-12T00:00:00+00:00",
        codex_exit_code=0,
        task_hash="a" * 64,
        result_hash="b" * 64,
        processing_duration_seconds=1.2345678,
        final_state="COMPLETED",
    )
    assert first == second

