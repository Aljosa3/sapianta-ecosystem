from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"


def _html():
    return (COMPANION / "sidepanel.html").read_text()


def _js():
    return (COMPANION / "sidepanel.js").read_text()


def _combined():
    return "\n".join((_html(), _js()))


def test_continuity_artifact_inspection_sections_exist():
    html = _html()
    sections = {
        "inspection-envelope-validation-artifact": "Envelope Validation Artifact",
        "inspection-validator-composition-artifact": "Validator Composition Artifact",
        "inspection-continuity-report-artifact": "Continuity Report Artifact",
        "inspection-replay-summary-artifact": "Replay Summary Artifact",
        "inspection-lifecycle-summary-artifact": "Lifecycle Summary Artifact",
        "inspection-lineage-summary-artifact": "Lineage Summary Artifact",
        "inspection-authority-boundary-artifact": "Authority Boundary Artifact",
        "inspection-semantic-boundary-artifact": "Semantic Boundary Artifact",
    }

    for section_id, title in sections.items():
        assert f'id="{section_id}"' in html
        assert title in html
    assert html.count("<details class=\"cockpit-panel inspection-panel\">") == len(sections)


def test_inspection_rendering_uses_deterministic_json_text_content():
    source = _js()

    assert "function artifactJson(value)" in source
    assert "JSON.stringify(canonicalize(value || {}), null, 2)" in source
    assert "node.textContent = value;" in source
    assert "innerHTML" not in source
    assert "Math.random" not in source
    assert "Date.now" not in source
    assert "crypto.randomUUID" not in source


def test_inspection_artifact_helpers_cover_required_artifacts():
    source = _js()
    helpers = (
        "function replaySummaryArtifact(entry)",
        "function lifecycleSummaryArtifact(entry)",
        "function lineageSummaryArtifact(entry)",
        "function authorityBoundaryArtifact(entry)",
        "function semanticBoundaryArtifact(entry)",
    )

    for helper in helpers:
        assert helper in source
    assert "latest.envelope_validation_report" in source
    assert "latest.validator_composition_report" in source
    assert "artifactJson(continuityReport(latest))" in source


def test_replay_lifecycle_and_lineage_inspection_are_read_only():
    combined = _combined()

    assert "Inspection does not append, rewrite, or mutate replay." in combined
    assert "Inspection creates no lifecycle transition." in combined
    assert "Inspection does not mutate lineage." in combined
    assert "REFERENCED_NOT_MUTATED" in combined
    assert "VISIBLE_APPEND_ONLY_REFERENCE" in combined
    assert "mutation: false" in combined


def test_authority_and_semantic_boundary_inspection_prevents_confusion():
    combined = _combined()

    assert "Inspection grants no approval, dispatch, or execution authority." in combined
    assert "Semantic cognition remains non-authoritative." in combined
    assert "VALID and CONTINUITY_VALID are not approval, dispatch, execution, or continuation authority." in combined
    assert "semantic_authority: false" in combined
    assert "hidden_authority: false" in combined


def test_inspection_adds_no_provider_dispatch_execution_or_persistence_path():
    lowered = _combined().lower()
    forbidden = (
        "fetch(",
        "xmlhttprequest",
        "chrome.storage",
        "localstorage",
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


def test_inspection_adds_no_replay_lifecycle_mutation_or_orchestration_path():
    source = _js()
    forbidden = (
        "appendReplay",
        "append_replay",
        "mutateReplay",
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
