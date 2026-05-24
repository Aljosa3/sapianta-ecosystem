"""Return-flow command helpers for the deterministic AiGOL CLI."""

from __future__ import annotations

from pathlib import Path

from aigol.cli.commands.return_continuity import inspect_governed_return


def return_flow_summary(*, execution_result: dict | None = None) -> dict:
    artifact = (execution_result or {}).get("execution_artifact", {}) if isinstance(execution_result, dict) else {}
    return {
        "command": "aigol return-flow",
        "return_status": "READY" if artifact else "NOT_STARTED",
        "execution_status": artifact.get("execution_status", "NOT_STARTED"),
        "replay_identity": artifact.get("replay_identity", "UNKNOWN"),
    }


def inspect_return(*, replay_identity: str, runtime_root: str | Path | None = None) -> dict:
    return inspect_governed_return(replay_identity=replay_identity, runtime_root=runtime_root)


__all__ = ["inspect_return", "return_flow_summary"]
