"""Immutable retry execution contract."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class RetryContract:
    retry_contract_id: str
    runtime_id: str
    parent_runtime_id: str
    goal_id: str
    retry_reason: str
    retry_count: int
    max_retry_limit: int
    governance_state: str
    lineage_refs: list[Any]
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "retry_contract_id": self.retry_contract_id,
            "runtime_id": self.runtime_id,
            "parent_runtime_id": self.parent_runtime_id,
            "goal_id": self.goal_id,
            "retry_reason": self.retry_reason,
            "retry_count": self.retry_count,
            "max_retry_limit": self.max_retry_limit,
            "governance_state": self.governance_state,
            "lineage_refs": deepcopy(self.lineage_refs),
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact

    @classmethod
    def from_runtime_package(cls, runtime_package, continuation_result=None) -> "RetryContract":
        payload = runtime_package.payload if isinstance(runtime_package.payload, dict) else {}
        retry = payload.get("retry", {}) if isinstance(payload.get("retry", {}), dict) else {}
        continuity = payload.get("continuity", {}) if isinstance(payload.get("continuity", {}), dict) else {}
        retry_reason = retry.get("retry_reason", continuity.get("continuation_reason", "continuity_evaluated"))
        if continuation_result is not None and not getattr(continuation_result, "retry_allowed", False):
            retry_reason = "retry_not_allowed_by_continuity"
        contract = cls(
            retry_contract_id=f"{runtime_package.runtime_id}:retry",
            runtime_id=runtime_package.runtime_id,
            parent_runtime_id=retry.get("parent_runtime_id", continuity.get("parent_runtime_id", runtime_package.runtime_id)),
            goal_id=retry.get("goal_id", payload.get("goal_id", "")),
            retry_reason=retry_reason,
            retry_count=retry.get("retry_count", continuity.get("retry_count", 0)),
            max_retry_limit=retry.get("max_retry_limit", continuity.get("max_retry_limit", 3)),
            governance_state=runtime_package.governance_state,
            lineage_refs=deepcopy(runtime_package.lineage_refs),
            created_at=runtime_package.created_at,
        )
        replay_input = contract.to_dict()
        replay_input.pop("replay_hash", None)
        return cls(
            retry_contract_id=contract.retry_contract_id,
            runtime_id=contract.runtime_id,
            parent_runtime_id=contract.parent_runtime_id,
            goal_id=contract.goal_id,
            retry_reason=contract.retry_reason,
            retry_count=contract.retry_count,
            max_retry_limit=contract.max_retry_limit,
            governance_state=contract.governance_state,
            lineage_refs=contract.lineage_refs,
            created_at=contract.created_at,
            replay_hash=replay_hash(replay_input),
        )
