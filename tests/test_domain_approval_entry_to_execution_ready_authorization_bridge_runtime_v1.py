from __future__ import annotations

import json
from pathlib import Path

import pytest

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.clarification_continuity_runtime import run_clarification_continuity
from aigol.runtime.clarified_domain_intent_handoff_review_runtime import (
    WORKER_BINDING_APPROVED,
    review_clarified_domain_intent,
)
from aigol.runtime.conversational_cli_runtime import route_conversational_cli_intent
from aigol.runtime.domain_approval_entry_to_execution_ready_authorization_bridge_runtime import (
    DOMAIN_EXECUTION_READY_BRIDGED,
    bridge_domain_approval_entry_to_execution_ready,
    detect_domain_execution_ready_entry_intent,
    find_latest_domain_approval_binding,
    reconstruct_domain_execution_ready_bridge_replay,
)
from aigol.runtime.domain_handoff_review_approval_binding_runtime import bind_domain_handoff_review_approval
from aigol.runtime.execution_authorization_runtime import (
    EXECUTION_AUTHORIZED,
    authorize_execution_ready,
    detect_domain_execution_authorization_entry_intent,
    find_latest_domain_execution_ready_bridge,
    reconstruct_execution_authorization_replay,
)
from aigol.runtime.execution_runtime import (
    EXECUTING,
    detect_domain_worker_execution_entry_intent,
    reconstruct_execution_replay,
)
from aigol.runtime.governed_implementation_dry_run import EXECUTION_READY
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, load_json
from aigol.runtime.unknown_domain_clarification_runtime import run_unknown_domain_clarification_workflow
from aigol.runtime.worker_assignment_runtime import (
    WORKER_ASSIGNED,
    assign_worker_from_invocation_request,
    default_worker_registry_for_request,
    detect_domain_worker_assignment_entry_intent,
    find_latest_domain_worker_invocation_request,
    reconstruct_worker_assignment_runtime_replay,
)
from aigol.runtime.worker_dispatch_runtime import (
    WORKER_DISPATCHED,
    detect_domain_worker_dispatch_entry_intent,
    dispatch_assigned_worker,
    find_latest_domain_worker_assignment,
    reconstruct_worker_dispatch_replay,
)
from aigol.runtime.worker_invocation_runtime import (
    WORKER_INVOKED,
    detect_domain_worker_invocation_entry_intent,
    find_latest_domain_worker_dispatch,
    invoke_dispatched_worker,
    reconstruct_worker_invocation_replay,
)
from aigol.runtime.worker_invocation_request_runtime import (
    WORKER_INVOCATION_REQUEST_CREATED,
    create_worker_invocation_request,
    detect_domain_worker_request_entry_intent,
    find_latest_domain_execution_authorization,
    reconstruct_worker_invocation_request_replay,
)


CREATED_AT = "2026-06-09T00:00:00Z"
SESSION_ID = "SESSION-DOMAIN-READY-BRIDGE-000001"
PROMPT = "Create a new governed domain called FreshDomain."
REPLY = "\n".join(
    [
        "Primary purpose: Create a safe pilot governed domain.",
        "Expected capabilities: Clarification handling and bounded workflow resume.",
        "Target users: Internal operators.",
    ]
)
APPROVAL_PROMPT = "Approve FreshDomain for domain artifact creation."
EXECUTION_READY_PROMPT = "Create execution-ready authorization packet for FreshDomain."
EXECUTION_AUTHORIZATION_PROMPT = "Authorize execution-ready packet for FreshDomain."
WORKER_REQUEST_PROMPT = "Create worker request for FreshDomain."
WORKER_ASSIGNMENT_PROMPT = "Assign worker for FreshDomain."
WORKER_DISPATCH_PROMPT = "Dispatch worker for FreshDomain."
WORKER_INVOCATION_PROMPT = "Invoke worker for FreshDomain."
WORKER_EXECUTION_PROMPT = "Execute worker for FreshDomain."


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


def _approval_entry(tmp_path, *, replay_dir=None):
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
    review = review_clarified_domain_intent(
        review_id="HANDOFF-REVIEW-FRESHDOMAIN-000001",
        clarification_continuity_replay_reference=continuity["clarification_continuity_replay_reference"],
        review_decision=WORKER_BINDING_APPROVED,
        reviewed_by="AIGOL_GOVERNANCE_REVIEW",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "handoff_review",
    )
    return bind_domain_handoff_review_approval(
        approval_entry_id="DOMAIN-APPROVAL-FRESHDOMAIN-000001",
        handoff_review_replay_reference=review["handoff_review_replay_reference"],
        operator_prompt=APPROVAL_PROMPT,
        approved_domain="FreshDomain",
        approving_actor="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
        replay_dir=replay_dir or tmp_path / "approval_binding",
        latest_handoff_review_replay_reference=review["handoff_review_replay_reference"],
    )


def _bridge(tmp_path, *, domain: str = "FreshDomain"):
    approval = _approval_entry(tmp_path)
    return bridge_domain_approval_entry_to_execution_ready(
        bridge_id="DOMAIN-READY-BRIDGE-FRESHDOMAIN-000001",
        domain_approval_binding_replay_reference=approval["domain_approval_binding_replay_reference"],
        approved_domain=domain,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ready_bridge",
    )


def test_domain_approval_entry_converts_to_execution_ready_packet(tmp_path) -> None:
    capture = _bridge(tmp_path)
    replay = reconstruct_domain_execution_ready_bridge_replay(tmp_path / "ready_bridge")

    assert capture["bridge_status"] == DOMAIN_EXECUTION_READY_BRIDGED
    assert capture["execution_status"] == EXECUTION_READY
    assert capture["execution_ready_replay_reference"]
    assert capture["execution_ready_replay_hash"].startswith("sha256:")
    assert capture["authorization_runtime_compatible"] is True
    assert capture["authorization_created"] is False
    assert capture["worker_request_created"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_started"] is False
    assert replay["bridge_status"] == DOMAIN_EXECUTION_READY_BRIDGED
    assert replay["authorization_runtime_compatible"] is True


def test_execution_ready_entry_intent_detection_supports_required_prompts() -> None:
    prompts = [
        "Continue FreshDomain to execution authorization.",
        "Create execution-ready authorization packet for FreshDomain.",
        "Continue FreshDomain authorization workflow.",
    ]

    for prompt in prompts:
        detected = detect_domain_execution_ready_entry_intent(prompt)
        assert detected["execution_ready_entry_intent_detected"] is True
        assert detected["domain_name"] == "FreshDomain"


def test_find_latest_domain_approval_binding_excludes_already_bridged_entries(tmp_path) -> None:
    session_root = tmp_path / "runtime" / SESSION_ID
    approval = _approval_entry(
        tmp_path,
        replay_dir=session_root / "TURN-000003" / "domain_approval_binding",
    )

    found = find_latest_domain_approval_binding(session_root=session_root, domain_name="FreshDomain")
    assert found["domain_approval_binding_replay_reference"] == approval["domain_approval_binding_replay_reference"]

    bridge_domain_approval_entry_to_execution_ready(
        bridge_id="DOMAIN-READY-BRIDGE-FRESHDOMAIN-000001",
        domain_approval_binding_replay_reference=approval["domain_approval_binding_replay_reference"],
        approved_domain="FreshDomain",
        created_at=CREATED_AT,
        replay_dir=session_root / "TURN-000004" / "domain_execution_ready_bridge",
    )

    with pytest.raises(FailClosedRuntimeError, match="matching approval binding not found"):
        find_latest_domain_approval_binding(session_root=session_root, domain_name="FreshDomain")


def test_bridge_output_feeds_existing_execution_authorization_runtime(tmp_path) -> None:
    bridge = _bridge(tmp_path)
    authorization = authorize_execution_ready(
        authorization_id="DOMAIN-AUTHORIZATION-FRESHDOMAIN-000001",
        execution_ready_replay_reference=bridge["execution_ready_replay_reference"],
        authorizing_actor="human_authorizer",
        authorized_at=CREATED_AT,
        replay_dir=tmp_path / "authorization",
    )

    assert authorization["authorization_status"] == "EXECUTION_AUTHORIZED"
    assert authorization["approval_status"] == "APPROVED"
    assert authorization["approval_reference"] == "DOMAIN-APPROVAL-FRESHDOMAIN-000001"
    assert authorization["worker_invoked"] is False
    assert authorization["execution_started"] is False


def test_execution_authorization_entry_intent_detection_supports_required_prompts() -> None:
    prompts = [
        "Authorize execution-ready packet for FreshDomain.",
        "Continue FreshDomain execution authorization.",
        "Authorize FreshDomain execution-ready workflow.",
    ]

    for prompt in prompts:
        detected = detect_domain_execution_authorization_entry_intent(prompt)
        assert detected["execution_authorization_entry_intent_detected"] is True
        assert detected["domain_name"] == "FreshDomain"


def test_find_latest_domain_execution_ready_bridge_excludes_authorized_entries(tmp_path) -> None:
    session_root = tmp_path / "runtime" / SESSION_ID
    approval = _approval_entry(
        tmp_path,
        replay_dir=session_root / "TURN-000003" / "domain_approval_binding",
    )
    bridge = bridge_domain_approval_entry_to_execution_ready(
        bridge_id="DOMAIN-READY-BRIDGE-FRESHDOMAIN-000001",
        domain_approval_binding_replay_reference=approval["domain_approval_binding_replay_reference"],
        approved_domain="FreshDomain",
        created_at=CREATED_AT,
        replay_dir=session_root / "TURN-000004" / "domain_execution_ready_bridge",
    )

    found = find_latest_domain_execution_ready_bridge(session_root=session_root, domain_name="FreshDomain")
    assert found["execution_ready_replay_reference"] == bridge["execution_ready_replay_reference"]

    authorize_execution_ready(
        authorization_id="DOMAIN-AUTHORIZATION-FRESHDOMAIN-000001",
        execution_ready_replay_reference=bridge["execution_ready_replay_reference"],
        authorizing_actor="HUMAN_OPERATOR",
        authorized_at=CREATED_AT,
        replay_dir=session_root / "TURN-000005" / "execution_authorization",
    )

    with pytest.raises(FailClosedRuntimeError, match="matching execution-ready bridge not found"):
        find_latest_domain_execution_ready_bridge(session_root=session_root, domain_name="FreshDomain")


def test_acli_execution_ready_prompt_bridges_reviewed_freshdomain_without_authorization(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence([PROMPT, REPLY, APPROVAL_PROMPT, EXECUTION_READY_PROMPT, "exit"]),
        output_func=output.append,
    )
    fourth = result["turns"][3]
    replay = reconstruct_domain_execution_ready_bridge_replay(
        tmp_path
        / "interactive_runtime"
        / SESSION_ID
        / "TURN-000004"
        / "domain_execution_ready_bridge"
    )

    assert result["failed_turns"] == 0
    assert fourth["response_source"] == "DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE"
    assert fourth["bridge_status"] == DOMAIN_EXECUTION_READY_BRIDGED
    assert fourth["approved_domain"] == "FreshDomain"
    assert fourth["execution_ready_replay_reference"]
    assert fourth["authorization_runtime_compatible"] is True
    assert fourth["authorization_created"] is False
    assert fourth["worker_invoked"] is False
    assert fourth["domain_created"] is False
    assert replay["bridge_status"] == DOMAIN_EXECUTION_READY_BRIDGED
    assert "Domain Execution-Ready Bridge" in output[3]
    assert "DEFAULT_PROVIDER_ASSISTED_CONVERSATION" not in output[3]


def test_acli_execution_authorization_prompt_authorizes_freshdomain_without_worker_request(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(
            [
                PROMPT,
                REPLY,
                APPROVAL_PROMPT,
                EXECUTION_READY_PROMPT,
                EXECUTION_AUTHORIZATION_PROMPT,
                "exit",
            ]
        ),
        output_func=output.append,
    )
    fifth = result["turns"][4]
    replay = reconstruct_execution_authorization_replay(
        tmp_path
        / "interactive_runtime"
        / SESSION_ID
        / "TURN-000005"
        / "execution_authorization"
    )

    assert result["failed_turns"] == 0
    assert fifth["response_source"] == "DOMAIN_EXECUTION_AUTHORIZATION"
    assert fifth["execution_authorization_status"] == EXECUTION_AUTHORIZED
    assert fifth["authorization_created"] is True
    assert fifth["worker_request_created"] is False
    assert fifth["worker_invoked"] is False
    assert fifth["execution_started"] is False
    assert fifth["domain_created"] is False
    assert replay["authorization_status"] == EXECUTION_AUTHORIZED
    assert "Authorization Status: EXECUTION_AUTHORIZED" in output[4]
    assert "DEFAULT_PROVIDER_ASSISTED_CONVERSATION" not in output[4]


def test_worker_request_entry_intent_detection_supports_required_prompts() -> None:
    prompts = {
        "Create worker request for FreshDomain.": "CREATE_WORKER_REQUEST",
        "Continue FreshDomain to worker request.": "CONTINUE_TO_WORKER_REQUEST",
        "Create authorized worker request for FreshDomain.": "CREATE_AUTHORIZED_WORKER_REQUEST",
    }

    for prompt, action in prompts.items():
        detected = detect_domain_worker_request_entry_intent(prompt)

        assert detected["worker_request_entry_intent_detected"] is True
        assert detected["domain_name"] == "FreshDomain"
        assert detected["worker_request_action"] == action


def test_find_latest_domain_execution_authorization_excludes_requested_entries(tmp_path) -> None:
    session_root = tmp_path / "session"
    approval = _approval_entry(
        tmp_path,
        replay_dir=session_root / "TURN-000003" / "domain_approval_binding",
    )
    bridge = bridge_domain_approval_entry_to_execution_ready(
        bridge_id="DOMAIN-READY-BRIDGE-FRESHDOMAIN-000001",
        domain_approval_binding_replay_reference=approval["domain_approval_binding_replay_reference"],
        approved_domain="FreshDomain",
        created_at=CREATED_AT,
        replay_dir=session_root / "TURN-000004" / "domain_execution_ready_bridge",
    )
    authorization = authorize_execution_ready(
        authorization_id="DOMAIN-AUTHORIZATION-FRESHDOMAIN-000001",
        execution_ready_replay_reference=bridge["execution_ready_replay_reference"],
        authorizing_actor="HUMAN_OPERATOR",
        authorized_at=CREATED_AT,
        replay_dir=session_root / "TURN-000005" / "execution_authorization",
    )

    latest = find_latest_domain_execution_authorization(session_root=session_root, domain_name="FreshDomain")

    assert latest["execution_authorization_replay_reference"] == authorization[
        "execution_authorization_replay_reference"
    ]
    assert latest["domain_name"] == "FreshDomain"

    create_worker_invocation_request(
        invocation_request_id="DOMAIN-WORKER-REQUEST-FRESHDOMAIN-000001",
        execution_authorization_replay_reference=authorization["execution_authorization_replay_reference"],
        requested_by="HUMAN_OPERATOR",
        requested_at=CREATED_AT,
        replay_dir=session_root / "TURN-000006" / "worker_invocation_request",
    )

    with pytest.raises(FailClosedRuntimeError, match="matching execution authorization not found"):
        find_latest_domain_execution_authorization(session_root=session_root, domain_name="FreshDomain")


def test_acli_worker_request_prompt_creates_request_without_assignment_or_invocation(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(
            [
                PROMPT,
                REPLY,
                APPROVAL_PROMPT,
                EXECUTION_READY_PROMPT,
                EXECUTION_AUTHORIZATION_PROMPT,
                WORKER_REQUEST_PROMPT,
                "exit",
            ]
        ),
        output_func=output.append,
    )
    sixth = result["turns"][5]
    replay = reconstruct_worker_invocation_request_replay(
        tmp_path
        / "interactive_runtime"
        / SESSION_ID
        / "TURN-000006"
        / "worker_invocation_request"
    )

    assert result["failed_turns"] == 0
    assert sixth["response_source"] == "DOMAIN_WORKER_REQUEST"
    assert sixth["worker_invocation_request_status"] == WORKER_INVOCATION_REQUEST_CREATED
    assert sixth["worker_request_created"] is True
    assert sixth["worker_assigned"] is False
    assert sixth["worker_dispatched"] is False
    assert sixth["worker_invoked"] is False
    assert sixth["execution_started"] is False
    assert sixth["domain_created"] is False
    assert replay["request_status"] == WORKER_INVOCATION_REQUEST_CREATED
    assert "Request Status: WORKER_INVOCATION_REQUEST_CREATED" in output[5]
    assert "No Worker has been assigned, dispatched, invoked, or executed." in output[5]
    assert "DEFAULT_PROVIDER_ASSISTED_CONVERSATION" not in output[5]


def test_worker_assignment_entry_intent_detection_supports_required_prompts() -> None:
    prompts = {
        "Assign worker for FreshDomain.": "ASSIGN_WORKER",
        "Continue FreshDomain to worker assignment.": "CONTINUE_TO_WORKER_ASSIGNMENT",
        "Create worker assignment for FreshDomain.": "CREATE_WORKER_ASSIGNMENT",
    }

    for prompt, action in prompts.items():
        detected = detect_domain_worker_assignment_entry_intent(prompt)

        assert detected["worker_assignment_entry_intent_detected"] is True
        assert detected["domain_name"] == "FreshDomain"
        assert detected["worker_assignment_action"] == action


def test_find_latest_domain_worker_invocation_request_excludes_assigned_entries(tmp_path) -> None:
    session_root = tmp_path / "session"
    approval = _approval_entry(
        tmp_path,
        replay_dir=session_root / "TURN-000003" / "domain_approval_binding",
    )
    bridge = bridge_domain_approval_entry_to_execution_ready(
        bridge_id="DOMAIN-READY-BRIDGE-FRESHDOMAIN-000001",
        domain_approval_binding_replay_reference=approval["domain_approval_binding_replay_reference"],
        approved_domain="FreshDomain",
        created_at=CREATED_AT,
        replay_dir=session_root / "TURN-000004" / "domain_execution_ready_bridge",
    )
    authorization = authorize_execution_ready(
        authorization_id="DOMAIN-AUTHORIZATION-FRESHDOMAIN-000001",
        execution_ready_replay_reference=bridge["execution_ready_replay_reference"],
        authorizing_actor="HUMAN_OPERATOR",
        authorized_at=CREATED_AT,
        replay_dir=session_root / "TURN-000005" / "execution_authorization",
    )
    worker_request = create_worker_invocation_request(
        invocation_request_id="DOMAIN-WORKER-REQUEST-FRESHDOMAIN-000001",
        execution_authorization_replay_reference=authorization["execution_authorization_replay_reference"],
        requested_by="HUMAN_OPERATOR",
        requested_at=CREATED_AT,
        replay_dir=session_root / "TURN-000006" / "worker_invocation_request",
    )

    latest = find_latest_domain_worker_invocation_request(session_root=session_root, domain_name="FreshDomain")

    assert latest["worker_invocation_request_replay_reference"] == worker_request[
        "worker_invocation_request_replay_reference"
    ]
    assert latest["domain_name"] == "FreshDomain"

    assign_worker_from_invocation_request(
        worker_assignment_id="DOMAIN-WORKER-ASSIGNMENT-FRESHDOMAIN-000001",
        worker_invocation_request_artifact=worker_request["worker_invocation_request_artifact"],
        worker_invocation_request_replay_reference=worker_request["worker_invocation_request_replay_reference"],
        worker_registry_artifacts=default_worker_registry_for_request(
            worker_request["worker_invocation_request_artifact"],
            created_at=CREATED_AT,
        ),
        assigned_by="HUMAN_OPERATOR",
        assigned_at=CREATED_AT,
        replay_dir=session_root / "TURN-000007" / "worker_assignment",
    )

    with pytest.raises(FailClosedRuntimeError, match="matching invocation request not found"):
        find_latest_domain_worker_invocation_request(session_root=session_root, domain_name="FreshDomain")


def test_acli_worker_assignment_prompt_assigns_worker_without_dispatch_or_invocation(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(
            [
                PROMPT,
                REPLY,
                APPROVAL_PROMPT,
                EXECUTION_READY_PROMPT,
                EXECUTION_AUTHORIZATION_PROMPT,
                WORKER_REQUEST_PROMPT,
                WORKER_ASSIGNMENT_PROMPT,
                "exit",
            ]
        ),
        output_func=output.append,
    )
    seventh = result["turns"][6]
    replay = reconstruct_worker_assignment_runtime_replay(
        tmp_path
        / "interactive_runtime"
        / SESSION_ID
        / "TURN-000007"
        / "worker_assignment"
    )

    assert result["failed_turns"] == 0
    assert seventh["response_source"] == "DOMAIN_WORKER_ASSIGNMENT"
    assert seventh["worker_assignment_status"] == WORKER_ASSIGNED
    assert seventh["worker_assigned"] is True
    assert seventh["worker_dispatched"] is False
    assert seventh["worker_invoked"] is False
    assert seventh["execution_started"] is False
    assert seventh["domain_created"] is False
    assert replay["assignment_status"] == WORKER_ASSIGNED
    assert "Assignment Status: WORKER_ASSIGNED" in output[6]
    assert "No Worker has been dispatched, invoked, or executed." in output[6]
    assert "DEFAULT_PROVIDER_ASSISTED_CONVERSATION" not in output[6]


def test_worker_dispatch_entry_intent_detection_supports_required_prompts() -> None:
    prompts = {
        "Dispatch worker for FreshDomain.": "DISPATCH_WORKER",
        "Continue FreshDomain to worker dispatch.": "CONTINUE_TO_WORKER_DISPATCH",
        "Create worker dispatch for FreshDomain.": "CREATE_WORKER_DISPATCH",
    }

    for prompt, action in prompts.items():
        detected = detect_domain_worker_dispatch_entry_intent(prompt)

        assert detected["worker_dispatch_entry_intent_detected"] is True
        assert detected["domain_name"] == "FreshDomain"
        assert detected["worker_dispatch_action"] == action


def test_find_latest_domain_worker_assignment_excludes_dispatched_entries(tmp_path) -> None:
    session_root = tmp_path / "session"
    approval = _approval_entry(
        tmp_path,
        replay_dir=session_root / "TURN-000003" / "domain_approval_binding",
    )
    bridge = bridge_domain_approval_entry_to_execution_ready(
        bridge_id="DOMAIN-READY-BRIDGE-FRESHDOMAIN-000001",
        domain_approval_binding_replay_reference=approval["domain_approval_binding_replay_reference"],
        approved_domain="FreshDomain",
        created_at=CREATED_AT,
        replay_dir=session_root / "TURN-000004" / "domain_execution_ready_bridge",
    )
    authorization = authorize_execution_ready(
        authorization_id="DOMAIN-AUTHORIZATION-FRESHDOMAIN-000001",
        execution_ready_replay_reference=bridge["execution_ready_replay_reference"],
        authorizing_actor="HUMAN_OPERATOR",
        authorized_at=CREATED_AT,
        replay_dir=session_root / "TURN-000005" / "execution_authorization",
    )
    worker_request = create_worker_invocation_request(
        invocation_request_id="DOMAIN-WORKER-REQUEST-FRESHDOMAIN-000001",
        execution_authorization_replay_reference=authorization["execution_authorization_replay_reference"],
        requested_by="HUMAN_OPERATOR",
        requested_at=CREATED_AT,
        replay_dir=session_root / "TURN-000006" / "worker_invocation_request",
    )
    assignment = assign_worker_from_invocation_request(
        worker_assignment_id="DOMAIN-WORKER-ASSIGNMENT-FRESHDOMAIN-000001",
        worker_invocation_request_artifact=worker_request["worker_invocation_request_artifact"],
        worker_invocation_request_replay_reference=worker_request["worker_invocation_request_replay_reference"],
        worker_registry_artifacts=default_worker_registry_for_request(
            worker_request["worker_invocation_request_artifact"],
            created_at=CREATED_AT,
        ),
        assigned_by="HUMAN_OPERATOR",
        assigned_at=CREATED_AT,
        replay_dir=session_root / "TURN-000007" / "worker_assignment",
    )

    latest = find_latest_domain_worker_assignment(session_root=session_root, domain_name="FreshDomain")

    assert latest["worker_assignment_replay_reference"] == assignment["worker_assignment_replay_reference"]
    assert latest["domain_name"] == "FreshDomain"

    dispatch_assigned_worker(
        worker_dispatch_id="DOMAIN-WORKER-DISPATCH-FRESHDOMAIN-000001",
        worker_assignment_artifact=assignment["worker_assignment_artifact"],
        worker_assignment_replay_reference=assignment["worker_assignment_replay_reference"],
        dispatched_by="HUMAN_OPERATOR",
        dispatched_at=CREATED_AT,
        replay_dir=session_root / "TURN-000008" / "worker_dispatch",
    )

    with pytest.raises(FailClosedRuntimeError, match="matching worker assignment not found"):
        find_latest_domain_worker_assignment(session_root=session_root, domain_name="FreshDomain")


def test_acli_worker_dispatch_prompt_dispatches_worker_without_invocation_or_execution(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(
            [
                PROMPT,
                REPLY,
                APPROVAL_PROMPT,
                EXECUTION_READY_PROMPT,
                EXECUTION_AUTHORIZATION_PROMPT,
                WORKER_REQUEST_PROMPT,
                WORKER_ASSIGNMENT_PROMPT,
                WORKER_DISPATCH_PROMPT,
                "exit",
            ]
        ),
        output_func=output.append,
    )
    eighth = result["turns"][7]
    replay = reconstruct_worker_dispatch_replay(
        tmp_path
        / "interactive_runtime"
        / SESSION_ID
        / "TURN-000008"
        / "worker_dispatch"
    )

    assert result["failed_turns"] == 0
    assert eighth["response_source"] == "DOMAIN_WORKER_DISPATCH"
    assert eighth["worker_dispatch_status"] == WORKER_DISPATCHED
    assert eighth["worker_assigned"] is True
    assert eighth["worker_dispatched"] is True
    assert eighth["worker_invoked"] is False
    assert eighth["execution_started"] is False
    assert eighth["domain_created"] is False
    assert replay["dispatch_status"] == WORKER_DISPATCHED
    assert "Dispatch Status: WORKER_DISPATCHED" in output[7]
    assert "No Worker has been invoked, executed, or produced results." in output[7]
    assert "DEFAULT_PROVIDER_ASSISTED_CONVERSATION" not in output[7]


def test_worker_invocation_entry_intent_detection_supports_required_prompts() -> None:
    cases = {
        "Invoke worker for FreshDomain.": "INVOKE_WORKER",
        "Continue FreshDomain to worker invocation.": "CONTINUE_TO_WORKER_INVOCATION",
        "Create worker invocation for FreshDomain.": "CREATE_WORKER_INVOCATION",
    }

    for prompt, action in cases.items():
        detected = detect_domain_worker_invocation_entry_intent(prompt)

        assert detected["worker_invocation_entry_intent_detected"] is True
        assert detected["domain_name"] == "FreshDomain"
        assert detected["worker_invocation_action"] == action


def test_find_latest_domain_worker_dispatch_excludes_invoked_entries(tmp_path) -> None:
    session_root = tmp_path / "session"
    approval = _approval_entry(
        tmp_path,
        replay_dir=session_root / "TURN-000003" / "domain_approval_binding",
    )
    bridge = bridge_domain_approval_entry_to_execution_ready(
        bridge_id="DOMAIN-READY-BRIDGE-FRESHDOMAIN-000001",
        domain_approval_binding_replay_reference=approval["domain_approval_binding_replay_reference"],
        approved_domain="FreshDomain",
        created_at=CREATED_AT,
        replay_dir=session_root / "TURN-000004" / "domain_execution_ready_bridge",
    )
    authorization = authorize_execution_ready(
        authorization_id="DOMAIN-AUTHORIZATION-FRESHDOMAIN-000001",
        execution_ready_replay_reference=bridge["execution_ready_replay_reference"],
        authorizing_actor="HUMAN_OPERATOR",
        authorized_at=CREATED_AT,
        replay_dir=session_root / "TURN-000005" / "execution_authorization",
    )
    worker_request = create_worker_invocation_request(
        invocation_request_id="DOMAIN-WORKER-REQUEST-FRESHDOMAIN-000001",
        execution_authorization_replay_reference=authorization["execution_authorization_replay_reference"],
        requested_by="HUMAN_OPERATOR",
        requested_at=CREATED_AT,
        replay_dir=session_root / "TURN-000006" / "worker_invocation_request",
    )
    assignment = assign_worker_from_invocation_request(
        worker_assignment_id="DOMAIN-WORKER-ASSIGNMENT-FRESHDOMAIN-000001",
        worker_invocation_request_artifact=worker_request["worker_invocation_request_artifact"],
        worker_invocation_request_replay_reference=worker_request["worker_invocation_request_replay_reference"],
        worker_registry_artifacts=default_worker_registry_for_request(
            worker_request["worker_invocation_request_artifact"],
            created_at=CREATED_AT,
        ),
        assigned_by="HUMAN_OPERATOR",
        assigned_at=CREATED_AT,
        replay_dir=session_root / "TURN-000007" / "worker_assignment",
    )
    dispatch = dispatch_assigned_worker(
        worker_dispatch_id="DOMAIN-WORKER-DISPATCH-FRESHDOMAIN-000001",
        worker_assignment_artifact=assignment["worker_assignment_artifact"],
        worker_assignment_replay_reference=assignment["worker_assignment_replay_reference"],
        dispatched_by="HUMAN_OPERATOR",
        dispatched_at=CREATED_AT,
        replay_dir=session_root / "TURN-000008" / "worker_dispatch",
    )

    latest = find_latest_domain_worker_dispatch(session_root=session_root, domain_name="FreshDomain")

    assert latest["worker_dispatch_replay_reference"] == dispatch["worker_dispatch_replay_reference"]
    assert latest["domain_name"] == "FreshDomain"

    invoke_dispatched_worker(
        worker_invocation_id="DOMAIN-WORKER-INVOCATION-FRESHDOMAIN-000001",
        worker_dispatch_artifact=dispatch["worker_dispatch_artifact"],
        worker_dispatch_replay_reference=dispatch["worker_dispatch_replay_reference"],
        invoked_by="HUMAN_OPERATOR",
        invoked_at=CREATED_AT,
        replay_dir=session_root / "TURN-000009" / "worker_invocation",
    )

    with pytest.raises(FailClosedRuntimeError, match="matching worker dispatch not found"):
        find_latest_domain_worker_dispatch(session_root=session_root, domain_name="FreshDomain")


def test_worker_invocation_binds_latest_dispatch_with_relative_replay_references(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    session_root = Path("runtime") / SESSION_ID
    prompt_id = _seed_open_clarification(session_root)
    continuity = run_clarification_continuity(
        continuity_id=f"{SESSION_ID}:TURN-000002:CLARIFICATION-CONTINUITY",
        session_root=session_root,
        turn_id="TURN-000002",
        prompt_id=f"{SESSION_ID}:TURN-000002",
        operator_reply=REPLY,
        current_chain_id=prompt_id,
        created_at=CREATED_AT,
        replay_dir=session_root / "TURN-000002" / "clarification_continuity",
    )
    review = review_clarified_domain_intent(
        review_id=f"{SESSION_ID}:TURN-000002:CLARIFIED-DOMAIN-HANDOFF-REVIEW",
        clarification_continuity_replay_reference=continuity["clarification_continuity_replay_reference"],
        review_decision=WORKER_BINDING_APPROVED,
        reviewed_by="AIGOL_GOVERNANCE_REVIEW",
        created_at=CREATED_AT,
        replay_dir=session_root / "TURN-000002" / "clarified_domain_handoff_review",
    )
    approval = bind_domain_handoff_review_approval(
        approval_entry_id=f"{SESSION_ID}:TURN-000003:DOMAIN-APPROVAL-BINDING",
        handoff_review_replay_reference=review["handoff_review_replay_reference"],
        operator_prompt=APPROVAL_PROMPT,
        approved_domain="FreshDomain",
        approving_actor="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
        replay_dir=session_root / "TURN-000003" / "domain_approval_binding",
        latest_handoff_review_replay_reference=review["handoff_review_replay_reference"],
    )
    bridge = bridge_domain_approval_entry_to_execution_ready(
        bridge_id=f"{SESSION_ID}:TURN-000004:DOMAIN-EXECUTION-READY-BRIDGE",
        domain_approval_binding_replay_reference=approval["domain_approval_binding_replay_reference"],
        approved_domain="FreshDomain",
        created_at=CREATED_AT,
        replay_dir=session_root / "TURN-000004" / "domain_execution_ready_bridge",
    )
    authorization = authorize_execution_ready(
        authorization_id=f"{SESSION_ID}:TURN-000005:EXECUTION-AUTHORIZATION",
        execution_ready_replay_reference=bridge["execution_ready_replay_reference"],
        authorizing_actor="HUMAN_OPERATOR",
        authorized_at=CREATED_AT,
        replay_dir=session_root / "TURN-000005" / "execution_authorization",
    )
    worker_request = create_worker_invocation_request(
        invocation_request_id=f"{SESSION_ID}:TURN-000006:WORKER-INVOCATION-REQUEST",
        execution_authorization_replay_reference=authorization["execution_authorization_replay_reference"],
        requested_by="HUMAN_OPERATOR",
        requested_at=CREATED_AT,
        replay_dir=session_root / "TURN-000006" / "worker_invocation_request",
    )
    assignment = assign_worker_from_invocation_request(
        worker_assignment_id=f"{SESSION_ID}:TURN-000007:WORKER-ASSIGNMENT",
        worker_invocation_request_artifact=worker_request["worker_invocation_request_artifact"],
        worker_invocation_request_replay_reference=worker_request["worker_invocation_request_replay_reference"],
        worker_registry_artifacts=default_worker_registry_for_request(
            worker_request["worker_invocation_request_artifact"],
            created_at=CREATED_AT,
        ),
        assigned_by="HUMAN_OPERATOR",
        assigned_at=CREATED_AT,
        replay_dir=session_root / "TURN-000007" / "worker_assignment",
    )
    dispatch = dispatch_assigned_worker(
        worker_dispatch_id=f"{SESSION_ID}:TURN-000008:WORKER-DISPATCH",
        worker_assignment_artifact=assignment["worker_assignment_artifact"],
        worker_assignment_replay_reference=assignment["worker_assignment_replay_reference"],
        dispatched_by="HUMAN_OPERATOR",
        dispatched_at=CREATED_AT,
        replay_dir=session_root / "TURN-000008" / "worker_dispatch",
    )

    other_cwd = tmp_path / "other"
    other_cwd.mkdir()
    monkeypatch.chdir(other_cwd)
    absolute_session_root = tmp_path / "runtime" / SESSION_ID

    latest = find_latest_domain_worker_dispatch(
        session_root=absolute_session_root,
        domain_name="FreshDomain",
    )
    invocation = invoke_dispatched_worker(
        worker_invocation_id=f"{SESSION_ID}:TURN-000009:WORKER-INVOCATION",
        worker_dispatch_artifact=latest["worker_dispatch_artifact"],
        worker_dispatch_replay_reference=latest["worker_dispatch_replay_reference"],
        invoked_by="HUMAN_OPERATOR",
        invoked_at=CREATED_AT,
        replay_dir=absolute_session_root / "TURN-000009" / "worker_invocation",
    )

    assert latest["worker_dispatch_replay_reference"] == str(
        tmp_path / dispatch["worker_dispatch_replay_reference"]
    )
    assert invocation["invocation_status"] == WORKER_INVOKED
    assert invocation["worker_dispatch_reference"] == dispatch["worker_dispatch_reference"]
    assert invocation["execution_started"] is False


def test_acli_worker_invocation_prompt_invokes_worker_without_execution_or_result_validation(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(
            [
                PROMPT,
                REPLY,
                APPROVAL_PROMPT,
                EXECUTION_READY_PROMPT,
                EXECUTION_AUTHORIZATION_PROMPT,
                WORKER_REQUEST_PROMPT,
                WORKER_ASSIGNMENT_PROMPT,
                WORKER_DISPATCH_PROMPT,
                WORKER_INVOCATION_PROMPT,
                "exit",
            ]
        ),
        output_func=output.append,
    )
    ninth = result["turns"][8]
    replay = reconstruct_worker_invocation_replay(
        tmp_path
        / "interactive_runtime"
        / SESSION_ID
        / "TURN-000009"
        / "worker_invocation"
    )

    assert result["failed_turns"] == 0
    assert ninth["response_source"] == "DOMAIN_WORKER_INVOCATION"
    assert ninth["worker_invocation_status"] == WORKER_INVOKED
    assert ninth["worker_assigned"] is True
    assert ninth["worker_dispatched"] is True
    assert ninth["worker_invoked"] is True
    assert ninth["execution_started"] is False
    assert ninth["domain_created"] is False
    assert replay["invocation_status"] == WORKER_INVOKED
    assert replay["execution_started"] is False
    assert replay["result_created"] is False
    assert "Invocation Status: WORKER_INVOKED" in output[8]
    assert "No result validation yet." in output[8]
    assert "No replay review yet." in output[8]
    assert "No termination yet." in output[8]
    assert "DEFAULT_PROVIDER_ASSISTED_CONVERSATION" not in output[8]


def test_acli_worker_invocation_continuation_creates_missing_assignment_and_dispatch(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(
            [
                PROMPT,
                REPLY,
                APPROVAL_PROMPT,
                EXECUTION_READY_PROMPT,
                EXECUTION_AUTHORIZATION_PROMPT,
                WORKER_REQUEST_PROMPT,
                WORKER_INVOCATION_PROMPT,
                "exit",
            ]
        ),
        output_func=output.append,
    )
    seventh = result["turns"][6]
    session_root = tmp_path / "interactive_runtime" / SESSION_ID
    assignment = reconstruct_worker_assignment_runtime_replay(
        session_root / "TURN-000007" / "worker_assignment"
    )
    dispatch = reconstruct_worker_dispatch_replay(
        session_root / "TURN-000007" / "worker_dispatch"
    )
    invocation = reconstruct_worker_invocation_replay(
        session_root / "TURN-000007" / "worker_invocation"
    )

    assert result["failed_turns"] == 0
    assert seventh["response_source"] == "DOMAIN_WORKER_INVOCATION"
    assert assignment["assignment_status"] == WORKER_ASSIGNED
    assert dispatch["dispatch_status"] == WORKER_DISPATCHED
    assert invocation["invocation_status"] == WORKER_INVOKED
    assert seventh["worker_invocation_status"] == WORKER_INVOKED
    assert seventh["worker_assigned"] is True
    assert seventh["worker_dispatched"] is True
    assert seventh["worker_invoked"] is True
    assert seventh["execution_started"] is False
    assert "Assignment Status: WORKER_ASSIGNED" in output[6]
    assert "Dispatch Status: WORKER_DISPATCHED" in output[6]
    assert "Invocation Status: WORKER_INVOKED" in output[6]


def test_worker_execution_entry_intent_detection_supports_required_prompts(tmp_path) -> None:
    cases = {
        "Execute worker for FreshDomain.": "EXECUTE_WORKER",
        "Start worker execution for FreshDomain.": "START_WORKER_EXECUTION",
        "Continue FreshDomain to worker execution.": "CONTINUE_TO_WORKER_EXECUTION",
        "Create worker execution for FreshDomain.": "CREATE_WORKER_EXECUTION",
    }

    for prompt, action in cases.items():
        detected = detect_domain_worker_execution_entry_intent(prompt)
        routed = route_conversational_cli_intent(
            routing_id=f"ROUTE-{action}",
            prompt_id=f"PROMPT-{action}",
            human_prompt=prompt,
            canonical_chain_id=f"CHAIN-{action}",
            created_at=CREATED_AT,
            replay_dir=tmp_path / f"routing_{action}",
        )

        assert detected["worker_execution_entry_intent_detected"] is True
        assert detected["domain_name"] == "FreshDomain"
        assert detected["worker_execution_action"] == action
        assert routed["workflow_id"] == "DOMAIN_WORKER_EXECUTION"


def test_acli_worker_execution_prompt_starts_execution_without_result_validation(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(
            [
                PROMPT,
                REPLY,
                APPROVAL_PROMPT,
                EXECUTION_READY_PROMPT,
                EXECUTION_AUTHORIZATION_PROMPT,
                WORKER_REQUEST_PROMPT,
                WORKER_ASSIGNMENT_PROMPT,
                WORKER_DISPATCH_PROMPT,
                WORKER_INVOCATION_PROMPT,
                WORKER_EXECUTION_PROMPT,
                "exit",
            ]
        ),
        output_func=output.append,
    )
    tenth = result["turns"][9]
    session_root = tmp_path / "interactive_runtime" / SESSION_ID
    invocation = reconstruct_worker_invocation_replay(
        session_root
        / "TURN-000009"
        / "worker_invocation"
    )
    dispatch = reconstruct_worker_dispatch_replay(
        session_root
        / "TURN-000008"
        / "worker_dispatch"
    )
    replay = reconstruct_execution_replay(
        session_root
        / "TURN-000010"
        / "execution_runtime"
    )
    invocation_artifact = load_json(
        session_root
        / "TURN-000009"
        / "worker_invocation"
        / "002_invocation_artifact_recorded.json"
    )["artifact"]

    assert result["failed_turns"] == 0
    assert tenth["response_source"] == "DOMAIN_WORKER_EXECUTION"
    assert tenth["execution_runtime_status"] == EXECUTING
    assert tenth["execution_started"] is True
    assert tenth["worker_invoked"] is True
    assert tenth["worker_result_captured"] is False
    assert tenth["worker_result_validated"] is False
    assert tenth["post_execution_replay_reviewed"] is False
    assert replay["execution_status"] == EXECUTING
    assert invocation_artifact["invoked_by"] == "AIGOL_GOVERNANCE"
    assert replay["worker_invocation_reference"] == invocation["worker_invocation_id"]
    assert replay["dispatch_reference"] == dispatch["worker_dispatch_id"]
    assert replay["completion_recorded"] is False
    assert replay["result_certified"] is False
    assert "Execution Status: EXECUTING" in output[9]
    assert "No completion recorded." in output[9]
    assert "No result certification recorded." in output[9]
    assert "DEFAULT_PROVIDER_ASSISTED_CONVERSATION" not in output[9]


def test_bridge_replay_tampering_is_detected(tmp_path) -> None:
    _bridge(tmp_path)
    path = tmp_path / "ready_bridge" / "execution_ready" / "000_execution_candidate_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["target_domain"] = "OtherDomain"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_domain_execution_ready_bridge_replay(tmp_path / "ready_bridge")


def test_domain_mismatch_fails_closed(tmp_path) -> None:
    capture = _bridge(tmp_path, domain="OtherDomain")

    assert capture["fail_closed"] is True
    assert "approved-domain mismatch" in capture["failure_reason"]
    assert capture["authorization_created"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_started"] is False


def test_approval_lineage_mismatch_fails_closed(tmp_path) -> None:
    approval = _approval_entry(tmp_path)
    path = tmp_path / "approval_binding" / "000_domain_approval_binding_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["approval_reference"] = "OTHER-APPROVAL"
    wrapper["artifact"]["artifact_hash"] = "sha256:broken"
    wrapper["replay_hash"] = "sha256:broken"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    capture = bridge_domain_approval_entry_to_execution_ready(
        bridge_id="DOMAIN-READY-BRIDGE-FRESHDOMAIN-000002",
        domain_approval_binding_replay_reference=approval["domain_approval_binding_replay_reference"],
        approved_domain="FreshDomain",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "approval_mismatch_bridge",
    )

    assert capture["fail_closed"] is True
    assert "hash mismatch" in capture["failure_reason"]
