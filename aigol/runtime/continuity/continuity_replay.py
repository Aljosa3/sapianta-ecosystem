"""Replay reconstruction for bounded runtime continuity."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.runtime.transport.runtime_store import RuntimeStore


def reconstruct_continuity_decision(runtime_id: str, root: Path | str) -> dict[str, Any]:
    store = RuntimeStore(root)
    contract = store.load_continuity_contract(runtime_id)
    retry_evaluation = store.load_retry_evaluation(runtime_id)
    result = store.load_continuity_result(runtime_id)
    ledger_entries = store.ledger.read(runtime_id)
    return {
        "status": "CONTINUITY_DECISION_RECONSTRUCTED",
        "runtime_id": runtime_id,
        "continuation_contract": contract,
        "retry_evaluation": retry_evaluation,
        "continuation_result": result,
        "ledger_entries": ledger_entries,
        "replay_chain": [
            contract["replay_hash"],
            retry_evaluation["replay_hash"],
            result["replay_hash"],
            *[entry["entry_hash"] for entry in ledger_entries],
        ],
    }
