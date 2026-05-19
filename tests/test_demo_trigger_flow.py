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


def test_demo_trigger_controls_exist():
    html = _html()

    assert 'id="governed-demo-request"' in html
    assert 'id="run-governed-demo"' in html
    assert "Run Governed Demo" in html
    assert "Show governed continuity without execution" in html


def test_demo_trigger_invokes_in_memory_demo_and_existing_render_path():
    source = _js()

    assert "function runMinimalGovernedOperationalLoopDemo(userRequest)" in source
    assert "function runGovernedDemoFromSidepanel()" in source
    assert 'document.getElementById("governed-demo-request")' in source
    assert 'document.getElementById("run-governed-demo")' in source
    assert "window.sidepanelRenderResult(runMinimalGovernedOperationalLoopDemo(value));" in source
    assert "governedDemoButton.onclick = runGovernedDemoFromSidepanel;" in source


def test_demo_trigger_uses_deterministic_rendering_without_time_random_or_environment():
    source = _js()

    assert "function deterministicId(prefix, value)" in source
    assert "Math.imul(hash, 16777619)" in source
    assert "Date(" not in source
    assert "Date.now" not in source
    assert "Math.random" not in source
    assert "crypto.randomUUID" not in source
    assert "process.env" not in source


def test_demo_trigger_renders_continuity_replay_lifecycle_and_authority_data():
    source = _js()

    assert 'aggregate_governance_status: "CONTINUITY_VALID"' in source
    assert "replay_visibility_summary" in source
    assert "lifecycle_visibility_summary" in source
    assert "authority_boundary_summary" in source
    assert "semantic_boundary_summary" in source
    assert "lineage_summary" in source
    assert "continuity_recommendations" in source


def test_python_demo_invocation_remains_deterministic_for_same_request():
    first = run_minimal_governed_operational_loop_demo("Trigger governed demo")
    second = run_minimal_governed_operational_loop_demo("Trigger governed demo")

    assert first == second
    assert first["continuity_report"]["aggregate_governance_status"] == "CONTINUITY_VALID"
    assert first["sidepanel_rendering"]["replay_lifecycle_visibility"]["replay"]["visible"] is True
    assert first["sidepanel_rendering"]["replay_lifecycle_visibility"]["lifecycle"]["visible"] is True


def test_demo_trigger_adds_no_provider_dispatch_approval_execution_or_persistence_path():
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


def test_demo_trigger_adds_no_replay_lifecycle_mutation_or_orchestration_path():
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
