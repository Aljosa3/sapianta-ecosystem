"""Read-only continuity inspection."""

from __future__ import annotations

from aigol.runtime.transport.runtime_store import RuntimeStore


class ContinuityInspector:
    def __init__(self, store: RuntimeStore) -> None:
        self.store = store

    def inspect(self, runtime_id: str) -> dict:
        contract = self.store.load_continuity_contract(runtime_id)
        retry = self.store.load_retry_evaluation(runtime_id)
        result = self.store.load_continuity_result(runtime_id)
        return {
            "status": "CONTINUITY_INSPECTED",
            "runtime_id": runtime_id,
            "continuation_contract": contract,
            "retry_evaluation": retry,
            "continuation_result": result,
            "retry_count": contract.get("retry_count"),
            "max_retry_limit": contract.get("max_retry_limit"),
            "continuation_decision": result.get("continuation_decision"),
        }
