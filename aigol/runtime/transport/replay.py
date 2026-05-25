"""Replay reconstruction for runtime transport persistence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .runtime_store import RuntimeStore


def reconstruct_runtime_lineage(runtime_id: str, root: Path | str) -> dict[str, Any]:
    store = RuntimeStore(root)
    dispatch = store.load_dispatch(runtime_id)
    result = store.load_result(runtime_id)
    ledger_entries = store.ledger.read(runtime_id)
    return {
        "status": "RECONSTRUCTED",
        "runtime_id": runtime_id,
        "dispatch": dispatch,
        "result": result,
        "ledger_entries": ledger_entries,
        "replay_chain": [
            dispatch["replay_hash"],
            *[entry["entry_hash"] for entry in ledger_entries],
            result["replay_hash"],
        ],
    }
