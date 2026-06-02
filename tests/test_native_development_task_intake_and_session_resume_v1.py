"""Tests for AIGOL_NATIVE_DEVELOPMENT_TASK_INTAKE_AND_SESSION_RESUME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import build_parser, render_command_result, run_interactive_conversation
from aigol.runtime.conversation_session_resume_runtime import (
    CONVERSATION_SESSION_RESUME_STATUS,
    resume_conversation_session,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.native_development_task_intake_runtime import (
    AIGOL_NATIVE_DEVELOPMENT_TASK_INTAKE_ARTIFACT_V1,
    NATIVE_DEVELOPMENT_TASK_INTAKE_ACCEPTED,
    is_native_development_prompt,
    reconstruct_native_development_task_intake_replay,
    run_native_development_task_intake,
)
from aigol.runtime.transport.serialization import canonical_serialize


CREATED_AT = "2026-06-02T14:00:00+00:00"
MILESTONE_ID = "TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1"


def _args(tmp_path, *, session_id: str = "NATIVE-DEVELOPMENT-SESSION-000001"):
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


def test_session_resume_allocates_next_unused_turn_without_router_collision(tmp_path) -> None:
    session_id = "NATIVE-DEVELOPMENT-RESUME-000001"
    args = _args(tmp_path, session_id=session_id)
    output: list[str] = []

    first = run_interactive_conversation(
        args,
        input_func=_input_sequence(["What is AiGOL?", "exit"]),
        output_func=output.append,
    )
    second = run_interactive_conversation(
        args,
        input_func=_input_sequence([f"Implement {MILESTONE_ID} foundation only. No dispatch. No execution.", "exit"]),
        output_func=output.append,
    )

    session_root = tmp_path / "interactive_runtime" / session_id
    assert first["turns"][0]["turn_id"] == "TURN-000001"
    assert second["session_resumed"] is True
    assert second["existing_turn_count"] == 1
    assert second["next_turn_id_at_start"] == "TURN-000002"
    assert second["turns"][0]["turn_id"] == "TURN-000002"
    assert second["failed_turns"] == 0
    assert (session_root / "TURN-000002" / "source_router" / "000_source_of_truth_router_selected.json").exists()
    assert (
        session_root
        / "TURN-000002"
        / "native_development_task_intake"
        / "000_native_development_task_intake_recorded.json"
    ).exists()


def test_resume_runtime_reports_existing_session_state(tmp_path) -> None:
    session_root = tmp_path / "runtime" / "SESSION-RESUME-000001"
    (session_root / "TURN-000001").mkdir(parents=True)
    (session_root / "TURN-000003").mkdir(parents=True)

    resume = resume_conversation_session(
        session_id="SESSION-RESUME-000001",
        runtime_root=tmp_path / "runtime",
        created_at=CREATED_AT,
    )

    assert resume["resume_status"] == CONVERSATION_SESSION_RESUME_STATUS
    assert resume["session_resumed"] is True
    assert resume["existing_turn_ids"] == ["TURN-000001", "TURN-000003"]
    assert resume["next_turn_id"] == "TURN-000004"
    assert resume["append_only_semantics_preserved"] is True
    assert resume["worker_invoked"] is False
    assert resume["execution_requested"] is False


def test_native_development_task_intake_records_reconstructable_trading_worker_foundation(tmp_path) -> None:
    prompt = (
        f"Implement {MILESTONE_ID}. Foundation only. No broker integration. "
        "No exchange integration. No order placement. No live trading. No financial claims."
    )
    capture = run_native_development_task_intake(
        intake_id="INTAKE-TRADING-000001",
        human_prompt_reference="PROMPT-TRADING-000001",
        human_prompt=prompt,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "intake",
        session_id="SESSION-TRADING-000001",
        turn_id="TURN-000001",
    )
    reconstructed = reconstruct_native_development_task_intake_replay(tmp_path / "intake")
    artifact = capture["native_development_task_intake_artifact"]

    assert artifact["artifact_type"] == AIGOL_NATIVE_DEVELOPMENT_TASK_INTAKE_ARTIFACT_V1
    assert capture["intake_status"] == NATIVE_DEVELOPMENT_TASK_INTAKE_ACCEPTED
    assert capture["requested_milestone_id"] == MILESTONE_ID
    assert capture["requested_domain"] == "TRADING"
    assert capture["requested_worker_family"] == "MARKET_EVIDENCE_NORMALIZATION"
    assert "FOUNDATION_ONLY" in capture["task_kind"]
    assert "WORKER" in capture["task_kind"]
    assert capture["safe_for_native_development"] is True
    assert capture["codex_assisted_handoff_required"] is True
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert reconstructed["requested_milestone_id"] == MILESTONE_ID
    assert reconstructed["replay_artifact_count"] == 2


def test_native_development_task_intake_fails_closed_without_milestone(tmp_path) -> None:
    capture = run_native_development_task_intake(
        intake_id="INTAKE-NO-MILESTONE-000001",
        human_prompt_reference="PROMPT-NO-MILESTONE-000001",
        human_prompt="Implement the next trading worker foundation.",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "no_milestone",
    )
    reconstructed = reconstruct_native_development_task_intake_replay(tmp_path / "no_milestone")

    assert capture["fail_closed"] is True
    assert capture["requested_milestone_id"] is None
    assert "milestone id cannot be identified" in capture["failure_reason"]
    assert reconstructed["safe_for_native_development"] is False


def test_native_development_task_intake_fails_closed_on_authority_bearing_scope(tmp_path) -> None:
    capture = run_native_development_task_intake(
        intake_id="INTAKE-UNSAFE-000001",
        human_prompt_reference="PROMPT-UNSAFE-000001",
        human_prompt=f"Implement {MILESTONE_ID} and place order through broker integration.",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "unsafe",
    )

    assert capture["fail_closed"] is True
    assert capture["requested_milestone_id"] == MILESTONE_ID
    assert capture["safe_for_native_development"] is False
    assert "prohibited authority" in capture["failure_reason"]
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False


def test_interactive_conversation_surfaces_development_intake_without_provider_or_execution(tmp_path) -> None:
    args = _args(tmp_path, session_id="NATIVE-DEVELOPMENT-INTAKE-000001")
    output: list[str] = []

    result = run_interactive_conversation(
        args,
        input_func=_input_sequence([f"Implement {MILESTONE_ID}. Foundation only. No dispatch. No execution.", "exit"]),
        output_func=output.append,
    )
    rendered = render_command_result(result)
    turn = result["turns"][0]

    assert result["turn_count"] == 1
    assert result["failed_turns"] == 0
    assert turn["response_source"] == "NATIVE_DEVELOPMENT_CONTEXT_ASSEMBLY"
    assert turn["recognized_development_task"] is True
    assert turn["task_intake_reference"]
    assert turn["context_assembly_reference"]
    assert turn["context_status"] == "CONTEXT_ASSEMBLED"
    assert turn["context_hash"].startswith("sha256:")
    assert turn["provider_necessity_classification"] == "PROVIDER_REQUIRED_FOR_PROPOSAL"
    assert turn["worker_invoked"] is False
    assert turn["execution_requested"] is False
    assert "context_status: CONTEXT_ASSEMBLED" in output[0]
    assert "session_resumed: False" in rendered


def test_reconstruction_detects_corrupt_native_development_intake_replay(tmp_path) -> None:
    run_native_development_task_intake(
        intake_id="INTAKE-CORRUPT-000001",
        human_prompt_reference="PROMPT-CORRUPT-000001",
        human_prompt=f"Implement {MILESTONE_ID}. Foundation only.",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
    )
    path = tmp_path / "corrupt" / "000_native_development_task_intake_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["requested_milestone_id"] = "CORRUPTED_V1"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_native_development_task_intake_replay(tmp_path / "corrupt")


def test_native_development_runtime_has_no_worker_dispatch_or_execution_imports() -> None:
    import aigol.runtime.native_development_task_intake_runtime as intake_runtime
    import aigol.runtime.conversation_session_resume_runtime as resume_runtime

    intake_source = inspect.getsource(intake_runtime)
    resume_source = inspect.getsource(resume_runtime)
    cli_source = inspect.getsource(aigol_cli)

    for source in (intake_source, resume_source, cli_source):
        assert "dispatch_worker(" not in source
        assert "invoke_worker(" not in source
        assert "create_execution_request(" not in source
        assert "start_execution(" not in source


def test_native_development_prompt_detection_is_conservative() -> None:
    assert is_native_development_prompt(f"Open {MILESTONE_ID}. Foundation only.") is True
    assert is_native_development_prompt("What is AiGOL?") is False
