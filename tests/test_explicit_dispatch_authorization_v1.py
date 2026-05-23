from copy import deepcopy
from pathlib import Path

from agol_bridge.chatgpt_ingress import create_chatgpt_ingress_artifact
from agol_bridge.chatgpt_ingress.explicit_dispatch_authorization import (
    ALLOWED_DISPATCH_AUTHORIZATION_STATUSES,
    DISPATCH_AUTHORIZED,
    DISPATCH_REJECTED,
    READY_FOR_CONTROLLED_EXECUTION_CONTINUITY,
    create_explicit_dispatch_authorization,
    validate_explicit_dispatch_authorization,
)
from agol_bridge.chatgpt_ingress.governed_handoff_package_preview import create_governed_handoff_package_preview
from agol_bridge.chatgpt_ingress.governed_task_package_preview import create_governed_task_package_preview
from agol_bridge.chatgpt_ingress.human_approval_gate import create_human_approval_gate


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "browser_companion" / "sidepanel.html"
JS = ROOT / "browser_companion" / "sidepanel.js"
MODULE = ROOT / "agol_bridge" / "chatgpt_ingress" / "explicit_dispatch_authorization.py"
DOC = ROOT / "EXPLICIT_DISPATCH_AUTHORIZATION_V1.md"


def _artifact():
    return create_chatgpt_ingress_artifact(
        created_at="1970-01-01T00:00:00Z",
        session_id="CHATGPT-DISPATCH-AUTH-SESSION-1",
        human_request="Authorize dispatch preview evidence.",
        chatgpt_semantic_output="The request asks for explicit dispatch authorization evidence only.",
        normalized_intent="AUTHORIZE_DISPATCH_PREVIEW_EVIDENCE",
        expected_artifacts=["explicit dispatch authorization"],
        constraints=["dispatch authorization only", "no execution", "provider boundary only"],
        forbidden_operations=["Codex dispatch", "Native Messaging execution", "provider execution"],
        provenance={"source_conversation_id": "CONV-DISPATCH-AUTH-1"},
    )


def _task_preview():
    return create_governed_task_package_preview(_artifact())


def _approval(task_preview=None):
    task = task_preview or _task_preview()
    return create_human_approval_gate(
        preview=task,
        human_decision="APPROVE",
        approval_reason="Operator approved dispatch authorization preview setup.",
        operator_label="TEST_OPERATOR",
        created_at="1970-01-01T00:00:00Z",
    )


def _handoff():
    task = _task_preview()
    return create_governed_handoff_package_preview(
        task_package_preview=task,
        human_approval=_approval(task),
    )


def _authorization(handoff_preview=None, decision="AUTHORIZE"):
    return create_explicit_dispatch_authorization(
        handoff_preview=handoff_preview or _handoff(),
        dispatch_decision=decision,
        dispatch_authorization_reason="Operator created explicit dispatch authorization evidence.",
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


def test_valid_governed_handoff_preview_can_be_dispatch_authorized():
    authorization = _authorization(decision="AUTHORIZE")

    assert authorization["artifact_type"] == "EXPLICIT_DISPATCH_AUTHORIZATION_V1"
    assert authorization["dispatch_authorization_status"] == DISPATCH_AUTHORIZED
    assert authorization["provider_boundary_state"] == READY_FOR_CONTROLLED_EXECUTION_CONTINUITY
    assert validate_explicit_dispatch_authorization(authorization)["valid"] is True


def test_valid_governed_handoff_preview_can_be_dispatch_rejected():
    authorization = _authorization(decision="REJECT")

    assert authorization["dispatch_authorization_status"] == DISPATCH_REJECTED
    assert authorization["dispatch_authorized"] is False
    assert validate_explicit_dispatch_authorization(authorization)["valid"] is True


def test_missing_handoff_preview_blocks_authorization():
    authorization = create_explicit_dispatch_authorization(
        handoff_preview=None,
        dispatch_decision="AUTHORIZE",
        dispatch_authorization_reason="missing handoff preview",
    )

    assert authorization["dispatch_authorization_status"] == DISPATCH_REJECTED


def test_invalid_replay_identity_blocks_authorization():
    handoff = _handoff()
    handoff["replay_identity"] = ""

    authorization = _authorization(handoff_preview=handoff)

    assert authorization["dispatch_authorization_status"] == DISPATCH_REJECTED


def test_missing_provenance_blocks_authorization():
    handoff = _handoff()
    handoff["provenance"] = {}

    authorization = _authorization(handoff_preview=handoff)

    assert authorization["dispatch_authorization_status"] == DISPATCH_REJECTED


def test_invalid_hashes_block_authorization():
    handoff = _handoff()
    handoff["handoff_preview_hash"] = "sha256:BROKEN"

    authorization = _authorization(handoff_preview=handoff)

    assert authorization["dispatch_authorization_status"] == DISPATCH_REJECTED


def test_dispatch_authorization_hash_deterministic():
    first = _authorization()["dispatch_authorization_hash"]
    second = _authorization()["dispatch_authorization_hash"]

    assert first == second
    assert first.startswith("sha256:")


def test_status_only_allows_authorized_or_rejected():
    assert ALLOWED_DISPATCH_AUTHORIZATION_STATUSES == (
        DISPATCH_AUTHORIZED,
        DISPATCH_REJECTED,
    )
    assert _authorization()["dispatch_authorization_status"] in ALLOWED_DISPATCH_AUTHORIZATION_STATUSES
    assert _authorization(decision="REJECT")["dispatch_authorization_status"] in ALLOWED_DISPATCH_AUTHORIZATION_STATUSES


def test_dispatch_authorization_never_performs_execution():
    assert _authorization()["execution_performed"] is False


def test_dispatch_authorization_never_dispatches_codex():
    assert _authorization()["codex_dispatch_performed"] is False


def test_dispatch_authorization_never_invokes_provider_execution():
    assert _authorization()["provider_dispatch_performed"] is False


def test_dispatch_authorization_never_calls_native_messaging():
    assert _authorization()["native_messaging_called"] is False


def test_dispatch_authorization_never_authorizes_autonomous_continuation():
    assert _authorization()["autonomous_continuation_performed"] is False


def test_dispatch_authorization_remains_non_executable_and_not_dispatched():
    authorization = _authorization()

    assert authorization["executable"] is False
    assert authorization["dispatched"] is False


def test_mutated_authorization_hash_is_invalid():
    authorization = deepcopy(_authorization())
    authorization["dispatch_authorization_hash"] = "sha256:BROKEN"

    assert validate_explicit_dispatch_authorization(authorization)["valid"] is False


def test_cockpit_renders_explicit_dispatch_authorization_card():
    section = _preview_section()

    assert 'id="explicit-dispatch-authorization-card"' in section
    assert "Explicit Dispatch Authorization" in section
    assert "EXPLICIT_DISPATCH_AUTHORIZATION_V1" in section


def test_cockpit_renders_authorize_dispatch_preview_button():
    section = _preview_section()

    assert 'id="authorize-dispatch-preview"' in section
    assert "Authorize Dispatch Preview" in section


def test_cockpit_renders_reject_dispatch_preview_button():
    section = _preview_section()

    assert 'id="reject-dispatch-preview"' in section
    assert "Reject Dispatch Preview" in section


def test_cockpit_renders_dispatch_authorized_and_rejected_labels():
    combined = "\n".join((_preview_section(), JS.read_text(encoding="utf-8")))

    assert "DISPATCH_AUTHORIZED" in combined
    assert "DISPATCH_REJECTED" in combined


def test_cockpit_renders_no_execution():
    assert "NO EXECUTION" in _preview_section()


def test_cockpit_renders_no_codex_dispatch():
    assert "NO CODEX DISPATCH" in _preview_section()


def test_cockpit_renders_no_provider_execution():
    assert "NO PROVIDER EXECUTION" in _preview_section()


def test_cockpit_renders_native_messaging_not_called():
    assert "NATIVE MESSAGING NOT CALLED" in _preview_section()


def test_cockpit_renders_stop_boundary():
    assert "STOP boundary after EXPLICIT DISPATCH AUTHORIZATION" in _preview_section()


def test_cockpit_contains_no_run_execute_dispatch_execution_button():
    section = _preview_section().lower()
    start = section.index('id="explicit-dispatch-authorization-card"')
    fragment = section[start - 420 : start + 1000]

    assert "run" not in fragment
    assert "execute" not in fragment
    assert "dispatch execution" not in fragment
    assert "send to codex" not in fragment


def test_native_messaging_runtime_path_is_not_called():
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


def test_documentation_exists():
    doc = DOC.read_text(encoding="utf-8")

    assert "EXPLICIT_DISPATCH_AUTHORIZATION_V1" in doc
    assert "dispatch authorization != execution continuity" in doc
    assert "Native Messaging is not called" in doc
