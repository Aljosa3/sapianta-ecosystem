"""Execution handoff command helpers for the deterministic AiGOL CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from agol_bridge.chatgpt_ingress.controlled_execution_handoff import create_controlled_execution_handoff

from aigol.cli.commands.continuity import build_governed_chain


def run_execution_handoff(
    *,
    ingress_artifact: dict,
    workspace_path: str | None = None,
    timeout_seconds: int = 600,
    native_message_handler: Callable[[dict], dict] | None = None,
) -> dict:
    chain = build_governed_chain(ingress_artifact=ingress_artifact)
    kwargs = {
        "continuity_preview": chain["continuity_preview"],
        "workspace_path": workspace_path or str(Path.cwd()),
        "timeout_seconds": timeout_seconds,
    }
    if native_message_handler is not None:
        kwargs["native_message_handler"] = native_message_handler
    artifact = create_controlled_execution_handoff(**kwargs)
    return {
        "command": "aigol execution handoff",
        "execution_artifact": artifact,
        "execution_status": artifact.get("execution_status", "UNKNOWN"),
        "provider_invoked": artifact.get("provider_invoked") is True,
        "replay_identity": artifact.get("replay_identity", "UNKNOWN"),
        "execution_governance_hash": artifact.get("execution_governance_hash", ""),
        "execution_result_hash": artifact.get("execution_result_hash", ""),
    }


__all__ = ["run_execution_handoff"]

