from pathlib import Path

from agol_bridge.continuity.minimal_operational_loop_demo import run_minimal_governed_operational_loop_demo


ROOT = Path(__file__).resolve().parents[1]
DEMO_SOURCE = ROOT / "agol_bridge/continuity/minimal_operational_loop_demo.py"


def _demo():
    return run_minimal_governed_operational_loop_demo("Show governed continuity without execution")


def test_demo_output_is_deterministic():
    assert _demo() == _demo()


def test_demo_runs_expected_operational_flow():
    result = _demo()

    assert result["operational_flow"] == [
        "User Request",
        "Envelope Validation",
        "Validator Composition",
        "Continuity Report Synthesis",
        "Replay/Lifecycle Visibility",
        "Sidepanel Observability",
    ]
    assert result["envelope_validation_report"]["status"] == "VALID"
    assert result["validator_composition_report"]["aggregate_status"] == "VALID"
    assert result["continuity_report"]["aggregate_governance_status"] == "CONTINUITY_VALID"


def test_continuity_report_rendering_works():
    rendering = _demo()["sidepanel_rendering"]

    assert "continuity_findings" in rendering
    assert rendering["observability_label"].startswith("Read-only sidepanel observability")
    assert rendering["authority_boundary_visibility"]["authority_created"] is False
    assert rendering["semantic_boundary_visibility"]["semantic_authority_created"] is False
    assert rendering["lineage_summary"]["visible"] is True


def test_replay_lifecycle_rendering_works():
    visibility = _demo()["sidepanel_rendering"]["replay_lifecycle_visibility"]

    assert visibility["replay"]["visible"] is True
    assert visibility["replay"]["reference_count"] == 3
    assert visibility["replay"]["mutated"] is False
    assert visibility["lifecycle"]["visible"] is True
    assert visibility["lifecycle"]["reference_count"] == 2
    assert visibility["lifecycle"]["mutated"] is False


def test_authority_boundary_rendering_works():
    result = _demo()

    assert result["authority_guarantees"] == {
        "provider_calls": False,
        "dispatch": False,
        "approval": False,
        "execution": False,
        "lifecycle_mutation": False,
        "replay_mutation": False,
        "persistence": False,
        "orchestration": False,
        "autonomous_continuation": False,
        "hidden_authority": False,
    }


def test_no_provider_dispatch_approval_execution_or_persistence_behavior_is_introduced():
    source = DEMO_SOURCE.read_text()
    forbidden = (
        "fetch(",
        "requests",
        "urllib",
        "socket",
        "subprocess",
        "provider.call",
        "dispatch_task",
        "approve_task",
        "execute_governed",
        "open(",
        "write_text",
        "read_text",
        "localStorage",
        "chrome.storage",
        "append_replay_event",
        "transition_lifecycle",
        "__import__",
        "importlib",
    )
    for token in forbidden:
        assert token not in source


def test_no_replay_lifecycle_mutation_or_autonomous_continuation_claims():
    result = _demo()

    assert result["authority_guarantees"]["replay_mutation"] is False
    assert result["authority_guarantees"]["lifecycle_mutation"] is False
    assert result["authority_guarantees"]["autonomous_continuation"] is False
    assert result["input_boundary"]["hidden_persistence"] is False
    assert result["input_boundary"]["provider_calls"] is False


def test_demo_uses_explicit_in_memory_artifacts_only():
    result = _demo()
    artifacts = result["artifacts"]

    assert artifacts["envelope"]["originating_human_request_ref"]["authority"] == "context_only"
    assert artifacts["artifact_map"]["task_packages"]
    assert artifacts["artifact_map"]["replay_records"]
    assert artifacts["artifact_map"]["lifecycle_records"]
    assert result["input_boundary"]["explicit_local_input_only"] is True
