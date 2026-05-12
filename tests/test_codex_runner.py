from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from protocol_fixtures import valid_task

from sapianta_bridge.transport.codex_runner import CodexRunner
from sapianta_bridge.transport.transport_config import TransportConfig


def test_codex_subprocess_timeout_handled_fail_closed(monkeypatch, tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    def raise_timeout(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(cmd=["codex", "exec"], timeout=1)

    monkeypatch.setattr(subprocess, "run", raise_timeout)
    runner = CodexRunner(TransportConfig(workspace=workspace, timeout_seconds=1))

    result = runner.run(valid_task())
    assert result.exit_code == 124
    assert result.timed_out is True
    assert result.failed_closed is True


def test_unknown_subprocess_error_fails_closed(monkeypatch, tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    def raise_error(*_args, **_kwargs):
        raise OSError("missing executable")

    monkeypatch.setattr(subprocess, "run", raise_error)
    runner = CodexRunner(TransportConfig(workspace=workspace))

    result = runner.run(valid_task())
    assert result.exit_code == 125
    assert result.failed_closed is True
    assert result.error == "OSError"


def test_execution_outside_workspace_blocked(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    task = valid_task()
    task["target_paths"] = [str(tmp_path.parent / "outside")]
    runner = CodexRunner(TransportConfig(workspace=workspace))

    result = runner.run(task)
    assert result.exit_code == 126
    assert result.failed_closed is True

