from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from protocol_fixtures import valid_task

from sapianta_bridge.protocol.validator import ValidationResult
from sapianta_bridge.transport.bridge_listener import process_one_task
from sapianta_bridge.transport.codex_runner import CodexExecutionResult
from sapianta_bridge.transport.transport_config import TransportConfig


class FakeRunner:
    def __init__(self, exit_code: int = 0, failed_closed: bool = False) -> None:
        self.exit_code = exit_code
        self.failed_closed = failed_closed
        self.calls = 0

    def run(self, _task: dict) -> CodexExecutionResult:
        self.calls += 1
        return CodexExecutionResult(
            exit_code=self.exit_code,
            stdout="ok",
            stderr="" if self.exit_code == 0 else "failed",
            duration_seconds=0.1,
            failed_closed=self.failed_closed,
            error="failed" if self.exit_code != 0 else None,
        )


def _config(tmp_path: Path) -> TransportConfig:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    config = TransportConfig(
        runtime_root=tmp_path / "runtime",
        workspace=workspace,
        quarantine_root=tmp_path / "quarantine",
    )
    config.ensure_directories()
    return config


def _write_task(config: TransportConfig, task: dict | None = None, name: str = "task.json") -> Path:
    path = config.tasks_dir / name
    path.write_text(json.dumps(task or valid_task(), sort_keys=True), encoding="utf-8")
    return path


def test_valid_result_enters_completed(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _write_task(config)
    runner = FakeRunner(exit_code=0)

    result = process_one_task(config, runner=runner)

    assert result["final_state"] == "COMPLETED"
    assert runner.calls == 1
    assert (config.completed_dir / "task.json").exists()
    assert (config.completed_dir / "result.json").exists()
    assert not list(config.tasks_dir.glob("*.json"))


def test_failed_result_enters_failed(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _write_task(config)

    result = process_one_task(config, runner=FakeRunner(exit_code=1, failed_closed=True))

    assert result["final_state"] == "FAILED"
    assert (config.failed_dir / "task.json").exists()
    assert (config.failed_dir / "result.json").exists()


def test_invalid_task_blocked_before_execution(tmp_path: Path) -> None:
    config = _config(tmp_path)
    task = valid_task()
    del task["task_id"]
    _write_task(config, task)
    runner = FakeRunner(exit_code=0)

    result = process_one_task(config, runner=runner)

    assert result["processed"] is False
    assert runner.calls == 0
    assert (config.failed_dir / "task.json").exists()
    assert list((config.quarantine_root / "malformed").glob("QUARANTINE-*"))


def test_malformed_result_quarantined(monkeypatch, tmp_path: Path) -> None:
    config = _config(tmp_path)
    _write_task(config)

    def fail_result_validation(artifact, artifact_type):
        if artifact_type == "result.json":
            return ValidationResult(False, ({"field": "result", "reason": "forced invalid"},))
        from sapianta_bridge.protocol.validator import validate_artifact as real_validate

        return real_validate(artifact, artifact_type)

    monkeypatch.setattr(
        "sapianta_bridge.transport.bridge_listener.validate_artifact",
        fail_result_validation,
    )
    result = process_one_task(config, runner=FakeRunner(exit_code=0))

    assert result["final_state"] == "FAILED"
    assert (config.failed_dir / "result.json").exists()
    assert list((config.quarantine_root / "malformed").glob("QUARANTINE-*"))


def test_no_recursive_task_generation_occurs(tmp_path: Path) -> None:
    config = _config(tmp_path)
    _write_task(config)

    process_one_task(config, runner=FakeRunner(exit_code=0))

    assert not list(config.tasks_dir.glob("*.json"))
    assert not list(config.processing_dir.glob("*.json"))


def test_replay_log_append_failure_fails_closed(monkeypatch, tmp_path: Path) -> None:
    config = _config(tmp_path)
    _write_task(config)

    def raise_append_failure(*_args, **_kwargs) -> None:
        raise OSError("ledger unavailable")

    monkeypatch.setattr(
        "sapianta_bridge.transport.bridge_listener.append_replay_log",
        raise_append_failure,
    )
    result = process_one_task(config, runner=FakeRunner(exit_code=0))

    assert result["final_state"] == "FAILED"
    assert (config.failed_dir / "task.json").exists()
    assert (config.failed_dir / "result.json").exists()
    assert not (config.completed_dir / "task.json").exists()
