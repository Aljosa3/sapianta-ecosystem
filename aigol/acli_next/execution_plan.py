"""ACLI Next adapter for Platform Core execution plan previews."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.acli_next.interactive import run_acli_next_interactive_session
from aigol.runtime.platform_core_execution_planning_service import (
    EXECUTION_PLAN_COMPLETED as ACLI_NEXT_EXECUTION_PLAN_COMPLETED,
    run_platform_core_execution_plan_preview,
)


ACLI_NEXT_EXECUTION_PLAN_VERSION = "G8_06_EXECUTION_PLAN_AND_MUTATION_PREVIEW_V1"
EXECUTION_PLAN_COMMAND_NAME = "aigol next execution-plan"


def run_acli_next_execution_plan(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    worker_sequence: list[str] | None = None,
    requested_capabilities: list[str] | None = None,
    expected_artifacts: list[str] | None = None,
    potential_repository_impacts: list[str] | None = None,
) -> dict[str, Any]:
    """Delegate advisory execution planning to Platform Core."""

    return run_platform_core_execution_plan_preview(
        session_id=session_id,
        interactive_result=interactive_result,
        created_at=created_at,
        replay_dir=replay_dir,
        command_name=EXECUTION_PLAN_COMMAND_NAME,
        runtime_version=ACLI_NEXT_EXECUTION_PLAN_VERSION,
        worker_sequence=worker_sequence,
        requested_capabilities=requested_capabilities,
        expected_artifacts=expected_artifacts,
        potential_repository_impacts=potential_repository_impacts,
    )


def run_acli_next_interactive_with_execution_plan(
    *,
    session_id: str,
    turns: list[dict[str, str]],
    created_at: str,
    replay_dir: str | Path,
    workspace: str | Path = ".",
    worker_sequence: list[str] | None = None,
    requested_capabilities: list[str] | None = None,
    expected_artifacts: list[str] | None = None,
    potential_repository_impacts: list[str] | None = None,
) -> dict[str, Any]:
    """Run an interactive session and delegate execution plan preview to Platform Core."""

    replay_path = Path(replay_dir)
    interactive_result = run_acli_next_interactive_session(
        session_id=session_id,
        turns=turns,
        created_at=created_at,
        replay_dir=replay_path / "interactive_session",
        workspace=workspace,
    )
    return run_acli_next_execution_plan(
        session_id=session_id,
        interactive_result=interactive_result,
        created_at=created_at,
        replay_dir=replay_path / "execution_plan",
        worker_sequence=worker_sequence,
        requested_capabilities=requested_capabilities,
        expected_artifacts=expected_artifacts,
        potential_repository_impacts=potential_repository_impacts,
    )


def render_acli_next_execution_plan_summary(result: dict[str, Any]) -> str:
    """Render ACLI Next execution plan evidence returned by Platform Core."""

    return "\n".join(
        [
            f"command: {result.get('command')}",
            f"runtime_version: {result.get('runtime_version')}",
            f"platform_core_service_version: {result.get('platform_core_service_version')}",
            f"session_id: {result.get('session_id')}",
            f"plan_status: {result.get('plan_status')}",
            f"risk_level: {result.get('execution_risk_summary', {}).get('risk_level')}",
            f"worker_sequence: {', '.join(result.get('selected_worker_sequence', []))}",
            f"requested_capabilities: {', '.join(result.get('requested_capabilities', []))}",
            f"mutation_preview_status: {result.get('mutation_preview', {}).get('preview_status')}",
            f"replay_reference: {result.get('replay_reference')}",
            f"interactive_replay_reference: {result.get('interactive_replay_reference')}",
            f"execution_authorized: {result.get('execution_authorized')}",
            f"worker_invoked: {result.get('worker_invoked')}",
            f"provider_invoked: {result.get('provider_invoked')}",
            f"repository_mutated: {result.get('repository_mutated')}",
            f"deployment_performed: {result.get('deployment_performed')}",
        ]
    )
