"""Tests for AIGOL_UNKNOWN_DOMAIN_AND_CLARIFICATION_UX_V1."""

from __future__ import annotations

import json

import pytest

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command, run_interactive_conversation
from aigol.runtime.conversation_native_development_intent_routing import (
    NATIVE_DEVELOPMENT_INTENT_ROUTED,
    run_conversation_native_development_intent_routing,
)
from aigol.runtime.conversation_session_resume_runtime import resume_conversation_session
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize
from aigol.runtime.unknown_domain_clarification_runtime import (
    CLARIFICATION_REQUEST_ARTIFACT_V1,
    CLARIFICATION_REQUIRED,
    CREATE_DOMAIN,
    UNKNOWN_DOMAIN,
    UNKNOWN_DOMAIN_ARTIFACT_V1,
    reconstruct_unknown_domain_clarification_replay,
    run_unknown_domain_clarification_workflow,
)


CREATED_AT = "2026-06-05T00:00:00Z"
SESSION_ID = "SESSION-UNKNOWN-DOMAIN-CLARIFICATION-000001"


def _workflow(tmp_path, prompt: str):
    return run_unknown_domain_clarification_workflow(
        clarification_id="UNKNOWN-DOMAIN-CLARIFICATION-1",
        prompt_id=f"{SESSION_ID}:TURN-000001",
        human_prompt=prompt,
        canonical_chain_id=f"{SESSION_ID}:TURN-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "unknown_domain",
    )


def _conversation_args(tmp_path):
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


def test_create_compliance_domain_enters_unknown_domain_clarification(tmp_path) -> None:
    capture = _workflow(tmp_path, "Create a compliance domain.")
    reconstructed = reconstruct_unknown_domain_clarification_replay(tmp_path / "unknown_domain")
    unknown = capture["unknown_domain_artifact"]
    request = capture["clarification_request_artifact"]

    assert capture["response_status"] == CLARIFICATION_REQUIRED
    assert capture["fail_closed"] is False
    assert unknown["artifact_type"] == UNKNOWN_DOMAIN_ARTIFACT_V1
    assert unknown["unknown_domain_status"] == UNKNOWN_DOMAIN
    assert unknown["requested_domain"] == "COMPLIANCE"
    assert unknown["domain_mapping_missing"] is True
    assert unknown["capability_mapping_missing"] is True
    assert request["artifact_type"] == CLARIFICATION_REQUEST_ARTIFACT_V1
    assert request["originating_intent"] == CREATE_DOMAIN
    assert request["proposed_domain"] == "COMPLIANCE"
    assert [option["option_id"] for option in request["operator_options"]] == [
        "CREATE_NEW_DOMAIN",
        "MAP_TO_EXISTING_DOMAIN",
        "CANCEL",
    ]
    assert "Unknown Domain Detected" in capture["response_text"]
    assert "Requested Domain: COMPLIANCE" in capture["response_text"]
    assert "Operator Selection Required" in capture["response_text"]
    assert reconstructed["workflow_status"] == CLARIFICATION_REQUIRED
    assert reconstructed["provider_invoked"] is False
    assert reconstructed["domain_created"] is False


def test_regulatory_compliance_new_domain_requests_missing_details(tmp_path) -> None:
    capture = _workflow(tmp_path, "Create a new domain for validating regulatory compliance requirements.")
    request = capture["clarification_request_artifact"]

    assert capture["response_status"] == CLARIFICATION_REQUIRED
    assert request["originating_intent"] == CREATE_DOMAIN
    assert request["proposed_domain"] == "COMPLIANCE"
    assert request["clarification_mode"] == "DOMAIN_DETAILS"
    assert request["missing_information"] == ["primary purpose", "expected capabilities", "target users"]
    assert "Clarification Required" in capture["response_text"]
    assert "Detected Intent: CREATE_DOMAIN" in capture["response_text"]
    assert "* primary purpose" in capture["response_text"]
    assert "Operator Response Required" in capture["response_text"]


def test_interactive_conversation_uses_unknown_domain_clarification_without_provider(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(["Create a compliance domain.", "exit"]),
        output_func=output.append,
    )
    turn = result["turns"][0]
    replay_path = (
        tmp_path
        / "interactive_runtime"
        / SESSION_ID
        / "TURN-000001"
        / "unknown_domain_clarification"
        / "000_unknown_domain_recorded.json"
    )

    assert result["turn_count"] == 1
    assert result["failed_turns"] == 0
    assert turn["response_status"] == CLARIFICATION_REQUIRED
    assert turn["response_source"] == "UNKNOWN_DOMAIN_CLARIFICATION_WORKFLOW"
    assert turn["unknown_domain_artifact_type"] == UNKNOWN_DOMAIN_ARTIFACT_V1
    assert turn["clarification_request_artifact_type"] == CLARIFICATION_REQUEST_ARTIFACT_V1
    assert turn["proposed_domain"] == "COMPLIANCE"
    assert turn["provider_invoked"] is False
    assert turn["worker_invoked"] is False
    assert turn["domain_created"] is False
    assert "Unknown Domain Detected" in output[0]
    assert replay_path.exists()


def test_trading_domain_existing_behavior_unchanged(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    allocation = resume_conversation_session(session_id=SESSION_ID, runtime_root=runtime_root, created_at=CREATED_AT)
    prompt_id = f"{SESSION_ID}:{allocation['next_turn_id']}"
    capture = run_conversation_native_development_intent_routing(
        routing_id=f"{prompt_id}:NATIVE_DEVELOPMENT_INTENT_ROUTING",
        prompt_id=prompt_id,
        human_prompt="Create a trading domain.",
        canonical_chain_id=prompt_id,
        turn_allocation_evidence=allocation,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "trading_routing",
    )

    assert capture["routing_status"] == NATIVE_DEVELOPMENT_INTENT_ROUTED
    assert capture["intent_class"] == CREATE_DOMAIN
    assert capture["target_domain"] == "TRADING"
    assert capture["target_resource"] == "DOMAIN"


def test_unknown_domain_cli_renders_operator_workflow(tmp_path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "clarification",
            "unknown-domain",
            "--prompt",
            "Create a compliance domain.",
            "--runtime-root",
            str(tmp_path / "cli_runtime"),
        ]
    )
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol clarification unknown-domain"
    assert result["response_status"] == CLARIFICATION_REQUIRED
    assert "AIGOL UNKNOWN DOMAIN CLARIFICATION" in rendered
    assert "Create new domain COMPLIANCE" in rendered


def test_replay_tampering_is_detected(tmp_path) -> None:
    _workflow(tmp_path, "Create a compliance domain.")
    path = tmp_path / "unknown_domain" / "001_clarification_request_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["proposed_domain"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_unknown_domain_clarification_replay(tmp_path / "unknown_domain")
