"""Tests for AIGOL_IMPLEMENTATION_HANDOFF_VISIBILITY_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.conversation_native_development_intent_routing import run_conversation_native_development_intent_routing
from aigol.runtime.conversation_session_resume_runtime import resume_conversation_session
from aigol.runtime.conversation_to_implementation_handoff_runtime import IMPLEMENTATION_HANDOFF_CREATED
from aigol.runtime.conversation_to_ppp_handoff_execution import run_conversation_to_ppp_handoff_execution
from aigol.runtime.implementation_handoff_visibility import (
    IMPLEMENTATION_HANDOFF_SUMMARY_CREATED,
    create_implementation_handoff_visibility_summary,
    reconstruct_implementation_handoff_visibility_replay,
    render_implementation_handoff_visibility_summary,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


CREATED_AT = "2026-06-04T00:00:00+00:00"
SESSION_ID = "SESSION-HANDOFF-VISIBILITY-000001"


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


def _handoff_capture(tmp_path, *, prompt: str = "Create a filesystem worker."):
    allocation = resume_conversation_session(
        session_id=SESSION_ID,
        runtime_root=tmp_path / "routing_runtime",
        created_at=CREATED_AT,
    )
    prompt_id = f"{SESSION_ID}:{allocation['next_turn_id']}"
    routed = run_conversation_native_development_intent_routing(
        routing_id=f"{prompt_id}:NATIVE_DEVELOPMENT_INTENT_ROUTING",
        prompt_id=prompt_id,
        human_prompt=prompt,
        canonical_chain_id=prompt_id,
        turn_allocation_evidence=allocation,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "routing",
    )
    return run_conversation_to_ppp_handoff_execution(
        execution_id=f"{prompt_id}:CONVERSATION-TO-PPP-HANDOFF",
        native_development_intent_routed_artifact=routed["native_development_intent_routed_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "handoff_execution",
    )


def test_creates_human_readable_handoff_visibility_summary(tmp_path) -> None:
    handoff = _handoff_capture(tmp_path)
    capture = create_implementation_handoff_visibility_summary(
        visibility_id="HANDOFF-VISIBILITY-000001",
        handoff_replay_reference=handoff["handoff_replay_reference"],
        approval_status=handoff["approval_status"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "visibility",
    )
    reconstructed = reconstruct_implementation_handoff_visibility_replay(tmp_path / "visibility")
    rendered = render_implementation_handoff_visibility_summary(capture)

    assert handoff["terminal_status"] == IMPLEMENTATION_HANDOFF_CREATED
    assert capture["summary_status"] == IMPLEMENTATION_HANDOFF_SUMMARY_CREATED
    assert capture["target_domain"] == "SERVER_MANAGEMENT"
    assert capture["target_resource"] == "WORKER"
    assert capture["target_worker"] == "FILESYSTEM"
    assert "governance/SERVER_MANAGEMENT_FILESYSTEM_WORKER_FOUNDATION_V1.md" in capture["planned_artifacts"]
    assert "governance/SERVER_MANAGEMENT_FILESYSTEM_WORKER_MODEL_V1.md" in capture["planned_artifacts"]
    assert "governance/SERVER_MANAGEMENT_FILESYSTEM_WORKER_CERTIFICATION.json" in capture["planned_artifacts"]
    assert "CLAUDE_CODE (WORKER_ROLE)" in capture["required_resource_roles"]
    assert capture["estimated_scope"] == {"governance_artifacts": 3, "runtime_artifacts": 1, "tests": 2}
    assert capture["approval_status"] == "NOT REQUIRED"
    assert capture["implementation_authorized"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert reconstructed["summary_hash"] == capture["summary_hash"]
    assert reconstructed["planned_artifacts"] == capture["planned_artifacts"]
    assert "Handoff Summary" in rendered
    assert "Target Domain:\nSERVER_MANAGEMENT" in rendered
    assert "* CLAUDE_CODE (WORKER_ROLE)" in rendered


def test_cli_prints_handoff_summary_for_created_handoff(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-HANDOFF-VISIBILITY-CLI-000001"),
        input_func=_input_sequence(["Create a filesystem worker.", "exit"]),
        output_func=output.append,
    )

    assert result["failed_turns"] == 0
    assert result["turns"][0]["response_status"] == IMPLEMENTATION_HANDOFF_CREATED
    assert result["turns"][0]["implementation_handoff_visibility_replay_reference"]
    assert result["turns"][0]["implementation_handoff_summary_hash"].startswith("sha256:")
    assert "Handoff Summary" in output[0]
    assert "Target Worker:\nFILESYSTEM" in output[0]
    assert "* governance/SERVER_MANAGEMENT_FILESYSTEM_WORKER_MODEL_V1.md" in output[0]
    assert "Approval Status:\nNOT REQUIRED" in output[0]


def test_visibility_fails_closed_when_handoff_lineage_is_invalid(tmp_path) -> None:
    handoff = _handoff_capture(tmp_path)
    handoff_path = (
        tmp_path
        / "handoff_execution"
        / "implementation_handoff"
        / "000_implementation_handoff_created.json"
    )
    wrapper = json.loads(handoff_path.read_text(encoding="utf-8"))
    wrapper["artifact"]["output_targets"] = []
    handoff_path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    capture = create_implementation_handoff_visibility_summary(
        visibility_id="HANDOFF-VISIBILITY-CORRUPT-000001",
        handoff_replay_reference=handoff["handoff_replay_reference"],
        approval_status=handoff["approval_status"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "visibility",
    )

    assert capture["summary_status"] == "FAILED_CLOSED"
    assert "hash mismatch" in capture["failure_reason"]


def test_visibility_reconstruction_detects_corrupt_summary_replay(tmp_path) -> None:
    handoff = _handoff_capture(tmp_path)
    create_implementation_handoff_visibility_summary(
        visibility_id="HANDOFF-VISIBILITY-REPLAY-CORRUPT-000001",
        handoff_replay_reference=handoff["handoff_replay_reference"],
        approval_status=handoff["approval_status"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "visibility",
    )
    path = tmp_path / "visibility" / "000_implementation_handoff_summary_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["target_worker"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_implementation_handoff_visibility_replay(tmp_path / "visibility")


def test_implementation_handoff_visibility_preserves_authority_boundaries() -> None:
    import aigol.runtime.implementation_handoff_visibility as runtime

    source = inspect.getsource(runtime)

    assert "create_artifact(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "authorize_implementation(" not in source
    assert "start_execution(" not in source
    assert "mutate_governance(" not in source
