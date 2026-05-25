"""Replay reconstruction for bounded goal continuity."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.runtime.transport.runtime_store import RuntimeStore


def reconstruct_goal_continuity(runtime_id: str, root: Path | str) -> dict[str, Any]:
    store = RuntimeStore(root)
    contract = store.load_goal_contract(runtime_id)
    sequence = store.load_goal_sequence(runtime_id)
    validation = store.load_goal_validation(runtime_id)
    result = store.load_goal_result(runtime_id)
    ledger_entries = store.ledger.read(runtime_id)
    return {
        "status": "GOAL_CONTINUITY_RECONSTRUCTED",
        "runtime_id": runtime_id,
        "goal_contract": contract,
        "goal_sequence": sequence,
        "goal_validation": validation,
        "goal_result": result,
        "ledger_entries": ledger_entries,
        "replay_chain": [
            contract["replay_hash"],
            sequence["replay_hash"],
            validation["replay_hash"],
            result["replay_hash"],
            *[entry["entry_hash"] for entry in ledger_entries],
        ],
    }
