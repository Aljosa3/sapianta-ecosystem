from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"


def _html():
    return (COMPANION / "sidepanel.html").read_text(encoding="utf-8")


def _js():
    return (COMPANION / "sidepanel.js").read_text(encoding="utf-8")


def _combined():
    return "\n".join((_html(), _js()))


def test_end_to_end_bridge_controls_and_lifecycle_panel_exist():
    html = _html()

    assert 'id="run-minimal-end-to-end-bridge"' in html
    assert "Run End-to-End Bridge" in html
    assert "Minimal End-to-End Bridge Lifecycle" in html
    assert 'id="end-to-end-bridge-lifecycle"' in html
    assert "HUMAN REQUEST" in html
    assert "SEMANTIC PROPOSAL" in html
    assert "GOVERNED TRANSPORT STATUS" in html
    assert "GOVERNED TASK PACKAGE" in html
    assert "MOCK CODEX RESULT" in html
    assert "RESULT VALIDATION" in html
    assert "GOVERNED CHAT RETURN" in html
    assert "RECOMMENDED NEXT STEP" in html


def test_sidepanel_invokes_existing_runtime_mirror_and_renders_result():
    source = _js()

    assert "function runMinimalEndToEndBridgeFromSidepanel()" in source
    assert "prepareChatFirstTransportEnvelope({" in source
    assert "handle_local_governed_transport({" in source
    assert "bridgeTaskPackage({" in source
    assert "mockCodexBridgeResult({" in source
    assert "validateBridgeResult({" in source
    assert "governedBridgeReturn({" in source
    assert "window.sidepanelRenderResult(result);" in source
    assert "runMinimalEndToEndBridgeButton.onclick = runMinimalEndToEndBridgeFromSidepanel;" in source


def test_accepted_lifecycle_rendering_fields_are_present():
    source = _js()

    assert "function endToEndBridgeLifecycleSummary(entry)" in source
    assert "BRIDGE_ACCEPTED" in source
    assert "TASK_PACKAGED" in source
    assert "MOCK_CODEX_RESULT_RETURNED" in source
    assert "RESULT_VALIDATED" in source
    assert "GOVERNED_TASK_PACKAGE_CREATED" in source
    assert "MOCK_CODEX_RESULT_CREATED" in source
    assert "GOVERNED_RESULT_VALIDATED" in source


def test_rejected_lifecycle_rendering_fields_are_present():
    source = _js()

    assert "function rejectedEndToEndBridgeResult" in source
    assert "BRIDGE_REJECTED" in source
    assert "RESULT_REJECTED" in source
    assert "SEMANTIC_PROPOSAL_REJECTED" in source
    assert "transportStatus: \"NOT_PREPARED\"" in source
    assert "transportReport.rejection_reason" in source
    assert "REJECTION REASON:" in source


def test_compact_governed_return_rendering_is_preserved():
    source = _js()

    assert "governed_chat_return" in source
    assert "governedBridgeReturn" in source
    assert "governed bridge lifecycle accepted with mocked bounded Codex result" in source
    assert "Review the bounded task and mock result evidence before any separate governed action." in source
    assert "No execution occurred. No provider was invoked. No approval, dispatch, or continuation authority was created." in source
    assert "governanceChatReturnSummary(entry)" in source
    assert 'entry.demo_id === "MINIMAL_END_TO_END_BRIDGE_SIDEPANEL_ATTACHMENT_V1"' in source


def test_replay_visibility_rendering_is_compact_and_session_local():
    source = _js()

    assert "function bridgeReplayEvent" in source
    assert "BRIDGE-REPLAY" in source
    assert "SESSION_LOCAL_REPLAY_VISIBLE" in source
    assert "REPLAY EVENT IDS:" in source
    assert "durable_persistence: false" in source
    assert "mutation: false" in source


def test_authority_reminders_are_visible():
    combined = _combined()

    assert "ChatGPT = advisory cognition only" in combined
    assert "AiGOL = governance authority" in combined
    assert "Codex = mocked bounded provider only" in combined
    assert "NO REAL EXECUTION" in combined
    assert "NO PROVIDER CALLS" in combined
    assert "NO AUTONOMOUS CONTINUATION" in combined
    assert "MOCK_CODEX_ONLY_NO_PROVIDER_EXECUTION" in combined
    assert "NO_EXECUTION_AUTHORITY" in combined
    assert "NO_ORCHESTRATION" in combined


def test_no_execution_provider_or_orchestration_behavior_added():
    lowered = _combined().lower()

    forbidden = (
        "fetch(",
        "xmlhttprequest",
        "websocket",
        "eventsource",
        "provider.call",
        "dispatchtask",
        "approvetask",
        "executeprovider",
        "orchestrationruntime",
        "autonomouscontinuation",
        "chatgpt api",
        "llm call",
        "localstorage",
        "sessionstorage",
        "indexeddb",
        "chrome.storage",
    )
    for token in forbidden:
        assert token not in lowered
    assert "provider_calls: false" in _js()
    assert "dispatch: false" in _js()
    assert "approval: false" in _js()
    assert "execution: false" in _js()
    assert "orchestration: false" in _js()
    assert "autonomous_continuation: false" in _js()


def test_rendering_remains_deterministic():
    source = _js()

    assert "deterministicId(\"BRIDGE-REPLAY\"" in source
    assert "deterministicId(\"BRIDGE-TASK\"" in source
    assert "deterministicId(\"MOCK-CODEX-RESULT\"" in source
    assert "deterministicId(\"MOCK-ARTIFACT\"" in source
    assert "Date(" not in source
    assert "Date.now" not in source
    assert "Math.random" not in source
    assert "crypto.randomUUID" not in source
    assert "process.env" not in source
