"""Regression tests for G14-08A Platform Core project services extraction."""

from __future__ import annotations

import json
from pathlib import Path

from aigol.cli import aigol_cli
from aigol.runtime.platform_core_project_services import (
    PLATFORM_CORE_PROJECT_SERVICES_VERSION,
    goal_mapping_from_workspace,
)


CREATED_AT = "2026-07-03T00:00:00Z"
SESSION_ID = "G14-08A-PLATFORM-CORE-PROJECT-SERVICES"


def _run_aigol_next(monkeypatch, tmp_path, inputs: list[str]) -> int:
    class TtyStdin:
        def isatty(self) -> bool:
            return True

    iterator = iter(inputs)
    monkeypatch.setattr("sys.stdin", TtyStdin())
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(iterator))
    return aigol_cli.main(
        [
            "next",
            "--session-id",
            SESSION_ID,
            "--runtime-root",
            str(tmp_path / "runtime"),
            "--workspace",
            str(tmp_path),
            "--created-at",
            CREATED_AT,
        ]
    )


def test_project_services_are_platform_core_authoritative_and_acli_next_renders(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    result = _run_aigol_next(
        monkeypatch,
        tmp_path,
        [
            "I want AiGOL Next to support GitHub Actions.",
            "/send",
            "exit",
        ],
    )
    output = capsys.readouterr().out
    state_path = (
        tmp_path
        / "runtime"
        / SESSION_ID
        / "workspace_state"
        / "001_acli_next_workspace_state_recorded.json"
    )
    workspace_state = json.loads(state_path.read_text(encoding="utf-8"))
    pending_summary = workspace_state["pending_implementation_summary"]
    contextual_mapping = pending_summary["goal_mapping"]["contextual_task_mapping"]

    assert result == 0
    assert "contextual_task_mapping:" in output
    assert workspace_state["platform_core_project_services_version"] == PLATFORM_CORE_PROJECT_SERVICES_VERSION
    assert workspace_state["project_workspace_authority"] == "PLATFORM_CORE"
    assert workspace_state["project_guidance_authority"] == "PLATFORM_CORE"
    assert workspace_state["project_knowledge_reuse_authority"] == "PLATFORM_CORE"
    assert workspace_state["contextual_task_mapping_authority"] == "PLATFORM_CORE"
    assert workspace_state["project_guidance"]["guidance_authority"] == "PLATFORM_CORE"
    assert workspace_state["project_knowledge_index"]["knowledge_reuse_authority"] == "PLATFORM_CORE"
    assert pending_summary["goal_mapping"]["goal_mapping_authority"] == "PLATFORM_CORE"
    assert contextual_mapping["contextual_task_mapping_authority"] == "PLATFORM_CORE"
    assert pending_summary["acli_next_executes"] is False


def test_project_services_are_reusable_without_acli_next_runtime_state() -> None:
    mapping = goal_mapping_from_workspace(
        message="I want AiGOL Next to support GitHub Actions.",
        workspace_state=None,
    )

    assert mapping["platform_core_project_services_version"] == PLATFORM_CORE_PROJECT_SERVICES_VERSION
    assert mapping["goal_mapping_authority"] == "PLATFORM_CORE"
    assert mapping["goal_target"] == "github_actions"
    assert mapping["contextual_task_mapping"]["contextual_task_mapping_authority"] == "PLATFORM_CORE"
    assert mapping["acli_next_executes_mapping"] is False


def test_acli_next_no_longer_defines_project_service_business_logic() -> None:
    source = Path("aigol/acli_next/conversational.py").read_text(encoding="utf-8")

    assert "def _persistent_workspace_state_artifact" not in source
    assert "def _project_guidance_model" not in source
    assert "def _goal_mapping_from_workspace" not in source
    assert "def _project_knowledge_index_model" not in source
    assert "def _project_knowledge_context_from_workspace" not in source
    assert "def _guided_development_clarification_required" not in source
