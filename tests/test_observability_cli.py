from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.observability import observability_cli
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


def _args(config: TransportConfig, *command: str) -> list[str]:
    return [
        "--runtime-root",
        str(config.runtime_root),
        "--quarantine-root",
        str(config.quarantine_root),
        *command,
    ]


def _append_entry(config: TransportConfig) -> None:
    append_replay_log(
        config.replay_log_path,
        replay_entry(
            task_id="TASK-001",
            execution_timestamp="2026-05-12T00:00:00+00:00",
            codex_exit_code=0,
            task_hash="a" * 64,
            result_hash="b" * 64,
            processing_duration_seconds=1.25,
            final_state="COMPLETED",
        ),
    )


def test_cli_status_command_works(tmp_path: Path, capsys) -> None:
    config = _config(tmp_path)

    exit_code = observability_cli.main(_args(config, "status"))
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["transport_active"] is True
    assert output["queue_depth"] == 0


def test_cli_replay_command_works(tmp_path: Path, capsys) -> None:
    config = _config(tmp_path)
    _append_entry(config)

    exit_code = observability_cli.main(_args(config, "replay", "--latest"))
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output == {
        "duration_seconds": 1.25,
        "exit_code": 0,
        "final_state": "COMPLETED",
        "task_id": "TASK-001",
        "timestamp": "2026-05-12T00:00:00+00:00",
    }


def test_cli_summary_command_works(tmp_path: Path, capsys) -> None:
    config = _config(tmp_path)
    _append_entry(config)

    exit_code = observability_cli.main(_args(config, "summary"))
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["total_executions"] == 1
    assert output["last_result_state"] == "COMPLETED"


def test_observability_layer_never_mutates_runtime(tmp_path: Path, capsys) -> None:
    config = _config(tmp_path)
    _append_entry(config)
    before = {
        str(path.relative_to(config.runtime_root)): path.read_text(encoding="utf-8")
        for path in sorted(config.runtime_root.rglob("*"))
        if path.is_file()
    }

    assert observability_cli.main(_args(config, "status")) == 0
    assert observability_cli.main(_args(config, "queue")) == 0
    assert observability_cli.main(_args(config, "summary")) == 0
    capsys.readouterr()
    after = {
        str(path.relative_to(config.runtime_root)): path.read_text(encoding="utf-8")
        for path in sorted(config.runtime_root.rglob("*"))
        if path.is_file()
    }

    assert after == before
