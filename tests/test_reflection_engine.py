from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.reflection.reflection_engine import (
    build_reflection_artifact,
    generate_reflection,
)
from sapianta_bridge.reflection.reflection_models import ReflectionError
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
    (config.runtime_root / "reflections").mkdir()
    return config


def _append_completed(config: TransportConfig, task_id: str = "TASK-001") -> None:
    append_replay_log(
        config.replay_log_path,
        replay_entry(
            task_id=task_id,
            execution_timestamp="2026-05-12T00:00:00+00:00",
            codex_exit_code=0,
            task_hash="a" * 64,
            result_hash="b" * 64,
            processing_duration_seconds=4.2,
            final_state="COMPLETED",
        ),
    )


def test_reflection_artifact_generation_deterministic(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _append_completed(config)
    timestamp = "2026-05-12T00:00:01+00:00"

    first = build_reflection_artifact("TASK-001", config, timestamp=timestamp)
    second = build_reflection_artifact("TASK-001", config, timestamp=timestamp)

    assert first == second
    assert first["advisory_only"] is True
    assert first["allowed_to_execute_automatically"] is False
    assert first["execution_outcome"] == {
        "duration_seconds": 4.2,
        "exit_code": 0,
        "final_state": "COMPLETED",
    }


def test_reflection_derived_only_from_replay_evidence(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _append_completed(config)
    (config.tasks_dir / "unrelated-task.json").write_text("{}", encoding="utf-8")

    first = build_reflection_artifact(
        "TASK-001",
        config,
        timestamp="2026-05-12T00:00:01+00:00",
    )
    (config.tasks_dir / "another-unrelated-task.json").write_text("{}", encoding="utf-8")
    second = build_reflection_artifact(
        "TASK-001",
        config,
        timestamp="2026-05-12T00:00:01+00:00",
    )

    assert first["execution_outcome"] == second["execution_outcome"]
    assert first["capability_delta"] == second["capability_delta"]
    assert first["governance_risk"] == second["governance_risk"]


def test_malformed_replay_evidence_fails_closed(tmp_path: Path) -> None:
    config = _config(tmp_path)
    config.replay_log_path.write_text("{malformed\n", encoding="utf-8")

    with pytest.raises(ReflectionError) as exc_info:
        generate_reflection("TASK-001", config, timestamp="2026-05-12T00:00:01+00:00")

    assert exc_info.value.field == "line_1"


def test_generate_command_creates_reflection_artifact_only(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _append_completed(config)
    before_tasks = sorted(path.name for path in config.tasks_dir.glob("*"))

    result = generate_reflection("TASK-001", config, timestamp="2026-05-12T00:00:01+00:00")
    after_tasks = sorted(path.name for path in config.tasks_dir.glob("*"))

    assert result["created"] is True
    assert Path(result["reflection_path"]).parent == config.runtime_root / "reflections"
    assert after_tasks == before_tasks
    assert sorted(path.name for path in config.processing_dir.glob("*.json")) == []


def test_no_execution_authority_introduced(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _append_completed(config)

    artifact = build_reflection_artifact(
        "TASK-001",
        config,
        timestamp="2026-05-12T00:00:01+00:00",
    )

    assert artifact["allowed_to_execute_automatically"] is False
    assert all(
        proposal["allowed_to_execute_automatically"] is False
        for proposal in artifact["advisory_proposals"]
    )


def test_no_task_creation_introduced(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _append_completed(config)

    generate_reflection("TASK-001", config, timestamp="2026-05-12T00:00:01+00:00")

    assert list(config.tasks_dir.glob("*.json")) == []
