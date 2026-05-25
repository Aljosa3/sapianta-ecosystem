"""Replay reconstruction for governed semantic continuity memory."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .memory_store import MemoryStore


def reconstruct_memory_lineage(runtime_id: str, root: Path | str) -> dict[str, Any]:
    store = MemoryStore(root)
    contract = store.load_contract(runtime_id)
    record = store.load_record(runtime_id)
    validation = store.load_validation(runtime_id)
    summary = store.load_summary(runtime_id)
    return {
        "status": "MEMORY_LINEAGE_RECONSTRUCTED",
        "runtime_id": runtime_id,
        "memory_contract": contract,
        "memory_record": record,
        "memory_validation": validation,
        "semantic_summary": summary,
        "replay_chain": [
            contract["replay_hash"],
            record["replay_hash"],
            validation["replay_hash"],
            summary["summary_replay_hash"],
        ],
    }
