"""Read-only runtime inspector."""

from __future__ import annotations

from aigol.runtime.transport.runtime_store import RuntimeStore

from .capability_inspector import CapabilityInspector
from .continuity_inspector import ContinuityInspector
from .lineage_inspector import LineageInspector
from .policy_inspector import PolicyInspector
from .runtime_snapshot import RuntimeSnapshot


class RuntimeInspector:
    """Inspects persisted runtime evidence without mutating it."""

    def __init__(self, store: RuntimeStore) -> None:
        self.store = store

    def inspect(self, runtime_id: str) -> dict:
        dispatch = self.store.load_dispatch(runtime_id)
        result = self.store.load_result(runtime_id)
        snapshot = RuntimeSnapshot.from_artifacts(runtime_id, dispatch, result, self.store)
        inspection = {
            "status": "RUNTIME_INSPECTED",
            "runtime_id": runtime_id,
            "snapshot": snapshot.to_dict(),
            "dispatch": dispatch,
            "result": result,
            "lineage": LineageInspector(self.store).inspect(runtime_id),
        }
        if self.store.capability_result_path(runtime_id).exists():
            inspection["capability"] = CapabilityInspector(self.store).inspect(runtime_id)
        if self.store.policy_result_path(runtime_id).exists():
            inspection["policy"] = PolicyInspector(self.store).inspect(runtime_id)
        if self.store.continuity_result_path(runtime_id).exists():
            inspection["continuity"] = ContinuityInspector(self.store).inspect(runtime_id)
        return inspection
