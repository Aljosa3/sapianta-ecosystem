from copy import deepcopy
from pathlib import Path

from agol_bridge.chatgpt_ingress import create_chatgpt_ingress_artifact
from agol_bridge.chatgpt_ingress.controlled_execution_continuity_preview import (
    ALLOWED_CONTINUITY_PREVIEW_STATUSES,
    EXECUTION_CONTINUITY_PREVIEW_REJECTED,
    READY_FOR_CONTROLLED_EXECUTION_HANDOFF,
    create_controlled_execution_continuity_preview,
    validate_controlled_execution_continuity_preview,
)
from agol_bridge.chatgpt_ingress.explicit_dispatch_authorization import create_explicit_dispatch_authorization
from agol_bridge.chatgpt_ingress.governed_handoff_package_preview import create_governed_handoff_package_preview
from agol_bridge.chatgpt_ingress.governed_task_package_preview import create_governed_task_package_preview
from agol_bridge.chatgpt_ingress.human_approval_gate import create_human_approval_gate


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "browser_companion" / "sidepanel.html"
JS = ROOT / "browser_companion" / "sidepanel.js"
MODULE = ROOT / "agol_bridge" / "chatgpt_ingress" / "controlled_execution_continuity_preview.py"
DOC = ROOT / "CONTROLLED_EXECUTION_CONTINUITY_PREVIEW_V1.md"


def _artifact():
    return create_chatgpt_ingress_artifact(
        created_at="1970-01-01T00:00:00Z",
        session_id="CHATGPT-CONTINUITY-PREVIEW-SESSION-1",
        human_request="Preview controlled execution continuity.",
        chatgpt_semantic_output="The request asks to show execution path candidates only.",
        normalized_intent="PREVIEW_CONTROLLED_EXECUTION_CONTINUITY",
        expected_artifacts=["controlled execution continuity preview"],
        constraints=["continuity preview only", "no execution", "no Native Messaging call"],
        forbidden_operations=["Codex dispatch", "Native Messaging execution", "provider invocation"],
        provenance={"source_conversation_id": "CONV-CONTINUITY-PREVIEW-1"},
    )


def _task_preview():
    return create_governed_task_package_preview(_artifact())


def _handoff():
    task = _task_preview()
    approval = create_human_approval_gate(
        preview=task,
        human_decision="APPROVE",
        approval_reason="Operator approved continuity preview setup.",
        operator_label="TEST_OPERATOR",
        created_at="1970-01-01T00:00:00Z",
    )
    return create_governed_handoff_package_preview(
        task_package_preview=task,
        human_approval=approval,
    )


def _authorization(decision="AUTHORIZE"):
    return create_explicit_dispatch_authorization(
        handoff_preview=_handoff(),
        dispatch_decision=decision,
        dispatch_authorization_reason="Operator created dispatch authorization evidence.",
    )


def _preview(authorization=None):
    return create_controlled_execution_continuity_preview(
        dispatch_authorization=authorization or _authorization(),
    )


def _preview_section() -> str:
    html = HTML.read_text(encoding="utf-8")
    start = html.index('id="chatgpt-ingress-preview"')
    end = html.index('id="governed-execution-observatory"', start)
    return html[start:end]


def _preview_source() -> str:
    source = JS.read_text(encoding="utf-8")
    start = source.index("function chatgptIngressPreviewArtifact")
    end = source.index("function replaySummaryArtifact", start)
    return source[start:end]


def _path_text(preview):
    return " ".join(stage["stage"] for stage in preview["execution_path_candidate"]["stages"])


def test_dispatch_authorized_creates_controlled_execution_continuity_preview():
    preview = _preview()

    assert preview["artifact_type"] == "CONTROLLED_EXECUTION_CONTINUITY_PREVIEW_V1"
    assert preview["execution_continuity_status"] == READY_FOR_CONTROLLED_EXECUTION_HANDOFF
    assert validate_controlled_execution_continuity_preview(preview)["valid"] is True


def test_dispatch_rejected_blocks_preview():
    preview = _preview(_authorization(decision="REJECT"))

    assert preview["execution_continuity_status"] == EXECUTION_CONTINUITY_PREVIEW_REJECTED


def test_missing_dispatch_authorization_blocks_preview():
    preview = create_controlled_execution_continuity_preview(dispatch_authorization=None)

    assert preview["execution_continuity_status"] == EXECUTION_CONTINUITY_PREVIEW_REJECTED


def test_replay_identity_is_preserved():
    authorization = _authorization()
    preview = _preview(authorization)

    assert preview["replay_identity"] == authorization["replay_identity"]


def test_replay_identity_mismatch_is_rejected():
    authorization = _authorization()
    authorization["provenance"]["replay_identity"] = "MISMATCH"

    preview = _preview(authorization)

    assert preview["execution_continuity_status"] == EXECUTION_CONTINUITY_PREVIEW_REJECTED


def test_provenance_is_preserved():
    preview = _preview()

    source = preview["provenance"]["dispatch_authorization_provenance"]
    assert source["source"] == "GOVERNED_HANDOFF_PACKAGE_PREVIEW_V1"


def test_required_source_hashes_are_preserved():
    authorization = _authorization()
    preview = _preview(authorization)

    assert preview["source_dispatch_authorization_hash"] == authorization["dispatch_authorization_hash"]
    assert preview["source_handoff_preview_hash"] == authorization["source_handoff_preview_hash"]
    assert preview["human_approval_hash"] == authorization["human_approval_hash"]
    assert preview["governed_task_package_preview_hash"] == authorization["provenance"]["governed_task_package_preview_hash"]
    assert preview["semantic_contract_candidate_hash"] == authorization["provenance"]["semantic_contract_candidate_hash"]
    assert preview["admissibility_gate_hash"] == authorization["admissibility_gate_hash"]


def test_continuity_preview_hash_is_deterministic():
    first = _preview()["continuity_preview_hash"]
    second = _preview()["continuity_preview_hash"]

    assert first == second
    assert first.startswith("sha256:")


def test_status_only_allows_ready_or_rejected():
    assert ALLOWED_CONTINUITY_PREVIEW_STATUSES == (
        READY_FOR_CONTROLLED_EXECUTION_HANDOFF,
        EXECUTION_CONTINUITY_PREVIEW_REJECTED,
    )
    assert _preview()["execution_continuity_status"] in ALLOWED_CONTINUITY_PREVIEW_STATUSES


def test_preview_marks_preview_only_true():
    assert _preview()["preview_only"] is True


def test_preview_marks_execution_performed_false():
    assert _preview()["execution_performed"] is False


def test_preview_marks_codex_dispatch_performed_false():
    assert _preview()["codex_dispatch_performed"] is False


def test_preview_marks_native_messaging_called_false():
    assert _preview()["native_messaging_called"] is False


def test_preview_marks_provider_invoked_false():
    assert _preview()["provider_invoked"] is False


def test_preview_marks_service_worker_called_false():
    assert _preview()["service_worker_called"] is False


def test_execution_path_candidate_includes_sidepanel():
    assert "sidepanel" in _path_text(_preview())


def test_execution_path_candidate_includes_service_worker():
    assert "service_worker" in _path_text(_preview())


def test_execution_path_candidate_includes_native_messaging_host():
    assert "Native Messaging host" in _path_text(_preview())


def test_execution_path_candidate_includes_python_runtime_bridge():
    assert "Python runtime bridge" in _path_text(_preview())


def test_execution_path_candidate_includes_bounded_codex_cli_provider():
    assert "bounded Codex CLI provider" in _path_text(_preview())


def test_every_execution_path_stage_is_preview_or_not_called():
    for stage in _preview()["execution_path_candidate"]["stages"]:
        assert stage["status"] in {"PREVIEW_ONLY", "NOT_CALLED"}
        assert stage["called"] is False


def test_mutated_continuity_preview_hash_is_invalid():
    preview = deepcopy(_preview())
    preview["continuity_preview_hash"] = "sha256:BROKEN"

    assert validate_controlled_execution_continuity_preview(preview)["valid"] is False


def test_execution_claim_rejects_preview():
    authorization = _authorization()
    authorization["execution_performed"] = True

    assert _preview(authorization)["execution_continuity_status"] == EXECUTION_CONTINUITY_PREVIEW_REJECTED


def test_cockpit_renders_controlled_execution_continuity_preview_card():
    section = _preview_section()

    assert 'id="controlled-execution-continuity-preview-card"' in section
    assert "Controlled Execution Continuity Preview" in section
    assert "CONTROLLED_EXECUTION_CONTINUITY_PREVIEW_V1" in section


def test_cockpit_renders_ready_for_controlled_execution_handoff():
    combined = "\n".join((_preview_section(), JS.read_text(encoding="utf-8")))

    assert "READY_FOR_CONTROLLED_EXECUTION_HANDOFF" in combined


def test_cockpit_renders_no_execution():
    assert "NO EXECUTION" in _preview_section()


def test_cockpit_renders_no_codex_dispatch():
    assert "NO CODEX DISPATCH" in _preview_section()


def test_cockpit_renders_native_messaging_not_called():
    assert "NATIVE MESSAGING NOT CALLED" in _preview_section()


def test_cockpit_renders_provider_not_invoked():
    assert "PROVIDER NOT INVOKED" in _preview_section()


def test_cockpit_renders_stop_boundary():
    assert "STOP boundary after CONTROLLED EXECUTION CONTINUITY PREVIEW" in _preview_section()


def test_cockpit_contains_no_run_execute_dispatch_button_in_continuity_section():
    section = _preview_section().lower()
    start = section.index('id="controlled-execution-continuity-preview-card"')
    fragment = section[start - 360 : start + 900]

    assert "<button" not in fragment
    assert "run preview" not in fragment
    assert "execute preview" not in fragment
    assert "dispatch preview" not in fragment
    assert "send to codex" not in fragment
    assert "call native messaging" not in fragment


def test_native_messaging_runtime_path_is_not_called():
    source = MODULE.read_text(encoding="utf-8")
    preview_source = _preview_source()

    assert "from agol_bridge.native" not in source
    assert "import agol_bridge.native" not in source
    assert "send_native_message" not in source.lower()
    assert "sendNativeMessage" not in preview_source
    assert "runNativeBridgeFromSidepanel" not in preview_source


def test_codex_provider_is_never_invoked():
    source = MODULE.read_text(encoding="utf-8")
    preview_source = _preview_source()

    assert "codex_cli_provider" not in source
    assert "run_bounded_codex_cli_task" not in source
    assert "codex_cli_provider" not in preview_source
    assert "run_bounded_codex_cli_task" not in preview_source


def test_documentation_exists():
    doc = DOC.read_text(encoding="utf-8")

    assert "CONTROLLED_EXECUTION_CONTINUITY_PREVIEW_V1" in doc
    assert "Native Messaging is not called" in doc
    assert "Codex is not dispatched" in doc
