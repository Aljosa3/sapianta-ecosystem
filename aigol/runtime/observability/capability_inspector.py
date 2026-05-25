"""Read-only capability inspection."""

from __future__ import annotations

from aigol.runtime.transport.runtime_store import RuntimeStore


class CapabilityInspector:
    def __init__(self, store: RuntimeStore) -> None:
        self.store = store

    def inspect(self, runtime_id: str) -> dict:
        request = self.store.load_capability_request(runtime_id)
        validation = self.store.load_capability_validation(runtime_id)
        result = self.store.load_capability_result(runtime_id)
        return {
            "status": "CAPABILITY_INSPECTED",
            "runtime_id": runtime_id,
            "capability_request": request,
            "capability_validation": validation,
            "capability_result": result,
            "sandbox_id": request.get("sandbox_id"),
            "execution_summary": result.get("execution_summary"),
        }
