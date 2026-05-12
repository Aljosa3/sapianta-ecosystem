from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.reflection import reflection_cli
from sapianta_bridge.reflection.reflection_engine import generate_reflection
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


def _append_completed(config: TransportConfig, task_id: str = "TASK-001") -> None:
    append_replay_log(
        config.replay_log_path,
        replay_entry(
            task_id=task_id,
            execution_timestamp="2026-05-12T00:00:00+00:00",
            codex_exit_code=0,
            task_hash="a" * 64,
            result_hash="b" * 64,
            processing_duration_seconds=1.0,
            final_state="COMPLETED",
        ),
    )


def test_cli_latest_command_works(tmp_path: Path, capsys) -> None:
    config = _config(tmp_path)
    _append_completed(config)
    generate_reflection("TASK-001", config, timestamp="2026-05-12T00:00:01+00:00")

    exit_code = reflection_cli.main(_args(config, "latest"))
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["source_task_id"] == "TASK-001"


def test_cli_summary_command_works(tmp_path: Path, capsys) -> None:
    config = _config(tmp_path)
    _append_completed(config)
    generate_reflection("TASK-001", config, timestamp="2026-05-12T00:00:01+00:00")

    exit_code = reflection_cli.main(_args(config, "summary"))
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["total_reflections"] == 1
    assert output["allowed_to_execute_automatically"] is False


def test_cli_task_lookup_works(tmp_path: Path, capsys) -> None:
    config = _config(tmp_path)
    _append_completed(config)
    generate_reflection("TASK-001", config, timestamp="2026-05-12T00:00:01+00:00")

    exit_code = reflection_cli.main(_args(config, "task", "--task-id", "TASK-001"))
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert len(output) == 1
    assert output[0]["source_task_id"] == "TASK-001"


def test_cli_generate_creates_reflection_artifact_only(tmp_path: Path, capsys) -> None:
    config = _config(tmp_path)
    _append_completed(config)
    before_tasks = sorted(config.tasks_dir.glob("*"))

    exit_code = reflection_cli.main(
        _args(
            config,
            "generate",
            "--task-id",
            "TASK-001",
            "--timestamp",
            "2026-05-12T00:00:01+00:00",
        )
    )
    output = json.loads(capsys.readouterr().out)
    after_tasks = sorted(config.tasks_dir.glob("*"))

    assert exit_code == 0
    assert output["created"] is True
    assert after_tasks == before_tasks
    assert len(list((config.runtime_root / "reflections").glob("*.json"))) == 1
