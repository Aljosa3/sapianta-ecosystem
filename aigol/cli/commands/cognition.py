"""Read-only cognition observability command helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.cognition.registry import inspect_cognition_registry
from aigol.cognition.semantic_replay import inspect_semantic_replay_continuity
from aigol.cognition.state_envelope import inspect_cognition_input


def inspect_cognition(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    return inspect_cognition_input(input_path=input_path, output_path=output_path)


def check_semantic_replay_continuity(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    return inspect_semantic_replay_continuity(input_path=input_path, output_path=output_path)


def inspect_registry(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    return inspect_cognition_registry(input_path=input_path, output_path=output_path)


__all__ = ["check_semantic_replay_continuity", "inspect_cognition", "inspect_registry"]
