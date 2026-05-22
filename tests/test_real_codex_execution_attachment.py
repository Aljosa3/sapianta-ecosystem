import subprocess

from agol_bridge.native.native_messaging_host import (
    NATIVE_BRIDGE_ACCEPTED,
    handle_native_message,
)
from agol_bridge.runtime.minimal_end_to_end_bridge import (
    BRIDGE_ACCEPTED,
    RESULT_VALIDATED,
    export_minimal_bridge_result_artifact,
    run_minimal_end_to_end_bridge,
)


def _fake_codex_completed(monkeypatch):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="bounded codex complete", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


def test_runtime_invokes_real_bounded_codex_provider(monkeypatch, tmp_path):
    calls = _fake_codex_completed(monkeypatch)

    result = run_minimal_end_to_end_bridge(
        human_request="Review this change with the governed bridge.",
        session_id="SESSION-REAL-CODEX-1",
        workspace_path=str(tmp_path),
        timeout_seconds=30,
    )

    assert result["status"] == BRIDGE_ACCEPTED
    assert result["codex_cli_result"]["bounded_execution_status"] == "COMPLETED"
    assert result["result_validation"]["status"] == RESULT_VALIDATED
    assert result["result_validation"]["valid"] is True
    assert len(calls) == 1
    command, kwargs = calls[0]
    assert command[0:2] == ["codex", "exec"]
    assert "AGOL Bridge bounded Codex CLI task" in command[2]
    assert kwargs["cwd"] == str(tmp_path.resolve())
    assert kwargs["timeout"] == 30


def test_native_messaging_path_returns_real_codex_artifact(monkeypatch, tmp_path):
    calls = _fake_codex_completed(monkeypatch)

    response = handle_native_message(
        {
            "action": "RUN_MINIMAL_END_TO_END_BRIDGE",
            "request_id": "REQ-1",
            "human_request": "Review this through the native bridge.",
            "session_id": "SESSION-REAL-CODEX-2",
            "workspace_path": str(tmp_path),
            "timeout_seconds": 30,
            "operator_triggered": True,
            "authority_boundary": "SEMANTIC_TRANSPORT_ONLY",
        }
    )

    assert response["status"] == NATIVE_BRIDGE_ACCEPTED
    assert len(calls) == 1
    artifact = response["result_artifact"]
    assert artifact["codex_cli_result"]["bounded_execution_status"] == "COMPLETED"
    assert "REAL_CODEX_EXECUTION" in response["labels"]
    assert "BOUNDED_CODEX_CLI_PROVIDER" in response["labels"]


def test_timeout_flows_through_validation_and_governed_return(monkeypatch, tmp_path):
    def fake_run(command, **kwargs):
        raise subprocess.TimeoutExpired(cmd=command, timeout=1, output="partial", stderr="timed out")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_minimal_end_to_end_bridge(
        human_request="Review this with timeout visibility.",
        session_id="SESSION-REAL-CODEX-3",
        workspace_path=str(tmp_path),
        timeout_seconds=1,
    )

    assert result["status"] == BRIDGE_ACCEPTED
    assert result["codex_cli_result"]["bounded_execution_status"] == "TIMEOUT"
    assert result["governed_chat_return"]["execution_status"] == "EXECUTION_TIMEOUT"
    assert result["governed_chat_return"]["workspace_path"] == str(tmp_path.resolve())
    assert result["result_validation"]["valid"] is True


def test_failed_execution_flows_through_governed_return(monkeypatch, tmp_path):
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 7, stdout="", stderr="failure")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_minimal_end_to_end_bridge(
        human_request="Review failed provider visibility.",
        session_id="SESSION-REAL-CODEX-4",
        workspace_path=str(tmp_path),
    )

    assert result["status"] == BRIDGE_ACCEPTED
    assert result["codex_cli_result"]["bounded_execution_status"] == "FAILED"
    assert result["governed_chat_return"]["execution_status"] == "EXECUTION_FAILED"
    assert result["result_validation"]["valid"] is True


def test_provider_rejection_is_visible_without_mocking_execution(tmp_path):
    missing_workspace = tmp_path / "missing"

    result = run_minimal_end_to_end_bridge(
        human_request="Review rejected provider visibility.",
        session_id="SESSION-REAL-CODEX-5",
        workspace_path=str(missing_workspace),
    )

    assert result["status"] == BRIDGE_ACCEPTED
    assert result["codex_cli_result"]["bounded_execution_status"] == "REJECTED"
    assert result["governed_chat_return"]["execution_status"] == "EXECUTION_REJECTED"
    assert result["result_validation"]["valid"] is True


def test_canonical_artifact_contains_real_codex_result(monkeypatch, tmp_path):
    _fake_codex_completed(monkeypatch)
    result = run_minimal_end_to_end_bridge(
        human_request="Review artifact export.",
        session_id="SESSION-REAL-CODEX-6",
        workspace_path=str(tmp_path),
    )

    artifact = export_minimal_bridge_result_artifact(result)

    assert "codex_cli_result" in artifact
    assert "mock_codex_result" not in artifact
    assert artifact["codex_cli_result"]["provider_result"]["provider"] == "CODEX_CLI"
    assert artifact["governed_chat_return"]["bounded_execution_status"] == "COMPLETED"


def test_no_mock_execution_path_remaining_in_python_runtime():
    source = open("agol_bridge/runtime/minimal_end_to_end_bridge.py", encoding="utf-8").read()

    assert "_mock_codex_result" not in source
    assert "MOCK_CODEX_RESULT_CREATED" not in source
    assert "MOCK_CODEX_RESULT_RETURNED" not in source
    assert "run_bounded_codex_cli_task" in source


def test_no_autonomous_continuation_or_retry(monkeypatch, tmp_path):
    calls = _fake_codex_completed(monkeypatch)

    result = run_minimal_end_to_end_bridge(
        human_request="Review authority boundaries.",
        session_id="SESSION-REAL-CODEX-7",
        workspace_path=str(tmp_path),
    )

    provider_result = result["codex_cli_result"]["provider_result"]
    assert len(calls) == 1
    assert provider_result["retry_count"] == 0
    assert provider_result["execution_boundary"]["auto_continue"] is False
    assert provider_result["execution_boundary"]["silent_retry"] is False
    assert result["codex_cli_result"]["autonomous_continuation_created"] is False
