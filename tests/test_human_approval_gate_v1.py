from copy import deepcopy
from pathlib import Path

from agol_bridge.chatgpt_ingress import create_chatgpt_ingress_artifact
from agol_bridge.chatgpt_ingress.governed_task_package_preview import create_governed_task_package_preview
from agol_bridge.chatgpt_ingress.human_approval_gate import (
    ALLOWED_APPROVAL_STATUSES,
    APPROVED_FOR_GOVERNED_HANDOFF,
    REJECTED_BY_HUMAN,
    create_human_approval_gate,
    validate_human_approval_gate,
)


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "browser_companion" / "sidepanel.html"
JS = ROOT / "browser_companion" / "sidepanel.js"
MODULE = ROOT / "agol_bridge" / "chatgpt_ingress" / "human_approval_gate.py"
DOC = ROOT / "HUMAN_APPROVAL_GATE_V1.md"


def _artifact():
    return create_chatgpt_ingress_artifact(
        created_at="1970-01-01T00:00:00Z",
        session_id="CHATGPT-HUMAN-APPROVAL-SESSION-1",
        human_request="Approve governed preview evidence.",
        chatgpt_semantic_output="The request asks for human approval evidence only.",
        normalized_intent="APPROVE_GOVERNED_PREVIEW_EVIDENCE",
        expected_artifacts=["human approval gate evidence"],
        constraints=["human approval only", "no execution"],
        forbidden_operations=["Codex dispatch", "Native Messaging execution", "provider dispatch"],
        provenance={"source_conversation_id": "CONV-HUMAN-APPROVAL-1"},
    )


def _preview():
    return create_governed_task_package_preview(_artifact())


def _approval(preview=None, decision="APPROVE"):
    return create_human_approval_gate(
        preview=preview or _preview(),
        human_decision=decision,
        approval_reason="Operator reviewed preview boundary evidence.",
        operator_label="TEST_OPERATOR",
        created_at="1970-01-01T00:00:00Z",
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


def test_valid_ready_for_human_approval_preview_can_be_approved():
    approval = _approval(decision="APPROVE")

    assert approval["artifact_type"] == "HUMAN_APPROVAL_GATE_V1"
    assert approval["approval_status"] == APPROVED_FOR_GOVERNED_HANDOFF
    assert approval["human_approved"] is True
    assert validate_human_approval_gate(approval)["valid"] is True


def test_valid_ready_for_human_approval_preview_can_be_rejected():
    approval = _approval(decision="REJECT")

    assert approval["approval_status"] == REJECTED_BY_HUMAN
    assert approval["human_approved"] is False
    assert validate_human_approval_gate(approval)["valid"] is True


def test_invalid_preview_is_rejected():
    preview = _preview()
    preview["governance_status"] = "BROKEN"

    approval = _approval(preview=preview)

    assert approval["approval_status"] == REJECTED_BY_HUMAN
    assert approval["human_approved"] is False


def test_missing_replay_identity_is_rejected():
    preview = _preview()
    preview["replay_identity"] = ""

    approval = _approval(preview=preview)

    assert approval["approval_status"] == REJECTED_BY_HUMAN


def test_missing_provenance_is_rejected():
    preview = _preview()
    preview["provenance"] = {}

    approval = _approval(preview=preview)

    assert approval["approval_status"] == REJECTED_BY_HUMAN


def test_invalid_preview_hash_is_rejected():
    preview = _preview()
    preview["preview_hash"] = "sha256:BROKEN"

    approval = _approval(preview=preview)

    assert approval["approval_status"] == REJECTED_BY_HUMAN


def test_approval_hash_is_deterministic():
    first = _approval()["approval_hash"]
    second = _approval()["approval_hash"]

    assert first == second
    assert first.startswith("sha256:")


def test_approval_status_only_allows_approved_or_rejected():
    assert ALLOWED_APPROVAL_STATUSES == (
        APPROVED_FOR_GOVERNED_HANDOFF,
        REJECTED_BY_HUMAN,
    )
    assert _approval()["approval_status"] in ALLOWED_APPROVAL_STATUSES
    assert _approval(decision="REJECT")["approval_status"] in ALLOWED_APPROVAL_STATUSES


def test_approval_never_performs_execution():
    assert _approval()["execution_performed"] is False


def test_approval_never_dispatches_codex():
    assert _approval()["codex_dispatch_performed"] is False


def test_approval_never_dispatches_provider():
    assert _approval()["provider_dispatch_performed"] is False


def test_approval_never_authorizes_autonomous_continuation():
    assert _approval()["autonomous_continuation_performed"] is False


def test_authority_boundary_violation_is_rejected():
    preview = _preview()
    preview["execution_authorized"] = True

    approval = _approval(preview=preview)

    assert approval["approval_status"] == REJECTED_BY_HUMAN


def test_cockpit_renders_human_approval_gate_card():
    section = _preview_section()

    assert 'id="human-approval-gate-card"' in section
    assert "Human Approval Gate" in section
    assert "HUMAN_APPROVAL_GATE_V1" in section


def test_cockpit_renders_approve_preview_button():
    section = _preview_section()

    assert 'id="approve-task-package-preview"' in section
    assert "Approve Preview" in section


def test_cockpit_renders_reject_preview_button():
    section = _preview_section()

    assert 'id="reject-task-package-preview"' in section
    assert "Reject Preview" in section


def test_cockpit_labels_no_execution():
    assert "NO EXECUTION" in _preview_section()


def test_cockpit_labels_no_codex_dispatch():
    assert "NO CODEX DISPATCH" in _preview_section()


def test_cockpit_shows_approval_hash():
    combined = "\n".join((_preview_section(), JS.read_text(encoding="utf-8")))

    assert "approval_hash:" in combined


def test_cockpit_shows_stop_boundary():
    section = _preview_section()

    assert "STOP boundary after HUMAN APPROVAL GATE" in section


def test_native_messaging_execution_path_is_not_called():
    source = MODULE.read_text(encoding="utf-8")
    preview_source = _preview_source()

    assert "from agol_bridge.native" not in source
    assert "import agol_bridge.native" not in source
    assert "send_native_message" not in source.lower()
    assert "sendNativeMessage" not in preview_source
    assert "runNativeBridgeFromSidepanel" not in preview_source


def test_codex_provider_is_not_invoked():
    source = MODULE.read_text(encoding="utf-8")
    preview_source = _preview_source()

    assert "codex_cli_provider" not in source
    assert "run_bounded_codex_cli_task" not in source
    assert "codex_cli_provider" not in preview_source
    assert "run_bounded_codex_cli_task" not in preview_source


def test_mutated_approval_hash_is_invalid():
    approval = deepcopy(_approval())
    approval["approval_hash"] = "sha256:BROKEN"

    assert validate_human_approval_gate(approval)["valid"] is False


def test_documentation_exists():
    doc = DOC.read_text(encoding="utf-8")

    assert "HUMAN_APPROVAL_GATE_V1" in doc
    assert "APPROVED_FOR_GOVERNED_HANDOFF" in doc
    assert "No execution occurs" in doc
