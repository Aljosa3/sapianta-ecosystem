"""Read-only policy evaluation history."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sapianta_bridge.transport.transport_config import TransportConfig

from .policy_evidence import evaluations_dir
from .policy_models import PolicyError, validate_policy_evaluation


def policy_evaluation_paths(config: TransportConfig | None = None) -> list[Path]:
    directory = evaluations_dir(config)
    if not directory.exists():
        return []
    return sorted(path for path in directory.glob("*.json") if path.is_file())


def read_policy_evaluation(path: Path) -> dict[str, Any]:
    try:
        artifact = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PolicyError(str(path), f"malformed policy evaluation JSON: {exc.msg}") from exc
    validate_policy_evaluation(artifact)
    return artifact


def policy_history(config: TransportConfig | None = None) -> list[dict[str, Any]]:
    return sorted(
        [read_policy_evaluation(path) for path in policy_evaluation_paths(config)],
        key=lambda item: (item["timestamp"], item["policy_evaluation_id"]),
    )


def latest_policy_evaluation(config: TransportConfig | None = None) -> dict[str, Any] | None:
    history = policy_history(config)
    return history[-1] if history else None


def evaluations_by_source(source_id: str, config: TransportConfig | None = None) -> list[dict[str, Any]]:
    return [item for item in policy_history(config) if item["source_id"] == source_id]


def evaluations_by_risk(risk_level: str, config: TransportConfig | None = None) -> list[dict[str, Any]]:
    return [item for item in policy_history(config) if item["classification"]["risk_level"] == risk_level]


def evaluations_by_admissibility(
    admissibility: str,
    config: TransportConfig | None = None,
) -> list[dict[str, Any]]:
    return [
        item
        for item in policy_history(config)
        if item["classification"]["admissibility"] == admissibility
    ]
