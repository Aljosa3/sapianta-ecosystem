from copy import deepcopy
from pathlib import Path

from agol_bridge.chatgpt_ingress import create_chatgpt_ingress_artifact
from agol_bridge.chatgpt_ingress.governed_handoff_package_preview import (
    ALLOWED_HANDOFF_PREVIEW_STATUSES,
    HANDOFF_PREVIEW_REJECTED,
    READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION,
    create_governed_handoff_package_preview,
    validate_governed_handoff_package_preview,
)
from agol_bridge.chatgpt_ingress.governed_task_package_preview import create_governed_task_package_preview
from agol_bridge.chatgpt_ingress.human_approval_gate import create_human_approval_gate


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "browser_companion" / "sidepanel.html"
JS = ROOT / "browser_companion" / "sidepanel.js"
MODULE = ROOT / "agol_bridge" / "chatgpt_ingress" / "governed_handoff_package_preview.py"
DOC = ROOT / "GOVERNED_HANDOFF_PACKAGE_PREVIEW_V1.md"


def _artifact():
    return create_chatgpt_ingress_artifact(
        created_at="1970-01-01T00:00:00Z",
        session_id="CHATGPT-HANDOFF-PREVIEW-SESSION-1",
        human_request="Prepare governed handoff package preview.",
        chatgpt_semantic_output="The request asks for provider-boundary preview only.",
        normalized_intent="PREPARE_GOVERNED_HANDOFF_PACKAGE_PREVIEW",
        expected_artifacts=["governed handoff package preview"],
        constraints=["handoff preview only", "no execution", "provider boundary remains closed"],
        forbidden_operations=["Codex dispatch", "Native Messaging execution", "provider dispatch"],
        provenance={"source_conversation_id": "CONV-HANDOFF-PREVIEW-1"},
    )


def _task_preview():
    return create_governed_task_package_preview(_artifact())


def _approval(task_preview=None, decision="APPROVE"):
    return create_human_approval_gate(
        preview=task_preview or _task_preview(),
        human_decision=decision,
        approval_reason="Operator approved handoff preview evidence.",
        operator_label="TEST_OPERATOR",
        created_at="1970-01-01T00:00:00Z",
    )


def _handoff(task_preview=None, approval=None):
    task = task_preview or _task_preview()
    return create_governed_handoff_package_preview(
        task_package_preview=task,
        human_approval=approval or _approval(task),
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


def test_approved_human_approval_creates_governed_handoff_package_preview():
    preview = _handoff()

    assert preview["artifact_type"] == "GOVERNED_HANDOFF_PACKAGE_PREVIEW_V1"
    assert preview["handoff_preview_status"] == READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION
    assert preview["handoff_boundary_state"] == READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION
    assert validate_governed_handoff_package_preview(preview)["valid"] is True


def test_rejected_human_approval_blocks_handoff_preview():
    task = _task_preview()
    approval = _approval(task, decision="REJECT")

    preview = _handoff(task_preview=task, approval=approval)

    assert preview["handoff_preview_status"] == HANDOFF_PREVIEW_REJECTED


def test_missing_human_approval_blocks_preview():
    preview = create_governed_handoff_package_preview(
        task_package_preview=_task_preview(),
        human_approval=None,
    )

    assert preview["handoff_preview_status"] == HANDOFF_PREVIEW_REJECTED


def test_missing_governed_task_package_preview_blocks_preview():
    task = _task_preview()
    approval = _approval(task)
    preview = create_governed_handoff_package_preview(
        task_package_preview=None,
        human_approval=approval,
    )

    assert preview["handoff_preview_status"] == HANDOFF_PREVIEW_REJECTED


def test_replay_identity_is_preserved():
    task = _task_preview()
    preview = _handoff(task_preview=task)

    assert preview["replay_identity"] == task["replay_identity"]


def test_replay_identity_mismatch_is_rejected():
    task = _task_preview()
    approval = _approval(task)
    approval["replay_identity"] = "MISMATCH"

    preview = _handoff(task_preview=task, approval=approval)

    assert preview["handoff_preview_status"] == HANDOFF_PREVIEW_REJECTED


def test_provenance_is_preserved():
    preview = _handoff()

    source_provenance = preview["provenance"]["task_package_preview_provenance"]
    lineage = source_provenance["provenance_lineage"]
    assert lineage["source_conversation_id"] == "CONV-HANDOFF-PREVIEW-1"


def test_handoff_preview_hash_is_deterministic():
    first = _handoff()["handoff_preview_hash"]
    second = _handoff()["handoff_preview_hash"]

    assert first == second
    assert first.startswith("sha256:")


def test_status_only_allows_ready_or_rejected():
    assert ALLOWED_HANDOFF_PREVIEW_STATUSES == (
        READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION,
        HANDOFF_PREVIEW_REJECTED,
    )
    assert _handoff()["handoff_preview_status"] in ALLOWED_HANDOFF_PREVIEW_STATUSES


def test_handoff_preview_marks_preview_only_true():
    assert _handoff()["preview_only"] is True


def test_handoff_preview_marks_executable_false():
    assert _handoff()["executable"] is False


def test_handoff_preview_marks_dispatchable_false():
    assert _handoff()["dispatchable"] is False


def test_handoff_preview_marks_execution_performed_false():
    assert _handoff()["execution_performed"] is False


def test_handoff_preview_marks_codex_dispatch_performed_false():
    assert _handoff()["codex_dispatch_performed"] is False


def test_handoff_preview_marks_provider_dispatch_performed_false():
    assert _handoff()["provider_dispatch_performed"] is False


def test_handoff_preview_requires_explicit_dispatch_authorization():
    assert _handoff()["explicit_dispatch_authorization_required"] is True


def test_human_approval_is_not_dispatch_authorization():
    boundary = _handoff()["authority_boundary"]

    assert boundary["human_approval_present"] is True
    assert boundary["dispatch_authorized"] is False
    assert boundary["codex_dispatch_authorized"] is False
    assert boundary["provider_dispatch_authorized"] is False


def test_authority_boundary_violation_rejects_preview():
    task = _task_preview()
    approval = _approval(task)
    task["provider_dispatch_authorized"] = True

    preview = _handoff(task_preview=task, approval=approval)

    assert preview["handoff_preview_status"] == HANDOFF_PREVIEW_REJECTED


def test_mutated_handoff_preview_hash_is_invalid():
    preview = deepcopy(_handoff())
    preview["handoff_preview_hash"] = "sha256:BROKEN"

    assert validate_governed_handoff_package_preview(preview)["valid"] is False


def test_cockpit_renders_governed_handoff_package_preview_card():
    section = _preview_section()

    assert 'id="governed-handoff-package-preview-card"' in section
    assert "Governed Handoff Package Preview" in section
    assert "GOVERNED_HANDOFF_PACKAGE_PREVIEW_V1" in section


def test_cockpit_renders_ready_for_explicit_dispatch_authorization():
    assert "READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION" in _preview_section()


def test_cockpit_renders_explicit_dispatch_authorization_required():
    assert "EXPLICIT DISPATCH AUTHORIZATION REQUIRED" in _preview_section()


def test_cockpit_renders_no_execution():
    assert "NO EXECUTION" in _preview_section()


def test_cockpit_renders_no_codex_dispatch():
    assert "NO CODEX DISPATCH" in _preview_section()


def test_cockpit_renders_no_provider_dispatch():
    assert "NO PROVIDER DISPATCH" in _preview_section()


def test_cockpit_renders_stop_boundary():
    assert "STOP boundary after GOVERNED HANDOFF PACKAGE PREVIEW" in _preview_section()


def test_cockpit_contains_no_execution_dispatch_button_in_handoff_preview_section():
    section = _preview_section().lower()
    start = section.index('id="governed-handoff-package-preview-card"')
    fragment = section[start - 360 : start + 900]

    assert "<button" not in fragment
    assert "run" not in fragment
    assert "execute" not in fragment
    assert "dispatch button" not in fragment
    assert "send to codex" not in fragment
    assert "authorize execution" not in fragment


def test_native_messaging_execution_path_is_not_called():
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

    assert "GOVERNED_HANDOFF_PACKAGE_PREVIEW_V1" in doc
    assert "READY_FOR_EXPLICIT_DISPATCH_AUTHORIZATION" in doc
    assert "Human approval is not dispatch authorization" in doc
