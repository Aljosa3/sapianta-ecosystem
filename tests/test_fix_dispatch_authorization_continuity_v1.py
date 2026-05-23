import subprocess
from pathlib import Path

from agol_bridge.chatgpt_ingress import create_chatgpt_ingress_artifact
from agol_bridge.chatgpt_ingress.controlled_execution_continuity_preview import (
    READY_FOR_CONTROLLED_EXECUTION_HANDOFF,
    create_controlled_execution_continuity_preview,
)
from agol_bridge.chatgpt_ingress.controlled_execution_handoff import (
    EXECUTION_BLOCKED,
    EXECUTION_COMPLETED,
    create_controlled_execution_handoff,
)
from agol_bridge.chatgpt_ingress.explicit_dispatch_authorization import (
    DISPATCH_AUTHORIZED,
    create_explicit_dispatch_authorization,
)
from agol_bridge.chatgpt_ingress.governed_handoff_package_preview import create_governed_handoff_package_preview
from agol_bridge.chatgpt_ingress.governed_task_package_preview import create_governed_task_package_preview
from agol_bridge.chatgpt_ingress.human_approval_gate import create_human_approval_gate


ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "browser_companion" / "sidepanel.js"


def _authorization():
    return create_explicit_dispatch_authorization(
        handoff_preview=_handoff(),
        dispatch_decision="AUTHORIZE",
        dispatch_authorization_reason="Operator authorizes dispatch preview.",
    )


def _artifact():
    return create_chatgpt_ingress_artifact(
        created_at="1970-01-01T00:00:00Z",
        session_id="CHATGPT-FIX-DISPATCH-AUTHORIZATION-CONTINUITY",
        human_request="Repair dispatch authorization continuity.",
        chatgpt_semantic_output="The request asks for bounded governed dispatch continuity repair.",
        normalized_intent="FIX_DISPATCH_AUTHORIZATION_CONTINUITY",
        expected_artifacts=["dispatch authorization continuity evidence"],
        constraints=["single path", "fail closed"],
        forbidden_operations=["orchestration", "retry", "autonomous continuation"],
        provenance={"source_conversation_id": "CONV-FIX-DISPATCH-CONTINUITY"},
    )


def _handoff():
    task = create_governed_task_package_preview(_artifact())
    approval = create_human_approval_gate(
        preview=task,
        human_decision="APPROVE",
        approval_reason="Operator approved handoff preview.",
        operator_label="TEST_OPERATOR",
        created_at="1970-01-01T00:00:00Z",
    )
    return create_governed_handoff_package_preview(task_package_preview=task, human_approval=approval)


def _continuity_preview():
    return create_controlled_execution_continuity_preview(dispatch_authorization=_authorization())


def _mock_codex(monkeypatch):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="controlled bounded codex complete", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


def _execute(monkeypatch, tmp_path, preview=None):
    calls = _mock_codex(monkeypatch)
    artifact = create_controlled_execution_handoff(
        continuity_preview=_continuity_preview() if preview is None else preview,
        workspace_path=str(tmp_path),
        timeout_seconds=30,
    )
    return artifact, calls


def test_authorize_dispatch_preview_persists_dispatch_authorized_state():
    source = JS.read_text(encoding="utf-8")
    assert "let latestExplicitDispatchAuthorization = null;" in source
    assert "latestExplicitDispatchAuthorization = canonicalize(authorization);" in source


def test_dispatch_authorized_becomes_true():
    authorization = _authorization()
    assert authorization["dispatch_authorization_status"] == DISPATCH_AUTHORIZED
    assert authorization["dispatch_authorized"] is True


def test_continuity_preview_consumes_authorized_state():
    preview = create_controlled_execution_continuity_preview(dispatch_authorization=_authorization())
    assert preview["execution_continuity_status"] == READY_FOR_CONTROLLED_EXECUTION_HANDOFF
    assert preview["authority_boundary"]["dispatch_authorized"] is True


def test_execution_handoff_consumes_authorized_state(monkeypatch, tmp_path):
    calls = _mock_codex(monkeypatch)
    artifact = create_controlled_execution_handoff(
        continuity_preview=create_controlled_execution_continuity_preview(dispatch_authorization=_authorization()),
        workspace_path=str(tmp_path),
        timeout_seconds=30,
    )
    assert artifact["execution_status"] == EXECUTION_COMPLETED
    assert len(calls) == 1


def test_authorized_state_survives_rerender():
    source = JS.read_text(encoding="utf-8")
    assert "if (latestExplicitDispatchAuthorization) {" in source
    assert "renderExplicitDispatchAuthorization(latestExplicitDispatchAuthorization);" in source


def test_authorized_state_survives_continuity_preview_generation():
    source = JS.read_text(encoding="utf-8")
    assert "let latestControlledExecutionContinuityPreview = null;" in source
    assert "latestControlledExecutionContinuityPreview = canonicalize(preview);" in source


def test_rendered_authorization_generates_downstream_continuity_preview():
    source = JS.read_text(encoding="utf-8")
    assert "const continuityPreview = controlledExecutionContinuityPreview(authorization);" in source
    assert "renderControlledExecutionContinuityPreview(continuityPreview);" in source


def test_authorized_state_survives_execution_handoff_preparation():
    source = JS.read_text(encoding="utf-8")
    assert "const continuityPreview = latestControlledExecutionContinuityPreview || {};" in source
    assert "continuityPreview.execution_continuity_status === \"READY_FOR_CONTROLLED_EXECUTION_HANDOFF\"" in source
    assert "(continuityPreview.authority_boundary || {}).dispatch_authorized === true" in source


def test_execution_still_blocks_if_authorization_missing(monkeypatch, tmp_path):
    artifact, calls = _execute(monkeypatch, tmp_path, preview={})
    assert artifact["execution_status"] == EXECUTION_BLOCKED
    assert calls == []


def test_execution_still_blocks_if_replay_identity_invalid(monkeypatch, tmp_path):
    preview = _continuity_preview()
    preview["replay_identity"] = ""
    artifact, calls = _execute(monkeypatch, tmp_path, preview=preview)
    assert artifact["execution_status"] == EXECUTION_BLOCKED
    assert calls == []


def test_execution_still_blocks_if_continuity_hashes_invalid(monkeypatch, tmp_path):
    preview = _continuity_preview()
    preview["continuity_preview_hash"] = "sha256:BROKEN"
    artifact, calls = _execute(monkeypatch, tmp_path, preview=preview)
    assert artifact["execution_status"] == EXECUTION_BLOCKED
    assert calls == []


def test_fail_closed_behavior_preserved():
    source = JS.read_text(encoding="utf-8")
    assert "renderControlledExecutionHandoff(controlledExecutionBlockedSummary(\"valid continuity chain is required\"));" in source


def test_no_retries_introduced():
    source = JS.read_text(encoding="utf-8").lower()
    assert "retry button" not in source


def test_no_orchestration_introduced():
    source = JS.read_text(encoding="utf-8").lower()
    assert "orchestrationruntime" not in source


def test_no_autonomous_continuation_introduced():
    source = JS.read_text(encoding="utf-8").lower()
    assert "autonomous continue" not in source
