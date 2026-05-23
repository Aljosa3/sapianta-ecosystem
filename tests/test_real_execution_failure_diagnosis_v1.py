import subprocess
from pathlib import Path

from agol_bridge.native.native_messaging_host import (
    NATIVE_BRIDGE_ACCEPTED,
    NATIVE_BRIDGE_REJECTED,
    handle_native_message,
)
from agol_bridge.providers.codex_cli_provider import (
    STATUS_COMPLETED,
    STATUS_FAILED,
    run_bounded_codex_cli_task,
)


ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT / "agol_bridge" / "native" / "native_messaging_host.py"
SERVICE_WORKER = ROOT / "browser_companion" / "service_worker.js"


def _message(tmp_path):
    return {
        "action": "RUN_MINIMAL_END_TO_END_BRIDGE",
        "request_id": "REAL-EXECUTION-DIAGNOSIS-REQUEST",
        "human_request": "Review real execution diagnosis continuity.",
        "session_id": "SESSION-REAL-EXECUTION-DIAGNOSIS",
        "workspace_path": str(tmp_path),
        "timeout_seconds": 30,
        "operator_triggered": True,
        "authority_boundary": "SEMANTIC_TRANSPORT_ONLY",
    }


def _task(tmp_path):
    return {
        "task_id": "BRIDGE-TASK-DIAGNOSIS",
        "governance_mode": "governed_execution_bridge",
        "risk_class": "LOW",
        "approval_required": False,
        "codex_prompt": "Inspect the bounded request and return a concise summary.",
        "constraints": ["no autonomous continuation", "no hidden retries"],
        "expected_outputs": ["summary"],
        "metadata": {
            "session_id": "SESSION-REAL-EXECUTION-DIAGNOSIS",
            "proposal_id": "PROPOSAL-DIAGNOSIS",
            "approved": False,
            "allowed_workspace_root": str(tmp_path),
        },
    }


def test_native_host_script_bootstraps_when_launched_directly():
    result = subprocess.run(
        ["python", str(HOST)],
        cwd=str(ROOT),
        input=b"",
        capture_output=True,
        timeout=5,
        check=False,
    )

    assert result.returncode == 0
    assert b"ModuleNotFoundError" not in result.stderr


def test_native_messaging_response_continuity_contains_diagnostics(monkeypatch, tmp_path):
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="diagnostic complete", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    response = handle_native_message(_message(tmp_path))

    assert response["status"] == NATIVE_BRIDGE_ACCEPTED
    assert response["diagnostic_evidence"]["python_runtime_bridge_called"] is True
    assert response["diagnostic_evidence"]["provider_invoked"] is True
    assert response["diagnostic_evidence"]["subprocess_invoked"] is True
    assert response["diagnostic_evidence"]["response_serialization_ready"] is True


def test_provider_invocation_continuity_records_subprocess(monkeypatch, tmp_path):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="provider complete", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_bounded_codex_cli_task(task_package=_task(tmp_path), workspace_path=str(tmp_path), timeout_seconds=30)

    assert result["status"] == STATUS_COMPLETED
    assert result["diagnostic_evidence"]["provider_invoked"] is True
    assert result["diagnostic_evidence"]["subprocess_invoked"] is True
    assert result["diagnostic_evidence"]["subprocess_returncode"] == 0
    assert len(calls) == 1


def test_subprocess_failure_is_diagnostic_and_fail_closed(monkeypatch, tmp_path):
    def fake_run(command, **kwargs):
        raise FileNotFoundError("codex executable not found")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_bounded_codex_cli_task(task_package=_task(tmp_path), workspace_path=str(tmp_path), timeout_seconds=30)

    assert result["status"] == STATUS_FAILED
    assert result["diagnostic_evidence"]["failing_layer"] == "bounded_codex_cli_subprocess"
    assert result["diagnostic_evidence"]["failing_function"] == "subprocess.run"
    assert result["diagnostic_evidence"]["provider_invoked"] is True
    assert result["diagnostic_evidence"]["subprocess_invoked"] is True
    assert result["retry_count"] == 0


def test_native_validation_failure_preserves_fail_closed_diagnostics():
    response = handle_native_message({"action": "RUN_MINIMAL_END_TO_END_BRIDGE", "human_request": ""})

    assert response["status"] == NATIVE_BRIDGE_REJECTED
    assert response["diagnostic_evidence"]["failing_layer"] == "native_message_validation"
    assert response["diagnostic_evidence"]["python_runtime_bridge_called"] is False
    assert response["diagnostic_evidence"]["provider_invoked"] is False


def test_service_worker_response_handling_has_diagnostic_evidence():
    source = SERVICE_WORKER.read_text(encoding="utf-8")
    assert "diagnostic_evidence" in source
    assert "service_worker_native_bridge_response_handling" in source
    assert "provider_invoked" in source
    assert "subprocess_invoked" in source
