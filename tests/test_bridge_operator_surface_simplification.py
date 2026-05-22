from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"


def _html():
    return (COMPANION / "sidepanel.html").read_text(encoding="utf-8")


def _js():
    return (COMPANION / "sidepanel.js").read_text(encoding="utf-8")


def _combined():
    return "\n".join((_html(), _js()))


def test_governed_return_is_primary_operator_surface():
    html = _html()

    assert "primary-operator-answer" in html
    assert "Primary operator answer" in html
    assert 'id="governance-chat-return"' in html
    assert html.index('id="governance-chat-return"') < html.index('id="audit-evidence"')
    assert html.index("Governance Chat Return") < html.index("Minimal End-to-End Bridge Lifecycle")


def test_audit_evidence_is_collapsed_by_default():
    html = _html()

    assert '<details id="audit-evidence" class="audit-evidence">' in html
    assert "<summary>Show audit evidence</summary>" in html
    assert '<details id="audit-evidence" class="audit-evidence" open>' not in html


def test_raw_evidence_remains_available_behind_audit_evidence():
    html = _html()
    audit_section = html[html.index('<details id="audit-evidence" class="audit-evidence">') :]

    for section_id in (
        "end-to-end-bridge-lifecycle",
        "canonical-bridge-result-artifact-status",
        "replay-timeline",
        "lifecycle-view",
        "lineage-summary",
        "inspection-envelope-validation-artifact",
        "inspection-validator-composition-artifact",
        "inspection-continuity-report-artifact",
        "inspection-replay-summary-artifact",
        "inspection-lifecycle-summary-artifact",
        "inspection-lineage-summary-artifact",
        "inspection-authority-boundary-artifact",
        "inspection-semantic-boundary-artifact",
    ):
        assert f'id="{section_id}"' in audit_section
    assert html.count('<details class="cockpit-panel inspection-panel">') == 8


def test_replay_ids_are_not_primary_operator_surface():
    html = _html()
    primary_surface = html[: html.index('<details id="audit-evidence" class="audit-evidence">')]
    audit_section = html[html.index('<details id="audit-evidence" class="audit-evidence">') :]

    assert "REPLAY EVENT IDS" not in primary_surface
    assert "REPLAY EVENT IDS" in _js()
    assert 'id="replay-timeline"' in audit_section


def test_authority_labels_remain_visible():
    combined = _combined()
    primary_surface = _html()[: _html().index('<details id="audit-evidence" class="audit-evidence">')]

    assert "ChatGPT = advisory cognition only" in primary_surface
    assert "AiGOL = governance authority" in primary_surface
    assert "Codex = bounded CLI provider only" in primary_surface
    assert "REAL CODEX EXECUTION / BOUNDED CODEX CLI ONLY" in primary_surface
    assert "SEMANTIC_TRANSPORT_ONLY" in combined
    assert "NO_APPROVAL" in combined
    assert "NO_DISPATCH" in combined
    assert "BOUNDED_CODEX_CLI_PROVIDER" in combined


def test_governed_return_rendering_carries_authority_summary():
    source = _js()

    assert "function governanceChatReturnSummary(entry)" in source
    assert "Authority: ChatGPT = advisory cognition only; AiGOL = governance authority; Codex = bounded CLI provider only." in source
    assert "REAL CODEX EXECUTION / BOUNDED CODEX CLI ONLY" in source


def test_no_execution_provider_or_orchestration_added():
    lowered = _combined().lower().replace("codex dispatch", "codex-dispatch-claim")

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


def test_deterministic_rendering_preserved():
    source = _js()

    assert "governanceChatReturnSummary(latest)" in source
    assert "setCockpitText(COCKPIT_IDS.endToEndBridgeLifecycle, endToEndBridgeLifecycleSummary(latest));" in source
    assert "setCockpitText(COCKPIT_IDS.canonicalBridgeResultArtifactStatus, canonicalBridgeResultArtifactStatusSummary(latest));" in source
    assert "Date.now" not in source
    assert "Math.random" not in source
    assert "crypto.randomUUID" not in source
    assert "innerHTML" not in source
