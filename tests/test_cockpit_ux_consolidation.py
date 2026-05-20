from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"


def _html():
    return (COMPANION / "sidepanel.html").read_text()


def _js():
    return (COMPANION / "sidepanel.js").read_text()


def _combined():
    return "\n".join((_html(), _js()))


def test_executive_operational_layer_exists():
    html = _html()

    assert "Executive Operational Layer" in html
    assert 'id="executive-operational-summary"' in html
    for label in (
        "SYSTEM STATUS",
        "CONTINUITY STATUS",
        "REPLAY STATUS",
        "LIFECYCLE STATUS",
        "BOUNDARY STATUS",
        "RISK LEVEL",
        "CURRENT MODE",
    ):
        assert label in html


def test_executive_layer_rendering_is_deterministic_and_non_authoritative():
    source = _js()

    assert "function executiveOperationalSummary(entry)" in source
    assert "SYSTEM STATUS: STABLE" in source
    assert "REPLAY STATUS: PRESERVED" in source
    assert "LIFECYCLE STATUS: READ_ONLY" in source
    assert "BOUNDARY STATUS: PRESERVED" in source
    assert "VISIBILITY_ONLY_NOT_APPROVAL_DISPATCH_EXECUTION_OR_CONTINUATION" in source
    assert "setCockpitText(COCKPIT_IDS.executiveOperationalSummary, executiveOperationalSummary(latest));" in source
    assert "Date.now" not in source
    assert "Math.random" not in source
    assert "crypto.randomUUID" not in source


def test_operational_narrative_exists_and_is_deterministic():
    combined = _combined()
    source = _js()

    assert "Operational Narrative" in combined
    assert 'id="operational-narrative"' in combined
    assert "function operationalNarrative(entry)" in source
    assert "Governance continuity is stable." in source
    assert "Replay visibility is preserved." in source
    assert "No authority violations detected." in source
    assert "Lifecycle visibility remains read-only." in source
    assert "never implies execution readiness" in combined
    assert "setCockpitText(COCKPIT_IDS.operationalNarrative, operationalNarrative(latest));" in source


def test_grouping_structure_exists_for_operator_workflows():
    html = _html()

    for group in ("Governance", "Replay", "Lifecycle", "Semantic", "Authority", "Inspection"):
        assert f'aria-label="{group}"' in html
        assert f"<legend>{group}</legend>" in html


def test_progressive_disclosure_and_artifact_inspection_remain_available():
    html = _html()

    assert "Deep inspection" not in html or "Inspection" in html
    assert html.count("<details class=\"cockpit-panel inspection-panel\">") == 8
    for section_id in (
        "inspection-envelope-validation-artifact",
        "inspection-validator-composition-artifact",
        "inspection-continuity-report-artifact",
        "inspection-replay-summary-artifact",
        "inspection-lifecycle-summary-artifact",
        "inspection-lineage-summary-artifact",
        "inspection-authority-boundary-artifact",
        "inspection-semantic-boundary-artifact",
        "semantic-proposal-artifact",
        "replay-entry-inspection",
    ):
        assert f'id="{section_id}"' in html


def test_authority_boundary_labels_are_preserved_and_reinforced():
    combined = _combined()

    assert "not approval, dispatch, execution, or continuation authority" in combined
    assert "This is not an approval control and grants no execution authority." in combined
    assert "no hidden execution, no automatic dispatch, no hidden persistence" in combined
    assert "CONTINUITY_VALID is not approval, dispatch, execution, or continuation" in combined
    assert "Import creates no provider call, approval, dispatch, execution, or continuation authority." in combined
    assert "replay visibility creates no provider call, dispatch, approval, execution, or continuation" in combined


def test_no_replay_or_lifecycle_mutation_is_introduced():
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
    )

    for token in forbidden:
        assert token not in source
    assert "lifecycle_mutation: false" in source
    assert "replay_mutation: false" in source


def test_no_provider_dispatch_approval_execution_or_persistence_semantics_added():
    lowered = _combined().lower()
    forbidden = (
        "fetch(",
        "xmlhttprequest",
        "chrome.storage",
        "localstorage",
        "sessionstorage",
        "indexeddb",
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


def test_rendering_still_uses_safe_text_content_and_canonical_json():
    source = _js()

    assert "node.textContent = value;" in source
    assert "JSON.stringify(canonicalize(value || {}), null, 2)" in source
    assert "lifecycleEntries.push(canonicalize(summary));" in source
    assert "replaySessionEntries.push(replaySessionEntry(canonicalSummary, replaySessionEntries.length));" in source
    assert "innerHTML" not in source
