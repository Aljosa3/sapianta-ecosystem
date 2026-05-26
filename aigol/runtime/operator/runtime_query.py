"""Read-only runtime query helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.runtime_store import RuntimeStore
from aigol.runtime.transport.serialization import load_json, verify_replay_hash

from .runtime_summary import RuntimeSummary


class RuntimeQuery:
    """Queries persisted runtime artifacts without mutating them."""

    def __init__(self, root: Path | str = ".") -> None:
        self.store = RuntimeStore(root)

    def get_runtime_summary(self, runtime_id: str) -> dict[str, Any]:
        dispatch = self.store.load_dispatch(runtime_id)
        result = self.store.load_result(runtime_id)
        self.store.ledger.read(runtime_id)
        summary = RuntimeSummary(
            runtime_id=runtime_id,
            goal_state=self._optional_state(self.store.goal_result_path(runtime_id), "goal_decision"),
            approval_state=self._optional_state(self.store.approval_result_path(runtime_id), "approval_state"),
            routing_state=self._optional_state(self.store.routing_result_path(runtime_id), "routing_decision"),
            retry_state=self._optional_state(self.store.retry_result_path(runtime_id), "retry_state"),
            continuity_state=self._optional_state(self.store.continuity_result_path(runtime_id), "continuation_decision"),
            replay_integrity_state="VERIFIED",
            created_at=result.get("closure_timestamp", dispatch.get("dispatch_timestamp", "")),
            lineage_refs=dispatch.get("lineage_refs", []),
        )
        return summary.to_dict()

    def get_goal_summary(self, goal_id: str) -> dict[str, Any]:
        if not goal_id:
            raise FailClosedRuntimeError("goal_id is required")
        goal_dir = self.store.goal_dir
        for path in sorted(goal_dir.glob("runtime_*_goal_contract.json")):
            contract = load_json(path)
            verify_replay_hash(contract)
            if contract.get("goal_id") != goal_id:
                continue
            runtime_id = contract.get("runtime_id", "")
            result = self.store.load_goal_result(runtime_id)
            sequence = self.store.load_goal_sequence(runtime_id)
            return {
                "goal_id": goal_id,
                "runtime_id": runtime_id,
                "goal_state": result.get("goal_decision", "UNKNOWN"),
                "step_count": result.get("step_count", len(sequence.get("steps", []))),
                "max_step_limit": result.get("max_step_limit", contract.get("max_step_limit", 0)),
                "replay_integrity_state": "VERIFIED",
                "replay_hash": result["replay_hash"],
            }
        raise FailClosedRuntimeError(f"goal artifact missing: {goal_id}")

    def get_retry_summary(self, runtime_id: str) -> dict[str, Any]:
        result = self.store.load_retry_result(runtime_id)
        request = self.store.load_retry_request(runtime_id)
        validation = self.store.load_retry_validation(runtime_id)
        return {
            "runtime_id": runtime_id,
            "retry_state": result.get("retry_state", "UNKNOWN"),
            "retry_count": result.get("retry_count", 0),
            "retry_scope": request.get("retry_scope", "UNKNOWN"),
            "bounded_local_only": validation.get("bounded_local_only", False),
            "replay_integrity_state": "VERIFIED",
            "replay_hash": result["replay_hash"],
        }

    def _optional_state(self, path: Path, field: str) -> str:
        if not path.exists():
            return "ABSENT"
        artifact = load_json(path)
        verify_replay_hash(artifact)
        return str(artifact.get(field, "UNKNOWN"))
