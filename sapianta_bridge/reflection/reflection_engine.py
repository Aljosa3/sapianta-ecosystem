"""Replay-derived advisory reflection generation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sapianta_bridge.observability.execution_summary import execution_summary
from sapianta_bridge.observability.replay_reader import ReplayEvidenceError, find_by_task_id
from sapianta_bridge.observability.runtime_status import runtime_status
from sapianta_bridge.observability.state_transitions import transition_history
from sapianta_bridge.protocol.hashing import compute_hash
from sapianta_bridge.transport.transport_config import TransportConfig

from .advisory_proposals import advisory_proposals_from_risk
from .capability_delta import capability_delta_from_evidence
from .governance_risk import governance_risk_from_evidence
from .reflection_models import ReflectionError, validate_reflection_artifact


def reflections_dir(config: TransportConfig | None = None) -> Path:
    active_config = config or TransportConfig()
    return active_config.runtime_root / "reflections"


def _reflection_id(task_id: str, timestamp: str, replay_entry: dict[str, Any]) -> str:
    digest = compute_hash(
        {
            "task_id": task_id,
            "timestamp": timestamp,
            "replay_entry": replay_entry,
        }
    )
    return f"REFLECTION-{digest[:16].upper()}"


def build_reflection_artifact(
    task_id: str,
    config: TransportConfig | None = None,
    *,
    timestamp: str | None = None,
) -> dict[str, Any]:
    active_config = config or TransportConfig()
    entries = find_by_task_id(task_id, active_config)
    if not entries:
        raise ReflectionError("task_id", "no replay evidence for task")

    replay_entry = entries[-1]
    effective_timestamp = timestamp or datetime.now(timezone.utc).isoformat()
    summary = execution_summary(active_config)
    transitions = transition_history(task_id, active_config)
    if transitions["invalid_transition_detected"]:
        raise ReflectionError("lifecycle", "invalid lifecycle transition evidence")

    delta = capability_delta_from_evidence(replay_entry, summary)
    risk = governance_risk_from_evidence(replay_entry, summary, transitions)
    status = runtime_status(active_config)
    observations = [
        "protocol enforcement remained upstream of transport evidence",
        "reflection remained advisory-only",
    ]
    if status["active_lock_present"] is False:
        observations.append("no active processing lock present during reflection")
    if transitions["transition_count"] > 0:
        observations.append("lifecycle transition evidence was inspectable")

    artifact = {
        "reflection_id": _reflection_id(task_id, effective_timestamp, replay_entry),
        "timestamp": effective_timestamp,
        "source_task_id": task_id,
        "execution_outcome": {
            "final_state": replay_entry["final_state"],
            "exit_code": replay_entry["codex_exit_code"],
            "duration_seconds": replay_entry["processing_duration_seconds"],
        },
        "capability_delta": delta,
        "governance_risk": risk,
        "observations": observations,
        "advisory_proposals": advisory_proposals_from_risk(risk),
        "advisory_only": True,
        "allowed_to_execute_automatically": False,
        "source_evidence": {
            "task_hash": replay_entry["task_hash"],
            "result_hash": replay_entry["result_hash"],
            "replay_timestamp": replay_entry["execution_timestamp"],
        },
    }
    validate_reflection_artifact(artifact)
    return artifact


def write_reflection_artifact(
    artifact: dict[str, Any],
    config: TransportConfig | None = None,
) -> Path:
    validate_reflection_artifact(artifact)
    destination_dir = reflections_dir(config)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / f"{artifact['timestamp']}_{artifact['reflection_id']}.json"
    if destination.exists():
        raise ReflectionError("reflection_path", "reflection artifact already exists")
    destination.write_text(json.dumps(artifact, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return destination


def generate_reflection(
    task_id: str,
    config: TransportConfig | None = None,
    *,
    timestamp: str | None = None,
) -> dict[str, Any]:
    try:
        artifact = build_reflection_artifact(task_id, config, timestamp=timestamp)
    except ReplayEvidenceError as exc:
        raise ReflectionError(exc.field, exc.reason) from exc
    path = write_reflection_artifact(artifact, config)
    return {"created": True, "reflection_path": str(path), "reflection": artifact}
