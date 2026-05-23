from copy import deepcopy
from pathlib import Path

from agol_bridge.chatgpt_ingress import create_chatgpt_ingress_artifact
from agol_bridge.chatgpt_ingress.governed_task_package_preview import (
    PREVIEW_REJECTED,
    READY_FOR_HUMAN_APPROVAL,
    create_governed_task_package_preview,
    create_governed_task_package_preview_from_import_result,
    validate_governed_task_package_preview,
)
from agol_bridge.chatgpt_ingress.ingress_acceptance_gate import evaluate_chatgpt_ingress_acceptance_gate


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "browser_companion" / "sidepanel.html"
JS = ROOT / "browser_companion" / "sidepanel.js"
MODULE = ROOT / "agol_bridge" / "chatgpt_ingress" / "governed_task_package_preview.py"
DOC = ROOT / "GOVERNED_TASK_PACKAGE_PREVIEW_V1.md"


def _artifact():
    return create_chatgpt_ingress_artifact(
        created_at="1970-01-01T00:00:00Z",
        session_id="CHATGPT-TASK-PREVIEW-SESSION-1",
        human_request="Prepare a governed task package preview.",
        chatgpt_semantic_output="The request asks for execution-boundary continuity only.",
        normalized_intent="PREPARE_GOVERNED_TASK_PACKAGE_PREVIEW",
        expected_artifacts=["governed task package preview"],
        constraints=["preview only", "no execution"],
        forbidden_operations=["Codex dispatch", "Native Messaging execution", "provider dispatch"],
        provenance={"source_conversation_id": "CONV-TASK-PREVIEW-1"},
    )


def _preview(artifact=None):
    return create_governed_task_package_preview(artifact or _artifact())


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


def test_accepted_ingress_path_creates_governed_task_package_preview():
    preview = _preview()

    assert preview["artifact_type"] == "GOVERNED_TASK_PACKAGE_PREVIEW_V1"
    assert preview["governance_status"] == READY_FOR_HUMAN_APPROVAL
    assert preview["execution_boundary_state"] == READY_FOR_HUMAN_APPROVAL
    assert validate_governed_task_package_preview(preview)["valid"] is True


def test_rejected_acceptance_gate_blocks_preview_creation():
    artifact = _artifact()
    artifact["authority_boundary"]["execution_authority"] = True

    preview = _preview(artifact)

    assert preview["governance_status"] == PREVIEW_REJECTED
    assert preview["execution_boundary_state"] == PREVIEW_REJECTED
    assert preview["execution_authorized"] is False


def test_replay_identity_preserved():
    artifact = _artifact()
    preview = _preview(artifact)

    assert preview["replay_identity"] == artifact["replay_identity"]


def test_provenance_preserved():
    preview = _preview()

    lineage = preview["provenance"]["provenance_lineage"]
    assert lineage["source_conversation_id"] == "CONV-TASK-PREVIEW-1"


def test_preview_hash_deterministic():
    first = _preview()["preview_hash"]
    second = _preview()["preview_hash"]

    assert first == second
    assert first.startswith("sha256:")


def test_ready_for_human_approval_visible():
    preview = _preview()

    assert preview["execution_boundary_state"] == "READY_FOR_HUMAN_APPROVAL"
    assert preview["human_approval_required"] is True


def test_preview_explicitly_marks_execution_authorized_false():
    assert _preview()["execution_authorized"] is False


def test_preview_explicitly_marks_codex_dispatch_authorized_false():
    assert _preview()["codex_dispatch_authorized"] is False


def test_preview_explicitly_marks_governance_execution_approved_false():
    assert _preview()["governance_execution_approved"] is False


def test_preview_explicitly_marks_executable_false():
    assert _preview()["executable"] is False


def test_preview_explicitly_marks_dispatchable_false():
    assert _preview()["dispatchable"] is False


def test_preview_explicitly_marks_preview_only_true():
    assert _preview()["preview_only"] is True


def test_cockpit_renders_governed_task_package_preview_card():
    section = _preview_section()
    combined = "\n".join((section, JS.read_text(encoding="utf-8")))

    assert 'id="governed-task-package-preview-card"' in section
    assert "Governed Task Package Preview" in combined
    assert "GOVERNED_TASK_PACKAGE_PREVIEW_V1" in combined
    assert "preview_hash:" in combined


def test_cockpit_renders_human_approval_required():
    assert "HUMAN APPROVAL REQUIRED" in _preview_section()


def test_cockpit_renders_no_execution():
    assert "NO EXECUTION" in _preview_section()


def test_cockpit_renders_no_codex_dispatch():
    assert "NO CODEX DISPATCH" in _preview_section()


def test_cockpit_contains_no_execution_button():
    section = _preview_section().lower()
    preview_start = section.index('id="governed-task-package-preview-card"')
    fragment = section[preview_start - 360 : preview_start + 900]

    assert "<button" not in fragment
    assert "run governed" not in fragment
    assert "execute task" not in fragment
    assert "dispatch task" not in fragment
    assert "send to codex" not in fragment


def test_native_messaging_execution_path_never_called():
    source = MODULE.read_text(encoding="utf-8")
    preview_source = _preview_source()

    assert "from agol_bridge.native" not in source
    assert "import agol_bridge.native" not in source
    assert "send_native_message" not in source.lower()
    assert "sendNativeMessage" not in preview_source
    assert "runNativeBridgeFromSidepanel" not in preview_source


def test_codex_provider_never_invoked():
    source = MODULE.read_text(encoding="utf-8")
    preview_source = _preview_source()

    assert "codex_cli_provider" not in source
    assert "run_bounded_codex_cli_task" not in source
    assert "codex_cli_provider" not in preview_source
    assert "run_bounded_codex_cli_task" not in preview_source


def test_preview_remains_structural_only_advisory_only():
    preview = _preview()
    section = _preview_section()

    assert preview["classification"] == ["STRUCTURAL_ONLY", "ADVISORY_ONLY"]
    assert "STRUCTURAL_ONLY / ADVISORY_ONLY" in section


def test_stop_boundary_visible_after_preview_state():
    section = _preview_section()

    assert "READY_FOR_HUMAN_APPROVAL" in section
    assert "STOP boundary after READY_FOR_HUMAN_APPROVAL" in section
    assert section.index("READY_FOR_HUMAN_APPROVAL") < section.index("STOP boundary after READY_FOR_HUMAN_APPROVAL")


def test_authority_violation_rejects_preview_creation():
    accepted = evaluate_chatgpt_ingress_acceptance_gate(_artifact())
    import_result = deepcopy(accepted["import_result"])
    import_result["governance_acceptance_report"]["execution_performed"] = True

    preview = create_governed_task_package_preview_from_import_result(import_result)

    assert preview["governance_status"] == PREVIEW_REJECTED


def test_documentation_exists():
    doc = DOC.read_text(encoding="utf-8")

    assert "GOVERNED_TASK_PACKAGE_PREVIEW_V1" in doc
    assert "READY_FOR_HUMAN_APPROVAL" in doc
    assert "Codex is not dispatched" in doc
