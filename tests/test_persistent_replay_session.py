from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"


def _html():
    return (COMPANION / "sidepanel.html").read_text()


def _js():
    return (COMPANION / "sidepanel.js").read_text()


def _combined():
    return "\n".join((_html(), _js()))


def test_replay_session_ui_exists_with_explicit_load_control():
    html = _html()

    assert "Replay Sessions" in html
    assert 'id="load-replay-session"' in html
    assert "Load Replay" in html
    assert 'id="current-replay-session"' in html
    assert "Replay Entry Inspection" in html
    assert 'id="replay-entry-inspection"' in html
    assert "Explicit loading only" in html


def test_replay_session_is_bounded_in_memory_and_append_only():
    source = _js()

    assert "const replaySessionEntries = [];" in source
    assert 'const REPLAY_SESSION_ID = "PERSISTENT_REPLAY_SESSION_V1";' in source
    assert "replaySessionEntries.push(replaySessionEntry(canonicalSummary, replaySessionEntries.length));" in source
    assert "append_only: true" in source
    assert "rewrite: false" in source
    assert "repair: false" in source
    for token in (".splice(", ".pop(", ".shift(", ".unshift(", ".reverse("):
        assert token not in source


def test_replay_serialization_is_deterministic_and_canonical():
    source = _js()

    assert "function replaySessionEntry(summary, index)" in source
    assert "function replaySessionSummary()" in source
    assert "function loadedReplayInspection()" in source
    assert "artifactJson({" in source
    assert "JSON.stringify(canonicalize(value || {}), null, 2)" in source
    assert 'deterministicId("REPLAY-ENTRY"' in source
    assert "Date.now" not in source
    assert "Math.random" not in source
    assert "crypto.randomUUID" not in source


def test_replay_loading_is_explicit_and_read_only():
    source = _js()

    assert "function loadReplaySession()" in source
    assert "renderReplaySessionVisibility();" in source
    assert "setCockpitText(COCKPIT_IDS.replayEntryInspection, loadedReplayInspection());" in source
    assert 'document.getElementById("load-replay-session")' in source
    assert "loadReplayButton.onclick = loadReplaySession;" in source
    assert "addEventListener" not in source


def test_persisted_continuity_scope_contains_required_summaries():
    source = _js()

    for token in (
        "continuity_report: report",
        "replay_summary: replaySummaryArtifact(entry)",
        "lifecycle_summary: lifecycleSummaryArtifact(entry)",
        "lineage_summary: lineage",
        "authority_boundary_summary: authorityBoundaryArtifact(entry)",
        "semantic_boundary_summary: semanticBoundaryArtifact(entry)",
    ):
        assert token in source


def test_lineage_and_continuity_identity_remain_visible():
    source = _js()

    assert "continuity_report_id: report.continuity_report_id" in source
    assert "lineage_id: lineage.lineage_id" in source
    assert "sequence: index + 1" in source
    assert "entry_count: replaySessionEntries.length" in source


def test_replay_session_adds_no_hidden_or_durable_persistence():
    lowered = _combined().lower()

    forbidden = (
        "chrome.storage",
        "localstorage",
        "sessionstorage",
        "indexeddb",
        "filesystem",
        "filehandle",
        "caches.open",
    )
    for token in forbidden:
        assert token not in lowered
    assert "durable_storage: false" in _js()
    assert "no durable storage" in lowered


def test_replay_session_adds_no_provider_dispatch_execution_or_orchestration():
    lowered = _combined().lower()

    forbidden = (
        "fetch(",
        "xmlhttprequest",
        "provider.call",
        "dispatchtask",
        "approvetask",
        "executeprovider",
        "setinterval",
        "settimeout",
        "websocket",
    )
    for token in forbidden:
        assert token not in lowered


def test_replay_session_adds_no_replay_rewrite_or_lifecycle_transition_path():
    source = _js()

    forbidden = (
        "appendReplay",
        "append_replay",
        "mutateReplay",
        "rewriteReplay",
        "repairReplay",
        "transitionLifecycle",
        "transition_lifecycle",
        "createLifecycleTransition",
        "orchestrate",
        "autonomousContinuation",
        "hiddenPersistence",
    )
    for token in forbidden:
        assert token not in source
    assert "lifecycle_mutation: false" in source
    assert "replay_mutation: false" in source
    assert "autonomous_continuation: false" in source
