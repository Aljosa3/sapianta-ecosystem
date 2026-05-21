import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"


def _manifest():
    return json.loads((COMPANION / "manifest.json").read_text())


def _sidepanel_html():
    return (COMPANION / "sidepanel.html").read_text()


def _sidepanel_js():
    return (COMPANION / "sidepanel.js").read_text()


def test_manifest_exposes_persistent_side_panel_entry_without_broadening_hosts():
    manifest = _manifest()
    assert manifest["side_panel"]["default_path"] == "sidepanel.html"
    assert manifest["permissions"] == ["nativeMessaging", "sidePanel"]
    assert manifest["host_permissions"] == ["http://127.0.0.1:8110/*"]


def test_popup_exposes_explicit_sidepanel_launcher():
    html = (COMPANION / "popup.html").read_text()
    source = (COMPANION / "popup.js").read_text()
    assert 'id="open-sidepanel"' in html
    assert "function openPersistentSidePanel()" in source
    assert 'chrome.sidePanel.open({ windowId: window.id });' in source


def test_sidepanel_preserves_existing_governed_controls():
    html = _sidepanel_html()
    for control_id in (
        "preview",
        "confirm",
        "transfer-export",
        "transfer-ingest",
        "export",
        "authorize",
        "consume",
        "codex-execute",
        "observe",
        "invoke",
    ):
        assert f'id="{control_id}"' in html
    assert '<script src="popup.js"></script>' in html


def test_sidepanel_renders_scrollable_session_lifecycle_output():
    html = _sidepanel_html()
    source = _sidepanel_js()
    assert 'id="result"' in html
    assert "Operational lifecycle" in html
    assert "overflow: auto;" in html
    assert "const lifecycleEntries = [];" in source
    assert "window.sidepanelRenderResult = function renderLifecycleResult(summary)" in source
    assert "lifecycleEntries.push(canonicalize(summary));" in source
    assert "result.append(entry);" in source
    assert "result.scrollTop = result.scrollHeight;" in source


def test_sidepanel_replay_cockpit_sections_exist():
    html = _sidepanel_html()
    for section_id in (
        "replay-timeline",
        "lifecycle-view",
        "approval-visibility",
        "governance-boundary",
        "constitutional-layer",
        "semantic-direction",
    ):
        assert f'id="{section_id}"' in html
    assert "Replay Timeline" in html
    assert "Lifecycle View" in html
    assert "Approval Visibility" in html
    assert "Governance Boundary View" in html
    assert "Constitutional Layer View" in html
    assert "Semantic Direction View" in html


def test_sidepanel_cockpit_labels_prevent_authority_confusion():
    combined = "\n".join((_sidepanel_html(), _sidepanel_js()))
    assert "Transport replay - deterministic package movement evidence" in combined
    assert "Semantic reasoning is model-native and non-deterministic" in combined
    assert "Approval state - visibility only" in combined
    assert "not an approval control" in combined
    assert "grants no execution authority" in combined
    assert "Observability only" in combined
    assert "no automatic dispatch" in combined
    assert "In-memory sidepanel continuity - non-durable" in combined


def test_sidepanel_cockpit_renders_existing_session_entries_only():
    source = _sidepanel_js()
    assert "function renderReadOnlyCockpit()" in source
    assert "lifecycleEntries.map(replaySummary)" in source
    assert "lifecycleEntries.push(canonicalize(summary));" in source
    assert "renderReadOnlyCockpit();" in source
    assert "addEventListener" not in source


def test_sidepanel_adds_no_automatic_dispatch_or_authority_expansion():
    combined = "\n".join((_sidepanel_html(), _sidepanel_js()))
    lowered = combined.lower()
    assert "setinterval" not in lowered
    assert "settimeout" not in lowered
    assert "chrome.storage" not in lowered
    assert "localstorage" not in lowered
    assert "indexeddb" not in lowered
    assert "fetch(" not in lowered
    assert "dispatchtask" not in lowered
    assert "approvetask" not in lowered
    assert "background execution" not in lowered
    assert "sidepanelrenderresult" in lowered


def test_sidepanel_reuses_existing_explicit_governed_runtime_path():
    html = _sidepanel_html()
    popup_source = (COMPANION / "popup.js").read_text()
    assert '<script src="popup.js"></script>' in html
    assert 'addEventListener("click", previewIntent)' in popup_source
    assert 'addEventListener("click", confirmIntentPreview)' in popup_source
    assert 'addEventListener("click", invokeGovernedRuntime)' in popup_source
    assert 'typeof window.sidepanelRenderResult === "function"' in popup_source
    assert 'const LOCAL_ENDPOINT = "http://127.0.0.1:8110/governed-invoke";' in popup_source
