"""Tests for AIGOL_GOVERNED_IMPLEMENTATION_DRY_RUN_V1."""

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
from aigol.runtime.governed_implementation_dry_run import (
    EXECUTION_READY,
    prepare_governed_implementation_dry_run,
    reconstruct_governed_implementation_dry_run_replay,
)
from aigol.runtime.implementation_approval_resume import (
    create_human_implementation_approval,
    resume_implementation_after_approval,
)
from aigol.runtime.implementation_handoff_visibility import create_implementation_handoff_visibility_summary
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


CREATED_AT = "2026-06-04T00:00:00+00:00"
SESSION_ID = "SESSION-GOVERNED-IMPLEMENTATION-DRY-RUN-000001"


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


def _visibility(tmp_path, *, handoff_replay_reference: str, approval_status: str, suffix: str):
    return create_implementation_handoff_visibility_summary(
        visibility_id=f"VISIBILITY-{suffix}",
        handoff_replay_reference=handoff_replay_reference,
        approval_status=approval_status,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"visibility_{suffix}",
    )


@pytest.mark.parametrize(
    ("prompt", "suffix", "target_worker"),
    [
        ("Create a filesystem worker.", "filesystem", "FILESYSTEM"),
        ("Create a monitoring worker.", "monitoring", "MONITORING"),
    ],
)
def test_worker_handoff_becomes_execution_ready_without_execution(
    tmp_path,
    prompt: str,
    suffix: str,
    target_worker: str,
) -> None:
    ppp = _ppp_capture(tmp_path, prompt=prompt, suffix=suffix)
    visibility = _visibility(
        tmp_path,
        handoff_replay_reference=ppp["handoff_replay_reference"],
        approval_status=ppp["approval_status"],
        suffix=suffix,
    )
    capture = prepare_governed_implementation_dry_run(
        dry_run_id=f"DRY-RUN-{suffix}",
        handoff_replay_reference=ppp["handoff_replay_reference"],
        handoff_visibility_artifact=visibility["implementation_handoff_visibility_artifact"],
        upstream_lineage_artifact=ppp["conversation_to_ppp_handoff_execution_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"dry_run_{suffix}",
    )
    reconstructed = reconstruct_governed_implementation_dry_run_replay(tmp_path / f"dry_run_{suffix}")

    candidate = capture["execution_candidate_artifact"]
    packet = capture["execution_packet_artifact"]
    validation = capture["execution_validation_artifact"]
    assert capture["execution_status"] == EXECUTION_READY
    assert candidate["target_worker"] == target_worker
    assert candidate["execution_scope"]["mode"] == "PREPARATION_ONLY"
    assert candidate["execution_scope"]["execution_authorized"] is False
    assert packet["execution_contract"]["execution_state"] == "NOT_STARTED"
    assert packet["execution_contract"]["execution_authorized"] is False
    assert "INVOKE_WORKER" in packet["forbidden_operations"]
    assert "CREATE_FILE" in packet["forbidden_operations"]
    assert all(validation["validation_checks"].values())
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert capture["dispatch_requested"] is False
    assert reconstructed["execution_status"] == EXECUTION_READY


def test_approved_trading_handoff_becomes_execution_ready(tmp_path) -> None:
    ppp = _ppp_capture(tmp_path, prompt="Improve trading strategy.", suffix="trading")
    assert ppp["terminal_status"] == HUMAN_APPROVAL_REQUIRED
    request = ppp["conversation_to_ppp_handoff_execution_artifact"]["approval_resume_packet"][
        "approval_request_artifact"
    ]
    approval = create_human_implementation_approval(
        approval_id="HUMAN-APPROVAL-TRADING-000001",
        approval_request_artifact=request,
        approving_actor="human.operator",
        approval_timestamp=CREATED_AT,
    )
    resumed = resume_implementation_after_approval(
        resume_id="APPROVAL-RESUME-TRADING-000001",
        approval_required_replay_reference=ppp["conversation_to_ppp_handoff_execution_replay_reference"],
        human_approval_artifact=approval,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "approval_resume_trading",
    )
    visibility = _visibility(
        tmp_path,
        handoff_replay_reference=resumed["implementation_handoff_replay_reference"],
        approval_status="APPROVED",
        suffix="trading",
    )
    capture = prepare_governed_implementation_dry_run(
        dry_run_id="DRY-RUN-TRADING",
        handoff_replay_reference=resumed["implementation_handoff_replay_reference"],
        handoff_visibility_artifact=visibility["implementation_handoff_visibility_artifact"],
        upstream_lineage_artifact=resumed["implementation_approval_resume_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "dry_run_trading",
    )

    assert capture["execution_status"] == EXECUTION_READY
    assert capture["execution_candidate_artifact"]["approval_status"] == "APPROVED"
    assert capture["execution_candidate_artifact"]["approval_reference"] == approval["approval_id"]
    assert capture["execution_ready_status_artifact"]["execution_started"] is False


def test_corrupt_lineage_fails_closed(tmp_path) -> None:
    ppp = _ppp_capture(tmp_path, prompt="Create a filesystem worker.", suffix="corrupt")
    visibility = _visibility(
        tmp_path,
        handoff_replay_reference=ppp["handoff_replay_reference"],
        approval_status=ppp["approval_status"],
        suffix="corrupt",
    )
    corrupt = dict(visibility["implementation_handoff_visibility_artifact"])
    corrupt["handoff_reference"] = "WRONG-HANDOFF"
    capture = prepare_governed_implementation_dry_run(
        dry_run_id="DRY-RUN-CORRUPT",
        handoff_replay_reference=ppp["handoff_replay_reference"],
        handoff_visibility_artifact=corrupt,
        upstream_lineage_artifact=ppp["conversation_to_ppp_handoff_execution_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "dry_run_corrupt",
    )

    assert capture["execution_status"] == "FAILED_CLOSED"
    assert "hash mismatch" in capture["failure_reason"]


def test_reconstruction_detects_corrupt_packet_replay(tmp_path) -> None:
    ppp = _ppp_capture(tmp_path, prompt="Create a filesystem worker.", suffix="replay")
    visibility = _visibility(
        tmp_path,
        handoff_replay_reference=ppp["handoff_replay_reference"],
        approval_status=ppp["approval_status"],
        suffix="replay",
    )
    prepare_governed_implementation_dry_run(
        dry_run_id="DRY-RUN-REPLAY",
        handoff_replay_reference=ppp["handoff_replay_reference"],
        handoff_visibility_artifact=visibility["implementation_handoff_visibility_artifact"],
        upstream_lineage_artifact=ppp["conversation_to_ppp_handoff_execution_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "dry_run_replay",
    )
    path = tmp_path / "dry_run_replay" / "001_execution_packet_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["allowed_outputs"] = []
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_governed_implementation_dry_run_replay(tmp_path / "dry_run_replay")


def test_cli_acceptance_flows_reach_execution_ready(tmp_path) -> None:
    filesystem_output: list[str] = []
    filesystem = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-DRY-RUN-CLI-FILESYSTEM"),
        input_func=_input_sequence(["Create a filesystem worker.", "exit"]),
        output_func=filesystem_output.append,
    )
    trading_output: list[str] = []
    trading = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-DRY-RUN-CLI-TRADING"),
        input_func=_input_sequence(["Improve trading strategy.", "Approve.", "exit"]),
        output_func=trading_output.append,
    )

    assert filesystem["turns"][0]["execution_preparation_status"] == EXECUTION_READY
    assert "Execution Status: EXECUTION_READY" in filesystem_output[0]
    assert "Execution has not started." in filesystem_output[0]
    assert trading["turns"][0]["response_status"] == HUMAN_APPROVAL_REQUIRED
    assert trading["turns"][1]["execution_preparation_status"] == EXECUTION_READY
    assert "Execution Status: EXECUTION_READY" in trading_output[1]


def test_governed_implementation_dry_run_preserves_authority_boundaries() -> None:
    import aigol.runtime.governed_implementation_dry_run as runtime

    source = inspect.getsource(runtime)

    assert "invoke_worker(" not in source
    assert "invoke_codex(" not in source
    assert "invoke_claude_code(" not in source
    assert "create_file(" not in source
    assert "generate_code(" not in source
    assert "dispatch_execution(" not in source
    assert "authorize_execution(" not in source
    assert "mutate_governance(" not in source
