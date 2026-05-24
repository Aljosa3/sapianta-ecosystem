"""Return-flow command helpers for the deterministic AiGOL CLI."""

from __future__ import annotations


def return_flow_summary(*, execution_result: dict | None = None) -> dict:
    artifact = (execution_result or {}).get("execution_artifact", {}) if isinstance(execution_result, dict) else {}
    return {
        "command": "aigol return-flow",
        "return_status": "READY" if artifact else "NOT_STARTED",
        "execution_status": artifact.get("execution_status", "NOT_STARTED"),
        "replay_identity": artifact.get("replay_identity", "UNKNOWN"),
    }


__all__ = ["return_flow_summary"]
