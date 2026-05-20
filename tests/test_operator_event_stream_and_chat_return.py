from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"


def _html():
    return (COMPANION / "sidepanel.html").read_text()


def _js():
    return (COMPANION / "sidepanel.js").read_text()


def _combined():
    return "\n".join((_html(), _js()))


def test_operator_event_stream_renders():
    html = _html()
    source = _js()

    assert "Operator Event Stream" in html
    assert 'id="operator-event-stream"' in html
    assert "function operatorEventStreamSummary(entry)" in source
    assert "Human request received" in source
    assert "Semantic proposal normalized" in source
    assert "Semantic proposal validated" in source
    assert "Hash verified" in source
    assert "Transport envelope prepared" in source
    assert "Governed transport attached" in source
    assert "Replay append candidate created" in source
    assert "Governed transport accepted" in source
    assert "Governed transport rejected" in source


def test_accepted_flow_creates_success_events():
    source = _js()

    assert 'operatorEventLine(8, accepted ? "SUCCESS" : "REJECTED", finalLabel' in source
    assert 'operatorEventLine(6, attachOk ? "SUCCESS" : "BLOCKED", "Governed transport attached"' in source
    assert 'operatorEventLine(7, replayOk ? "SUCCESS" : "BLOCKED", "Replay append candidate created"' in source
    assert 'const accepted = report.status === "TRANSPORT_ACCEPTED";' in source


def test_rejected_flow_creates_rejection_event():
    source = _js()

    assert 'operatorEventLine(8, accepted ? "SUCCESS" : "REJECTED", finalLabel' in source
    assert "latestActionReason(entry)" in source
    assert "TRANSPORT_REJECTED_SCHEMA" in source
    assert "TRANSPORT_REJECTED_UNSAFE_MODE" in source
    assert "TRANSPORT_REJECTED_AUTHORITY" in source


def test_action_result_card_renders_accepted_and_rejected_state():
    html = _html()
    source = _js()

    assert "Latest Action Result" in html
    assert 'id="latest-action-result-card"' in html
    assert "function latestActionResultCardSummary(entry)" in source
    assert "Governed transport accepted" in source
    assert "Governed transport rejected" in source
    assert "Reason:" in source
    assert "Replay: ${latestReplayStatus(entry)}" in source
    assert "Authority: SEMANTIC_TRANSPORT_ONLY" in source
    assert "No execution occurred." in source
    assert "No provider invoked." in source


def test_audit_evidence_is_collapsed_by_default_and_raw_evidence_remains():
    html = _html()

    assert '<details id="audit-evidence" class="audit-evidence">' in html
    assert "<summary>Show audit evidence</summary>" in html
    assert '<details id="audit-evidence" class="audit-evidence" open>' not in html
    assert 'id="replay-timeline"' in html
    assert 'id="lifecycle-view"' in html
    assert 'id="continuity-status"' in html
    assert 'id="lineage-summary"' in html
    assert 'id="inspection-continuity-report-artifact"' in html
    assert 'id="inspection-validator-composition-artifact"' in html
    assert html.count('<details class="cockpit-panel inspection-panel">') == 8


def test_governance_chat_return_renders_deterministic_text():
    html = _html()
    source = _js()

    assert "Governance Chat Return" in html
    assert 'id="governance-chat-return"' in html
    assert "readonly" in html
    assert "function governanceChatReturnSummary(entry)" in source
    assert "Governed transport accepted" in source
    assert "Governed transport rejected" in source
    assert "Mode: ${latestActionMode(entry)}" in source
    assert "Integrity:" in source
    assert "Replay:" in source
    assert "Authority: SEMANTIC_TRANSPORT_ONLY" in source


def test_non_authority_labels_are_preserved():
    combined = _combined()

    assert "SEMANTIC_TRANSPORT_ONLY" in combined
    assert "No execution occurred." in combined
    assert "No provider invoked." in combined
    assert "not approval, dispatch, execution, orchestration, or autonomous continuation" in combined
    assert "visibility only and does not approve, dispatch, execute, call providers, or continue autonomously" in combined


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


def test_rendering_is_deterministic():
    source = _js()

    assert "operatorEventLine(sequence, status, label, reason)" in source
    assert "String(sequence).padStart(3, \"0\")" in source
    assert "governanceChatReturnSummary(latest)" in source
    assert "latestActionResultCardSummary(latest)" in source
    assert "operatorEventStreamSummary(latest)" in source
    assert "Date(" not in source
    assert "Date.now" not in source
    assert "Math.random" not in source
    assert "crypto.randomUUID" not in source
    assert "process.env" not in source
