"""Tests for the G8-06D Platform Core execution planning service."""

from __future__ import annotations

from pathlib import Path

from aigol.acli_next import run_acli_next_interactive_session
from aigol.runtime.platform_core_execution_planning_service import (
    PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_VERSION,
    run_platform_core_execution_plan_preview,
)


CREATED_AT = "2026-07-01T00:00:00Z"


def _turn(request: str, response: str) -> dict[str, str]:
    return {"operator_request": request, "operator_response": response}


def test_platform_core_execution_plan_service_builds_plan_for_any_interface(tmp_path) -> None:
    interactive = run_acli_next_interactive_session(
        session_id="PLATFORM-CORE-PLAN-001",
        turns=[_turn("Create an advisory platform plan.", "confirm")],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "interactive",
        workspace=tmp_path,
    )

    result = run_platform_core_execution_plan_preview(
        session_id="PLATFORM-CORE-PLAN-001",
        interactive_result=interactive,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "platform_core_plan",
        command_name="web execution-plan preview",
        runtime_version="WEB_ADAPTER_TEST_V1",
        worker_sequence=["READONLY_REVIEW"],
        requested_capabilities=["validation_summary"],
        expected_artifacts=["PLATFORM_CORE_EXECUTION_PLAN_ARTIFACT_V1"],
        potential_repository_impacts=["No repository mutation."],
    )

    assert result["command"] == "web execution-plan preview"
    assert result["runtime_version"] == "WEB_ADAPTER_TEST_V1"
    assert result["platform_core_service_version"] == PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_VERSION
    assert result["plan_status"] == "ACLI_NEXT_EXECUTION_PLAN_COMPLETED"
    assert result["selected_worker_sequence"] == ["READONLY_REVIEW"]
    assert result["requested_capabilities"] == ["validation_summary"]
    assert result["worker_invoked"] is False
    assert result["repository_mutated"] is False
    assert (tmp_path / "platform_core_plan" / "003_acli_next_execution_plan_completed.json").exists()


def test_acli_next_execution_plan_adapter_no_longer_owns_plan_logic() -> None:
    source = Path("aigol/acli_next/execution_plan.py").read_text(encoding="utf-8")

    assert "DEFAULT_WORKER_SEQUENCE" not in source
    assert "AUTHORIZED_ADVISORY_EXECUTION_PLAN" not in source
    assert "def _risk_summary" not in source
    assert "def _governance_checkpoints" not in source
    assert "def _mutation_preview" not in source
    assert "run_platform_core_execution_plan_preview" in source


def test_acli_next_readonly_worker_adapter_no_longer_owns_capability_lookup() -> None:
    source = Path("aigol/acli_next/readonly_worker.py").read_text(encoding="utf-8")

    assert "SUPPORTED_READONLY_CAPABILITIES" not in source
    assert "def _lookup_readonly_capability" not in source
    assert "def _readonly_worker_summary" not in source
    assert "def _governance_authorization_check" not in source
    assert "run_platform_core_readonly_worker_handoff" in source


def test_platform_core_execution_planning_service_delegates_owner_responsibilities() -> None:
    source = Path("aigol/runtime/platform_core_execution_planning_service.py").read_text(encoding="utf-8")

    assert "lookup_readonly_worker_capability" in source
    assert "readonly_worker_authorization" in source
    assert "execution_plan_authorization" in source
    assert "readonly_worker_result" in source
    assert "execution_plan_artifact" in source
    assert "mutation_preview_artifact" in source
    assert "execution_plan_replay_plan" in source
    assert "persist_platform_core_preview_artifact" in source
    assert "SUPPORTED_READONLY_CAPABILITIES" not in source
    assert "def _readonly_worker_authorization" not in source
    assert "def _execution_plan_authorization" not in source
    assert "def _readonly_worker_result" not in source
    assert "def _readonly_worker_summary" not in source
    assert "def _execution_plan(" not in source
    assert "def _mutation_preview" not in source
    assert "def _replay_plan" not in source
    assert "def _governance_checkpoints" not in source
    assert "def _risk_summary" not in source
