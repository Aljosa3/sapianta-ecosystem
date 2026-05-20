from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"


def _html():
    return (COMPANION / "sidepanel.html").read_text()


def _js():
    return (COMPANION / "sidepanel.js").read_text()


def _combined():
    return "\n".join((_html(), _js()))


def test_executive_governance_layer_exists():
    html = _html()

    assert "Executive Governance Layer" in html
    assert 'id="executive-governance-summary"' in html
    for state in (
        "SAFE_REVIEW_ONLY",
        "BLOCKED",
        "INTEGRITY_VERIFIED",
        "SESSION_REPLAY_ONLY",
        "CONTINUITY_VISIBLE",
    ):
        assert state in html


def test_three_level_evidence_hierarchy_exists():
    html = _html()

    assert "Level 1: Compact Operator Summary" in html
    assert "Level 2: Governance Findings / Risks / Recommendations" in html
    assert "Level 3: Full Artifact Inspection" in html
    assert "Raw artifact evidence remains available and unchanged." in html


def test_replay_simplification_label_exists():
    html = _html()

    assert 'id="session-replay-only-summary"' in html
    assert "SESSION_REPLAY_ONLY: current sidepanel session visibility only." in html
    assert "Replay is session-local, read-only, visibility-only, not durable, not mutation, and not repair." in html


def test_authority_compression_label_exists():
    html = _html()

    assert 'id="compact-authority-summary"' in html
    assert "SEMANTIC_TRANSPORT_ONLY" in html
    for label in (
        "NO_APPROVAL",
        "NO_DISPATCH",
        "NO_EXECUTION",
        "NO_PROVIDER_CALLS",
        "NO_ORCHESTRATION",
        "NO_AUTONOMOUS_CONTINUATION",
    ):
        assert label in html


def test_semantic_clarification_labels_prevent_confusion():
    html = _html()

    assert "HASH_VERIFIED: artifact integrity only, not semantic correctness." in html
    assert "CERTIFIED_FOR_CONTINUITY_INGESTION: continuity-ingestion readiness, not approval." in html
    assert "CONTINUITY_VISIBLE: evidence visibility, not execution authorization." in html
    assert "SESSION_REPLAY_ONLY: session-local visibility, not durable replay persistence." in html


def test_raw_artifact_inspection_still_exists():
    html = _html()

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


def test_no_artifact_rendering_removed_from_sidepanel_js():
    source = _js()

    for render_call in (
        "setCockpitText(COCKPIT_IDS.envelopeValidationArtifact, artifactJson(latest.envelope_validation_report));",
        "setCockpitText(COCKPIT_IDS.validatorCompositionArtifact, artifactJson(latest.validator_composition_report));",
        "setCockpitText(COCKPIT_IDS.continuityReportArtifact, artifactJson(continuityReport(latest)));",
        "setCockpitText(COCKPIT_IDS.replaySummaryArtifact, artifactJson(replaySummaryArtifact(latest)));",
        "setCockpitText(COCKPIT_IDS.lifecycleSummaryArtifact, artifactJson(lifecycleSummaryArtifact(latest)));",
        "setCockpitText(COCKPIT_IDS.lineageSummaryArtifact, artifactJson(lineageSummaryArtifact(latest)));",
        "setCockpitText(COCKPIT_IDS.authorityBoundaryArtifact, artifactJson(authorityBoundaryArtifact(latest)));",
        "setCockpitText(COCKPIT_IDS.semanticBoundaryArtifact, artifactJson(semanticBoundaryArtifact(latest)));",
        "setCockpitText(COCKPIT_IDS.semanticProposalArtifact, artifactJson(semanticProposalArtifact(latest)));",
    ):
        assert render_call in source


def test_no_runtime_behavior_changed():
    source = _js()

    assert "function importSemanticProposalFileFromSidepanel()" in source
    assert "await localSemanticProposalFileValidation(rawText, file.name)" in source
    assert "verifySemanticProposalArtifactHash(validation.proposal)" in source
    assert "window.sidepanelRenderResult(result);" in source
    assert "lifecycleEntries.push(canonicalize(summary));" in source
    assert "replaySessionEntries.push(replaySessionEntry(canonicalSummary, replaySessionEntries.length));" in source


def test_no_provider_dispatch_execution_or_orchestration_introduced():
    lowered = _combined().lower().replace("codex dispatch", "codex-dispatch-claim")

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
        "orchestrationruntime",
        "autonomouscontinuation",
        "setinterval",
        "settimeout",
        "websocket",
    )
    for token in forbidden:
        assert token not in lowered


def test_deterministic_rendering_preserved():
    source = _js()

    assert "node.textContent = value;" in source
    assert "JSON.stringify(canonicalize(value || {}), null, 2)" in source
    assert "deterministicId(" in source
    assert "Date.now" not in source
    assert "Math.random" not in source
    assert "crypto.randomUUID" not in source
    assert "innerHTML" not in source
