"""Tests for AIGOL_EXECUTION_AUTHORIZATION_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.conversation_native_development_intent_routing import run_conversation_native_development_intent_routing
from aigol.runtime.conversation_session_resume_runtime import resume_conversation_session
from aigol.runtime.conversation_to_ppp_handoff_execution import (
    HUMAN_APPROVAL_REQUIRED,
    run_conversation_to_ppp_handoff_execution,
)
from aigol.runtime.execution_authorization_runtime import (
    EXECUTION_AUTHORIZED,
    authorize_execution_ready,
    reconstruct_execution_authorization_replay,
)
from aigol.runtime.governed_implementation_dry_run import prepare_governed_implementation_dry_run
from aigol.runtime.implementation_approval_resume import (
    create_human_implementation_approval,
    resume_implementation_after_approval,
)
from aigol.runtime.implementation_handoff_visibility import create_implementation_handoff_visibility_summary
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


CREATED_AT = "2026-06-04T00:00:00+00:00"
SESSION_ID = "SESSION-EXECUTION-AUTHORIZATION-000001"


def _args(tmp_path, *, session_id: str):
    parser = build_parser()
    return parser.parse_args(
        [
            "conversation",
            "--session-id",
            session_id,
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "interactive_runtime"),
        ]
    )


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _ppp_capture(tmp_path, *, prompt: str, suffix: str):
    session_id = f"{SESSION_ID}-{suffix}"
    allocation = resume_conversation_session(
        session_id=session_id,
        runtime_root=tmp_path / f"routing_runtime_{suffix}",
        created_at=CREATED_AT,
    )
    prompt_id = f"{session_id}:{allocation['next_turn_id']}"
    routed = run_conversation_native_development_intent_routing(
        routing_id=f"{prompt_id}:NATIVE_DEVELOPMENT_INTENT_ROUTING",
        prompt_id=prompt_id,
        human_prompt=prompt,
        canonical_chain_id=prompt_id,
        turn_allocation_evidence=allocation,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"routing_{suffix}",
    )
    return run_conversation_to_ppp_handoff_execution(
        execution_id=f"{prompt_id}:CONVERSATION-TO-PPP-HANDOFF",
        native_development_intent_routed_artifact=routed["native_development_intent_routed_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"ppp_{suffix}",
    )


def _execution_ready(tmp_path, *, prompt: str, suffix: str):
    ppp = _ppp_capture(tmp_path, prompt=prompt, suffix=suffix)
    upstream = ppp["conversation_to_ppp_handoff_execution_artifact"]
    handoff_replay_reference = ppp.get("handoff_replay_reference")
    approval_status = ppp["approval_status"]
    if ppp["terminal_status"] == HUMAN_APPROVAL_REQUIRED:
        request = upstream["approval_resume_packet"]["approval_request_artifact"]
        approval = create_human_implementation_approval(
            approval_id=f"HUMAN-APPROVAL-{suffix}",
            approval_request_artifact=request,
            approving_actor="human.operator",
            approval_timestamp=CREATED_AT,
        )
        resumed = resume_implementation_after_approval(
            resume_id=f"APPROVAL-RESUME-{suffix}",
            approval_required_replay_reference=ppp["conversation_to_ppp_handoff_execution_replay_reference"],
            human_approval_artifact=approval,
            created_at=CREATED_AT,
            replay_dir=tmp_path / f"approval_resume_{suffix}",
        )
        upstream = resumed["implementation_approval_resume_artifact"]
        handoff_replay_reference = resumed["implementation_handoff_replay_reference"]
        approval_status = "APPROVED"
    visibility = create_implementation_handoff_visibility_summary(
        visibility_id=f"VISIBILITY-{suffix}",
        handoff_replay_reference=handoff_replay_reference,
        approval_status=approval_status,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"visibility_{suffix}",
    )
    return prepare_governed_implementation_dry_run(
        dry_run_id=f"DRY-RUN-{suffix}",
        handoff_replay_reference=handoff_replay_reference,
        handoff_visibility_artifact=visibility["implementation_handoff_visibility_artifact"],
        upstream_lineage_artifact=upstream,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"dry_run_{suffix}",
    )


@pytest.mark.parametrize(
    ("prompt", "suffix", "approval_status"),
    [
        ("Create a filesystem worker.", "filesystem", "APPROVAL_NOT_REQUIRED_FOR_HANDOFF"),
        ("Improve trading strategy.", "trading", "APPROVED"),
    ],
)
def test_execution_ready_becomes_execution_authorized(
    tmp_path,
    prompt: str,
    suffix: str,
    approval_status: str,
) -> None:
    ready = _execution_ready(tmp_path, prompt=prompt, suffix=suffix)
    capture = authorize_execution_ready(
        authorization_id=f"AUTHORIZATION-{suffix}",
        execution_ready_replay_reference=ready["governed_implementation_dry_run_replay_reference"],
        authorizing_actor="AIGOL_GOVERNANCE",
        authorized_at=CREATED_AT,
        replay_dir=tmp_path / f"authorization_{suffix}",
    )
    reconstructed = reconstruct_execution_authorization_replay(tmp_path / f"authorization_{suffix}")

    authorization = capture["execution_authorization_artifact"]
    assert capture["authorization_status"] == EXECUTION_AUTHORIZED
    assert authorization["approval_status"] == approval_status
    assert authorization["authorization_revoked"] is False
    assert authorization["authorization_transferable"] is False
    assert capture["worker_assigned"] is False
    assert capture["worker_dispatched"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_started"] is False
    assert reconstructed["authorization_status"] == EXECUTION_AUTHORIZED


def test_execution_authorization_fails_closed_on_packet_corruption(tmp_path) -> None:
    ready = _execution_ready(tmp_path, prompt="Create a filesystem worker.", suffix="corrupt")
    replay_dir = ready["governed_implementation_dry_run_replay_reference"]
    path = tmp_path / "dry_run_corrupt" / "001_execution_packet_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["allowed_outputs"] = []
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    capture = authorize_execution_ready(
        authorization_id="AUTHORIZATION-CORRUPT",
        execution_ready_replay_reference=replay_dir,
        authorizing_actor="AIGOL_GOVERNANCE",
        authorized_at=CREATED_AT,
        replay_dir=tmp_path / "authorization_corrupt",
    )

    assert capture["authorization_status"] == "FAILED_CLOSED"
    assert "hash mismatch" in capture["failure_reason"]


def test_execution_authorization_reconstruction_detects_corruption(tmp_path) -> None:
    ready = _execution_ready(tmp_path, prompt="Create a filesystem worker.", suffix="replay")
    authorize_execution_ready(
        authorization_id="AUTHORIZATION-REPLAY",
        execution_ready_replay_reference=ready["governed_implementation_dry_run_replay_reference"],
        authorizing_actor="AIGOL_GOVERNANCE",
        authorized_at=CREATED_AT,
        replay_dir=tmp_path / "authorization_replay",
    )
    path = tmp_path / "authorization_replay" / "002_authorization_artifact_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["authorization_revoked"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_execution_authorization_replay(tmp_path / "authorization_replay")


def test_cli_acceptance_flows_reach_execution_authorized(tmp_path) -> None:
    filesystem_output: list[str] = []
    filesystem = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-AUTHORIZATION-CLI-FILESYSTEM"),
        input_func=_input_sequence(["Create a filesystem worker.", "exit"]),
        output_func=filesystem_output.append,
    )
    trading_output: list[str] = []
    trading = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-AUTHORIZATION-CLI-TRADING"),
        input_func=_input_sequence(["Improve trading strategy.", "Approve.", "exit"]),
        output_func=trading_output.append,
    )

    assert filesystem["turns"][0]["execution_authorization_status"] == EXECUTION_AUTHORIZED
    assert "Authorization Status: EXECUTION_AUTHORIZED" in filesystem_output[0]
    assert "No Worker has been assigned, dispatched, invoked, or executed." in filesystem_output[0]
    assert trading["turns"][0]["response_status"] == HUMAN_APPROVAL_REQUIRED
    assert trading["turns"][1]["execution_authorization_status"] == EXECUTION_AUTHORIZED
    assert "Authorization Status: EXECUTION_AUTHORIZED" in trading_output[1]


def test_execution_authorization_runtime_preserves_authority_boundaries() -> None:
    import aigol.runtime.execution_authorization_runtime as runtime

    source = inspect.getsource(runtime)

    assert "assign_worker(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_result(" not in source
    assert "create_human_implementation_approval(" not in source
    assert "mutate_governance(" not in source
