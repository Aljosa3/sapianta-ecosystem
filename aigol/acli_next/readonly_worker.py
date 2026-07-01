"""ACLI Next adapter for Platform Core read-only Worker handoff previews."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.acli_next.interactive import run_acli_next_interactive_session
from aigol.runtime.platform_core_execution_planning_service import (
    READONLY_WORKER_HANDOFF_COMPLETED as ACLI_NEXT_READONLY_WORKER_HANDOFF_COMPLETED,
    run_platform_core_readonly_worker_handoff,
)


ACLI_NEXT_READONLY_WORKER_VERSION = "G8_05_ACLI_NEXT_READONLY_WORKER_HANDOFF_V1"
READONLY_WORKER_COMMAND_NAME = "aigol next readonly-worker"


def run_acli_next_readonly_worker_handoff(
    *,
    session_id: str,
    interactive_result: dict[str, Any],
    worker_capability: str,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Delegate read-only Worker handoff preview to Platform Core."""

    return run_platform_core_readonly_worker_handoff(
        session_id=session_id,
        interactive_result=interactive_result,
        worker_capability=worker_capability,
        created_at=created_at,
        replay_dir=replay_dir,
        command_name=READONLY_WORKER_COMMAND_NAME,
        runtime_version=ACLI_NEXT_READONLY_WORKER_VERSION,
    )


def run_acli_next_interactive_with_readonly_worker(
    *,
    session_id: str,
    turns: list[dict[str, str]],
    worker_capability: str,
    created_at: str,
    replay_dir: str | Path,
    workspace: str | Path = ".",
) -> dict[str, Any]:
    """Run an interactive session and delegate read-only Worker handoff to Platform Core."""

    replay_path = Path(replay_dir)
    interactive_result = run_acli_next_interactive_session(
        session_id=session_id,
        turns=turns,
        created_at=created_at,
        replay_dir=replay_path / "interactive_session",
        workspace=workspace,
    )
    return run_acli_next_readonly_worker_handoff(
        session_id=session_id,
        interactive_result=interactive_result,
        worker_capability=worker_capability,
        created_at=created_at,
        replay_dir=replay_path / "readonly_worker_handoff",
    )


def render_acli_next_readonly_worker_summary(result: dict[str, Any]) -> str:
    """Render ACLI Next read-only Worker handoff evidence."""

    return "\n".join(
        [
            f"command: {result.get('command')}",
            f"runtime_version: {result.get('runtime_version')}",
            f"platform_core_service_version: {result.get('platform_core_service_version')}",
            f"session_id: {result.get('session_id')}",
            f"handoff_status: {result.get('handoff_status')}",
            f"worker_capability: {result.get('worker_capability')}",
            f"worker_id: {result.get('worker_id')}",
            f"governance_authorization_status: {result.get('governance_authorization_status')}",
            f"worker_result_status: {result.get('worker_result_status')}",
            f"replay_reference: {result.get('replay_reference')}",
            f"interactive_replay_reference: {result.get('interactive_replay_reference')}",
            f"read_only: {result.get('read_only')}",
            f"worker_invoked: {result.get('worker_invoked')}",
            f"provider_invoked: {result.get('provider_invoked')}",
            f"repository_mutated: {result.get('repository_mutated')}",
            f"deployment_performed: {result.get('deployment_performed')}",
        ]
    )
