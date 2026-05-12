"""Conservative capability delta summaries derived from replay evidence."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.observability.replay_reader import ReplayEvidenceError

from .reflection_models import ReflectionError


def capability_delta_from_evidence(
    replay_entry: dict[str, Any],
    summary: dict[str, Any],
) -> dict[str, Any]:
    try:
        final_state = replay_entry["final_state"]
        total = int(summary["total_executions"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ReflectionError("capability_delta", "insufficient replay evidence") from exc

    if final_state == "COMPLETED" and total > 0:
        return {
            "detected": True,
            "summary": "replay-safe bounded execution evidence confirmed",
        }
    if final_state == "FAILED":
        return {
            "detected": False,
            "summary": "capability delta not certified because latest execution failed",
        }
    raise ReplayEvidenceError("final_state", "unknown execution state")
