from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.observability.replay_reader import (
    ReplayEvidenceError,
    find_by_task_id,
    latest_execution,
    read_replay_entries,
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


def _entry(task_id: str, final_state: str = "COMPLETED") -> dict:
    return replay_entry(
        task_id=task_id,
        execution_timestamp=f"2026-05-12T00:00:0{task_id[-1]}+00:00",
        codex_exit_code=0 if final_state == "COMPLETED" else 1,
        task_hash="a" * 64,
        result_hash="b" * 64,
        processing_duration_seconds=1.5,
        final_state=final_state,
    )


def test_replay_reader_reads_latest_execution(tmp_path: Path) -> None:
    config = _config(tmp_path)
    append_replay_log(config.replay_log_path, _entry("TASK-001"))
    append_replay_log(config.replay_log_path, _entry("TASK-002", final_state="FAILED"))

    latest = latest_execution(config)

    assert latest is not None
    assert latest["task_id"] == "TASK-002"
    assert latest["final_state"] == "FAILED"


def test_replay_lookup_by_task_id_works(tmp_path: Path) -> None:
    config = _config(tmp_path)
    append_replay_log(config.replay_log_path, _entry("TASK-001"))
    append_replay_log(config.replay_log_path, _entry("TASK-002"))

    matches = find_by_task_id("TASK-001", config)

    assert len(matches) == 1
    assert matches[0]["task_id"] == "TASK-001"


def test_malformed_replay_evidence_fails_closed(tmp_path: Path) -> None:
    log_path = tmp_path / "replay_log.jsonl"
    log_path.write_text("{malformed\n", encoding="utf-8")

    with pytest.raises(ReplayEvidenceError) as exc_info:
        read_replay_entries(log_path)

    assert exc_info.value.field == "line_1"


def test_replay_log_treated_as_append_only(tmp_path: Path) -> None:
    config = _config(tmp_path)
    append_replay_log(config.replay_log_path, _entry("TASK-001"))
    before = config.replay_log_path.read_text(encoding="utf-8")

    read_replay_entries(config.replay_log_path)
    after = config.replay_log_path.read_text(encoding="utf-8")

    assert after == before


def test_unknown_execution_state_rejected(tmp_path: Path) -> None:
    log_path = tmp_path / "replay_log.jsonl"
    invalid = _entry("TASK-001")
    invalid["final_state"] = "UNKNOWN"
    log_path.write_text(json.dumps(invalid, sort_keys=True) + "\n", encoding="utf-8")

    with pytest.raises(ReplayEvidenceError) as exc_info:
        read_replay_entries(log_path)

    assert exc_info.value.to_dict() == {
        "field": "final_state",
        "reason": "unknown execution state",
    }
