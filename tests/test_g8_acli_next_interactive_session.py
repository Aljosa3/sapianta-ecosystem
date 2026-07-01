"""Tests for the G8-04 ACLI Next interactive session implementation."""

from __future__ import annotations

import pytest

from aigol.acli_next import ACLI_NEXT_INTERACTIVE_VERSION, run_acli_next_interactive_session
from aigol.acli_next.interactive import ACLI_NEXT_INTERACTIVE_COMPLETED
from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-07-01T00:00:00Z"


def _turn(request: str, response: str) -> dict[str, str]:
    return {"operator_request": request, "operator_response": response}


def test_acli_next_interactive_supports_clarification_then_confirmation(tmp_path) -> None:
    result = run_acli_next_interactive_session(
        session_id="ACLI-NEXT-INTERACTIVE-001",
        turns=[
            _turn("Create an advisory ACLI Next plan, but ask if anything is ambiguous.", "please clarify"),
            _turn("Clarification: keep it non-mutating and replay-visible.", "confirm"),
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "interactive",
        workspace=tmp_path,
    )

    assert result["command"] == "aigol next interactive"
    assert result["runtime_version"] == ACLI_NEXT_INTERACTIVE_VERSION
    assert result["session_status"] == ACLI_NEXT_INTERACTIVE_COMPLETED
    assert result["turn_count"] == 2
    assert result["final_response_class"] == "CONFIRMATION"
    assert result["turns"][0]["canonical_response_class"] == "CLARIFICATION"
    assert result["turns"][0]["continuation_allowed"] is True
    assert result["turns"][1]["canonical_response_class"] == "CONFIRMATION"
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["approval_created"] is False
    assert result["authorization_created"] is False
    assert result["repository_mutated"] is False
    assert result["deployment_performed"] is False
    assert (tmp_path / "interactive" / "000_acli_next_interactive_started.json").exists()
    assert (tmp_path / "interactive" / "001_acli_next_turn_recorded.json").exists()
    assert (tmp_path / "interactive" / "002_acli_next_turn_recorded.json").exists()
    assert (tmp_path / "interactive" / "003_acli_next_interactive_completed.json").exists()


def test_acli_next_interactive_fails_closed_after_terminal_turn(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="prior turn is terminal"):
        run_acli_next_interactive_session(
            session_id="ACLI-NEXT-INTERACTIVE-TERMINAL",
            turns=[
                _turn("Create an advisory plan.", "confirm"),
                _turn("Try to continue after terminal confirmation.", "confirm"),
            ],
            created_at=CREATED_AT,
            replay_dir=tmp_path / "terminal",
        )


def test_acli_next_interactive_cli_route_renders_session_summary(tmp_path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "next",
            "interactive",
            "--session-id",
            "ACLI-NEXT-INTERACTIVE-CLI",
            "--turn",
            "Create advisory plan=>please clarify",
            "--turn",
            "Clarification response=>confirm",
            "--runtime-root",
            str(tmp_path / "runtime"),
            "--workspace",
            str(tmp_path),
            "--created-at",
            CREATED_AT,
        ]
    )

    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol next interactive"
    assert result["session_status"] == ACLI_NEXT_INTERACTIVE_COMPLETED
    assert result["turn_count"] == 2
    assert result["repository_mutated"] is False
    assert "AIGOL NEXT INTERACTIVE" in rendered
    assert "final_response_class: CONFIRMATION" in rendered
