"""Tests for the G11-02 ACLI Next conversational development session UX."""

from __future__ import annotations

from aigol.acli_next import (
    ACLI_NEXT_CONVERSATIONAL_SESSION_VERSION,
    run_acli_next_conversational_session,
)
from aigol.acli_next.conversational import ACLI_NEXT_CONVERSATIONAL_SESSION_PRESENTED
from aigol.cli.aigol_cli import build_parser, render_command_result, run_command


CREATED_AT = "2026-07-02T00:00:00Z"


def test_acli_next_conversational_session_composes_existing_capabilities(tmp_path) -> None:
    result = run_acli_next_conversational_session(
        session_id="ACLI-NEXT-CONVERSATIONAL-TEST",
        prompts=["Implement governed Git remote workflow."],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "runtime",
        workspace=tmp_path,
    )

    assert result["command"] == "aigol next"
    assert result["runtime_version"] == ACLI_NEXT_CONVERSATIONAL_SESSION_VERSION
    assert result["session_status"] == ACLI_NEXT_CONVERSATIONAL_SESSION_PRESENTED
    assert result["turn_count"] == 1
    assert result["session_resumed"] is False
    assert result["show_guide_delegate_only"] is True
    assert result["minimal_ux_extension_only"] is True
    assert result["platform_core_coordinates"] is True
    assert result["governance_authority_preserved"] is True
    assert result["replay_authority_preserved"] is True
    assert result["worker_execution_authority_preserved"] is True
    assert result["architectural_health_advisory_only"] is True
    assert result["acli_next_authorizes"] is False
    assert result["acli_next_executes"] is False
    assert result["acli_next_records_replay_evidence"] is False
    assert result["repository_mutated"] is False
    assert result["deployment_performed"] is False
    assert result["dashboard_summary"]["hybrid_operation"]["operation_type"] == "git_remote"
    assert result["dashboard_summary"]["hybrid_operation"]["hybrid_status"] == "HYBRID_REQUIRED"
    assert (tmp_path / "runtime" / "ACLI-NEXT-CONVERSATIONAL-TEST" / "RUN-000001").exists()


def test_acli_next_conversational_session_resumes_by_creating_next_run(tmp_path) -> None:
    kwargs = {
        "session_id": "ACLI-NEXT-CONVERSATIONAL-RESUME",
        "prompts": ["Show governed development status."],
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "runtime",
        "workspace": tmp_path,
    }

    first = run_acli_next_conversational_session(**kwargs)
    second = run_acli_next_conversational_session(**kwargs)

    assert first["run_id"] == "RUN-000001"
    assert first["session_resumed"] is False
    assert second["run_id"] == "RUN-000002"
    assert second["session_resumed"] is True


def test_acli_next_conversational_cli_route_renders_summary(tmp_path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "next",
            "--session-id",
            "ACLI-NEXT-CONVERSATIONAL-CLI",
            "--prompt",
            "Prepare a governed development readiness review.",
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

    assert result["command"] == "aigol next"
    assert result["session_status"] == ACLI_NEXT_CONVERSATIONAL_SESSION_PRESENTED
    assert result["dashboard_summary"]["active_task"]["current_milestone"] == "G11_02"
    assert result["acli_next_executes"] is False
    assert "AIGOL NEXT" in rendered
    assert "session_id: ACLI-NEXT-CONVERSATIONAL-CLI" in rendered
    assert "hybrid_status: FULLY_GOVERNED" in rendered
