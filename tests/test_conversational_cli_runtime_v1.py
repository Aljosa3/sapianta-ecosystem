"""Tests for AIGOL_CONVERSATIONAL_CLI_RUNTIME_V1."""

from __future__ import annotations

import json

import pytest

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command, run_interactive_conversation
from aigol.runtime.conversational_cli_runtime import (
    CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
    CREATE_DOMAIN_TRADING,
    DOMAIN_ADAPTATION_REFERENCE,
    FAILED_CLOSED,
    FINAL_CLASSIFICATION,
    IMPROVE_PROVIDER_LAYER,
    OPERATOR_DECISION_SUPPORT,
    REVIEW_LATEST_AUDIT,
    SHOW_LATEST_REPLAY_CHAIN,
    WORKFLOW_SELECTED,
    reconstruct_conversational_cli_routing_replay,
    route_conversational_cli_intent,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize
from aigol.runtime.unknown_domain_clarification_runtime import CLARIFICATION_REQUIRED


CREATED_AT = "2026-06-05T00:00:00Z"
SESSION_ID = "SESSION-CONVERSATIONAL-CLI-RUNTIME-000001"


def _route(tmp_path, prompt: str):
    return route_conversational_cli_intent(
        routing_id="CONVERSATIONAL-ROUTING-1",
        prompt_id=f"{SESSION_ID}:TURN-000001",
        human_prompt=prompt,
        canonical_chain_id=f"{SESSION_ID}:TURN-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "routing",
    )


def _conversation_args(tmp_path):
    (tmp_path / "governance").mkdir(exist_ok=True)
    (tmp_path / "aigol" / "runtime").mkdir(parents=True, exist_ok=True)
    (tmp_path / "tests").mkdir(exist_ok=True)
    parser = build_parser()
    return parser.parse_args(
        [
            "conversation",
            "--session-id",
            SESSION_ID,
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "interactive_runtime"),
            "--workspace",
            str(tmp_path),
        ]
    )


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


@pytest.mark.parametrize(
    ("prompt", "workflow_id"),
    [
        ("Create a trading domain.", CREATE_DOMAIN_TRADING),
        ("Review latest audit.", REVIEW_LATEST_AUDIT),
        ("Show latest replay chain.", SHOW_LATEST_REPLAY_CHAIN),
        ("Improve provider layer.", IMPROVE_PROVIDER_LAYER),
        ("Create a compliance domain.", CREATE_DOMAIN_COMPLIANCE_CLARIFICATION),
        ("Create a healthcare version of the trading domain.", DOMAIN_ADAPTATION_REFERENCE),
        ("I want to create the first real AiGOL product domain.", OPERATOR_DECISION_SUPPORT),
    ],
)
def test_conversational_intents_route_to_certified_workflows(tmp_path, prompt: str, workflow_id: str) -> None:
    capture = _route(tmp_path, prompt)
    replay = reconstruct_conversational_cli_routing_replay(tmp_path / "routing")
    selection = capture["workflow_selection_artifact"]

    assert capture["final_classification"] == FINAL_CLASSIFICATION
    assert capture["workflow_id"] == workflow_id
    assert capture["routing_status"] in {WORKFLOW_SELECTED, CLARIFICATION_REQUIRED}
    assert selection["existing_runtime"]
    assert selection["existing_cli_command"]
    assert selection["provider_invoked"] is False
    assert selection["worker_invoked"] is False
    assert selection["authorization_created"] is False
    assert selection["approval_bypassed"] is False
    assert replay["workflow_id"] == workflow_id


def test_conversational_routing_records_coverage(tmp_path) -> None:
    capture = _route(tmp_path, "Show latest replay chain.")
    coverage = capture["coverage"]

    assert coverage["registered_workflows"] == 10
    assert coverage["conversationally_accessible_workflows"] == 10
    assert coverage["coverage_ratio"] == "10/10"
    assert CREATE_DOMAIN_TRADING in coverage["workflow_ids"]
    assert DOMAIN_ADAPTATION_REFERENCE in coverage["workflow_ids"]
    assert OPERATOR_DECISION_SUPPORT in coverage["workflow_ids"]
    assert REVIEW_LATEST_AUDIT in coverage["workflow_ids"]


def test_conversational_route_cli_renders_selection(tmp_path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "conversational",
            "route",
            "--prompt",
            "Improve provider layer.",
            "--runtime-root",
            str(tmp_path / "cli_runtime"),
        ]
    )

    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol conversational route"
    assert result["workflow_id"] == IMPROVE_PROVIDER_LAYER
    assert "AIGOL CONVERSATIONAL ROUTING" in rendered
    assert "coverage: 10/10" in rendered


def test_interactive_conversation_routes_readonly_provider_layer_prompt(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(["Improve provider layer.", "exit"]),
        output_func=output.append,
    )
    turn = result["turns"][0]
    replay_path = (
        tmp_path
        / "interactive_runtime"
        / SESSION_ID
        / "TURN-000001"
        / "conversational_cli_routing"
        / "000_conversational_routing_decision_recorded.json"
    )

    assert result["failed_turns"] == 0
    assert turn["response_source"] == "CONVERSATIONAL_CLI_WORKFLOW"
    assert turn["conversational_workflow_id"] == IMPROVE_PROVIDER_LAYER
    assert turn["provider_invoked"] is False
    assert turn["worker_invoked"] is False
    assert turn["execution_requested"] is False
    assert "PROVIDER LAYER IMPROVEMENT REVIEW" in output[0]
    assert replay_path.exists()


def test_interactive_domain_and_clarification_routes_record_conversational_decisions(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(["Create a trading domain.", "Create a compliance domain.", "exit"]),
        output_func=output.append,
    )

    assert result["failed_turns"] == 0
    assert result["turns"][0]["conversational_workflow_id"] == CREATE_DOMAIN_TRADING
    assert result["turns"][1]["conversational_workflow_id"] == CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
    assert result["turns"][1]["response_status"] == CLARIFICATION_REQUIRED
    assert "Unknown Domain Detected" in output[1]


def test_unmapped_prompt_fails_closed_with_replay(tmp_path) -> None:
    capture = _route(tmp_path, "Invent an unrestricted autonomous agent.")
    replay = reconstruct_conversational_cli_routing_replay(tmp_path / "routing")

    assert capture["routing_status"] == FAILED_CLOSED
    assert capture["fail_closed"] is True
    assert "no certified workflow mapping" in capture["failure_reason"]
    assert replay["routing_status"] == FAILED_CLOSED
    assert replay["provider_invoked"] is False
    assert replay["worker_invoked"] is False


def test_replay_tampering_is_detected(tmp_path) -> None:
    _route(tmp_path, "Review latest audit.")
    path = tmp_path / "routing" / "001_conversational_workflow_selection_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["workflow_id"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_conversational_cli_routing_replay(tmp_path / "routing")
