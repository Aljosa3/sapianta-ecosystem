from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"
REPORT = ROOT / "SIDEPANEL_CORE_FLOW_REORGANIZATION_V1.md"


def _html() -> str:
    return (COMPANION / "sidepanel.html").read_text(encoding="utf-8")


def _js() -> str:
    return (COMPANION / "sidepanel.js").read_text(encoding="utf-8")


def _combined() -> str:
    return "\n".join((_html(), _js()))


def test_core_flow_is_visible_and_dominant():
    html = _html()

    assert 'id="core-flow-controls"' in html
    assert "Core Flow" in html
    assert "Human Request -> Semantic Contract -> AiGOL Governance Gateway -> Canonical Task Package -> Codex Execution -> Structural Verification -> Governed Return" in html
    assert html.index('id="core-flow-controls"') < html.index('id="advanced-debug-controls"')
    assert html.index('id="core-flow-controls"') < html.index('id="legacy-experimental-controls"')
    assert html.index('id="core-flow-controls"') < html.index('id="governance-chat-return"')
    assert html.index('id="governance-chat-return"') < html.index('id="governed-execution-observatory"')


def test_canonical_runtime_controls_remain_primary():
    html = _html()
    core = html[html.index('id="core-flow-controls"') : html.index('id="advanced-debug-controls"')]

    assert 'id="chat-first-human-request"' in core
    assert 'id="local-transport-session-id"' in core
    assert 'id="run-native-bridge"' in core
    assert "Run via Native Bridge" in core


def test_advanced_debug_is_collapsed_and_contains_debug_controls():
    html = _html()

    assert '<details id="advanced-debug-controls" class="audit-evidence">' in html
    assert '<details id="advanced-debug-controls" class="audit-evidence" open>' not in html
    advanced = html[html.index('id="advanced-debug-controls"') : html.index('id="legacy-experimental-controls"')]

    for section_id in (
        "semantic-proposal-file",
        "bridge-result-artifact-file",
        "import-semantic-proposal-file",
        "import-canonical-bridge-result",
        "attach-local-governed-transport",
        "run-chat-first-governed-flow",
    ):
        assert f'id="{section_id}"' in advanced


def test_legacy_experimental_is_collapsed_and_labeled_noncanonical():
    html = _html()

    assert '<details id="legacy-experimental-controls" class="audit-evidence">' in html
    assert '<details id="legacy-experimental-controls" class="audit-evidence" open>' not in html
    legacy = html[html.index('id="legacy-experimental-controls"') : html.index('class="lifecycle-shell"')]

    assert "Legacy / Experimental - NON-CANONICAL" in legacy
    assert "JS Demo Bridge" in legacy
    assert "Run mock governed execution" in legacy
    assert "Preview intent" in legacy
    assert "Request execution authorization" in legacy
    assert "These do not replace the canonical Native Bridge core flow" in legacy


def test_pre_observatory_narration_is_collapsed_into_advanced_summaries():
    html = _html()

    assert '<details id="advanced-summary-cards" class="audit-evidence">' in html
    assert '<details id="advanced-summary-cards" class="audit-evidence" open>' not in html
    summary_block = html[html.index('id="advanced-summary-cards"') : html.index('id="governance-chat-return"')]

    assert "Executive Governance Layer" in summary_block
    assert "Operator Event Stream" in summary_block
    assert "Chat-first Result Card" in summary_block


def test_observability_and_governance_labels_are_preserved():
    combined = _combined()

    for label in (
        "ENFORCED",
        "STRUCTURAL_ONLY",
        "ADVISORY_ONLY",
        "UI_ONLY",
        "Governed Execution Observatory",
        "Semantic Contract",
        "AiGOL Governance Gateway",
        "Canonical Governed Task Package",
        "Codex Execution Layer",
        "AiGOL Post-Execution Verification",
        "Governed Return Layer",
    ):
        assert label in combined


def test_audit_evidence_and_raw_inspection_remain_available():
    html = _html()

    assert '<details id="audit-evidence" class="audit-evidence">' in html
    assert '<details id="audit-evidence" class="audit-evidence" open>' not in html
    for section_id in (
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
        assert f'id="{section_id}"' in html


def test_no_runtime_capability_or_transport_added():
    combined = _combined().lower().replace("codex dispatch", "codex-dispatch-claim")

    forbidden = (
        "xmlhttprequest",
        "websocket",
        "eventsource",
        "setinterval",
        "provider.call",
        "dispatchtask",
        "approvetask",
        "orchestrationruntime",
        "autonomouscontinuation",
        "localstorage",
        "sessionstorage",
        "indexeddb",
        "chrome.storage",
    )
    for token in forbidden:
        assert token not in combined


def test_reorganization_document_exists():
    report = REPORT.read_text(encoding="utf-8")

    assert "SIDEPANEL_CORE_FLOW_REORGANIZATION_V1" in report
    assert "Core Flow" in report
    assert "Advanced Debug" in report
    assert "Legacy / Experimental" in report
