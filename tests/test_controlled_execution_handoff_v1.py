import subprocess
from copy import deepcopy
from pathlib import Path

from agol_bridge.chatgpt_ingress import create_chatgpt_ingress_artifact
from agol_bridge.chatgpt_ingress.controlled_execution_continuity_preview import create_controlled_execution_continuity_preview
from agol_bridge.chatgpt_ingress.controlled_execution_handoff import (
    EXECUTION_BLOCKED,
    EXECUTION_COMPLETED,
    create_controlled_execution_handoff,
    validate_controlled_execution_handoff,
)
from agol_bridge.chatgpt_ingress.explicit_dispatch_authorization import create_explicit_dispatch_authorization
from agol_bridge.chatgpt_ingress.governed_handoff_package_preview import create_governed_handoff_package_preview
from agol_bridge.chatgpt_ingress.governed_task_package_preview import create_governed_task_package_preview
from agol_bridge.chatgpt_ingress.human_approval_gate import create_human_approval_gate


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "browser_companion" / "sidepanel.html"
JS = ROOT / "browser_companion" / "sidepanel.js"
MODULE = ROOT / "agol_bridge" / "chatgpt_ingress" / "controlled_execution_handoff.py"


def _artifact():
    return create_chatgpt_ingress_artifact(
        created_at="1970-01-01T00:00:00Z",
        session_id="CHATGPT-CONTROLLED-HANDOFF-SESSION-1",
        human_request="Run controlled execution handoff.",
        chatgpt_semantic_output="The request asks for bounded governed execution.",
        normalized_intent="RUN_CONTROLLED_EXECUTION_HANDOFF",
        expected_artifacts=["controlled execution handoff artifact"],
        constraints=["single path", "single provider", "no retries"],
        forbidden_operations=["autonomous continuation", "orchestration", "retry"],
        provenance={"source_conversation_id": "CONV-CONTROLLED-HANDOFF-1"},
    )


def _continuity_preview():
    task = create_governed_task_package_preview(_artifact())
    approval = create_human_approval_gate(
        preview=task,
        human_decision="APPROVE",
        approval_reason="Operator approved execution handoff setup.",
        operator_label="TEST_OPERATOR",
        created_at="1970-01-01T00:00:00Z",
    )
    handoff = create_governed_handoff_package_preview(task_package_preview=task, human_approval=approval)
    auth = create_explicit_dispatch_authorization(
        handoff_preview=handoff,
        dispatch_decision="AUTHORIZE",
        dispatch_authorization_reason="Operator authorized controlled handoff.",
    )
    return create_controlled_execution_continuity_preview(dispatch_authorization=auth)


def _mock_codex(monkeypatch):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="controlled bounded codex complete", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


def _execute(monkeypatch, tmp_path, preview=None, prior=None):
    calls = _mock_codex(monkeypatch)
    artifact = create_controlled_execution_handoff(
        continuity_preview=_continuity_preview() if preview is None else preview,
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        prior_execution_artifact=prior,
    )
    return artifact, calls


def _preview_section() -> str:
    html = HTML.read_text(encoding="utf-8")
    start = html.index('id="chatgpt-ingress-preview"')
    end = html.index('id="governed-execution-observatory"', start)
    return html[start:end]


def test_dispatch_authorized_allows_execution_handoff(monkeypatch, tmp_path):
    artifact, calls = _execute(monkeypatch, tmp_path)

    assert artifact["artifact_type"] == "CONTROLLED_EXECUTION_HANDOFF_V1"
    assert artifact["execution_status"] == EXECUTION_COMPLETED
    assert artifact["execution_performed"] is True
    assert len(calls) == 1
    assert validate_controlled_execution_handoff(artifact)["valid"] is True


def test_missing_dispatch_authorization_blocks_execution(monkeypatch, tmp_path):
    artifact, calls = _execute(monkeypatch, tmp_path, preview={})

    assert artifact["execution_status"] == EXECUTION_BLOCKED
    assert calls == []


def test_invalid_replay_identity_blocks_execution(monkeypatch, tmp_path):
    preview = _continuity_preview()
    preview["replay_identity"] = ""

    artifact, calls = _execute(monkeypatch, tmp_path, preview=preview)

    assert artifact["execution_status"] == EXECUTION_BLOCKED
    assert calls == []


def test_missing_provenance_blocks_execution(monkeypatch, tmp_path):
    preview = _continuity_preview()
    preview["provenance"] = {}

    artifact, calls = _execute(monkeypatch, tmp_path, preview=preview)

    assert artifact["execution_status"] == EXECUTION_BLOCKED
    assert calls == []


def test_invalid_continuity_hashes_block_execution(monkeypatch, tmp_path):
    preview = _continuity_preview()
    preview["continuity_preview_hash"] = "sha256:BROKEN"

    artifact, calls = _execute(monkeypatch, tmp_path, preview=preview)

    assert artifact["execution_status"] == EXECUTION_BLOCKED
    assert calls == []


def test_execution_path_uses_sidepanel(monkeypatch, tmp_path):
    artifact, _ = _execute(monkeypatch, tmp_path)
    assert "sidepanel" in artifact["execution_path_used"]


def test_execution_path_uses_service_worker(monkeypatch, tmp_path):
    artifact, _ = _execute(monkeypatch, tmp_path)
    assert "service_worker" in artifact["execution_path_used"]
    assert artifact["service_worker_called"] is True


def test_execution_path_uses_native_messaging(monkeypatch, tmp_path):
    artifact, _ = _execute(monkeypatch, tmp_path)
    assert "Native Messaging" in artifact["execution_path_used"]
    assert artifact["native_messaging_called"] is True


def test_execution_path_uses_python_runtime_bridge(monkeypatch, tmp_path):
    artifact, _ = _execute(monkeypatch, tmp_path)
    assert "Python runtime bridge" in artifact["execution_path_used"]


def test_execution_path_uses_bounded_codex_cli_provider(monkeypatch, tmp_path):
    artifact, calls = _execute(monkeypatch, tmp_path)
    assert "bounded Codex CLI provider" in artifact["execution_path_used"]
    assert artifact["codex_provider_used"] == "BOUNDED_CODEX_CLI_PROVIDER"
    assert calls[0][0][0:2] == ["codex", "exec"]


def test_execution_executes_only_once(monkeypatch, tmp_path):
    _, calls = _execute(monkeypatch, tmp_path)
    assert len(calls) == 1


def test_retries_are_blocked(monkeypatch, tmp_path):
    artifact, calls = _execute(monkeypatch, tmp_path)
    assert len(calls) == 1
    assert artifact["execution_boundary"]["retries"] is False


def test_autonomous_continuation_blocked(monkeypatch, tmp_path):
    artifact, _ = _execute(monkeypatch, tmp_path)
    assert artifact["autonomous_continuation_performed"] is False
    assert artifact["execution_boundary"]["autonomous_continuation"] is False


def test_execution_governance_hash_deterministic(monkeypatch, tmp_path):
    first, _ = _execute(monkeypatch, tmp_path)
    second, _ = _execute(monkeypatch, tmp_path)
    assert first["execution_governance_hash"] == second["execution_governance_hash"]


def test_execution_result_hash_deterministic(monkeypatch, tmp_path):
    first, _ = _execute(monkeypatch, tmp_path)
    second, _ = _execute(monkeypatch, tmp_path)
    assert first["execution_result_hash"] == second["execution_result_hash"]


def test_second_execution_with_prior_artifact_is_blocked(monkeypatch, tmp_path):
    first, _ = _execute(monkeypatch, tmp_path)
    second, calls = _execute(monkeypatch, tmp_path, prior=first)
    assert second["execution_status"] == EXECUTION_BLOCKED
    assert calls == []


def test_cockpit_renders_controlled_execution_handoff_card():
    section = _preview_section()
    assert 'id="controlled-execution-handoff-card"' in section
    assert "Controlled Execution Handoff" in section


def test_cockpit_renders_execute_controlled_handoff_button():
    section = _preview_section()
    assert 'id="execute-controlled-handoff"' in section
    assert "Execute Controlled Handoff" in section


def test_cockpit_renders_real_governed_execution():
    assert "REAL GOVERNED EXECUTION" in _preview_section()


def test_cockpit_renders_fail_closed():
    assert "FAIL-CLOSED" in _preview_section()


def test_cockpit_renders_execution_status():
    combined = "\n".join((_preview_section(), JS.read_text(encoding="utf-8")))
    assert "execution_status:" in combined


def test_cockpit_renders_execution_result_summary():
    assert "execution_result_summary" in _preview_section()


def test_cockpit_renders_execution_result_hash():
    assert "execution_result_hash" in _preview_section()


def test_cockpit_renders_execution_governance_hash():
    assert "execution_governance_hash" in _preview_section()


def test_cockpit_renders_stop_boundary():
    assert "STOP" in _preview_section()


def test_native_messaging_runtime_actually_called(monkeypatch, tmp_path):
    artifact, _ = _execute(monkeypatch, tmp_path)
    assert artifact["native_messaging_called"] is True
    assert artifact["native_response"]["status"] == "NATIVE_BRIDGE_ACCEPTED"


def test_codex_provider_actually_invoked(monkeypatch, tmp_path):
    artifact, calls = _execute(monkeypatch, tmp_path)
    assert artifact["provider_invoked"] is True
    assert artifact["codex_dispatch_performed"] is True
    assert len(calls) == 1


def test_execution_remains_single_path_only(monkeypatch, tmp_path):
    artifact, _ = _execute(monkeypatch, tmp_path)
    assert artifact["execution_boundary"]["single_path"] is True
    assert artifact["execution_path_used"] == [
        "sidepanel",
        "service_worker",
        "Native Messaging",
        "Python runtime bridge",
        "bounded Codex CLI provider",
    ]


def test_execution_remains_single_provider_only(monkeypatch, tmp_path):
    artifact, _ = _execute(monkeypatch, tmp_path)
    assert artifact["execution_boundary"]["single_provider"] is True
    assert artifact["codex_provider_used"] == "BOUNDED_CODEX_CLI_PROVIDER"


def test_source_has_no_retry_or_orchestration_loop():
    source = MODULE.read_text(encoding="utf-8").lower()
    assert "for attempt" not in source
    assert "while " not in source
    assert "threading" not in source
    assert "orchestrationruntime" not in source


def test_mutated_execution_governance_hash_is_invalid(monkeypatch, tmp_path):
    artifact, _ = _execute(monkeypatch, tmp_path)
    mutated = deepcopy(artifact)
    mutated["execution_governance_hash"] = "sha256:BROKEN"
    assert validate_controlled_execution_handoff(mutated)["valid"] is False
