from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.observability.state_transitions import transition_history
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


def test_transition_history_reconstructs_task_lifecycle(tmp_path: Path) -> None:
    config = _config(tmp_path)
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

    result = transition_history("TASK-001", config)

    assert result == {
        "errors": [],
        "invalid_transition_detected": False,
        "task_id": "TASK-001",
        "transition_count": 4,
        "transitions": ["CREATED", "VALIDATED", "PROCESSING", "COMPLETED"],
    }


def test_invalid_transition_detected(tmp_path: Path) -> None:
    config = _config(tmp_path)
    invalid = replay_entry(
        task_id="TASK-001",
        execution_timestamp="2026-05-12T00:00:00+00:00",
        codex_exit_code=0,
        task_hash="a" * 64,
        result_hash="b" * 64,
        processing_duration_seconds=1.0,
        final_state="COMPLETED",
    )
    invalid["final_state"] = "EXECUTING"
    config.replay_log_path.write_text(json.dumps(invalid, sort_keys=True) + "\n", encoding="utf-8")

    result = transition_history("TASK-001", config)

    assert result["invalid_transition_detected"] is True
    assert result["errors"] == [{"field": "final_state", "reason": "unknown execution state"}]
