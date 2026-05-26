"""Replay reconstruction for controlled retry execution."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.runtime.transport.runtime_store import RuntimeStore


def reconstruct_retry_execution(runtime_id: str, root: Path | str) -> dict[str, Any]:
    store = RuntimeStore(root)
    contract = store.load_retry_contract(runtime_id)
    request = store.load_retry_request(runtime_id)
    validation = store.load_retry_validation(runtime_id)
    result = store.load_retry_result(runtime_id)
    ledger_entries = store.ledger.read(runtime_id)
    return {
        "status": "RETRY_EXECUTION_RECONSTRUCTED",
        "runtime_id": runtime_id,
        "retry_contract": contract,
        "retry_request": request,
        "retry_validation": validation,
        "retry_result": result,
        "ledger_entries": ledger_entries,
        "replay_chain": [
            contract["replay_hash"],
            request["replay_hash"],
            validation["replay_hash"],
            result["replay_hash"],
            *[entry["entry_hash"] for entry in ledger_entries],
        ],
    }
