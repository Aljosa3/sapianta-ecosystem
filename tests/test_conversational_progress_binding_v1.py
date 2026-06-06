"""Tests for AIGOL_CONVERSATIONAL_PROGRESS_BINDING_V1."""

from __future__ import annotations

import inspect

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.conversational_progress_binding_runtime import (
    CLARIFICATION,
    COGNITION,
    COMPARISON,
    COMPLETED,
    CONTINUITY,
    PROVIDER_INVOCATION,
    REPLAY,
    RESULT_ASSEMBLY,
    ROUTING,
    CONVERSATIONAL_PROGRESS_BINDING_ARTIFACT_V1,
    CONVERSATIONAL_PROGRESS_STAGE_MODEL,
    create_conversational_progress_binding,
    record_conversational_progress_checkpoint,
    reconstruct_conversational_progress_binding,
)
from aigol.runtime.runtime_progress_visibility import reconstruct_runtime_progress_replay


CREATED_AT = "2026-06-06T00:00:00Z"
SESSION_ID = "SESSION-CONVERSATIONAL-PROGRESS-000001"
PROMPT_ID = f"{SESSION_ID}:TURN-000001"


def _binding(tmp_path):
    return create_conversational_progress_binding(
        binding_id=f"{PROMPT_ID}:PROGRESS-BINDING",
        session_id=SESSION_ID,
        turn_id="TURN-000001",
        prompt_id=PROMPT_ID,
        workflow_id="TEST_WORKFLOW",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "conversational_progress",
    )


def test_conversational_progress_binding_records_replay_visible_snapshots(tmp_path) -> None:
    binding = _binding(tmp_path)
    artifact = binding["conversational_progress_binding_artifact"]

    assert artifact["artifact_type"] == CONVERSATIONAL_PROGRESS_BINDING_ARTIFACT_V1
    assert artifact["uses_existing_runtime_progress_visibility"] is True
    assert artifact["stage_model"] == list(CONVERSATIONAL_PROGRESS_STAGE_MODEL)
    assert artifact["provider_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["execution_requested"] is False

    stages = (
        ROUTING,
        COGNITION,
        PROVIDER_INVOCATION,
        COMPARISON,
        CONTINUITY,
        CLARIFICATION,
        RESULT_ASSEMBLY,
        REPLAY,
    )
    lines = []
    for stage in stages[:-1]:
        capture = record_conversational_progress_checkpoint(
            binding_artifact=artifact,
            stage=stage,
            activity=f"{stage} checkpoint recorded.",
            snapshot_at=CREATED_AT,
        )
        lines.append(capture["operator_progress_line"])
    final_capture = record_conversational_progress_checkpoint(
        binding_artifact=artifact,
        stage=REPLAY,
        activity="Replay checkpoint recorded.",
        snapshot_at=CREATED_AT,
        runtime_status=COMPLETED,
    )
    lines.append(final_capture["operator_progress_line"])

    assert lines == [
        "[1/8] Routing",
        "[2/8] Cognition",
        "[3/8] Provider Invocation",
        "[4/8] Comparison",
        "[5/8] Continuity",
        "[6/8] Clarification",
        "[7/8] Result Assembly",
        "[8/8] Replay",
    ]
    progress = reconstruct_runtime_progress_replay(artifact["runtime_progress_replay_reference"])
    reconstructed = reconstruct_conversational_progress_binding(tmp_path / "conversational_progress")

    assert progress["runtime_status"] == COMPLETED
    assert progress["replay_artifact_count"] == 8
    assert reconstructed["latest_runtime_status"] == COMPLETED
    assert reconstructed["latest_stage"] == REPLAY


def test_interactive_conversation_renders_progress_without_new_authority(tmp_path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "conversation",
            "--session-id",
            SESSION_ID,
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "interactive_runtime"),
        ]
    )
    output: list[str] = []
    prompts = iter(["What is AiGOL?", "exit"])

    result = run_interactive_conversation(
        args,
        input_func=lambda _prompt: next(prompts),
        output_func=output.append,
    )

    assert output[0].splitlines()[:8] == [
        "[1/8] Routing",
        "[2/8] Cognition",
        "[3/8] Provider Invocation",
        "[4/8] Comparison",
        "[5/8] Continuity",
        "[6/8] Clarification",
        "[7/8] Result Assembly",
        "[8/8] Replay",
    ]
    assert result["worker_invoked"] is False
    assert result["execution_requested"] is False
    progress = reconstruct_conversational_progress_binding(
        tmp_path
        / "interactive_runtime"
        / SESSION_ID
        / "TURN-000001"
        / "conversational_progress"
    )
    assert progress["latest_runtime_status"] == COMPLETED
    assert progress["provider_invoked"] is False
    assert progress["worker_invoked"] is False
    assert progress["execution_requested"] is False


def test_conversational_progress_binding_does_not_invoke_workers_or_providers() -> None:
    import aigol.runtime.conversational_progress_binding_runtime as runtime

    source = inspect.getsource(runtime)

    assert "run_provider_attachment(" not in source
    assert "run_native_provider_execution(" not in source
    assert "dispatch_assigned_worker(" not in source
    assert "invoke_dispatched_worker(" not in source
    assert "authorize_execution_ready(" not in source
    assert "subprocess" not in source
