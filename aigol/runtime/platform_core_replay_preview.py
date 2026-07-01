"""Replay planning and persistence helpers for Platform Core previews."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.runtime.transport.serialization import write_json_immutable


PLATFORM_CORE_REPLAY_PREVIEW_VERSION = "G8_06D_PLATFORM_CORE_REPLAY_PREVIEW_V1"


def execution_plan_replay_plan(interactive_result: dict[str, Any]) -> dict[str, Any]:
    """Describe replay artifacts expected for advisory execution plan preview."""

    return {
        "replay_preview_version": PLATFORM_CORE_REPLAY_PREVIEW_VERSION,
        "interactive_replay_reference": interactive_result["replay_reference"],
        "interactive_replay_hash": interactive_result["replay_hash"],
        "planned_artifacts": [
            "000_acli_next_execution_plan_request.json",
            "001_acli_next_execution_plan_recorded.json",
            "002_acli_next_mutation_preview_recorded.json",
            "003_acli_next_execution_plan_completed.json",
        ],
        "replay_append_only": True,
        "replay_reconstruction_owner": "Replay",
    }


def persist_platform_core_preview_artifact(replay_path: Path, name: str, artifact: dict[str, Any]) -> None:
    """Persist one replay-visible Platform Core preview artifact append-only."""

    write_json_immutable(replay_path / name, artifact)
