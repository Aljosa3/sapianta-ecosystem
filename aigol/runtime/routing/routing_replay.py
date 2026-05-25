"""Replay reconstruction for capability routing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.runtime.transport.runtime_store import RuntimeStore


def reconstruct_routing_decision(runtime_id: str, root: Path | str) -> dict[str, Any]:
    store = RuntimeStore(root)
    contract = store.load_routing_contract(runtime_id)
    route = store.load_capability_route(runtime_id)
    validation = store.load_routing_validation(runtime_id)
    result = store.load_routing_result(runtime_id)
    ledger_entries = store.ledger.read(runtime_id)
    return {
        "status": "ROUTING_DECISION_RECONSTRUCTED",
        "runtime_id": runtime_id,
        "routing_contract": contract,
        "capability_route": route,
        "routing_validation": validation,
        "routing_result": result,
        "ledger_entries": ledger_entries,
        "replay_chain": [
            contract["replay_hash"],
            route["replay_hash"],
            validation["replay_hash"],
            result["replay_hash"],
            *[entry["entry_hash"] for entry in ledger_entries],
        ],
    }
