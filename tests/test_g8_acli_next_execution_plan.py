"""Tests for G8-06 ACLI Next execution planning."""

from __future__ import annotations

import pytest

from aigol.acli_next import (
    ACLI_NEXT_EXECUTION_PLAN_VERSION,
    run_acli_next_execution_plan,
    run_acli_next_interactive_session,
    run_acli_next_interactive_with_execution_plan,
)
from aigol.acli_next.execution_plan import ACLI_NEXT_EXECUTION_PLAN_COMPLETED
from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-07-01T00:00:00Z"


def _turn(request: str, response: str) -> dict[str, str]:
    return {"operator_request": request, "operator_response": response}


def test_acli_next_execution_plan_records_advisory_plan_without_mutation(tmp_path) -> None:
    result = run_acli_next_interactive_with_execution_plan(
        session_id="ACLI-NEXT-EXECUTION-PLAN-001",
        turns=[_turn("Create an advisory execution plan for ACLI Next.", "confirm")],
        worker_sequence=["ACLI_NEXT_READONLY_WORKER_HANDOFF", "FUTURE_MUTATION_WORKER_PREVIEW"],
        requested_capabilities=["replay_inspection", "patch_preview"],
        expected_artifacts=["PLAN.md", "PATCH_PREVIEW.diff"],
        potential_repository_impacts=["Future patch may edit docs after separate certification."],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "execution_plan",
        workspace=tmp_path,
    )

    assert result["command"] == "aigol next execution-plan"
    assert result["runtime_version"] == ACLI_NEXT_EXECUTION_PLAN_VERSION
    assert result["plan_status"] == ACLI_NEXT_EXECUTION_PLAN_COMPLETED
    assert result["selected_worker_sequence"] == [
        "ACLI_NEXT_READONLY_WORKER_HANDOFF",
        "FUTURE_MUTATION_WORKER_PREVIEW",
    ]
    assert result["requested_capabilities"] == ["replay_inspection", "patch_preview"]
    assert result["execution_risk_summary"]["risk_level"] == "MEDIUM"
    assert result["execution_risk_summary"]["mutation_possible_in_this_milestone"] is False
    assert result["mutation_preview"]["descriptive_only"] is True
    assert result["mutation_preview"]["repository_files_to_modify"] == []
    assert result["execution_authorized"] is False
    assert result["worker_invoked"] is False
    assert result["provider_invoked"] is False
    assert result["repository_mutated"] is False
    assert result["deployment_performed"] is False
    plan_dir = tmp_path / "execution_plan" / "execution_plan"
    assert (plan_dir / "000_acli_next_execution_plan_request.json").exists()
    assert (plan_dir / "001_acli_next_execution_plan_recorded.json").exists()
    assert (plan_dir / "002_acli_next_mutation_preview_recorded.json").exists()
    assert (plan_dir / "003_acli_next_execution_plan_completed.json").exists()


def test_acli_next_execution_plan_requires_human_confirmation(tmp_path) -> None:
    interactive = run_acli_next_interactive_session(
        session_id="ACLI-NEXT-EXECUTION-PLAN-REJECTED",
        turns=[_turn("Create an advisory execution plan.", "reject")],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "interactive",
        workspace=tmp_path,
    )

    with pytest.raises(FailClosedRuntimeError, match="human confirmation missing"):
        run_acli_next_execution_plan(
            session_id="ACLI-NEXT-EXECUTION-PLAN-REJECTED",
            interactive_result=interactive,
            created_at=CREATED_AT,
            replay_dir=tmp_path / "plan",
        )


def test_acli_next_execution_plan_fails_closed_on_duplicate_capability(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="unique requested_capabilities"):
        run_acli_next_interactive_with_execution_plan(
            session_id="ACLI-NEXT-EXECUTION-PLAN-DUPLICATE",
            turns=[_turn("Create an advisory execution plan.", "confirm")],
            requested_capabilities=["replay_inspection", "replay_inspection"],
            created_at=CREATED_AT,
            replay_dir=tmp_path / "duplicate",
            workspace=tmp_path,
        )


def test_acli_next_execution_plan_cli_route_renders_summary(tmp_path) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "next",
            "execution-plan",
            "--session-id",
            "ACLI-NEXT-EXECUTION-PLAN-CLI",
            "--turn",
            "Create advisory execution plan=>confirm",
            "--worker-step",
            "ACLI_NEXT_READONLY_WORKER_HANDOFF",
            "--capability",
            "validation_summary",
            "--expected-artifact",
            "ACLI_NEXT_EXECUTION_PLAN_ARTIFACT_V1",
            "--potential-impact",
            "No repository mutation in this milestone.",
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

    assert result["command"] == "aigol next execution-plan"
    assert result["plan_status"] == ACLI_NEXT_EXECUTION_PLAN_COMPLETED
    assert result["repository_mutated"] is False
    assert result["worker_invoked"] is False
    assert "AIGOL NEXT EXECUTION PLAN" in rendered
    assert "risk_level:" in rendered
