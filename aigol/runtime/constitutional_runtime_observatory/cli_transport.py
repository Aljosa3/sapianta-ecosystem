"""Thin deterministic terminal transport for the G67-03 Query Interface."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Sequence, TextIO

from aigol.runtime.models import FailClosedRuntimeError

from .query import (
    Journey,
    JourneyDecision,
    JourneyEvent,
    JourneyEvidenceReferences,
    JourneyGap,
    JourneyMetadata,
    JourneyOwnerMap,
    JourneyState,
    JourneySummary,
    JourneyTerminalState,
    JourneyTimeline,
    JourneyTopology,
    JourneyValidationSummary,
)


CRO_CLI_TRANSPORT_ADAPTER_VERSION = (
    "G67_04_CONSTITUTIONAL_RUNTIME_OBSERVATORY_CLI_TRANSPORT_ADAPTER_V1"
)
SUPPORTED_CRO_COMMANDS = (
    "summary",
    "current",
    "timeline",
    "events",
    "decisions",
    "states",
    "gaps",
    "owners",
    "metadata",
    "validation",
    "topology",
    "evidence",
)

_COMMAND_QUERY_METHODS = {
    "summary": "get_summary",
    "current": "get_current_state",
    "timeline": "get_timeline",
    "events": "get_events",
    "decisions": "get_decisions",
    "states": "get_states",
    "gaps": "get_gaps",
    "owners": "get_owner_map",
    "metadata": "get_metadata",
    "validation": "get_validation_summary",
    "topology": "get_topology",
    "evidence": "get_evidence_references",
}

_QUERY_RECORD_TYPES = (
    JourneySummary,
    JourneyEvent,
    JourneyDecision,
    JourneyState,
    JourneyGap,
    JourneyTimeline,
    JourneyOwnerMap,
    JourneyValidationSummary,
    JourneyMetadata,
    JourneyTopology,
    JourneyEvidenceReferences,
    JourneyTerminalState,
)


def build_cro_cli_parser() -> argparse.ArgumentParser:
    """Return the closed CRO terminal command grammar."""

    parser = argparse.ArgumentParser(
        prog="cro",
        description="Read-only Constitutional Runtime Observatory query transport",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in SUPPORTED_CRO_COMMANDS:
        subparsers.add_parser(command)
    return parser


def _detached_query_value(result: Any) -> Any:
    if isinstance(result, _QUERY_RECORD_TYPES):
        return result.as_dict()
    if isinstance(result, tuple) and all(
        isinstance(item, _QUERY_RECORD_TYPES) for item in result
    ):
        return [item.as_dict() for item in result]
    raise FailClosedRuntimeError(
        "CRO CLI received a value outside the G67-03 public query contracts"
    )


def render_cro_query_result(result: Any) -> str:
    """Render one public G67-03 query result as deterministic ASCII JSON."""

    return json.dumps(
        _detached_query_value(result),
        ensure_ascii=True,
        indent=2,
        sort_keys=True,
    )


def run_cro_cli_transport(
    *,
    journey: Journey,
    argv: Sequence[str] | None = None,
    output: TextIO | None = None,
) -> int:
    """Transport one closed terminal command to an existing G67-03 Journey."""

    if not isinstance(journey, Journey):
        raise FailClosedRuntimeError(
            "CRO CLI requires an existing G67-03 Journey query object"
        )
    args = build_cro_cli_parser().parse_args(argv)
    query_method = getattr(journey, _COMMAND_QUERY_METHODS[args.command])
    result = query_method()
    destination = output if output is not None else sys.stdout
    destination.write(render_cro_query_result(result) + "\n")
    return 0


__all__ = [
    "CRO_CLI_TRANSPORT_ADAPTER_VERSION",
    "SUPPORTED_CRO_COMMANDS",
    "build_cro_cli_parser",
    "render_cro_query_result",
    "run_cro_cli_transport",
]
