from pathlib import Path

from agol_bridge.continuity.minimal_operational_loop_demo import run_minimal_governed_operational_loop_demo


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "browser_companion"


def _html():
    return (COMPANION / "sidepanel.html").read_text()


def _js():
    return (COMPANION / "sidepanel.js").read_text()


def _combined():
    return "\n".join((_html(), _js()))


def test_sidepanel_continuity_sections_exist():
    html = _html()
    for section_id in (
        "continuity-human-request",
        "envelope-validation-status",
        "validator-composition-status",
        "continuity-status",
        "lineage-summary",
        "continuity-findings",
    ):
        assert f'id="{section_id}"' in html
    assert "Human Request" in html
    assert "Envelope Validation Status" in html
    assert "Validator Composition Status" in html
    assert "Continuity Status" in html
    assert "Findings / Risks / Recommendations" in html


def test_continuity_rendering_helpers_are_deterministic_and_read_only():
    source = _js()
    for helper in (
        "function continuityHumanRequestSummary(entry)",
        "function envelopeValidationStatusSummary(entry)",
        "function validatorCompositionStatusSummary(entry)",
        "function continuityStatusSummary(entry)",
        "function lineageSummary(entry)",
        "function continuityFindingsSummary(entry)",
    ):
        assert helper in source
    assert "setCockpitText(COCKPIT_IDS.continuityStatus, continuityStatusSummary(latest));" in source
    assert "lifecycleEntries.push(canonicalize(summary));" in source


def test_continuity_rendering_labels_prevent_authority_confusion():
    combined = _combined()
    assert "request context does not approve, dispatch, or execute" in combined
    assert "validation success is not approval" in combined
    assert "aggregate valid is not dispatch" in combined
    assert "CONTINUITY_VALID is not approval, dispatch, execution, or continuation" in combined
    assert "Lineage Summary - visibility without mutation" in combined
    assert "Report-only continuity findings, risks, and recommendations" in combined
    assert "No autonomous continuation" in combined


def test_replay_lifecycle_authority_and_semantic_visibility_labels_exist():
    combined = _combined()
    assert "Replay Visibility" not in combined or "Replay Timeline" in combined
    assert "Transport replay - deterministic package movement evidence" in combined
    assert "Lifecycle state - governed transport state" in combined
    assert "Visualization creates no lifecycle transition" in combined
    assert "Semantic direction proposal - not execution authority" in combined
    assert "Semantic reasoning is model-native and non-deterministic" in combined


def test_demo_output_contains_sidepanel_renderable_continuity_sections():
    first = run_minimal_governed_operational_loop_demo("Render continuity in sidepanel")
    second = run_minimal_governed_operational_loop_demo("Render continuity in sidepanel")
    assert first == second

    rendering = first["sidepanel_rendering"]
    assert first["continuity_report"]["aggregate_governance_status"] == "CONTINUITY_VALID"
    assert rendering["replay_lifecycle_visibility"]["replay"]["visible"] is True
    assert rendering["replay_lifecycle_visibility"]["lifecycle"]["visible"] is True
    assert rendering["authority_boundary_visibility"]["authority_created"] is False
    assert rendering["semantic_boundary_visibility"]["semantic_authority_created"] is False
    assert rendering["lineage_summary"]["visible"] is True


def test_sidepanel_adds_no_provider_dispatch_approval_execution_or_persistence():
    lowered = _combined().lower()
    forbidden = (
        "fetch(",
        "chrome.storage",
        "localstorage",
        "indexeddb",
        "provider.call",
        "dispatchtask",
        "approvetask",
        "executeprovider",
        "setinterval",
        "settimeout",
        "autonomous continuation authorized",
    )
    for token in forbidden:
        assert token not in lowered


def test_sidepanel_adds_no_replay_or_lifecycle_mutation_path():
    source = _js()
    forbidden = (
        "appendReplay",
        "append_replay",
        "mutateReplay",
        "transitionLifecycle",
        "transition_lifecycle",
        "createLifecycleTransition",
    )
    for token in forbidden:
        assert token not in source
    assert "mutation: false" in source
