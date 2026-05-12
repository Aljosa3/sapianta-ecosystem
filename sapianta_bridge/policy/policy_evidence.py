"""Append-only policy evaluation evidence storage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sapianta_bridge.transport.transport_config import TransportConfig

from .policy_models import PolicyError, validate_policy_evaluation


def evaluations_dir(config: TransportConfig | None = None) -> Path:
    active_config = config or TransportConfig()
    return active_config.runtime_root / "policy" / "evaluations"


def write_policy_evaluation(
    evaluation: dict[str, Any],
    config: TransportConfig | None = None,
) -> Path:
    validate_policy_evaluation(evaluation)
    destination_dir = evaluations_dir(config)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / f"{evaluation['timestamp']}_{evaluation['policy_evaluation_id']}.json"
    if destination.exists():
        raise PolicyError("policy_evaluation_id", "policy evaluation already exists")
    destination.write_text(json.dumps(evaluation, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return destination
