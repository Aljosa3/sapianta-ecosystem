import json
import os
import subprocess
from pathlib import Path

from agol_bridge.chatgpt_ingress import create_chatgpt_ingress_artifact
from agol_bridge.chatgpt_ingress.controlled_execution_continuity_preview import create_controlled_execution_continuity_preview
from agol_bridge.chatgpt_ingress.controlled_execution_handoff import (
    EXECUTION_BLOCKED,
    EXECUTION_COMPLETED,
    EXECUTION_FAILED,
    create_controlled_execution_handoff,
)
from agol_bridge.chatgpt_ingress.explicit_dispatch_authorization import create_explicit_dispatch_authorization
from agol_bridge.chatgpt_ingress.governed_handoff_package_preview import create_governed_handoff_package_preview
from agol_bridge.chatgpt_ingress.governed_task_package_preview import create_governed_task_package_preview
from agol_bridge.chatgpt_ingress.human_approval_gate import create_human_approval_gate
from agol_bridge.native.native_messaging_host import (
    NATIVE_BRIDGE_ACCEPTED,
    handle_native_message,
    write_native_message,
)


ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT / "agol_bridge" / "native" / "native_messaging_host.py"
SERVICE_WORKER = ROOT / "browser_companion" / "service_worker.js"
SIDEPANEL = ROOT / "browser_companion" / "sidepanel.js"


def _artifact():
    return create_chatgpt_ingress_artifact(
        created_at="1970-01-01T00:00:00Z",
        session_id="CHATGPT-REAL-PROVIDER-STABILIZATION",
        human_request="Stabilize real provider invocation.",
        chatgpt_semantic_output="The request asks to reach bounded Codex provider invocation.",
        normalized_intent="REAL_PROVIDER_INVOCATION_STABILIZATION",
        expected_artifacts=["real provider invocation evidence"],
        constraints=["single path", "single provider", "fail closed"],
        forbidden_operations=["orchestration", "retry", "autonomous continuation"],
        provenance={"source_conversation_id": "CONV-REAL-PROVIDER-STABILIZATION"},
    )


def _continuity_preview():
    task = create_governed_task_package_preview(_artifact())
    approval = create_human_approval_gate(
        preview=task,
        human_decision="APPROVE",
        approval_reason="Operator approved provider invocation stabilization.",
        operator_label="TEST_OPERATOR",
        created_at="1970-01-01T00:00:00Z",
    )
    handoff = create_governed_handoff_package_preview(task_package_preview=task, human_approval=approval)
    authorization = create_explicit_dispatch_authorization(
        handoff_preview=handoff,
        dispatch_decision="AUTHORIZE",
        dispatch_authorization_reason="Operator authorized provider invocation stabilization.",
    )
    return create_controlled_execution_continuity_preview(dispatch_authorization=authorization)


def _native_message(tmp_path):
    return {
        "action": "RUN_MINIMAL_END_TO_END_BRIDGE",
        "request_id": "REAL-PROVIDER-STABILIZATION-REQUEST",
        "human_request": "Reach bounded Codex CLI provider invocation.",
        "session_id": "SESSION-REAL-PROVIDER-STABILIZATION",
        "workspace_path": str(tmp_path),
        "timeout_seconds": 30,
        "operator_triggered": True,
        "authority_boundary": "SEMANTIC_TRANSPORT_ONLY",
    }


def test_native_messaging_response_reports_python_bridge_diagnostics(monkeypatch, tmp_path):
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="provider reached", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    response = handle_native_message(_native_message(tmp_path))

    assert response["status"] == NATIVE_BRIDGE_ACCEPTED
    assert response["diagnostic_evidence"]["python_runtime_bridge_called"] is True
    assert response["diagnostic_evidence"]["provider_invoked"] is True


def test_python_runtime_bridge_reaches_controlled_execution_handoff(monkeypatch, tmp_path):
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="handoff complete", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    artifact = create_controlled_execution_handoff(
        continuity_preview=_continuity_preview(),
        workspace_path=str(tmp_path),
        timeout_seconds=30,
    )

    assert artifact["execution_status"] == EXECUTION_COMPLETED
    assert artifact["native_response"]["diagnostic_evidence"]["python_runtime_bridge_called"] is True


def test_controlled_execution_handoff_reaches_bounded_provider_invocation(monkeypatch, tmp_path):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="bounded provider complete", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    artifact = create_controlled_execution_handoff(
        continuity_preview=_continuity_preview(),
        workspace_path=str(tmp_path),
        timeout_seconds=30,
    )

    assert artifact["provider_invoked"] is True
    assert artifact["codex_dispatch_performed"] is True
    assert calls[0][0][0:2] == ["codex", "exec"]


def test_provider_invoked_becomes_true_when_provider_call_is_attempted(monkeypatch, tmp_path):
    def fake_run(command, **kwargs):
        raise FileNotFoundError("codex executable not found")

    monkeypatch.setattr(subprocess, "run", fake_run)

    artifact = create_controlled_execution_handoff(
        continuity_preview=_continuity_preview(),
        workspace_path=str(tmp_path),
        timeout_seconds=30,
    )

    assert artifact["execution_status"] == EXECUTION_FAILED
    assert artifact["provider_invoked"] is True
    provider = artifact["native_response"]["result_artifact"]["codex_cli_result"]["provider_result"]
    assert provider["diagnostic_evidence"]["subprocess_invoked"] is True


def test_codex_missing_produces_execution_failed_but_provider_invoked_true(monkeypatch, tmp_path):
    def fake_run(command, **kwargs):
        raise FileNotFoundError("codex executable not found")

    monkeypatch.setattr(subprocess, "run", fake_run)

    artifact = create_controlled_execution_handoff(
        continuity_preview=_continuity_preview(),
        workspace_path=str(tmp_path),
        timeout_seconds=30,
    )

    assert artifact["execution_status"] == EXECUTION_FAILED
    assert artifact["provider_invoked"] is True
    assert artifact["execution_result_summary"]["provider_status"] == "FAILED"


def test_codex_subprocess_success_produces_execution_completed(monkeypatch, tmp_path):
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="success", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    artifact = create_controlled_execution_handoff(
        continuity_preview=_continuity_preview(),
        workspace_path=str(tmp_path),
        timeout_seconds=30,
    )

    assert artifact["execution_status"] == EXECUTION_COMPLETED
    assert artifact["provider_invoked"] is True


def test_response_serialization_returns_result_artifact_to_service_worker(monkeypatch, tmp_path):
    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="serialized", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    response = handle_native_message(_native_message(tmp_path))

    output = Path(tmp_path) / "native_response.bin"
    with output.open("wb") as stream:
        write_native_message(stream, response)

    raw = output.read_bytes()
    payload = json.loads(raw[4:].decode("utf-8"))
    assert payload["status"] == NATIVE_BRIDGE_ACCEPTED
    assert payload["result_artifact"]["codex_cli_result"]["provider_invoked"] is True


def test_service_worker_normalizes_provider_diagnostics():
    source = SERVICE_WORKER.read_text(encoding="utf-8")
    assert "python_runtime_bridge_called" in source
    assert "provider_invoked" in source
    assert "subprocess_invoked" in source
    assert "response_serialization_ready" in source


def test_sidepanel_renders_provider_invoked_true():
    source = SIDEPANEL.read_text(encoding="utf-8")
    assert "`provider_invoked: ${summary.provider_invoked}`" in source
    assert "provider_invoked: codexResult.provider_invoked === true" in source
    assert "diagnostic_evidence" in source


def test_fail_closed_behavior_remains_intact_for_invalid_continuity(monkeypatch, tmp_path):
    def fake_run(command, **kwargs):
        raise AssertionError("provider must not be reached for invalid continuity")

    monkeypatch.setattr(subprocess, "run", fake_run)

    artifact = create_controlled_execution_handoff(
        continuity_preview={},
        workspace_path=str(tmp_path),
        timeout_seconds=30,
    )

    assert artifact["execution_status"] == EXECUTION_BLOCKED
    assert artifact["provider_invoked"] is False


def test_no_retries_introduced():
    combined = "\n".join(
        (
            (ROOT / "agol_bridge" / "providers" / "codex_cli_provider.py").read_text(encoding="utf-8"),
            SIDEPANEL.read_text(encoding="utf-8"),
            SERVICE_WORKER.read_text(encoding="utf-8"),
        )
    ).lower()
    assert "retry_count\": 1" not in combined
    assert "for attempt" not in combined


def test_no_autonomous_continuation_introduced():
    combined = "\n".join((SIDEPANEL.read_text(encoding="utf-8"), SERVICE_WORKER.read_text(encoding="utf-8"))).lower()
    assert "autonomous continue" not in combined
    assert "autonomous_continuation: false" in combined


def test_no_alternate_provider_path_introduced():
    provider_source = (ROOT / "agol_bridge" / "providers" / "codex_cli_provider.py").read_text(encoding="utf-8")
    handoff_source = (ROOT / "agol_bridge" / "chatgpt_ingress" / "controlled_execution_handoff.py").read_text(encoding="utf-8")
    assert "CODEX_EXECUTABLE = \"codex\"" in provider_source
    assert "CODEX_PROVIDER = \"BOUNDED_CODEX_CLI_PROVIDER\"" in handoff_source
    assert "fallback" not in provider_source.lower()


def test_native_host_is_executable_for_real_native_messaging_launch():
    assert os.access(HOST, os.X_OK)
