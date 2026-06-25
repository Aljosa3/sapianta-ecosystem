"""Integration tests for ACLI_HARDENING_INTEGRATION_RUNTIME_V1."""

from __future__ import annotations

from pathlib import Path

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
from aigol.runtime.acli_hardening_integration_runtime import (
    ACLI_HARDENING_INTEGRATION_RUNTIME_VERSION,
    load_acli_hardening_metrics_state,
)
from aigol.runtime.acli_hardening_runtime import reconstruct_acli_hardening_replay


CREATED_AT = "2026-06-25T12:00:00Z"


def _args(tmp_path: Path, *, session_id: str = "HARDENING-INTEGRATION-SESSION"):
    parser = build_parser()
    return parser.parse_args(
        [
            "conversation",
            "--session-id",
            session_id,
            "--created-at",
            CREATED_AT,
            "--runtime-root",
            str(tmp_path / "runtime"),
        ]
    )


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _monotonic_sequence(values: list[float]):
    iterator = iter(values)

    def read() -> float:
        return next(iterator)

    return read


def test_completed_interactive_acli_turn_automatically_records_hardening_event(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path),
        input_func=_input_sequence(["What is AiGOL?", "exit"]),
        output_func=output.append,
        monotonic_func=_monotonic_sequence([100.0, 103.0]),
    )
    turn = result["turns"][0]
    session_root = tmp_path / "runtime" / "HARDENING-INTEGRATION-SESSION"
    hardening_root = session_root / "TURN-000001" / "acli_hardening"

    assert result["hardening_recorded"] is True
    assert result["hardening_event_count"] == 1
    assert turn["hardening_recorded"] is True
    assert turn["hardening_result"] == "PARTIAL PASS"
    assert turn["hardening_replay_reference"] == str(hardening_root)
    assert "Hardening" in output[0]
    assert "Operator feedback: Optional" in output[0]
    assert (hardening_root / "000_acli_hardening_evidence_recorded.json").exists()
    reconstructed = reconstruct_acli_hardening_replay(hardening_root)
    assert reconstructed["result"] == "PARTIAL PASS"
    assert reconstructed["source_replay_reference"] == turn["conversation_replay_reference"]


def test_hardening_metrics_persist_across_acli_restart(tmp_path) -> None:
    session_id = "HARDENING-PERSISTENCE-SESSION"
    first = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence(["What is AiGOL?", "exit"]),
        output_func=lambda _line: None,
        monotonic_func=_monotonic_sequence([100.0, 101.0]),
    )
    second = run_interactive_conversation(
        _args(tmp_path, session_id=session_id),
        input_func=_input_sequence(["Show status", "exit"]),
        output_func=lambda _line: None,
        monotonic_func=_monotonic_sequence([200.0, 202.0]),
    )
    session_root = tmp_path / "runtime" / session_id
    metrics = load_acli_hardening_metrics_state(session_root)

    assert first["hardening_event_count"] == 1
    assert second["session_resumed"] is True
    assert second["existing_turn_count"] == 1
    assert second["hardening_event_count"] == 1
    assert metrics is not None
    assert metrics["hardening_statistics"]["total_interactions"] == 2
    assert metrics["hardening_statistics"]["result_counts"]["PARTIAL PASS"] == 2
    assert (session_root / "TURN-000002" / "acli_hardening").exists()


def test_hardening_never_changes_authority_boundaries_or_workflow_behavior(tmp_path) -> None:
    result = run_interactive_conversation(
        _args(tmp_path, session_id="HARDENING-AUTHORITY-SESSION"),
        input_func=_input_sequence(["What is AiGOL?", "exit"]),
        output_func=lambda _line: None,
        monotonic_func=_monotonic_sequence([10.0, 12.0]),
    )
    turn = result["turns"][0]
    reconstructed = reconstruct_acli_hardening_replay(Path(turn["hardening_replay_reference"]))

    assert turn["response_source"] == "CONVERSATIONAL_CLI_WORKFLOW"
    assert turn["workflow_status"]["workflow_state"] == "WAITING_FOR_OPERATOR"
    assert turn["provider_invoked"] is False
    assert turn["worker_invoked"] is False
    assert turn["execution_requested"] is False
    assert turn["approval_bypassed"] is False
    assert turn["hardening_authority_preserved"] is True
    assert reconstructed["authority_flags"]["authorizes_execution"] is False
    assert reconstructed["authority_flags"]["authorizes_worker_invocation"] is False
    assert reconstructed["authority_flags"]["creates_approval"] is False


def test_hardening_integration_event_and_metrics_are_replay_visible(tmp_path) -> None:
    result = run_interactive_conversation(
        _args(tmp_path, session_id="HARDENING-EVIDENCE-SESSION"),
        input_func=_input_sequence(["What is AiGOL?", "exit"]),
        output_func=lambda _line: None,
        monotonic_func=_monotonic_sequence([1.0, 2.0]),
    )
    turn = result["turns"][0]
    turn_root = tmp_path / "runtime" / "HARDENING-EVIDENCE-SESSION" / "TURN-000001"
    integration_event = turn_root / "acli_hardening_integration" / "000_acli_hardening_integration_recorded.json"
    metrics_reference = Path(turn["hardening_metrics_reference"])

    assert integration_event.exists()
    assert metrics_reference.exists()
    assert result["hardening_metrics_reference"] == str(metrics_reference)
    metrics = load_acli_hardening_metrics_state(tmp_path / "runtime" / "HARDENING-EVIDENCE-SESSION")
    assert metrics is not None
    assert metrics["hardening_statistics"]["total_interactions"] == 1


def test_fail_closed_interactive_acli_turn_records_hardening_event(tmp_path) -> None:
    result = run_interactive_conversation(
        _args(tmp_path, session_id="HARDENING-FAIL-CLOSED-SESSION"),
        input_func=_input_sequence(["continue ppp", "exit"]),
        output_func=lambda _line: None,
        monotonic_func=_monotonic_sequence([1.0, 2.0]),
    )
    turn = result["turns"][0]
    hardening_root = Path(turn["hardening_replay_reference"])
    reconstructed = reconstruct_acli_hardening_replay(hardening_root)

    assert result["failed_turns"] == 1
    assert result["hardening_recorded"] is True
    assert result["hardening_event_count"] == 1
    assert turn["fail_closed"] is True
    assert turn["hardening_recorded"] is True
    assert turn["turn_completion_status"] == "FAILED_CLOSED"
    assert reconstructed["result"] == "PARTIAL PASS"
    assert reconstructed["evidence_completeness"]["operator_prompt"]["prompt_text"] == "continue ppp"
    assert reconstructed["evidence_completeness"]["fail_closed"]["fail_closed"] is True
    assert reconstructed["evidence_completeness"]["fail_closed"]["fail_closed_reason"]


def test_integration_runtime_version_is_stable() -> None:
    assert ACLI_HARDENING_INTEGRATION_RUNTIME_VERSION == "ACLI_HARDENING_INTEGRATION_RUNTIME_V1"
