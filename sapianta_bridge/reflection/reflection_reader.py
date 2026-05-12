"""Read-only reflection artifact inspection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sapianta_bridge.transport.transport_config import TransportConfig

from .reflection_engine import reflections_dir
from .reflection_models import ReflectionError, validate_reflection_artifact


def reflection_paths(config: TransportConfig | None = None) -> list[Path]:
    directory = reflections_dir(config)
    if not directory.exists():
        return []
    return sorted(path for path in directory.glob("*.json") if path.is_file())


def read_reflection(path: Path) -> dict[str, Any]:
    try:
        artifact = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReflectionError(str(path), f"malformed reflection JSON: {exc.msg}") from exc
    validate_reflection_artifact(artifact)
    return artifact


def reflection_history(config: TransportConfig | None = None) -> list[dict[str, Any]]:
    return [read_reflection(path) for path in reflection_paths(config)]


def latest_reflection(config: TransportConfig | None = None) -> dict[str, Any] | None:
    history = reflection_history(config)
    return history[-1] if history else None


def reflections_for_task(task_id: str, config: TransportConfig | None = None) -> list[dict[str, Any]]:
    return [
        artifact
        for artifact in reflection_history(config)
        if artifact["source_task_id"] == task_id
    ]


def reflection_summary(config: TransportConfig | None = None) -> dict[str, Any]:
    history = reflection_history(config)
    latest = history[-1] if history else None
    return {
        "total_reflections": len(history),
        "latest_reflection_id": latest["reflection_id"] if latest else None,
        "latest_source_task_id": latest["source_task_id"] if latest else None,
        "latest_governance_risk": latest["governance_risk"]["level"] if latest else None,
        "advisory_only": True,
        "allowed_to_execute_automatically": False,
    }
