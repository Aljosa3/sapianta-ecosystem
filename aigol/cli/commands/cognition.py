"""Read-only cognition observability command helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.cognition.authority_propagation import inspect_authority_propagation
from aigol.cognition.integrity_summary import inspect_cognition_integrity
from aigol.cognition.lifecycle_model import inspect_cognition_lifecycle
from aigol.cognition.registry import inspect_cognition_registry
from aigol.cognition.semantic_replay import inspect_semantic_replay_continuity
from aigol.cognition.state_envelope import inspect_cognition_input
from aigol.cognition.topology_report import inspect_cognition_topology


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


def inspect_topology(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    return inspect_cognition_topology(input_path=input_path, output_path=output_path)


def inspect_lifecycle(
    *,
    output_path: str | Path | None = None,
    validate: bool = False,
) -> dict[str, Any]:
    return inspect_cognition_lifecycle(output_path=output_path, validate=validate)


def inspect_integrity(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
    validate: bool = False,
) -> dict[str, Any]:
    return inspect_cognition_integrity(input_path=input_path, output_path=output_path, validate=validate)


def inspect_authority(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
    validate: bool = False,
) -> dict[str, Any]:
    return inspect_authority_propagation(input_path=input_path, output_path=output_path, validate=validate)


__all__ = [
    "check_semantic_replay_continuity",
    "inspect_authority",
    "inspect_cognition",
    "inspect_integrity",
    "inspect_lifecycle",
    "inspect_registry",
    "inspect_topology",
]
