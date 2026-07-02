"""Tests for G10-04 ACLI Next daily operational exposure."""

from __future__ import annotations

import pytest

from aigol.acli_next import (
    ACLI_NEXT_DAILY_OPERATIONAL_EXPOSURE_VERSION,
    render_acli_next_daily_dashboard,
    run_acli_next_daily_dashboard,
)
from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_daily_operational_exposure import (
    FULLY_GOVERNED,
    HYBRID_REQUIRED,
    create_daily_operational_exposure_snapshot,
)


CREATED_AT = "2026-07-02T00:00:00Z"


def _platform_core_state(requested_operation: str = "governed_development") -> dict:
    return {
        "workflow": {
            "current_stage": "Show Validation Result",
            "completed_stages": [
                "Capture Intent",
                "Classify Capability Coverage",
                "Show Workflow Stage",
                "Form Candidate / Proposal",
                "Request Human Approval",
                "Request Governance Authorization",
                "Delegate Worker Execution",
            ],
            "current_operation": "render validation result",
            "next_expected_operation": "Show Replay Evidence",
        },
        "active_task": {
            "task_id": "G10-04-DASHBOARD-TASK",
            "task_objective": "Expose certified governed development status",
            "current_milestone": "G10_04",
            "current_generation": "Generation 10",
            "governance_state": "authorized",
            "requested_operation": requested_operation,
        },
        "governance": {
            "approval_state": "approved",
            "authorization_state": "authorized",
            "pending_approvals": [],
            "completed_authorizations": ["G10-04-AUTHORIZATION"],
        },
        "validation": {
            "latest_validation": "git diff --check",
            "validation_suite_status": "passed",
            "validation_summary": "targeted validation clean",
            "validation_outcome": "passed",
        },
        "replay": {
            "latest_replay_record": "G10-04-REPLAY",
            "replay_summary": "dashboard presentation evidence available",
            "reconstruction_available": True,
            "evidence_available": True,
        },
        "architectural_health": {
            "health_status": "advisory_clear",
            "highest_severity": "none",
            "findings": [],
            "recommendations": ["continue preserving ownership boundaries"],
        },
    }


def test_acli_next_dashboard_presents_platform_core_state_without_authority(tmp_path) -> None:
    result = run_acli_next_daily_dashboard(
        dashboard_id="G10-04-DASHBOARD-001",
        platform_core_state=_platform_core_state(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "dashboard",
    )
    snapshot = result["platform_core_snapshot"]

    assert result["runtime_version"] == ACLI_NEXT_DAILY_OPERATIONAL_EXPOSURE_VERSION
    assert result["dashboard_status"] == "ACLI_NEXT_DAILY_DASHBOARD_PRESENTED"
    assert snapshot["workflow"]["current_stage"] == "Show Validation Result"
    assert snapshot["validation"]["validation_outcome"] == "passed"
    assert snapshot["replay"]["evidence_available"] is True
    assert snapshot["architectural_health"]["advisory_only"] is True
    assert snapshot["hybrid_operation"]["hybrid_status"] == FULLY_GOVERNED
    assert result["acli_next_authorizes"] is False
    assert result["acli_next_executes"] is False
    assert result["acli_next_records_replay_evidence"] is False
    assert result["external_operation_performed"] is False
    assert (tmp_path / "dashboard" / "000_acli_next_daily_dashboard_presented.json").exists()


def test_dashboard_flags_uncertified_git_remote_as_guidance_only() -> None:
    snapshot = create_daily_operational_exposure_snapshot(
        dashboard_id="G10-04-DASHBOARD-GIT",
        platform_core_state=_platform_core_state("git_remote"),
        created_at=CREATED_AT,
    )

    hybrid = snapshot["hybrid_operation"]
    assert hybrid["hybrid_status"] == HYBRID_REQUIRED
    assert hybrid["external_tool"] == "git"
    assert hybrid["guidance_only"] is True
    assert hybrid["external_operation_performed"] is False
    assert snapshot["git_remote_operation_performed"] is False


def test_dashboard_fails_closed_for_unknown_workflow_stage() -> None:
    state = _platform_core_state()
    state["workflow"]["current_stage"] = "Invent New Authority"

    with pytest.raises(FailClosedRuntimeError, match="unknown workflow stage"):
        create_daily_operational_exposure_snapshot(
            dashboard_id="G10-04-DASHBOARD-BAD-STAGE",
            platform_core_state=state,
            created_at=CREATED_AT,
        )


def test_acli_next_dashboard_cli_route_renders_status(tmp_path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "next",
            "dashboard",
            "--dashboard-id",
            "G10-04-DASHBOARD-CLI",
            "--task-objective",
            "Expose daily governed workflow",
            "--current-stage",
            "Show Replay Evidence",
            "--completed-stage",
            "Capture Intent",
            "--completed-stage",
            "Classify Capability Coverage",
            "--latest-validation",
            "git diff --check",
            "--validation-suite-status",
            "passed",
            "--validation-outcome",
            "passed",
            "--latest-replay-record",
            "G10-04-CLI-REPLAY",
            "--evidence-available",
            "--health-status",
            "advisory_clear",
            "--runtime-root",
            str(tmp_path / "runtime"),
            "--created-at",
            CREATED_AT,
        ]
    )

    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol next dashboard"
    assert result["platform_core_snapshot"]["workflow"]["current_stage"] == "Show Replay Evidence"
    assert result["platform_core_snapshot"]["validation"]["validation_outcome"] == "passed"
    assert "AIGOL NEXT DAILY DASHBOARD" in rendered
    assert "current_stage: Show Replay Evidence" in rendered
    assert "acli_next_executes: False" in rendered


def test_acli_next_dashboard_render_includes_hybrid_guidance(tmp_path) -> None:
    result = run_acli_next_daily_dashboard(
        dashboard_id="G10-04-DASHBOARD-HYBRID",
        platform_core_state=_platform_core_state("deployment"),
        created_at=CREATED_AT,
        replay_dir=tmp_path / "hybrid",
    )

    rendered = render_acli_next_daily_dashboard(result)

    assert "hybrid_status: HYBRID_REQUIRED" in rendered
    assert "hybrid_external_tool: deployment tool" in rendered
    assert "external_operation_performed: False" in rendered
