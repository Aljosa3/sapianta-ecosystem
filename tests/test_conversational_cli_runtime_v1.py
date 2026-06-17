"""Tests for AIGOL_CONVERSATIONAL_CLI_RUNTIME_V1."""

from __future__ import annotations

import json

import pytest

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command, run_interactive_conversation
from aigol.runtime.conversational_cli_runtime import (
    AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE,
    AI_DECISION_VALIDATOR_CAPABILITY_MODEL,
    AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION,
    AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW,
    BOUNDED_FILE_WRITE_WORKER_USER_SESSION,
    CAPABILITY_LIFECYCLE_GOVERNANCE,
    CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
    CREATE_DOMAIN_TRADING,
    DOMAIN_ADAPTATION_REFERENCE,
    DOMAIN_EXECUTION_AUTHORIZATION,
    DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE,
    DOMAIN_LIFECYCLE_GOVERNANCE,
    DOMAIN_WORKER_ASSIGNMENT,
    DOMAIN_WORKER_DISPATCH,
    DOMAIN_WORKER_EXECUTION,
    DOMAIN_GOVERNED_TERMINATION,
    DOMAIN_WORKER_INVOCATION,
    DOMAIN_POST_EXECUTION_REPLAY_REVIEW,
    DOMAIN_WORKER_RESULT_CAPTURE,
    DOMAIN_WORKER_RESULT_VALIDATION,
    DOMAIN_WORKER_REQUEST,
    DEFAULT_PROVIDER_ASSISTED_CONVERSATION,
    FAILED_CLOSED,
    FINAL_CLASSIFICATION,
    FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH,
    HUMAN_INTENT_CLARIFICATION_INTAKE,
    IMPROVE_PROVIDER_LAYER,
    IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST,
    IMPROVEMENT_PROPOSAL_RUNTIME,
    NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION,
    OCS_LLM_COGNITION,
    OPERATOR_DECISION_SUPPORT,
    PROPOSAL_RUNTIME,
    REVIEW_LATEST_AUDIT,
    SHOW_LATEST_REPLAY_CHAIN,
    WORKFLOW_SELECTED,
    reconstruct_conversational_cli_routing_replay,
    route_conversational_cli_intent,
)
from aigol.runtime.human_intent_clarification_continuity_runtime import (
    WORKFLOW_TARGET_REFINED_AFTER_CLARIFICATION,
    _initial_workflow_target,
    reconstruct_human_intent_clarification_continuity_replay,
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
        ("Create worker request for FreshDomain.", DOMAIN_WORKER_REQUEST),
        ("Continue FreshDomain to worker request.", DOMAIN_WORKER_REQUEST),
        ("Create authorized worker request for FreshDomain.", DOMAIN_WORKER_REQUEST),
        ("Assign worker for FreshDomain.", DOMAIN_WORKER_ASSIGNMENT),
        ("Continue FreshDomain to worker assignment.", DOMAIN_WORKER_ASSIGNMENT),
        ("Create worker assignment for FreshDomain.", DOMAIN_WORKER_ASSIGNMENT),
        ("Dispatch worker for FreshDomain.", DOMAIN_WORKER_DISPATCH),
        ("Continue FreshDomain to worker dispatch.", DOMAIN_WORKER_DISPATCH),
        ("Create worker dispatch for FreshDomain.", DOMAIN_WORKER_DISPATCH),
        ("Invoke worker for FreshDomain.", DOMAIN_WORKER_INVOCATION),
        ("Continue FreshDomain to worker invocation.", DOMAIN_WORKER_INVOCATION),
        ("Create worker invocation for FreshDomain.", DOMAIN_WORKER_INVOCATION),
        ("Execute worker for FreshDomain.", DOMAIN_WORKER_EXECUTION),
        ("Capture worker result for FreshDomain.", DOMAIN_WORKER_RESULT_CAPTURE),
        ("Validate worker result for FreshDomain.", DOMAIN_WORKER_RESULT_VALIDATION),
        ("Review post-execution replay for FreshDomain.", DOMAIN_POST_EXECUTION_REPLAY_REVIEW),
        ("Terminate reviewed operation for FreshDomain.", DOMAIN_GOVERNED_TERMINATION),
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
    assert workflow_id != DEFAULT_PROVIDER_ASSISTED_CONVERSATION


@pytest.mark.parametrize(
    ("action", "workflow_id"),
    [
        ("Approve FreshDomain for domain artifact creation.", AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW),
        (
            "Create execution-ready authorization packet for FreshDomain.",
            DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE,
        ),
        ("Authorize execution-ready packet for FreshDomain.", DOMAIN_EXECUTION_AUTHORIZATION),
        ("Create worker request for FreshDomain.", DOMAIN_WORKER_REQUEST),
        ("Assign worker for FreshDomain.", DOMAIN_WORKER_ASSIGNMENT),
        ("Dispatch worker for FreshDomain.", DOMAIN_WORKER_DISPATCH),
        ("Invoke worker for FreshDomain.", DOMAIN_WORKER_INVOCATION),
        ("Execute worker for FreshDomain.", DOMAIN_WORKER_EXECUTION),
        ("Capture worker result for FreshDomain.", DOMAIN_WORKER_RESULT_CAPTURE),
        ("Validate worker result for FreshDomain.", DOMAIN_WORKER_RESULT_VALIDATION),
        ("Review post-execution replay for FreshDomain.", DOMAIN_POST_EXECUTION_REPLAY_REVIEW),
        ("Terminate reviewed operation for FreshDomain.", DOMAIN_GOVERNED_TERMINATION),
    ],
)
def test_next_expected_action_commands_route_verbatim(tmp_path, action: str, workflow_id: str) -> None:
    capture = _route(tmp_path, action)

    assert capture["routing_status"] == WORKFLOW_SELECTED
    assert capture["workflow_id"] == workflow_id
    assert capture["workflow_id"] != DEFAULT_PROVIDER_ASSISTED_CONVERSATION


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

    assert coverage["registered_workflows"] == 37
    assert coverage["conversationally_accessible_workflows"] == 37
    assert coverage["coverage_ratio"] == "37/37"
    assert CREATE_DOMAIN_TRADING in coverage["workflow_ids"]
    assert DOMAIN_ADAPTATION_REFERENCE in coverage["workflow_ids"]
    assert OPERATOR_DECISION_SUPPORT in coverage["workflow_ids"]
    assert OCS_LLM_COGNITION in coverage["workflow_ids"]
    assert AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW in coverage["workflow_ids"]
    assert DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE in coverage["workflow_ids"]
    assert DOMAIN_EXECUTION_AUTHORIZATION in coverage["workflow_ids"]
    assert DOMAIN_WORKER_REQUEST in coverage["workflow_ids"]
    assert DOMAIN_WORKER_ASSIGNMENT in coverage["workflow_ids"]
    assert DOMAIN_WORKER_DISPATCH in coverage["workflow_ids"]
    assert DOMAIN_WORKER_INVOCATION in coverage["workflow_ids"]
    assert DOMAIN_WORKER_EXECUTION in coverage["workflow_ids"]
    assert DOMAIN_WORKER_RESULT_CAPTURE in coverage["workflow_ids"]
    assert DOMAIN_WORKER_RESULT_VALIDATION in coverage["workflow_ids"]
    assert DOMAIN_POST_EXECUTION_REPLAY_REVIEW in coverage["workflow_ids"]
    assert DOMAIN_GOVERNED_TERMINATION in coverage["workflow_ids"]
    assert DOMAIN_LIFECYCLE_GOVERNANCE in coverage["workflow_ids"]
    assert CAPABILITY_LIFECYCLE_GOVERNANCE in coverage["workflow_ids"]
    assert PROPOSAL_RUNTIME in coverage["workflow_ids"]
    assert IMPROVEMENT_PROPOSAL_RUNTIME in coverage["workflow_ids"]
    assert FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH in coverage["workflow_ids"]
    assert IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST in coverage["workflow_ids"]
    assert AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION in coverage["workflow_ids"]
    assert AI_DECISION_VALIDATOR_CAPABILITY_MODEL in coverage["workflow_ids"]
    assert AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE in coverage["workflow_ids"]
    assert HUMAN_INTENT_CLARIFICATION_INTAKE in coverage["workflow_ids"]
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
    assert "coverage: 37/37" in rendered


@pytest.mark.parametrize(
    ("prompt", "intent_family"),
    [
        (
            "I want to build a tool that helps managers trust AI recommendations.",
            "BUSINESS_GOAL_INTENT",
        ),
        (
            "Our AI sometimes gives answers that contradict company policy.",
            "PROBLEM_STATEMENT_INTENT",
        ),
        (
            "Automate review of AI-generated summaries before they are sent out.",
            "AUTOMATION_INTENT",
        ),
        (
            "We need to show auditors how AI decisions were reviewed.",
            "COMPLIANCE_INTENT",
        ),
        (
            "I need help with AI.",
            "AMBIGUOUS_INTENT",
        ),
        (
            "Nadaljuj.",
            "CONTINUATION_INTENT",
        ),
    ],
)
def test_human_intent_clarification_intake_routes_supported_families_before_provider_fallback(
    tmp_path,
    prompt: str,
    intent_family: str,
) -> None:
    capture = _route(tmp_path, prompt)
    decision = capture["routing_decision_artifact"]
    selection = capture["workflow_selection_artifact"]
    replay = reconstruct_conversational_cli_routing_replay(tmp_path / "routing")

    assert capture["workflow_id"] == HUMAN_INTENT_CLARIFICATION_INTAKE
    assert capture["workflow_id"] != DEFAULT_PROVIDER_ASSISTED_CONVERSATION
    assert capture["routing_status"] == CLARIFICATION_REQUIRED
    assert decision["intent_family"] == intent_family
    assert selection["intent_family"] == intent_family
    assert decision["clarification_questions"]
    assert selection["clarification_questions"] == decision["clarification_questions"]
    assert selection["expected_workflow_targets"] == ["CREATE_DOMAIN_COMPLIANCE_CLARIFICATION"]
    assert selection["provider_invoked"] is False
    assert selection["worker_invoked"] is False
    assert selection["authorization_created"] is False
    assert selection["execution_requested"] is False
    assert selection["approval_bypassed"] is False
    assert selection["governance_mutated"] is False
    assert selection["replay_mutated"] is False
    assert replay["workflow_id"] == HUMAN_INTENT_CLARIFICATION_INTAKE
    assert replay["provider_invoked"] is False
    assert replay["worker_invoked"] is False
    assert replay["execution_requested"] is False


def test_human_intent_unknown_prompt_clarifies_instead_of_provider_fallback(tmp_path) -> None:
    capture = _route(tmp_path, "Something unclear about my company needs help.")
    decision = capture["routing_decision_artifact"]
    selection = capture["workflow_selection_artifact"]

    assert capture["workflow_id"] == HUMAN_INTENT_CLARIFICATION_INTAKE
    assert capture["routing_status"] == CLARIFICATION_REQUIRED
    assert selection["intent_family"] == "AMBIGUOUS_INTENT"
    assert decision["matched_terms"] == ["unknown-human-intent"]
    assert selection["provider_invoked"] is False
    assert selection["worker_invoked"] is False
    assert selection["execution_requested"] is False


def test_interactive_human_intent_clarification_intake_renders_questions_without_execution(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(
            [
                "I want to build a tool that helps managers trust AI recommendations.",
                "exit",
            ]
        ),
        output_func=output.append,
    )

    rendered = "\n".join(output)
    assert result["failed_turns"] == 0
    assert "HUMAN INTENT CLARIFICATION REQUIRED" in rendered
    assert "Intent Family: BUSINESS_GOAL_INTENT" in rendered
    assert "No provider invoked." in rendered
    assert "No worker invoked." in rendered
    assert "No execution requested." in rendered


@pytest.mark.parametrize(
    ("prompt", "reply", "intent_family", "expected_workflow"),
    [
        (
            "I want to build a tool that helps managers trust AI recommendations.",
            "Review AI recommendations used by managers before they affect customer support decisions.",
            "BUSINESS_GOAL_INTENT",
            CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
        ),
        (
            "Automate review of AI-generated summaries before they are sent out.",
            "Automatically check AI-generated customer summaries for missing justification.",
            "AUTOMATION_INTENT",
            CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
        ),
        (
            "We need to show auditors how AI decisions were reviewed.",
            "We need internal audit evidence for customer-impacting AI recommendations.",
            "COMPLIANCE_INTENT",
            CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
        ),
        (
            "I need help with AI.",
            "I want to control AI outputs before staff use them in operational decisions.",
            "AMBIGUOUS_INTENT",
            CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
        ),
        (
            "Help improve how our company uses AI.",
            "Give advisory guidance for safer AI use and better AI review practices before implementation.",
            "GENERAL_IMPROVEMENT_INTENT",
            OCS_LLM_COGNITION,
        ),
        (
            "I want to improve how AiGOL handles normal human requests before they become governed work.",
            "Keep this advisory first: identify the next safest routing improvement and preserve replay evidence before any implementation.",
            "GENERAL_IMPROVEMENT_INTENT",
            OCS_LLM_COGNITION,
        ),
        (
            "ACLI misunderstood broad improvement requests last time. How should we reduce that risk?",
            "Analyze the routing failure and recommend a safer clarification path before changing runtime behavior.",
            "GENERAL_IMPROVEMENT_INTENT",
            OCS_LLM_COGNITION,
        ),
        (
            "Make it easier for a product manager to understand why ACLI asked a clarification question.",
            "Give advisory guidance for wording and evidence visibility; do not start implementation yet.",
            "GENERAL_IMPROVEMENT_INTENT",
            OCS_LLM_COGNITION,
        ),
        (
            "I need help making the governed workflow path more understandable to new operators.",
            "I want operator-facing guidance for the clarification-to-workflow path before any runtime changes.",
            "GENERAL_IMPROVEMENT_INTENT",
            OCS_LLM_COGNITION,
        ),
        (
            "Can you make a small proof note that shows this system really did something safely?",
            "Yes.",
            "BOUNDED_FILE_WRITE_PROOF_INTENT",
            BOUNDED_FILE_WRITE_WORKER_USER_SESSION,
        ),
        (
            "Kaj bi bilo najbolje narediti naprej?",
            "Give me a plan only.",
            "GENERAL_IMPROVEMENT_INTENT",
            OCS_LLM_COGNITION,
        ),
    ],
)
def test_interactive_human_intent_clarification_response_selects_expected_workflow(
    tmp_path,
    prompt: str,
    reply: str,
    intent_family: str,
    expected_workflow: str,
) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence([prompt, reply, "exit"]),
        output_func=output.append,
    )

    first_turn = result["turns"][0]
    second_turn = result["turns"][1]
    rendered = "\n".join(output)

    assert result["failed_turns"] == 0
    assert first_turn["workflow_status"]["workflow_state"] == "WAITING_FOR_OPERATOR"
    assert first_turn["clarification_required"] is True
    assert second_turn["operator_reply_bound"] is True
    assert second_turn["clarification_resolved"] is True
    assert second_turn["workflow_resumed"] is True
    assert second_turn["intent_family"] == intent_family
    assert second_turn["workflow_id"] == expected_workflow
    assert second_turn["response_status"] == WORKFLOW_SELECTED
    assert second_turn["provider_invoked"] is False
    assert second_turn["worker_invoked"] is False
    assert second_turn["execution_requested"] is False
    replay = reconstruct_human_intent_clarification_continuity_replay(second_turn["replay_reference"])
    assert replay["workflow_id"] == expected_workflow
    assert replay["workflow_target_refinement_status"] == WORKFLOW_TARGET_REFINED_AFTER_CLARIFICATION
    assert replay["refined_workflow_targets"] == [expected_workflow]
    assert "Human Intent Clarification Bound" in rendered
    assert f"Selected Workflow: {expected_workflow}" in rendered
    assert "Workflow Target Refinement: WORKFLOW_TARGET_REFINED_AFTER_CLARIFICATION" in rendered


def test_bare_slovenian_continuation_prompt_routes_to_continuation_clarification(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(["Nadaljuj.", "exit"]),
        output_func=output.append,
    )

    first_turn = result["turns"][0]
    rendered = "\n".join(output)

    assert result["failed_turns"] == 0
    assert first_turn["clarification_required"] is True
    assert first_turn["conversational_workflow_id"] == HUMAN_INTENT_CLARIFICATION_INTAKE
    assert first_turn["workflow_status"]["workflow_state"] == "WAITING_FOR_OPERATOR"
    assert first_turn["provider_invoked"] is False
    assert first_turn["worker_invoked"] is False
    assert first_turn["authorization_created"] is False
    assert first_turn["execution_requested"] is False
    assert "Intent Family: CONTINUATION_INTENT" in rendered
    assert "What should AiGOL continue?" in rendered


def test_bounded_file_write_confirmation_preserves_approval_boundary(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(
            [
                "Can you make a small proof note that shows this system really did something safely?",
                "Yes.",
                "exit",
            ]
        ),
        output_func=output.append,
    )

    first_turn = result["turns"][0]
    second_turn = result["turns"][1]
    rendered = "\n".join(output)

    assert result["failed_turns"] == 0
    assert first_turn["clarification_required"] is True
    assert first_turn["conversational_workflow_id"] == HUMAN_INTENT_CLARIFICATION_INTAKE
    assert first_turn["workflow_status"]["workflow_state"] == "WAITING_FOR_OPERATOR"
    assert second_turn["operator_reply_bound"] is True
    assert second_turn["workflow_id"] == BOUNDED_FILE_WRITE_WORKER_USER_SESSION
    assert second_turn["workflow_resumed"] is True
    assert second_turn["provider_invoked"] is False
    assert second_turn["worker_invoked"] is False
    assert second_turn["authorization_created"] is False
    assert second_turn["execution_requested"] is False
    assert "Selected Workflow: BOUNDED_FILE_WRITE_WORKER_USER_SESSION" in rendered


def test_human_intent_continuity_rejects_unsupported_targets() -> None:
    with pytest.raises(FailClosedRuntimeError, match="unsupported target workflow"):
        _initial_workflow_target({"expected_workflow_targets": ["UNSUPPORTED_WORKFLOW"]})


@pytest.mark.parametrize(
    ("prompt", "workflow_id", "existing_runtime"),
    [
        (
            "Define the AI Decision Validator domain foundation for Product 1.",
            AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION,
            "AI_DECISION_VALIDATOR_DOMAIN_FOUNDATION_V1.md",
        ),
        (
            "Define the decision model for Product 1 AI Decision Validator.",
            AI_DECISION_VALIDATOR_CAPABILITY_MODEL,
            "AI_DECISION_VALIDATOR_CAPABILITY_MODEL_V1.md",
        ),
        (
            "Define the capability lifecycle for Product 1 AI Decision Validator.",
            AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE,
            "AI_DECISION_VALIDATOR_CAPABILITY_LIFECYCLE_V1.md",
        ),
        (
            "Create a domain activation candidate for Product 1 AI Decision Validator.",
            DOMAIN_LIFECYCLE_GOVERNANCE,
            "domain_lifecycle_governance_runtime",
        ),
        (
            "Create a capability activation candidate for Product 1 AI Decision Validator.",
            CAPABILITY_LIFECYCLE_GOVERNANCE,
            "capability_lifecycle_governance_runtime",
        ),
        (
            "Create a governed proposal artifact for Product 1 decision validation.",
            PROPOSAL_RUNTIME,
            "proposal_runtime",
        ),
        (
            "Create an improvement proposal for Product 1 replay evidence requirements.",
            IMPROVEMENT_PROPOSAL_RUNTIME,
            "improvement_proposal_runtime",
        ),
        (
            "Run the first real implementation generation epoch for Product 1 evidence requirements.",
            FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH,
            "first_real_implementation_generation_epoch_runtime",
        ),
        (
            "Convert the implementation plan to an execution request for Product 1 decision model work.",
            IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST,
            "implementation_plan_to_execution_request_runtime",
        ),
    ],
)
def test_development_entrypoint_reachability_repair_routes_previously_unreachable_entrypoints(
    tmp_path,
    prompt: str,
    workflow_id: str,
    existing_runtime: str,
) -> None:
    capture = _route(tmp_path, prompt)
    selection = capture["workflow_selection_artifact"]
    replay = reconstruct_conversational_cli_routing_replay(tmp_path / "routing")

    assert capture["workflow_id"] == workflow_id
    assert capture["workflow_id"] != DEFAULT_PROVIDER_ASSISTED_CONVERSATION
    assert capture["routing_status"] == WORKFLOW_SELECTED
    assert selection["existing_runtime"] == existing_runtime
    assert selection["provider_invoked"] is False
    assert selection["worker_invoked"] is False
    assert selection["authorization_created"] is False
    assert selection["execution_requested"] is False
    assert selection["approval_bypassed"] is False
    assert selection["governance_mutated"] is False
    assert selection["replay_mutated"] is False
    assert replay["workflow_id"] == workflow_id
    assert replay["provider_invoked"] is False
    assert replay["worker_invoked"] is False
    assert replay["execution_requested"] is False


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
    ("prompt", "workflow_id"),
    [
        (
            "Prepare a governance validation report for ACLI primary interface adoption evidence.",
            NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION,
        ),
        (
            "Prepare a proposal for improving replay lineage validation visibility in ACLI.",
            NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION,
        ),
        (
            "Create a supplier evaluation domain proposal for Product 1 demo preparation.",
            CREATE_DOMAIN_COMPLIANCE_CLARIFICATION,
        ),
        (
            "Help improve the platform operator experience for ACLI adoption.",
            NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION,
        ),
        (
            "What is the best approach for EU AI Act aligned AI Decision Validator evidence presentation?",
            OPERATOR_DECISION_SUPPORT,
        ),
        (
            "Prepare an execution summary boundary check for external-user-impacting deployment requests.",
            NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION,
        ),
        (
            "Identify recurring governance failures from replay and propose bounded improvements.",
            NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION,
        ),
        (
            "Continue the approved AI Decision Validator domain proposal to the next governed boundary.",
            AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW,
        ),
        (
            "Add a capability candidate for document validation evidence extraction.",
            NATIVE_DEVELOPMENT_CONTEXT_INTEGRATION,
        ),
        (
            "Improve provider abstraction documentation so provider identity cannot be confused with governance authority.",
            IMPROVE_PROVIDER_LAYER,
        ),
    ],
)
def test_task_completion_repair_routes_real_development_prompts_before_provider_fallback(
    tmp_path,
    prompt: str,
    workflow_id: str,
) -> None:
    capture = _route(tmp_path, prompt)
    selection = capture["workflow_selection_artifact"]
    replay = reconstruct_conversational_cli_routing_replay(tmp_path / "routing")

    assert capture["workflow_id"] == workflow_id
    assert capture["workflow_id"] != DEFAULT_PROVIDER_ASSISTED_CONVERSATION
    assert capture["routing_status"] in {WORKFLOW_SELECTED, CLARIFICATION_REQUIRED}
    assert selection["provider_invoked"] is False
    assert selection["worker_invoked"] is False
    assert selection["authorization_created"] is False
    assert selection["execution_requested"] is False
    assert selection["approval_bypassed"] is False
    assert replay["workflow_id"] == workflow_id
    assert replay["provider_invoked"] is False
    assert replay["worker_invoked"] is False
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
