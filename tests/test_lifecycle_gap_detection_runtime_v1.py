"""Tests for AIGOL_LIFECYCLE_GAP_DETECTION_RUNTIME_V1."""

from __future__ import annotations

import inspect

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.lifecycle_gap_detection_runtime import (
    AIGOL_LIFECYCLE_GAP_DETECTION_RUNTIME_VERSION,
    detect_lifecycle_gaps,
    reconstruct_lifecycle_gap_detection_replay,
)
from aigol.runtime.replay_gap_detection_runtime import GAPS_DETECTED, NO_GAPS_DETECTED
from aigol.runtime.replay_to_improvement_intent_runtime import create_improvement_intent_from_replay_gap


CREATED_AT = "2026-06-11T00:00:00Z"
SESSION_ID = "SESSION-LIFECYCLE-GAP-DETECTION-000001"
PROMPT = "Create a new governed domain called FreshDomain."
REPLY = "\n".join(
    [
        "Primary purpose: Create a safe pilot governed domain.",
        "Expected capabilities: Clarification handling, bounded workflow resume, and governed domain artifact creation.",
        "Target users: Internal operators.",
    ]
)


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _conversation_args(tmp_path, *, auto_continue: bool = False):
    parser = build_parser()
    args = [
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
    if auto_continue:
        args.append("--auto-continue")
    return parser.parse_args(args)


def test_lifecycle_gap_detection_reports_no_gaps_for_completed_auto_continue_run(tmp_path) -> None:
    result = run_interactive_conversation(
        _conversation_args(tmp_path, auto_continue=True),
        input_func=_input_sequence([PROMPT, REPLY, "exit"]),
        output_func=lambda _line: None,
    )

    capture = detect_lifecycle_gaps(
        detection_id="LIFECYCLE-GAP-DETECTION-NONE-000001",
        observed_turns=result["turns"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "gap_detection",
    )
    reconstructed = reconstruct_lifecycle_gap_detection_replay(tmp_path / "gap_detection")

    assert capture["detection_status"] == NO_GAPS_DETECTED
    assert capture["gap_count"] == 0
    assert capture["gap_detection_artifact"]["runtime_version"] == AIGOL_LIFECYCLE_GAP_DETECTION_RUNTIME_VERSION
    assert capture["expected_state"]["lifecycle"][-1] == "TERMINATED"
    assert capture["observed_state"]["lifecycle"][-1] == "TERMINATED"
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert reconstructed["detection_status"] == NO_GAPS_DETECTED


def test_lifecycle_gap_detection_generates_gap_artifacts_for_failed_lifecycle_run(tmp_path) -> None:
    result = run_interactive_conversation(
        _conversation_args(tmp_path),
        input_func=_input_sequence(
            [
                PROMPT,
                REPLY,
                "Authorize FreshDomain domain artifact request.",
                "Create execution-ready authorization packet for FreshDomain.",
                "Authorize execution-ready packet for FreshDomain.",
                "Execute worker for the active domain.",
                "exit",
            ]
        ),
        output_func=lambda _line: None,
    )
    failed_turn = result["turns"][-1]
    failed_turn["workflow_status"]["next_expected_action"] = "Execute worker for the active domain."

    capture = detect_lifecycle_gaps(
        detection_id="LIFECYCLE-GAP-DETECTION-FAILED-000001",
        observed_turns=result["turns"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "failed_gap_detection",
    )
    reconstructed = reconstruct_lifecycle_gap_detection_replay(tmp_path / "failed_gap_detection")

    assert capture["detection_status"] == GAPS_DETECTED
    assert capture["gap_detection_artifact"]["artifact_type"] == "GAP_DETECTION_ARTIFACT_V1"
    assert capture["gap_classification_artifact"]["artifact_type"] == "GAP_CLASSIFICATION_ARTIFACT_V1"
    assert capture["gap_evidence_artifact"]["artifact_type"] == "GAP_EVIDENCE_ARTIFACT_V1"
    assert capture["gap_count"] >= 3
    assert "FAIL_CLOSED_INTERRUPTION" in capture["gap_categories"]
    assert "MISSING_CONTINUATION" in capture["gap_categories"]
    assert "PROJECTION_INCONSISTENCY" in capture["gap_categories"]
    assert capture["expected_state"]["lifecycle"][-1] == "TERMINATED"
    assert "FAILED_CLOSED" in capture["observed_state"]["lifecycle"]
    assert capture["human_review_required"] is True
    assert capture["improvement_intent_allowed"] is True
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_requested"] is False
    assert reconstructed["detection_status"] == GAPS_DETECTED
    assert reconstructed["gap_count"] == capture["gap_count"]

    intent = create_improvement_intent_from_replay_gap(
        improvement_intent_id="LIFECYCLE-GAP-IMPROVEMENT-INTENT-000001",
        gap_detection_artifact=capture["gap_detection_artifact"],
        gap_classification_artifact=capture["gap_classification_artifact"],
        gap_evidence_artifact=capture["gap_evidence_artifact"],
        canonical_chain_id="LIFECYCLE-GAP-CHAIN-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "lifecycle_gap_improvement_intent",
    )
    assert intent["intent_status"] == "IMPROVEMENT_INTENT_CREATED"
    assert intent["provider_invoked"] is False
    assert intent["worker_invoked"] is False
    assert intent["execution_requested"] is False


def test_lifecycle_gap_detection_runtime_is_detection_only() -> None:
    import aigol.runtime.lifecycle_gap_detection_runtime as runtime

    source = inspect.getsource(runtime)

    assert "submit_prompt_to_conversation(" not in source
    assert "run_conversation_to_ppp" not in source
    assert "dispatch_assigned_worker(" not in source
    assert "invoke_dispatched_worker(" not in source
    assert "start_execution(" not in source
