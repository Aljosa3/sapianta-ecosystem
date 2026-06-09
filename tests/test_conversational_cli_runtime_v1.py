"""Tests for AIGOL_CONVERSATIONAL_CLI_RUNTIME_V1."""

from __future__ import annotations

import json

import pytest

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command, run_interactive_conversation
from aigol.runtime.conversational_cli_runtime import (
    AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW,
    CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
    CREATE_DOMAIN_TRADING,
    DOMAIN_ADAPTATION_REFERENCE,
    DOMAIN_EXECUTION_AUTHORIZATION,
    DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE,
    FAILED_CLOSED,
    FINAL_CLASSIFICATION,
    IMPROVE_PROVIDER_LAYER,
    OCS_LLM_COGNITION,
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
PROGRESS_LINES = [
    "[1/8] Routing",
    "[2/8] Cognition",
    "[3/8] Provider Invocation",
    "[4/8] Comparison",
    "[5/8] Continuity",
    "[6/8] Clarification",
    "[7/8] Result Assembly",
    "[8/8] Replay",
]

OCS_GENERALIZATION_CASE_A = "I want to create the first real commercial Sapianta product."
OCS_GENERALIZATION_CASE_B = "\n\n".join(
    [
        OCS_GENERALIZATION_CASE_A,
        "Use the current AiGOL architecture and repository state.",
        "Assume:",
        "- Existing product domains remain read-only evidence.",
        "- Do not create a new domain or mutate governance.",
    ]
)
OCS_GENERALIZATION_CASE_C = "\n\n".join(
    [
        OCS_GENERALIZATION_CASE_A,
        "Produce:",
        "- Findings",
        "- Assumptions",
        "- Risks",
        "- Uncertainties",
        "- Recommended next milestone",
    ]
)
OCS_GENERALIZATION_CASE_D = "\n".join(
    [
        OCS_GENERALIZATION_CASE_A,
        "",
        "Context:",
        "Current AiGOL routing, OCS cognition, replay, and governance artifacts exist.",
        "Use repository state as context.",
        "Keep provider output non-authoritative.",
    ]
)


def _progress_lines(rendered: str) -> list[str]:
    return [line for line in rendered.splitlines() if line.startswith("[") and len(line) > 1 and line[1].isdigit()]


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
        ("Create a new governed domain called PilotDomain.", CREATE_DOMAIN_COMPLIANCE_CLARIFICATION),
        ("Create a healthcare version of the trading domain.", DOMAIN_ADAPTATION_REFERENCE),
        ("I want to create the first real AiGOL product domain.", OPERATOR_DECISION_SUPPORT),
        ("I want to create the first real AiGOL product.", OCS_LLM_COGNITION),
        ("I want to create the first real commercial Sapianta product.", OCS_LLM_COGNITION),
        ("Can you analyze the first real commercial Sapianta product opportunity?", OCS_LLM_COGNITION),
        ("Should Sapianta primarily sell domains, license the platform, or offer managed services?", OCS_LLM_COGNITION),
        ("Approve FreshDomain for domain artifact creation.", AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW),
        ("Approve reviewed FreshDomain workflow.", AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW),
        ("Continue FreshDomain to authorization.", AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW),
        ("Authorize FreshDomain domain artifact request.", AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW),
        ("Continue FreshDomain to execution authorization.", DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE),
        ("Create execution-ready authorization packet for FreshDomain.", DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE),
        ("Continue FreshDomain authorization workflow.", DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE),
        ("Authorize execution-ready packet for FreshDomain.", DOMAIN_EXECUTION_AUTHORIZATION),
        ("Continue FreshDomain execution authorization.", DOMAIN_EXECUTION_AUTHORIZATION),
        ("Authorize FreshDomain execution-ready workflow.", DOMAIN_EXECUTION_AUTHORIZATION),
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


@pytest.mark.parametrize(
    "prompt",
    [
        "Approve FreshDomain for domain artifact creation.",
        "Approve reviewed FreshDomain workflow.",
        "Continue FreshDomain to authorization.",
        "Authorize FreshDomain domain artifact request.",
    ],
)
def test_authorized_domain_artifact_request_prompts_do_not_fall_back_to_provider(tmp_path, prompt: str) -> None:
    capture = _route(tmp_path, prompt)
    selection = capture["workflow_selection_artifact"]

    assert capture["workflow_id"] == AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW
    assert capture["routing_status"] == WORKFLOW_SELECTED
    assert selection["existing_runtime"] == "domain_handoff_review_approval_binding_runtime"
    assert selection["provider_invoked"] is False
    assert selection["worker_invoked"] is False
    assert selection["authorization_created"] is False
    assert selection["execution_requested"] is False


@pytest.mark.parametrize(
    "prompt",
    [
        "Continue FreshDomain to execution authorization.",
        "Create execution-ready authorization packet for FreshDomain.",
        "Continue FreshDomain authorization workflow.",
    ],
)
def test_execution_ready_entry_prompts_route_to_bridge_without_provider_fallback(tmp_path, prompt: str) -> None:
    capture = _route(tmp_path, prompt)
    selection = capture["workflow_selection_artifact"]

    assert capture["workflow_id"] == DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE
    assert capture["routing_status"] == WORKFLOW_SELECTED
    assert selection["existing_runtime"] == "domain_approval_entry_to_execution_ready_authorization_bridge_runtime"
    assert selection["provider_invoked"] is False
    assert selection["worker_invoked"] is False
    assert selection["authorization_created"] is False
    assert selection["execution_requested"] is False


@pytest.mark.parametrize(
    "prompt",
    [
        "Authorize execution-ready packet for FreshDomain.",
        "Continue FreshDomain execution authorization.",
        "Authorize FreshDomain execution-ready workflow.",
    ],
)
def test_execution_authorization_entry_prompts_route_without_provider_fallback(tmp_path, prompt: str) -> None:
    capture = _route(tmp_path, prompt)
    selection = capture["workflow_selection_artifact"]

    assert capture["workflow_id"] == DOMAIN_EXECUTION_AUTHORIZATION
    assert capture["routing_status"] == WORKFLOW_SELECTED
    assert selection["existing_runtime"] == "execution_authorization_runtime"
    assert selection["provider_invoked"] is False
    assert selection["worker_invoked"] is False
    assert selection["authorization_created"] is False
    assert selection["execution_requested"] is False


@pytest.mark.parametrize(
    "prompt",
    [
        OCS_GENERALIZATION_CASE_A,
        OCS_GENERALIZATION_CASE_B,
        OCS_GENERALIZATION_CASE_C,
        OCS_GENERALIZATION_CASE_D,
    ],
)
def test_ocs_product_cognition_prompts_generalize_with_appended_context(tmp_path, prompt: str) -> None:
    capture = _route(tmp_path, prompt)
    replay = reconstruct_conversational_cli_routing_replay(tmp_path / "routing")

    assert capture["workflow_id"] == OCS_LLM_COGNITION
    assert capture["routing_status"] == WORKFLOW_SELECTED
    assert capture["workflow_selection_artifact"]["workflow_id"] == OCS_LLM_COGNITION
    assert replay["workflow_id"] == OCS_LLM_COGNITION


def test_conversational_routing_records_coverage(tmp_path) -> None:
    capture = _route(tmp_path, "Show latest replay chain.")
    coverage = capture["coverage"]

    assert coverage["registered_workflows"] == 16
    assert coverage["conversationally_accessible_workflows"] == 16
    assert coverage["coverage_ratio"] == "16/16"
    assert CREATE_DOMAIN_TRADING in coverage["workflow_ids"]
    assert DOMAIN_ADAPTATION_REFERENCE in coverage["workflow_ids"]
    assert OPERATOR_DECISION_SUPPORT in coverage["workflow_ids"]
    assert OCS_LLM_COGNITION in coverage["workflow_ids"]
    assert AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW in coverage["workflow_ids"]
    assert DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE in coverage["workflow_ids"]
    assert DOMAIN_EXECUTION_AUTHORIZATION in coverage["workflow_ids"]
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
    assert "coverage: 16/16" in rendered


def test_generic_governed_domain_creation_routes_to_clarification(tmp_path) -> None:
    capture = _route(tmp_path, "Create a new governed domain called PilotDomain.")
    replay = reconstruct_conversational_cli_routing_replay(tmp_path / "routing")
    selection = capture["workflow_selection_artifact"]
    decision = capture["routing_decision_artifact"]

    assert capture["workflow_id"] == CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
    assert capture["routing_status"] == CLARIFICATION_REQUIRED
    assert decision["confidence"] == "HIGH"
    assert "governed" in decision["matched_terms"]
    assert "domain" in decision["matched_terms"]
    assert selection["provider_invoked"] is False
    assert selection["worker_invoked"] is False
    assert selection["authorization_created"] is False
    assert replay["workflow_id"] == CREATE_DOMAIN_COMPLIANCE_CLARIFICATION
    assert replay["execution_requested"] is False


@pytest.mark.parametrize(
    "prompt",
    [
        "Create a governed artifact called PilotArtifact.",
        "Trigger a governed execution workflow.",
    ],
)
def test_generic_governed_execution_intent_fails_closed_without_provider_fallback(tmp_path, prompt: str) -> None:
    capture = _route(tmp_path, prompt)
    replay = reconstruct_conversational_cli_routing_replay(tmp_path / "routing")

    assert capture["routing_status"] == FAILED_CLOSED
    assert capture["workflow_id"] is None
    assert capture["fail_closed"] is True
    assert "generic governed execution intent requires a certified workflow mapping" in capture["failure_reason"]
    assert replay["provider_invoked"] is False
    assert replay["worker_invoked"] is False
    assert replay["execution_requested"] is False


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
    assert _progress_lines(output[0])[:8] == PROGRESS_LINES
    assert any("PROVIDER LAYER IMPROVEMENT REVIEW" in line for line in output)
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
    assert _progress_lines(output[0])[:8] == PROGRESS_LINES
    assert _progress_lines(output[1])[:8] == PROGRESS_LINES
    assert any("Unknown Domain Detected" in line for line in output)


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
