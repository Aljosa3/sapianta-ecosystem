from pathlib import Path

import pytest

from agol_bridge.chat_first.chat_first_normalization import prepare_chat_first_transport_envelope
from agol_bridge.transport.local_governed_transport import TRANSPORT_ACCEPTED, handle_local_governed_transport


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"


def _html():
    return (COMPANION / "sidepanel.html").read_text()


def _js():
    return (COMPANION / "sidepanel.js").read_text()


def _combined():
    return "\n".join((_html(), _js()))


def _session_registry():
    return {
        "SESSION-CHAT-FIRST": {
            "operator_visible": True,
            "ambiguous": False,
            "continuation_requested": False,
            "cross_session_mutation": False,
        }
    }


def test_chat_first_request_controls_exist():
    html = _html()

    assert 'id="chat-first-human-request"' in html
    assert 'id="chat-first-requested-mode"' in html
    assert "<option value=\"REVIEW_ONLY\">REVIEW_ONLY</option>" in html
    assert "<option value=\"DEMO_ONLY\">DEMO_ONLY</option>" in html
    assert "<option value=\"READ_ONLY\">READ_ONLY</option>" in html
    assert 'id="run-chat-first-governed-flow"' in html
    assert "Run Chat-first Governed Flow" in html


def test_chat_first_result_card_exists_and_shows_non_authority_note():
    html = _html()

    assert "Chat-first Result Card" in html
    assert 'id="chat-first-result-card"' in html
    assert "RESULT: not run" in html
    assert "AUTHORITY: SEMANTIC_TRANSPORT_ONLY" in html
    assert "NOTE: no execution, no dispatch, no approval" in html


def test_operator_flow_invokes_normalization_transport_and_rendering():
    source = _js()

    assert "function normalizeHumanRequestToSemanticProposal" in source
    assert "function prepareChatFirstTransportEnvelope" in source
    assert "function runChatFirstGovernedFlowFromSidepanel()" in source
    assert "prepareChatFirstTransportEnvelope({" in source
    assert "handle_local_governed_transport({" in source
    assert "window.sidepanelRenderResult(result);" in source
    assert "runChatFirstGovernedFlowButton.onclick = runChatFirstGovernedFlowFromSidepanel;" in source


def test_python_transport_integration_accepts_normalized_request():
    envelope = prepare_chat_first_transport_envelope(
        human_request="Review this chat-first operator flow.",
        session_id="SESSION-CHAT-FIRST",
        requested_mode="REVIEW_ONLY",
    )
    report = handle_local_governed_transport(envelope=envelope, session_registry=_session_registry())

    assert report["status"] == TRANSPORT_ACCEPTED
    assert report["proposal_id"].startswith("CHAT-FIRST-PROPOSAL-")
    assert report["replay_event_id"].startswith("TRANSPORT-REPLAY-")
    assert report["hash_verification_status"] == "HASH_VERIFIED"


def test_empty_request_and_unsafe_mode_are_rejected_in_flow():
    source = _js()

    assert 'return { error: "human_request is required" };' in source
    assert 'return { error: `unsafe requested_mode: ${mode || "UNKNOWN"}` };' in source
    assert "chatFirstBlockedResult({" in source
    for mode in ("EXECUTE", "AUTO_EXECUTE", "PROVIDER_RUNTIME", "ORCHESTRATION", "AUTONOMOUS"):
        assert f'"{mode}"' in source


def test_result_card_renders_accepted_rejected_reason_and_replay_event_id():
    source = _js()

    assert "function chatFirstResultCardSummary(entry)" in source
    assert 'RESULT: ${accepted ? "ACCEPTED" : flow.status || "not run"}' in source
    assert "reason:" in source
    assert "session_id:" in source
    assert "proposal_id:" in source
    assert "replay_event_id:" in source
    assert "integrity_status:" in source
    assert "authority_scope: SEMANTIC_TRANSPORT_ONLY" in source
    assert "note: no execution, no dispatch, no approval" in source


def test_raw_evidence_remains_available():
    html = _html()
    source = _js()

    assert "Inspection" in html
    assert 'id="inspection-continuity-report-artifact"' in html
    assert 'id="inspection-authority-boundary-artifact"' in html
    assert "chat_first_transport_envelope: envelope" in source
    assert "local_governed_transport_report: transportReport" in source


def test_flow_rendering_is_deterministic_without_time_random_or_environment():
    source = _js()

    assert "deterministicId(\"CHAT-FIRST-PROPOSAL\"" in source
    assert "deterministicId(\"CHAT-FIRST-TRANSPORT\"" in source
    assert "deterministicChatFirstArtifactHash(proposal)" in source
    assert "Date(" not in source
    assert "Date.now" not in source
    assert "Math.random" not in source
    assert "crypto.randomUUID" not in source
    assert "process.env" not in source


def test_no_provider_dispatch_approval_execution_or_orchestration_behavior():
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
    )
    for token in forbidden:
        assert token not in lowered
    assert "provider_calls: false" in _js()
    assert "dispatch: false" in _js()
    assert "approval: false" in _js()
    assert "execution: false" in _js()
    assert "orchestration: false" in _js()


def test_no_durable_persistence_or_endpoint_is_added():
    lowered = _combined().lower()

    forbidden = (
        "localstorage",
        "sessionstorage",
        "indexeddb",
        "chrome.storage",
        "governed-semantic-transport",
        "http://localhost",
        "http://127.0.0.1",
        "runtime.onmessage",
    )
    for token in forbidden:
        assert token not in lowered
    assert "serviceworker.register" not in lowered
    assert "navigator.serviceworker" not in lowered
    assert "durable_storage: false" in _js()
    assert "hidden_persistence: false" in _js()


def test_python_normalizer_rejects_unsafe_modes():
    with pytest.raises(ValueError, match="unsafe requested_mode"):
        prepare_chat_first_transport_envelope(
            human_request="Review this safely.",
            session_id="SESSION-CHAT-FIRST",
            requested_mode="EXECUTE",
        )
