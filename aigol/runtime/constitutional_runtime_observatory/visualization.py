"""Deterministic ASCII presentation over the canonical G67-03 Journey."""

from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from aigol.runtime.models import FailClosedRuntimeError

from .query import Journey


CRO_VISUALIZATION_VERSION = (
    "G67_06_CONSTITUTIONAL_RUNTIME_OBSERVATORY_VISUALIZATION_V1"
)


def _require_journey(journey: Journey) -> Journey:
    if not isinstance(journey, Journey):
        raise FailClosedRuntimeError(
            "CRO visualization requires an existing G67-03 Journey"
        )
    return journey


def _ascii_value(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )


def _record_lines(
    label: str,
    record: Mapping[str, Any],
) -> list[str]:
    lines = [f"[{label}]"]
    lines.extend(
        f"{key}={_ascii_value(record[key])}" for key in sorted(record)
    )
    return lines


def _sequence_lines(
    label: str,
    records: Sequence[Mapping[str, Any]],
) -> list[str]:
    lines = []
    for position, record in enumerate(records):
        if position:
            lines.append("")
        lines.extend(_record_lines(f"{label} {position:03d}", record))
    return lines


def _section(title: str, lines: Sequence[str]) -> str:
    return "\n".join([f"=== {title} ===", *lines])


def render_human_intent_journey(journey: Journey) -> str:
    """Render the Journey summary and exact Human Intent precedence events."""

    query = _require_journey(journey)
    summary = query.get_summary()
    intent_events = tuple(
        event
        for event in query.get_events()
        if event["stage"] == "HUMAN_INTENT_PRECEDENCE"
    )
    lines = _record_lines("journey summary", summary)
    if intent_events:
        lines.extend(["", *_sequence_lines("human intent event", intent_events)])
    return _section("HUMAN INTENT JOURNEY", lines)


def render_ordered_state_timeline(journey: Journey) -> str:
    """Render every query-returned Journey State in canonical order."""

    states = _require_journey(journey).get_states()
    return _section(
        "ORDERED STATE TIMELINE",
        _sequence_lines("state", states),
    )


def render_decision_timeline(journey: Journey) -> str:
    """Render every query-returned Decision in canonical order."""

    decisions = _require_journey(journey).get_decisions()
    return _section(
        "DECISION TIMELINE",
        _sequence_lines("decision", decisions),
    )


def render_owner_boundary_view(journey: Journey) -> str:
    """Render the exact source-owner membership returned by G67-03."""

    owner_map = _require_journey(journey).get_owner_map()
    lines = _record_lines(
        "owner map contract",
        {key: owner_map[key] for key in owner_map if key != "owners"},
    )
    owners = owner_map["owners"]
    if owners:
        lines.extend(["", *_sequence_lines("owner boundary", owners)])
    return _section("OWNER BOUNDARY VIEW", lines)


def _early_gap_lines(journey: Journey) -> list[str]:
    terminal = journey.get_terminal_state()
    if terminal["terminal_reached"] is True:
        return []

    current = journey.get_current_state()
    current_stage = current["stage"]
    events = journey.get_events()
    if not events or events[-1]["stage"] != current_stage:
        raise FailClosedRuntimeError(
            "early Journey lacks one last authenticated owner boundary"
        )

    topology = journey.get_topology()
    matching_edges = tuple(
        edge
        for edge in topology["known_uncomposed_edges"]
        if edge.get("from") == current_stage
    )
    if len(matching_edges) != 1:
        raise FailClosedRuntimeError(
            "early Journey lacks one authenticated next-state topology edge"
        )
    edge = matching_edges[0]
    matching_gaps = tuple(
        gap for gap in journey.get_gaps() if gap["subject"] == edge.get("to")
    )
    if len(matching_gaps) != 1:
        raise FailClosedRuntimeError(
            "early Journey lacks one authenticated next-state Gap"
        )

    return [
        "",
        "[early terminal boundary]",
        f"terminal_state={_ascii_value(terminal.as_dict())}",
        f"current_state={_ascii_value(current.as_dict())}",
        f"expected_next_state={_ascii_value(edge.get('to'))}",
        "expected_transition_classification="
        + _ascii_value(edge.get("gap_classification")),
        "responsible_owner_boundary=" + _ascii_value(events[-1]["owner"]),
        f"authenticated_gap={_ascii_value(matching_gaps[0].as_dict())}",
    ]


def render_gap_view(journey: Journey) -> str:
    """Render authenticated Gaps and a bounded early-terminal presentation."""

    query = _require_journey(journey)
    lines = _sequence_lines("gap", query.get_gaps())
    lines.extend(_early_gap_lines(query))
    return _section("GAP VIEW", lines)


def render_terminal_summary(journey: Journey) -> str:
    """Render current, terminal, and exact Execution Journey State records."""

    query = _require_journey(journey)
    execution_states = tuple(
        state for state in query.get_states() if state["stage"] == "EXECUTION"
    )
    if len(execution_states) != 1:
        raise FailClosedRuntimeError(
            "Journey visualization requires one exact Execution State"
        )
    lines = _record_lines("current state", query.get_current_state())
    lines.extend(
        [
            "",
            *_record_lines("execution status", execution_states[0]),
            "",
            *_record_lines("terminal state", query.get_terminal_state()),
        ]
    )
    return _section("TERMINAL SUMMARY", lines)


def render_overall_workflow_diagram(journey: Journey) -> str:
    """Render query timeline order as an ASCII workflow with descriptive Gaps."""

    timeline = _require_journey(journey).get_timeline()
    runtime_entries = tuple(
        entry
        for entry in timeline["entries"]
        if entry["entry_kind"] == "RUNTIME_EVENT"
    )
    gap_entries = tuple(
        entry
        for entry in timeline["entries"]
        if entry["entry_kind"] == "DESCRIPTIVE_GAP"
    )
    lines = [
        "connector_semantics=QUERY_TIMELINE_ORDER_ONLY",
        "gap_connectors_prove_runtime_traversal=false",
    ]
    for position, entry in enumerate(runtime_entries):
        if position:
            lines.extend(["    |", "    v"])
        lines.extend(
            [
                f"[{_ascii_value(entry['stage_or_subject'])}]",
                f"owner={_ascii_value(entry['owner'])}",
                "status_or_classification="
                + _ascii_value(entry["status_or_classification"]),
                "proves_runtime_traversal="
                + _ascii_value(entry["proves_runtime_traversal"]),
            ]
        )
    if gap_entries:
        lines.append("")
        lines.append("--- DESCRIPTIVE GAPS ---")
        for entry in gap_entries:
            lines.extend(
                [
                    f"[GAP {_ascii_value(entry['stage_or_subject'])}]",
                    "status_or_classification="
                    + _ascii_value(entry["status_or_classification"]),
                    "proves_runtime_traversal="
                    + _ascii_value(entry["proves_runtime_traversal"]),
                ]
            )
    return _section("OVERALL WORKFLOW DIAGRAM", lines)


def render_human_intent_journey_visualization(journey: Journey) -> str:
    """Render all certified G67-06 ASCII views in fixed order."""

    query = _require_journey(journey)
    return "\n\n".join(
        (
            render_human_intent_journey(query),
            render_overall_workflow_diagram(query),
            render_ordered_state_timeline(query),
            render_decision_timeline(query),
            render_owner_boundary_view(query),
            render_gap_view(query),
            render_terminal_summary(query),
        )
    )


__all__ = [
    "CRO_VISUALIZATION_VERSION",
    "render_human_intent_journey",
    "render_ordered_state_timeline",
    "render_decision_timeline",
    "render_owner_boundary_view",
    "render_gap_view",
    "render_terminal_summary",
    "render_overall_workflow_diagram",
    "render_human_intent_journey_visualization",
]
