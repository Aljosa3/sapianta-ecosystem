"""Tests for the G8-03 ACLI Next bootstrap implementation."""

from __future__ import annotations

import pytest

from aigol.acli_next import ACLI_NEXT_BOOTSTRAP_VERSION, run_acli_next_session
from aigol.acli_next.entrypoint import ACLI_NEXT_BOOTSTRAP_COMPLETED
from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-07-01T00:00:00Z"
REQUEST = "Create a non-mutating advisory plan for ACLI Next bootstrap validation."


def test_acli_next_bootstrap_starts_pgsp_session_without_mutation(tmp_path) -> None:
    result = run_acli_next_session(
        session_id="ACLI-NEXT-BOOTSTRAP-001",
        operator_request=REQUEST,
        operator_response="confirm",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "acli_next",
        workspace=tmp_path,
    )

    assert result["command"] == "aigol next session"
    assert result["runtime_version"] == ACLI_NEXT_BOOTSTRAP_VERSION
    assert result["session_status"] == ACLI_NEXT_BOOTSTRAP_COMPLETED
    assert result["canonical_response_class"] == "CONFIRMATION"
    assert result["replay_visible"] is True
    assert result["replay_reference"] == str(tmp_path / "acli_next")
    assert result["pgsp_replay_reference"].endswith("pgsp_session")
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["approval_created"] is False
    assert result["authorization_created"] is False
    assert result["repository_mutated"] is False
    assert result["deployment_performed"] is False
    assert result["copy_paste_workflow_used"] is False
    assert (tmp_path / "acli_next" / "000_acli_next_session_created.json").exists()
    assert (tmp_path / "acli_next" / "001_pgsp_invocation_recorded.json").exists()
    assert (tmp_path / "acli_next" / "002_acli_next_completion_recorded.json").exists()


def test_acli_next_cli_command_delegates_to_bootstrap_runtime(tmp_path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "next",
            "session",
            "--session-id",
            "ACLI-NEXT-CLI-001",
            "--request",
            REQUEST,
            "--response",
            "confirm",
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

    assert result["command"] == "aigol next session"
    assert result["session_status"] == ACLI_NEXT_BOOTSTRAP_COMPLETED
    assert result["repository_mutated"] is False
    assert "AIGOL NEXT SESSION" in rendered
    assert "copy_paste_workflow_used: False" in rendered


def test_acli_next_bootstrap_fails_closed_on_unmapped_response(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="does not map"):
        run_acli_next_session(
            session_id="ACLI-NEXT-BOOTSTRAP-FAIL-CLOSED",
            operator_request=REQUEST,
            operator_response="sounds interesting",
            created_at=CREATED_AT,
            replay_dir=tmp_path / "fail_closed",
        )
