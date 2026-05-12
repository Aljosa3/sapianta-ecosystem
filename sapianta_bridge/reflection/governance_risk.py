"""Deterministic governance risk interpretation from runtime evidence."""

from __future__ import annotations

from typing import Any

from .reflection_models import ReflectionError


def governance_risk_from_evidence(
    replay_entry: dict[str, Any],
    summary: dict[str, Any],
    transitions: dict[str, Any],
) -> dict[str, str]:
    if transitions.get("invalid_transition_detected") is True:
        return {
            "level": "HIGH",
            "summary": "replay transition inconsistency detected",
        }

    try:
        final_state = replay_entry["final_state"]
        failed = int(summary["failed_executions"])
        total = int(summary["total_executions"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ReflectionError("governance_risk", "insufficient governance evidence") from exc

    if total <= 0:
        raise ReflectionError("governance_risk", "missing replay execution evidence")
    if final_state == "FAILED" or failed >= 2:
        return {
            "level": "MEDIUM",
            "summary": "execution failures require bounded governance review",
        }
    if final_state == "COMPLETED":
        return {
            "level": "LOW",
            "summary": "bounded transport stable; no governance escalation detected",
        }
    return {
        "level": "CRITICAL",
        "summary": "unknown execution state indicates protocol enforcement uncertainty",
    }
