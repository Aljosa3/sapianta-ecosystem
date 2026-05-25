"""Policy replay reconstruction helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.runtime.transport.runtime_store import RuntimeStore


def reconstruct_policy_decision(runtime_id: str, root: Path | str) -> dict[str, Any]:
    store = RuntimeStore(root)
    contract = store.load_policy_contract(runtime_id)
    validation = store.load_policy_validation(runtime_id)
    result = store.load_policy_result(runtime_id)
    ledger_entries = store.ledger.read(runtime_id)
    return {
        "status": "POLICY_DECISION_RECONSTRUCTED",
        "runtime_id": runtime_id,
        "policy_contract": contract,
        "policy_validation": validation,
        "policy_result": result,
        "ledger_entries": ledger_entries,
        "replay_chain": [
            contract["replay_hash"],
            validation["replay_hash"],
            result["replay_hash"],
            *[entry["entry_hash"] for entry in ledger_entries],
        ],
    }
