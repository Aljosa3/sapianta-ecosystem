"""Immutable bounded continuation contract."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class ContinuationContract:
    continuation_id: str
    runtime_id: str
    parent_runtime_id: str
    sandbox_id: str
    capability_request_id: str
    continuation_reason: str
    retry_count: int
    max_retry_limit: int
    governance_state: str
    lineage_refs: list[Any]
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "continuation_id": self.continuation_id,
            "runtime_id": self.runtime_id,
            "parent_runtime_id": self.parent_runtime_id,
            "sandbox_id": self.sandbox_id,
            "capability_request_id": self.capability_request_id,
            "continuation_reason": self.continuation_reason,
            "retry_count": self.retry_count,
            "max_retry_limit": self.max_retry_limit,
            "governance_state": self.governance_state,
            "lineage_refs": deepcopy(self.lineage_refs),
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact

    @classmethod
    def from_runtime_return(cls, runtime_package, governed_return) -> "ContinuationContract":
        payload = runtime_package.payload if isinstance(runtime_package.payload, dict) else {}
        continuity = payload.get("continuity", {}) if isinstance(payload.get("continuity", {}), dict) else {}
        capability_request = payload.get("capability_request", {}) if isinstance(payload.get("capability_request", {}), dict) else {}
        sandbox_id = continuity.get("sandbox_id", f"{runtime_package.runtime_id}:{runtime_package.package_id}:sandbox")
        capability = capability_request.get("capability", "")
        capability_request_id = continuity.get(
            "capability_request_id",
            f"{runtime_package.runtime_id}:{runtime_package.package_id}:{capability}" if capability else "",
        )
        contract = cls(
            continuation_id=f"{runtime_package.runtime_id}:continuity",
            runtime_id=runtime_package.runtime_id,
            parent_runtime_id=continuity.get("parent_runtime_id", runtime_package.runtime_id),
            sandbox_id=sandbox_id,
            capability_request_id=capability_request_id,
            continuation_reason=continuity.get("continuation_reason", governed_return.status),
            retry_count=continuity.get("retry_count", 0),
            max_retry_limit=continuity.get("max_retry_limit", 3),
            governance_state=runtime_package.governance_state,
            lineage_refs=deepcopy(runtime_package.lineage_refs),
            created_at=runtime_package.created_at,
        )
        replay_input = contract.to_dict()
        replay_input.pop("replay_hash", None)
        return cls(
            continuation_id=contract.continuation_id,
            runtime_id=contract.runtime_id,
            parent_runtime_id=contract.parent_runtime_id,
            sandbox_id=contract.sandbox_id,
            capability_request_id=contract.capability_request_id,
            continuation_reason=contract.continuation_reason,
            retry_count=contract.retry_count,
            max_retry_limit=contract.max_retry_limit,
            governance_state=contract.governance_state,
            lineage_refs=contract.lineage_refs,
            created_at=contract.created_at,
            replay_hash=replay_hash(replay_input),
        )
