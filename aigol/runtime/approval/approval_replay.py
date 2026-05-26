"""Replay reconstruction for human governance checkpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.runtime.transport.runtime_store import RuntimeStore


def reconstruct_approval_decision(runtime_id: str, root: Path | str) -> dict[str, Any]:
    store = RuntimeStore(root)
    contract = store.load_approval_contract(runtime_id)
    request = store.load_approval_request(runtime_id)
    validation = store.load_approval_validation(runtime_id)
    result = store.load_approval_result(runtime_id)
    ledger_entries = store.ledger.read(runtime_id)
    return {
        "status": "APPROVAL_DECISION_RECONSTRUCTED",
        "runtime_id": runtime_id,
        "approval_contract": contract,
        "approval_request": request,
        "approval_validation": validation,
        "approval_result": result,
        "ledger_entries": ledger_entries,
        "replay_chain": [
            contract["replay_hash"],
            request["replay_hash"],
            validation["replay_hash"],
            result["replay_hash"],
            *[entry["entry_hash"] for entry in ledger_entries],
        ],
    }
