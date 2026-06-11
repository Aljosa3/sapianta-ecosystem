from __future__ import annotations

import json

import pytest

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.clarification_continuity_runtime import run_clarification_continuity
from aigol.runtime.clarified_domain_intent_handoff_review_runtime import (
    WORKER_BINDING_APPROVED,
    review_clarified_domain_intent,
)
from aigol.runtime.conversational_cli_runtime import route_conversational_cli_intent
from aigol.runtime.domain_handoff_review_approval_binding_runtime import (
    AUTHORIZATION_ENTRY_CREATED,
    DOMAIN_APPROVAL_BOUND,
    EXECUTION_READY_CONTINUATION_CREATED,
    bind_domain_handoff_review_approval,
    detect_domain_approval_entry_intent,
    find_latest_domain_handoff_review,
    reconstruct_domain_handoff_review_approval_binding_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize
from aigol.runtime.unknown_domain_clarification_runtime import run_unknown_domain_clarification_workflow


CREATED_AT = "2026-06-09T00:00:00Z"
SESSION_ID = "SESSION-DOMAIN-APPROVAL-BINDING-000001"
PROMPT = "Create a new governed domain called FreshDomain."
REPLY = "\n".join(
    [
        "Primary purpose: Create a safe pilot governed domain.",
        "Expected capabilities: Clarification handling and bounded workflow resume.",
        "Target users: Internal operators.",
    ]
)
APPROVAL_PROMPT = "Approve FreshDomain for domain artifact creation."


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


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


def _seed_open_clarification(session_root, turn_id: str = "TURN-000001") -> str:
    prompt_id = f"{SESSION_ID}:{turn_id}"
    turn_root = session_root / turn_id
    route_conversational_cli_intent(
        routing_id=f"{prompt_id}:CONVERSATIONAL-CLI-ROUTING",
        prompt_id=prompt_id,
        human_prompt=PROMPT,
        canonical_chain_id=prompt_id,
        created_at=CREATED_AT,
        replay_dir=turn_root / "conversational_cli_routing",
    )
    run_unknown_domain_clarification_workflow(
        clarification_id=f"{prompt_id}:UNKNOWN-DOMAIN-CLARIFICATION",
        prompt_id=prompt_id,
        human_prompt=PROMPT,
        canonical_chain_id=prompt_id,
        created_at=CREATED_AT,
        replay_dir=turn_root / "unknown_domain_clarification",
    )
    return prompt_id


def _handoff_review(tmp_path):
    session_root = tmp_path / "runtime" / SESSION_ID
    prompt_id = _seed_open_clarification(session_root)
    continuity = run_clarification_continuity(
        continuity_id=f"{SESSION_ID}:TURN-000002:CLARIFICATION-CONTINUITY",
        session_root=session_root,
        turn_id="TURN-000002",
        prompt_id=f"{SESSION_ID}:TURN-000002",
        operator_reply=REPLY,
        current_chain_id=prompt_id,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "continuity",
    )
    return review_clarified_domain_intent(
        review_id="HANDOFF-REVIEW-FRESHDOMAIN-000001",
        clarification_continuity_replay_reference=continuity["clarification_continuity_replay_reference"],
        review_decision=WORKER_BINDING_APPROVED,
        reviewed_by="AIGOL_GOVERNANCE_REVIEW",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "handoff_review",
    )


def _approve(tmp_path, *, prompt: str = APPROVAL_PROMPT, domain: str = "FreshDomain", latest: str | None = None):
    review = _handoff_review(tmp_path)
    return bind_domain_handoff_review_approval(
        approval_entry_id="DOMAIN-APPROVAL-FRESHDOMAIN-000001",
        handoff_review_replay_reference=review["handoff_review_replay_reference"],
        operator_prompt=prompt,
        approved_domain=domain,
        approving_actor="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
        replay_dir=tmp_path / "approval_binding",
        latest_handoff_review_replay_reference=latest,
    )


def test_approval_entry_intent_detection_supports_required_prompts() -> None:
    prompts = [
        "Approve FreshDomain for domain artifact creation.",
        "Approve reviewed FreshDomain workflow.",
        "Continue FreshDomain to authorization.",
        "Authorize FreshDomain domain artifact request.",
    ]

    for prompt in prompts:
        detected = detect_domain_approval_entry_intent(prompt)
        assert detected["approval_entry_intent_detected"] is True
        assert detected["domain_name"] == "FreshDomain"


def test_approval_success_creates_binding_authorization_entry_and_continuation(tmp_path) -> None:
    capture = _approve(tmp_path)
    replay = reconstruct_domain_handoff_review_approval_binding_replay(tmp_path / "approval_binding")
    binding = capture["domain_approval_binding_artifact"]

    assert capture["approval_status"] == DOMAIN_APPROVAL_BOUND
    assert capture["approved_domain"] == "FreshDomain"
    assert capture["authorization_entry_status"] == AUTHORIZATION_ENTRY_CREATED
    assert capture["execution_ready_continuation_status"] == EXECUTION_READY_CONTINUATION_CREATED
    assert binding["approval_hash"] == binding["binding_hash"]
    assert binding["authorization_created"] is False
    assert binding["worker_request_created"] is False
    assert binding["worker_invoked"] is False
    assert replay["approval_status"] == DOMAIN_APPROVAL_BOUND
    assert replay["approved_domain"] == "FreshDomain"


def test_replay_corruption_is_detected(tmp_path) -> None:
    _approve(tmp_path)
    replay_file = tmp_path / "approval_binding" / "000_domain_approval_binding_recorded.json"
    wrapper = json.loads(replay_file.read_text(encoding="utf-8"))
    wrapper["artifact"]["approved_domain"] = "OtherDomain"
    replay_file.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_domain_handoff_review_approval_binding_replay(tmp_path / "approval_binding")


def test_approval_domain_mismatch_fails_closed(tmp_path) -> None:
    capture = _approve(tmp_path, domain="OtherDomain")

    assert capture["fail_closed"] is True
    assert "approval-domain mismatch" in capture["failure_reason"]
    assert capture["authorization_created"] is False
    assert capture["worker_invoked"] is False


def test_stale_review_rejection_fails_closed(tmp_path) -> None:
    capture = _approve(tmp_path, latest=str(tmp_path / "newer_handoff_review"))

    assert capture["fail_closed"] is True
    assert "stale handoff review" in capture["failure_reason"]


def test_fail_closed_approval_rejection_for_unsupported_prompt(tmp_path) -> None:
    capture = _approve(tmp_path, prompt="Reject FreshDomain for domain artifact creation.")

    assert capture["fail_closed"] is True
    assert "approval intent missing" in capture["failure_reason"]


def test_acli_approval_prompt_binds_reviewed_freshdomain_without_execution(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence([PROMPT, REPLY, APPROVAL_PROMPT, "exit"]),
        output_func=output.append,
    )
    third = result["turns"][2]
    replay = reconstruct_domain_handoff_review_approval_binding_replay(
        tmp_path
        / "interactive_runtime"
        / SESSION_ID
        / "TURN-000003"
        / "domain_approval_binding"
    )

    assert result["failed_turns"] == 0
    assert third["approval_status"] == DOMAIN_APPROVAL_BOUND
    assert third["approved_domain"] == "FreshDomain"
    assert third["authorization_entry_status"] == AUTHORIZATION_ENTRY_CREATED
    assert third["execution_ready_continuation_status"] == EXECUTION_READY_CONTINUATION_CREATED
    assert third["authorization_created"] is False
    assert third["worker_invoked"] is False
    assert third["domain_created"] is False
    assert replay["approval_status"] == DOMAIN_APPROVAL_BOUND
    assert "Domain Approval Binding" in output[2]


def test_acli_authorize_prompt_binds_reviewed_freshdomain_without_provider_fallback(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence([PROMPT, REPLY, "Authorize FreshDomain domain artifact request.", "exit"]),
        output_func=output.append,
    )
    third = result["turns"][2]
    replay = reconstruct_domain_handoff_review_approval_binding_replay(
        tmp_path
        / "interactive_runtime"
        / SESSION_ID
        / "TURN-000003"
        / "domain_approval_binding"
    )

    assert result["failed_turns"] == 0
    assert third["response_source"] == "DOMAIN_HANDOFF_REVIEW_APPROVAL_AND_BINDING_ENTRY"
    assert third["approval_status"] == DOMAIN_APPROVAL_BOUND
    assert third["approved_domain"] == "FreshDomain"
    assert third["authorization_entry_status"] == AUTHORIZATION_ENTRY_CREATED
    assert third["execution_ready_continuation_status"] == EXECUTION_READY_CONTINUATION_CREATED
    assert third["authorization_created"] is False
    assert third["worker_invoked"] is False
    assert third["domain_created"] is False
    assert third["workflow_status"]["workflow_state"] == "CONTINUATION_AVAILABLE"
    assert third["workflow_status"]["current_lifecycle_stage"] == "EXECUTION_READY"
    assert (
        third["workflow_status"]["next_expected_action"]
        == "Create execution-ready authorization packet for FreshDomain."
    )
    assert replay["approval_status"] == DOMAIN_APPROVAL_BOUND
    assert "DEFAULT_PROVIDER_ASSISTED_CONVERSATION" not in output[2]
    assert "FAILED_CLOSED" not in output[2]


def test_acli_status_projection_advances_after_clarification_handoff_review(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence([PROMPT, REPLY, "exit"]),
        output_func=output.append,
    )
    second = result["turns"][1]
    workflow_status = second["workflow_status"]

    assert result["failed_turns"] == 0
    assert second["clarification_resolved"] is True
    assert second["workflow_resumed"] is True
    assert second["handoff_review_decision"] == WORKER_BINDING_APPROVED
    assert second["handoff_review_next_certified_stage"] == "AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW"
    assert workflow_status["workflow_state"] == "CONTINUATION_AVAILABLE"
    assert workflow_status["current_lifecycle_stage"] == "APPROVAL"
    assert workflow_status["next_expected_action"] == "Authorize FreshDomain domain artifact request."
    assert workflow_status["required_input"] == []
    assert "Workflow State: CONTINUATION_AVAILABLE" in output[1]
    assert "Current Lifecycle Stage: APPROVAL" in output[1]
    assert "Next Expected Action: Authorize FreshDomain domain artifact request." in output[1]
    assert "WAITING FOR OPERATOR INPUT" not in output[1]
