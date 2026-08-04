from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import runpy

import pytest

from aigol.runtime.constitutional_runtime_observatory import (
    build_constitutional_human_intent_journey_v1,
    build_journey,
)
from aigol.runtime.constitutional_runtime_observatory.visualization import (
    CRO_VISUALIZATION_VERSION,
    render_decision_timeline,
    render_gap_view,
    render_human_intent_journey,
    render_human_intent_journey_visualization,
    render_ordered_state_timeline,
    render_overall_workflow_diagram,
    render_owner_boundary_view,
    render_terminal_summary,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


@pytest.fixture(scope="module")
def journey(tmp_path_factory: pytest.TempPathFactory):
    helpers = runpy.run_path(
        str(
            Path(__file__).with_name(
                "test_g67_02_constitutional_runtime_observatory_core.py"
            )
        )
    )
    base = tmp_path_factory.mktemp("g67_06_visualization")
    evidence = helpers["_build_source"](
        base / "runtime",
        base / "workspace",
        base / "artifact",
    )
    projection = build_constitutional_human_intent_journey_v1(
        evidence_scope_root=evidence["scope"],
        evidence_roots=evidence["roots"],
        selector=evidence["selector"],
    )
    return build_journey(journey_projection=projection)


def _early_projection() -> dict:
    helpers = runpy.run_path(
        str(
            Path(__file__).with_name(
                "test_g67_03_constitutional_runtime_observatory_query_interface.py"
            )
        )
    )
    projection = deepcopy(helpers["_projection"]())
    human_event = projection["runtime_events"][0]
    execution_event = deepcopy(human_event)
    execution_event.update(
        {
            "event_identity": "runtime-event-execution",
            "stage": "EXECUTION",
            "owner": "EXECUTION_OWNER",
            "source_type": "EXECUTION_ARTIFACT_V1",
            "source_reference": "/bounded/runtime-event-execution.json",
            "source_artifact_hash": replay_hash({"event": "execution"}),
            "source_replay_reference": "/bounded/runtime-event-execution",
            "source_replay_hash": replay_hash({"replay": "execution"}),
            "occurrence": 1,
            "event_classification": "EXECUTION",
            "source_status_code": "OBSERVED_INCOMPLETE",
            "time_value": "2026-08-04T14:00:01Z",
        }
    )
    projection["runtime_events"] = [human_event, execution_event]
    projection["journey_states"] = [
        projection["journey_states"][0],
        {
            "journey_state_type": "CONSTITUTIONAL_RUNTIME_JOURNEY_STATE_V1",
            "stage": "EXECUTION",
            "stage_state": "REACHED",
            "outcome_state": "UNKNOWN",
            "observation_state": "OWNER_RECONSTRUCTED",
            "dimensions_independent": True,
        },
        {
            "journey_state_type": "CONSTITUTIONAL_RUNTIME_JOURNEY_STATE_V1",
            "stage": "RESULT_CAPTURE",
            "stage_state": "NOT_REACHED",
            "outcome_state": "UNKNOWN",
            "observation_state": "GAP_CLASSIFIED",
            "dimensions_independent": True,
        },
    ]
    projection["gaps"] = [
        {
            "gap_type": "CONSTITUTIONAL_RUNTIME_OBSERVATION_GAP_V1",
            "subject": "RESULT_CAPTURE",
            "classification": "NOT_REACHED",
            "matched_classifications": ["NOT_REACHED"],
            "precedence": ["NOT_REACHED", "UNKNOWN"],
            "detail": "Authenticated result-capture transition was not reached.",
            "evidence_references": [execution_event["source_reference"]],
            "descriptive_only": True,
            "runtime_event": False,
            "creates_task": False,
            "authorizes_repair": False,
            "authorizes_execution": False,
            "authorizes_mutation": False,
            "grants_authority": False,
        }
    ]
    projection["topology"]["current_stages"] = [
        "HUMAN_INTENT_PRECEDENCE",
        "EXECUTION",
        "RESULT_CAPTURE",
    ]
    projection["topology"]["known_uncomposed_edges"] = [
        {
            "from": "EXECUTION",
            "to": "RESULT_CAPTURE",
            "gap_classification": "NOT_REACHED",
            "correlated": False,
        }
    ]
    projection["journey_status"] = "OBSERVED_INCOMPLETE"
    projection["terminal_classification"] = None
    projection["validation_summary"]["runtime_events_projected"] = 2
    projection["validation_summary"]["correlation_edges_admitted"] = 1
    projection.pop("projection_hash")
    projection["projection_hash"] = replay_hash(projection)
    return projection


def test_version_and_all_required_views(journey) -> None:
    assert CRO_VISUALIZATION_VERSION == (
        "G67_06_CONSTITUTIONAL_RUNTIME_OBSERVATORY_VISUALIZATION_V1"
    )
    human = render_human_intent_journey(journey)
    states = render_ordered_state_timeline(journey)
    decisions = render_decision_timeline(journey)
    owners = render_owner_boundary_view(journey)
    gaps = render_gap_view(journey)
    terminal = render_terminal_summary(journey)
    workflow = render_overall_workflow_diagram(journey)

    assert "=== HUMAN INTENT JOURNEY ===" in human
    assert 'stage="HUMAN_INTENT_PRECEDENCE"' in human
    assert "=== ORDERED STATE TIMELINE ===" in states
    assert 'stage="EXECUTION"' in states
    assert "=== DECISION TIMELINE ===" in decisions
    assert 'stage="PROPOSAL_VALIDATION"' in decisions
    assert "=== OWNER BOUNDARY VIEW ===" in owners
    assert 'owner="EXECUTION"' in owners
    assert "=== GAP VIEW ===" in gaps
    assert 'subject="G64_CONSTITUTIONAL_COMPLETION"' in gaps
    assert "=== TERMINAL SUMMARY ===" in terminal
    assert 'terminal_classification="FINAL_EXECUTION_CERTIFIED"' in terminal
    assert "[execution status]" in terminal
    assert "=== OVERALL WORKFLOW DIAGRAM ===" in workflow
    assert '"HUMAN_INTENT_PRECEDENCE"' in workflow
    assert '"FINAL_EXECUTION_CERTIFICATION"' in workflow


def test_combined_visualization_has_fixed_view_order(journey) -> None:
    rendered = render_human_intent_journey_visualization(journey)
    headings = [
        "=== HUMAN INTENT JOURNEY ===",
        "=== OVERALL WORKFLOW DIAGRAM ===",
        "=== ORDERED STATE TIMELINE ===",
        "=== DECISION TIMELINE ===",
        "=== OWNER BOUNDARY VIEW ===",
        "=== GAP VIEW ===",
        "=== TERMINAL SUMMARY ===",
    ]
    positions = [rendered.index(heading) for heading in headings]
    assert positions == sorted(positions)


def test_workflow_is_ascii_and_connectors_mean_query_order_only(journey) -> None:
    rendered = render_overall_workflow_diagram(journey)
    rendered.encode("ascii")
    assert "\x1b" not in rendered
    assert "    |\n    v\n" in rendered
    assert "connector_semantics=QUERY_TIMELINE_ORDER_ONLY" in rendered
    assert "gap_connectors_prove_runtime_traversal=false" in rendered
    assert "--- DESCRIPTIVE GAPS ---" in rendered


def test_equal_journey_produces_byte_identical_views(journey) -> None:
    first = render_human_intent_journey_visualization(journey)
    second = render_human_intent_journey_visualization(journey)
    assert first == second


def test_visualization_does_not_modify_journey_or_persist(journey, tmp_path: Path) -> None:
    before = {
        "summary": journey.get_summary().as_dict(),
        "events": [event.as_dict() for event in journey.get_events()],
        "decisions": [decision.as_dict() for decision in journey.get_decisions()],
        "states": [state.as_dict() for state in journey.get_states()],
        "gaps": [gap.as_dict() for gap in journey.get_gaps()],
    }

    render_human_intent_journey_visualization(journey)

    after = {
        "summary": journey.get_summary().as_dict(),
        "events": [event.as_dict() for event in journey.get_events()],
        "decisions": [decision.as_dict() for decision in journey.get_decisions()],
        "states": [state.as_dict() for state in journey.get_states()],
        "gaps": [gap.as_dict() for gap in journey.get_gaps()],
    }
    assert after == before
    assert list(tmp_path.iterdir()) == []


def test_early_journey_shows_exact_next_gap_and_owner_boundary() -> None:
    early = build_journey(journey_projection=_early_projection())
    rendered = render_gap_view(early)
    terminal = render_terminal_summary(early)

    assert 'terminal_reached":false' in rendered
    assert 'expected_next_state="RESULT_CAPTURE"' in rendered
    assert 'expected_transition_classification="NOT_REACHED"' in rendered
    assert 'responsible_owner_boundary="EXECUTION_OWNER"' in rendered
    assert 'classification":"NOT_REACHED"' in rendered
    assert 'terminal_reached=false' in terminal
    assert 'outcome_state="UNKNOWN"' in terminal


@pytest.mark.parametrize("failure", ["ambiguous_edge", "missing_gap"])
def test_early_gap_presentation_fails_closed_without_exact_query_data(
    failure: str,
) -> None:
    projection = _early_projection()
    if failure == "ambiguous_edge":
        projection["topology"]["known_uncomposed_edges"].append(
            deepcopy(projection["topology"]["known_uncomposed_edges"][0])
        )
    else:
        projection["gaps"] = []
    projection.pop("projection_hash")
    projection["projection_hash"] = replay_hash(projection)
    early = build_journey(journey_projection=projection)

    with pytest.raises(FailClosedRuntimeError, match="early Journey lacks one"):
        render_gap_view(early)


def test_non_journey_input_fails_closed() -> None:
    with pytest.raises(FailClosedRuntimeError, match="existing G67-03 Journey"):
        render_human_intent_journey_visualization({})  # type: ignore[arg-type]


def test_visualization_imports_only_query_interface() -> None:
    source = Path(
        "aigol/runtime/constitutional_runtime_observatory/visualization.py"
    ).read_text(encoding="utf-8")
    assert "from .query import Journey" in source
    for forbidden in (
        "from .core import",
        "from .composition import",
        "from .cli_transport import",
        "build_journey",
        "transport.replay",
        "governance",
        "authorization",
        "worker",
        "provider",
        "platform_core",
        "conversation",
        "human_interface",
    ):
        assert forbidden not in source.lower()
