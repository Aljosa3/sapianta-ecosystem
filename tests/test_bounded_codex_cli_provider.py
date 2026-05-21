import copy
import subprocess

from agol_bridge.providers.codex_cli_provider import (
    CODEX_CLI_PROVIDER,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_REJECTED,
    STATUS_TIMEOUT,
    build_bounded_codex_prompt,
    run_bounded_codex_cli_task,
)


def _task(tmp_path):
    return {
        "task_id": "BRIDGE-TASK-1",
        "governance_mode": "governed_execution_bridge",
        "risk_class": "LOW",
        "approval_required": False,
        "codex_prompt": "Inspect the bounded request and return a concise summary.",
        "constraints": ["no autonomous continuation", "no hidden retries"],
        "expected_outputs": ["summary"],
        "metadata": {
            "session_id": "SESSION-1",
            "proposal_id": "PROPOSAL-1",
            "approved": False,
            "allowed_workspace_root": str(tmp_path),
        },
    }


def test_rejects_missing_task_package(tmp_path):
    result = run_bounded_codex_cli_task(task_package={}, workspace_path=str(tmp_path))

    assert result["status"] == STATUS_REJECTED
    assert result["provider"] == CODEX_CLI_PROVIDER
    assert "task_package" in result["errors"][0]


def test_rejects_package_without_codex_prompt(tmp_path):
    task = _task(tmp_path)
    del task["codex_prompt"]

    result = run_bounded_codex_cli_task(task_package=task, workspace_path=str(tmp_path))

    assert result["status"] == STATUS_REJECTED
    assert "codex_prompt" in result["errors"][0]


def test_rejects_invalid_workspace(tmp_path):
    task = _task(tmp_path)
    outside = tmp_path / "missing"

    result = run_bounded_codex_cli_task(task_package=task, workspace_path=str(outside))

    assert result["status"] == STATUS_REJECTED
    assert "workspace_path" in result["errors"][0]


def test_rejects_workspace_outside_allowed_root(tmp_path):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    task = _task(allowed)

    result = run_bounded_codex_cli_task(task_package=task, workspace_path=str(outside))

    assert result["status"] == STATUS_REJECTED
    assert result["errors"] == ["workspace_path is outside allowed root"]


def test_builds_bounded_prompt_deterministically(tmp_path):
    task = _task(tmp_path)

    first = build_bounded_codex_prompt(task_package=task)
    second = build_bounded_codex_prompt(task_package=task)

    assert first == second
    assert "AGOL Bridge bounded Codex CLI task" in first
    assert "Do not approve, dispatch, retry, orchestrate, or continue autonomously." in first
    assert "AIGOL_CODEX_TASK_COMPLETE" in first
    assert task["task_id"] in first


def test_invokes_subprocess_with_codex_command_mocked(monkeypatch, tmp_path):
    calls = []
    task = _task(tmp_path)

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="done", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_bounded_codex_cli_task(task_package=task, workspace_path=str(tmp_path), timeout_seconds=30)

    assert result["status"] == STATUS_COMPLETED
    assert result["stdout"] == "done"
    assert result["stderr"] == ""
    assert result["returncode"] == 0
    assert result["task_package_id"] == task["task_id"]
    assert result["command"] == ["codex", "exec", "<bounded_prompt>"]
    assert len(calls) == 1
    command, kwargs = calls[0]
    assert command[0:2] == ["codex", "exec"]
    assert "AGOL Bridge bounded Codex CLI task" in command[2]
    assert kwargs["cwd"] == str(tmp_path.resolve())
    assert kwargs["input"] == ""
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True
    assert kwargs["timeout"] == 30
    assert kwargs["check"] is False


def test_captures_stdout_stderr_and_failure(monkeypatch, tmp_path):
    task = _task(tmp_path)

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 2, stdout="partial", stderr="failed")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_bounded_codex_cli_task(task_package=task, workspace_path=str(tmp_path))

    assert result["status"] == STATUS_FAILED
    assert result["stdout"] == "partial"
    assert result["stderr"] == "failed"
    assert result["returncode"] == 2
    assert result["errors"] == ["Codex CLI returned non-zero exit status"]


def test_handles_timeout_without_retry(monkeypatch, tmp_path):
    calls = []
    task = _task(tmp_path)

    def fake_run(command, **kwargs):
        calls.append(command)
        raise subprocess.TimeoutExpired(cmd=command, timeout=1, output="out", stderr="err")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_bounded_codex_cli_task(task_package=task, workspace_path=str(tmp_path), timeout_seconds=1)

    assert result["status"] == STATUS_TIMEOUT
    assert result["stdout"] == "out"
    assert result["stderr"] == "err"
    assert result["returncode"] is None
    assert result["retry_count"] == 0
    assert len(calls) == 1


def test_no_autonomous_retry(monkeypatch, tmp_path):
    calls = []
    task = _task(tmp_path)

    def fake_run(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="nope")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_bounded_codex_cli_task(task_package=task, workspace_path=str(tmp_path))

    assert result["status"] == STATUS_FAILED
    assert result["retry_count"] == 0
    assert len(calls) == 1
    assert result["execution_boundary"]["silent_retry"] is False
    assert result["execution_boundary"]["orchestration"] is False


def test_deterministic_result_package(monkeypatch, tmp_path):
    task = _task(tmp_path)

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="same", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    first = run_bounded_codex_cli_task(task_package=task, workspace_path=str(tmp_path), timeout_seconds=30)
    second = run_bounded_codex_cli_task(task_package=task, workspace_path=str(tmp_path), timeout_seconds=30)

    assert first == second


def test_no_provider_call_without_governed_package(monkeypatch, tmp_path):
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="bad", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_bounded_codex_cli_task(task_package={"task_id": "TASK-1"}, workspace_path=str(tmp_path))

    assert result["status"] == STATUS_REJECTED
    assert calls == []


def test_does_not_mutate_task_package(monkeypatch, tmp_path):
    task = _task(tmp_path)
    original = copy.deepcopy(task)

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="done", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    run_bounded_codex_cli_task(task_package=task, workspace_path=str(tmp_path))

    assert task == original


def test_authority_guarantees_are_explicit(monkeypatch, tmp_path):
    task = _task(tmp_path)

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="done", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_bounded_codex_cli_task(task_package=task, workspace_path=str(tmp_path))

    assert "NO_AUTO_APPROVAL" in result["non_authority_guarantees"]
    assert "NO_AUTO_CONTINUATION" in result["non_authority_guarantees"]
    assert "NO_SILENT_RETRY" in result["non_authority_guarantees"]
    assert result["execution_boundary"]["contract"] == "codex exec <bounded_prompt>"
    assert result["execution_boundary"]["auto_approval"] is False
