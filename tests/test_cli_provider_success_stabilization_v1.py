import subprocess
from pathlib import Path

from agol_bridge.providers.codex_cli_provider import run_bounded_codex_cli_task

from aigol.cli.aigol_cli import render_command_result
from aigol.cli.commands.execution import run_execution_handoff
from aigol.cli.commands.ingress import generate_ingress_artifact


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "aigol" / "cli"
PROVIDER = ROOT / "agol_bridge" / "providers" / "codex_cli_provider.py"


def _artifact():
    return generate_ingress_artifact(
        human_request="Run CLI provider success stabilization.",
        semantic_intent="Minimal deterministic provider success proof",
    )


def _task(tmp_path):
    return {
        "task_id": "TASK-CLI-PROVIDER-SUCCESS",
        "codex_prompt": "Run deterministic provider proof.",
        "semantic_contract": {"mode": "PROVIDER_SUCCESS_PROOF"},
        "metadata": {
            "allowed_workspace_root": str(tmp_path),
            "provider_success_proof": True,
            "approved": False,
        },
    }


def test_provider_executable_found(tmp_path):
    result = run_bounded_codex_cli_task(task_package=_task(tmp_path), workspace_path=str(tmp_path), timeout_seconds=10)

    assert result["diagnostic_evidence"]["codex_executable_found"] is True
    assert result["diagnostic_evidence"]["codex_executable"]


def test_provider_command_generated_deterministically(tmp_path):
    first = run_bounded_codex_cli_task(task_package=_task(tmp_path), workspace_path=str(tmp_path), timeout_seconds=10)
    second = run_bounded_codex_cli_task(task_package=_task(tmp_path), workspace_path=str(tmp_path), timeout_seconds=10)

    assert first["command"] == ["codex", "--version"]
    assert second["command"] == ["codex", "--version"]
    assert first["diagnostic_evidence"]["provider_command"] == second["diagnostic_evidence"]["provider_command"]


def test_subprocess_run_reached(monkeypatch, tmp_path):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="codex-cli test\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = run_bounded_codex_cli_task(task_package=_task(tmp_path), workspace_path=str(tmp_path), timeout_seconds=10)

    assert calls[0][0] == ["codex", "--version"]
    assert result["diagnostic_evidence"]["subprocess_invoked"] is True


def test_successful_provider_returns_execution_completed(tmp_path):
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        runtime_root=tmp_path / "runtime",
        timeout_seconds=10,
    )

    assert result["execution_status"] == "EXECUTION_COMPLETED"
    assert result["provider_invoked"] is True


def test_governed_return_generated_on_success(tmp_path):
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        runtime_root=tmp_path / "runtime",
        timeout_seconds=10,
    )

    assert result["governed_return"]["artifact_type"] == "CLI_GOVERNED_RETURN_CONTINUITY_V1"
    assert result["diagnostic_evidence"]["governed_return_generated"] is True


def test_continuity_verified_true_on_success(tmp_path):
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        runtime_root=tmp_path / "runtime",
        timeout_seconds=10,
    )

    assert result["continuity_verified"] is True
    assert result["fail_closed"] is False


def test_provider_stdout_preserved(tmp_path):
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        runtime_root=tmp_path / "runtime",
        timeout_seconds=10,
    )

    assert "codex-cli" in result["diagnostic_evidence"]["provider_stdout"]


def test_provider_stderr_preserved(tmp_path):
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        runtime_root=tmp_path / "runtime",
        timeout_seconds=10,
    )

    assert isinstance(result["diagnostic_evidence"]["provider_stderr"], str)


def test_provider_failure_still_fail_closed(monkeypatch, tmp_path):
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="proof failed")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        runtime_root=tmp_path / "runtime",
        timeout_seconds=10,
    )

    assert result["execution_status"] == "EXECUTION_FAILED"
    assert result["provider_invoked"] is True
    assert result["fail_closed"] is True
    assert result["diagnostic_evidence"]["provider_failure_reason"] == "Codex CLI returned non-zero exit status"


def test_invalid_continuity_still_blocked(tmp_path):
    result = run_execution_handoff(
        ingress_artifact={},
        workspace_path=str(tmp_path),
        runtime_root=tmp_path / "runtime",
        timeout_seconds=10,
    )

    assert result["execution_status"] == "EXECUTION_BLOCKED"
    assert result["provider_invoked"] is False
    assert result["fail_closed"] is True


def test_no_retries_introduced():
    source = "\n".join(
        [
            PROVIDER.read_text(encoding="utf-8").lower(),
            (CLI / "commands" / "execution.py").read_text(encoding="utf-8").lower(),
        ]
    )

    assert "for attempt" not in source
    assert "retry_count\": 1" not in source


def test_no_orchestration_introduced():
    source = "\n".join(path.read_text(encoding="utf-8").lower() for path in CLI.rglob("*.py"))

    assert "orchestrator" not in source
    assert "orchestrationruntime" not in source
    assert "asyncio" not in source


def test_no_alternate_provider_introduced():
    source = PROVIDER.read_text(encoding="utf-8")

    assert "CODEX_EXECUTABLE = \"codex\"" in source
    assert "CODEX_CLI_PROVIDER" in source
    assert "fallback" not in source.lower()
    assert "provider_success_proof" in source


def test_replay_continuity_preserved(tmp_path):
    result = run_execution_handoff(
        ingress_artifact=_artifact(),
        workspace_path=str(tmp_path),
        runtime_root=tmp_path / "runtime",
        timeout_seconds=10,
    )

    assert result["replay_identity"] == result["governed_return"]["replay_identity"]
    assert result["execution_governance_hash"] == result["governed_return"]["execution_governance_hash"]


def test_governed_return_hash_preserved(tmp_path):
    first = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), runtime_root=tmp_path / "runtime", timeout_seconds=10)
    second = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), runtime_root=tmp_path / "runtime", timeout_seconds=10)

    assert first["governed_return_hash"] == second["governed_return_hash"]
    assert first["governed_return"]["governed_return_hash"] == first["governed_return_hash"]


def test_terminal_rendering_includes_success_command(tmp_path):
    result = run_execution_handoff(ingress_artifact=_artifact(), workspace_path=str(tmp_path), runtime_root=tmp_path / "runtime", timeout_seconds=10)
    rendered = render_command_result(result)

    assert "AIGOL EXECUTION RESULT" in rendered
    assert "EXECUTION_COMPLETED" in rendered
    assert "['codex', '--version']" in rendered
    assert "VERIFIED" in rendered
