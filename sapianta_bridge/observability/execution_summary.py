"""Deterministic execution summaries derived only from replay evidence."""

from __future__ import annotations

from typing import Any

from sapianta_bridge.transport.transport_config import TransportConfig

from .replay_reader import execution_history


def execution_summary(config: TransportConfig | None = None) -> dict[str, Any]:
    entries = execution_history(config)
    total = len(entries)
    successful = sum(1 for entry in entries if entry["final_state"] == "COMPLETED")
    failed = sum(1 for entry in entries if entry["final_state"] == "FAILED")
    duration_total = sum(float(entry["processing_duration_seconds"]) for entry in entries)
    average = round(duration_total / total, 6) if total else 0.0
    return {
        "total_executions": total,
        "successful_executions": successful,
        "failed_executions": failed,
        "quarantined_results": 0,
        "average_duration_seconds": average,
        "last_result_state": entries[-1]["final_state"] if entries else None,
    }

