"""Read-only lineage inspection."""

from __future__ import annotations

from aigol.runtime.continuity.continuity_replay import reconstruct_continuity_decision
from aigol.runtime.transport.replay import reconstruct_capability_execution, reconstruct_runtime_lineage
from aigol.runtime.transport.runtime_store import RuntimeStore


class LineageInspector:
    def __init__(self, store: RuntimeStore) -> None:
        self.store = store

    def inspect(self, runtime_id: str) -> dict:
        runtime = reconstruct_runtime_lineage(runtime_id, self.store.root)
        continuity = reconstruct_continuity_decision(runtime_id, self.store.root)
        capability = None
        if self.store.capability_result_path(runtime_id).exists():
            capability = reconstruct_capability_execution(runtime_id, self.store.root)
        return {
            "status": "LINEAGE_INSPECTED",
            "runtime_id": runtime_id,
            "runtime_lineage": runtime,
            "continuity_lineage": continuity,
            "capability_lineage": capability,
            "ledger_entries": self.store.ledger.read(runtime_id),
        }
