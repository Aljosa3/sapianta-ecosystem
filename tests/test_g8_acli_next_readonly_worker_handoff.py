"""Tests for the G8-05 ACLI Next read-only Worker handoff."""

from __future__ import annotations

import pytest

from aigol.acli_next import (
    ACLI_NEXT_READONLY_WORKER_VERSION,
    run_acli_next_interactive_session,
    run_acli_next_interactive_with_readonly_worker,
    run_acli_next_readonly_worker_handoff,
)
from aigol.acli_next.readonly_worker import ACLI_NEXT_READONLY_WORKER_HANDOFF_COMPLETED
from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-07-01T00:00:00Z"


def _turn(request: str, response: str) -> dict[str, str]:
    return {"operator_request": request, "operator_response": response}


def test_acli_next_readonly_worker_handoff_runs_after_confirmation(tmp_path) -> None:
    result = run_acli_next_interactive_with_readonly_worker(
        session_id="ACLI-NEXT-READONLY-WORKER-001",
        turns=[_turn("Create an advisory plan and prepare a read-only replay inspection.", "confirm")],
        worker_capability="replay_inspection",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "readonly_worker",
        workspace=tmp_path,
    )

    assert result["command"] == "aigol next readonly-worker"
    assert result["runtime_version"] == ACLI_NEXT_READONLY_WORKER_VERSION
    assert result["handoff_status"] == ACLI_NEXT_READONLY_WORKER_HANDOFF_COMPLETED
    assert result["worker_capability"] == "replay_inspection"
    assert result["governance_authorization_status"] == "AUTHORIZED_READONLY_WORKER"
    assert result["worker_result_status"] == "ACLI_NEXT_READONLY_WORKER_COMPLETED"
    assert result["result_summary"]["summary_type"] == "READONLY_REPLAY_INSPECTION_SUMMARY"
    assert result["read_only"] is True
    assert result["worker_invoked"] is True
    assert result["provider_invoked"] is False
    assert result["worker_write_performed"] is False
    assert result["repository_mutated"] is False
    assert result["deployment_performed"] is False
    handoff_dir = tmp_path / "readonly_worker" / "readonly_worker_handoff"
    assert (handoff_dir / "000_acli_next_readonly_worker_request.json").exists()
    assert (handoff_dir / "001_acli_next_readonly_worker_result.json").exists()
    assert (handoff_dir / "002_acli_next_readonly_worker_completion.json").exists()


def test_acli_next_readonly_worker_handoff_requires_confirmation(tmp_path) -> None:
    interactive = run_acli_next_interactive_session(
        session_id="ACLI-NEXT-READONLY-WORKER-REJECTED",
        turns=[_turn("Create an advisory plan.", "reject")],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "interactive",
        workspace=tmp_path,
    )

    with pytest.raises(FailClosedRuntimeError, match="human confirmation missing"):
        run_acli_next_readonly_worker_handoff(
            session_id="ACLI-NEXT-READONLY-WORKER-REJECTED",
            interactive_result=interactive,
            worker_capability="replay_inspection",
            created_at=CREATED_AT,
            replay_dir=tmp_path / "handoff",
        )


def test_acli_next_readonly_worker_handoff_fails_closed_on_unsupported_capability(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="unsupported capability"):
        run_acli_next_interactive_with_readonly_worker(
            session_id="ACLI-NEXT-READONLY-WORKER-UNSUPPORTED",
            turns=[_turn("Create an advisory plan.", "confirm")],
            worker_capability="write_patch",
            created_at=CREATED_AT,
            replay_dir=tmp_path / "unsupported",
            workspace=tmp_path,
        )


def test_acli_next_readonly_worker_cli_route_renders_summary(tmp_path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "next",
            "readonly-worker",
            "--session-id",
            "ACLI-NEXT-READONLY-WORKER-CLI",
            "--turn",
            "Create advisory plan=>confirm",
            "--worker-capability",
            "validation-summary",
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

    assert result["command"] == "aigol next readonly-worker"
    assert result["handoff_status"] == ACLI_NEXT_READONLY_WORKER_HANDOFF_COMPLETED
    assert result["worker_capability"] == "validation_summary"
    assert result["repository_mutated"] is False
    assert "AIGOL NEXT READONLY WORKER" in rendered
    assert "worker_capability: validation_summary" in rendered
