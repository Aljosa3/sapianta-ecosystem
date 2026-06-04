"""Tests for AIGOL_IMPLEMENTATION_APPROVAL_RESUME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.conversation_native_development_intent_routing import run_conversation_native_development_intent_routing
from aigol.runtime.conversation_session_resume_runtime import resume_conversation_session
from aigol.runtime.conversation_to_implementation_handoff_runtime import IMPLEMENTATION_HANDOFF_CREATED
from aigol.runtime.conversation_to_ppp_handoff_execution import (
    HUMAN_APPROVAL_REQUIRED,
    run_conversation_to_ppp_handoff_execution,
)
from aigol.runtime.implementation_approval_resume import (
    APPROVED,
    IMPLEMENTATION_APPROVAL_RESUMED,
    create_human_implementation_approval,
    reconstruct_implementation_approval_resume_replay,
    resume_implementation_after_approval,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


CREATED_AT = "2026-06-04T00:00:00+00:00"
SESSION_ID = "SESSION-IMPLEMENTATION-APPROVAL-RESUME-000001"


def _args(tmp_path, *, session_id: str = SESSION_ID):
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


def _approval_required(tmp_path):
    allocation = resume_conversation_session(
        session_id=SESSION_ID,
        runtime_root=tmp_path / "routing_runtime",
        created_at=CREATED_AT,
    )
    prompt_id = f"{SESSION_ID}:{allocation['next_turn_id']}"
    routed = run_conversation_native_development_intent_routing(
        routing_id=f"{prompt_id}:NATIVE_DEVELOPMENT_INTENT_ROUTING",
        prompt_id=prompt_id,
        human_prompt="Improve trading strategy.",
        canonical_chain_id=prompt_id,
        turn_allocation_evidence=allocation,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "routing",
    )
    return run_conversation_to_ppp_handoff_execution(
        execution_id=f"{prompt_id}:CONVERSATION-TO-PPP-HANDOFF",
        native_development_intent_routed_artifact=routed["native_development_intent_routed_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "approval_required",
    )


def _human_approval(capture, *, actor: str = "human.operator", expires_at: str = "NEVER"):
    request = capture["conversation_to_ppp_handoff_execution_artifact"]["approval_resume_packet"][
        "approval_request_artifact"
    ]
    return create_human_implementation_approval(
        approval_id="HUMAN-APPROVAL-000001",
        approval_request_artifact=request,
        approving_actor=actor,
        approval_timestamp=CREATED_AT,
        approval_expires_at=expires_at,
    )


def test_resumes_approval_required_chain_to_implementation_handoff(tmp_path) -> None:
    approval_required = _approval_required(tmp_path)
    approval = _human_approval(approval_required)
    capture = resume_implementation_after_approval(
        resume_id="APPROVAL-RESUME-000001",
        approval_required_replay_reference=approval_required["conversation_to_ppp_handoff_execution_replay_reference"],
        human_approval_artifact=approval,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "resume",
    )
    reconstructed = reconstruct_implementation_approval_resume_replay(tmp_path / "resume")

    assert approval_required["terminal_status"] == HUMAN_APPROVAL_REQUIRED
    assert approval["approval_status"] == APPROVED
    assert approval["approval_hash"].startswith("sha256:")
    assert capture["resume_status"] == IMPLEMENTATION_APPROVAL_RESUMED
    assert capture["handoff_status"] == IMPLEMENTATION_HANDOFF_CREATED
    assert capture["chain_id"] == approval_required["canonical_chain_id"]
    assert capture["approval_id"] == approval["approval_id"]
    assert capture["approval_scope"] == approval["approval_scope"]
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert reconstructed["resume_status"] == IMPLEMENTATION_APPROVAL_RESUMED
    assert reconstructed["handoff_status"] == IMPLEMENTATION_HANDOFF_CREATED


def test_cli_approval_resume_acceptance_flow(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-APPROVAL-RESUME-CLI-000001"),
        input_func=_input_sequence(["Improve trading strategy.", "Approve.", "exit"]),
        output_func=output.append,
    )

    assert result["turn_count"] == 2
    assert result["failed_turns"] == 0
    assert result["turns"][0]["response_status"] == HUMAN_APPROVAL_REQUIRED
    assert result["turns"][1]["response_source"] == "IMPLEMENTATION_APPROVAL_RESUME"
    assert result["turns"][1]["response_status"] == IMPLEMENTATION_HANDOFF_CREATED
    assert result["turns"][1]["approval_resume_status"] == IMPLEMENTATION_APPROVAL_RESUMED
    assert "approval_status: HUMAN_APPROVAL_REQUIRED" in output[0]
    assert "approval_resume_status: IMPLEMENTATION_APPROVAL_RESUMED" in output[1]
    assert "handoff_status: IMPLEMENTATION_HANDOFF_CREATED" in output[1]
    assert "Handoff Summary" in output[1]


def test_resume_fails_closed_when_approval_missing(tmp_path) -> None:
    approval_required = _approval_required(tmp_path)
    capture = resume_implementation_after_approval(
        resume_id="APPROVAL-RESUME-MISSING-000001",
        approval_required_replay_reference=approval_required["conversation_to_ppp_handoff_execution_replay_reference"],
        human_approval_artifact={},
        created_at=CREATED_AT,
        replay_dir=tmp_path / "resume",
    )

    assert capture["resume_status"] == "FAILED_CLOSED"
    assert "approval missing" in capture["failure_reason"]


def test_resume_fails_closed_on_chain_mismatch(tmp_path) -> None:
    approval_required = _approval_required(tmp_path)
    approval = _human_approval(approval_required)
    approval["chain_id"] = "WRONG-CHAIN"
    approval["approval_hash"] = "sha256:stale"
    approval["artifact_hash"] = "sha256:stale"
    capture = resume_implementation_after_approval(
        resume_id="APPROVAL-RESUME-CHAIN-MISMATCH-000001",
        approval_required_replay_reference=approval_required["conversation_to_ppp_handoff_execution_replay_reference"],
        human_approval_artifact=approval,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "resume",
    )

    assert capture["resume_status"] == "FAILED_CLOSED"
    assert "hash mismatch" in capture["failure_reason"]


def test_resume_fails_closed_on_scope_mismatch(tmp_path) -> None:
    approval_required = _approval_required(tmp_path)
    approval = _human_approval(approval_required)
    approval["approval_scope"] = "TRADING:UNRELATED"
    approval["approval_hash"] = "sha256:stale"
    approval["artifact_hash"] = "sha256:stale"
    capture = resume_implementation_after_approval(
        resume_id="APPROVAL-RESUME-SCOPE-MISMATCH-000001",
        approval_required_replay_reference=approval_required["conversation_to_ppp_handoff_execution_replay_reference"],
        human_approval_artifact=approval,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "resume",
    )

    assert capture["resume_status"] == "FAILED_CLOSED"
    assert "hash mismatch" in capture["failure_reason"]


def test_resume_fails_closed_when_approval_expired(tmp_path) -> None:
    approval_required = _approval_required(tmp_path)
    approval = _human_approval(approval_required, expires_at="2026-06-03T00:00:00+00:00")
    capture = resume_implementation_after_approval(
        resume_id="APPROVAL-RESUME-EXPIRED-000001",
        approval_required_replay_reference=approval_required["conversation_to_ppp_handoff_execution_replay_reference"],
        human_approval_artifact=approval,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "resume",
    )

    assert capture["resume_status"] == "FAILED_CLOSED"
    assert "approval expired" in capture["failure_reason"]


def test_resume_reconstruction_detects_replay_corruption(tmp_path) -> None:
    approval_required = _approval_required(tmp_path)
    approval = _human_approval(approval_required)
    resume_implementation_after_approval(
        resume_id="APPROVAL-RESUME-CORRUPT-000001",
        approval_required_replay_reference=approval_required["conversation_to_ppp_handoff_execution_replay_reference"],
        human_approval_artifact=approval,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "resume",
    )
    path = tmp_path / "resume" / "002_approval_resume_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["chain_id"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_implementation_approval_resume_replay(tmp_path / "resume")


def test_approval_resume_preserves_authority_boundaries() -> None:
    import aigol.runtime.implementation_approval_resume as runtime

    source = inspect.getsource(runtime)

    assert "invoke_worker(" not in source
    assert "dispatch_worker(" not in source
    assert "start_execution(" not in source
    assert "mutate_governance(" not in source
    assert "authorize_unrelated" not in source
