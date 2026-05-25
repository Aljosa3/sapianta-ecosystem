"""Immutable routing contract."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class RoutingContract:
    routing_contract_id: str
    runtime_id: str
    goal_id: str
    requested_capability: str
    requested_target: str
    governance_state: str
    lineage_refs: list[Any]
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "routing_contract_id": self.routing_contract_id,
            "runtime_id": self.runtime_id,
            "goal_id": self.goal_id,
            "requested_capability": self.requested_capability,
            "requested_target": self.requested_target,
            "governance_state": self.governance_state,
            "lineage_refs": deepcopy(self.lineage_refs),
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact

    @classmethod
    def from_runtime_package(cls, runtime_package, capability_request: dict[str, Any]) -> "RoutingContract":
        goal_id = ""
        if isinstance(runtime_package.payload, dict) and isinstance(runtime_package.payload.get("goal_sequence"), dict):
            goal_id = runtime_package.payload["goal_sequence"].get("goal_id", "")
        contract = cls(
            routing_contract_id=f"{runtime_package.runtime_id}:{capability_request.get('capability', '')}:routing",
            runtime_id=runtime_package.runtime_id,
            goal_id=goal_id,
            requested_capability=capability_request.get("capability", ""),
            requested_target=capability_request.get("target", ""),
            governance_state=runtime_package.governance_state,
            lineage_refs=deepcopy(runtime_package.lineage_refs),
            created_at=runtime_package.created_at,
        )
        replay_input = contract.to_dict()
        replay_input.pop("replay_hash", None)
        return cls(
            routing_contract_id=contract.routing_contract_id,
            runtime_id=contract.runtime_id,
            goal_id=contract.goal_id,
            requested_capability=contract.requested_capability,
            requested_target=contract.requested_target,
            governance_state=contract.governance_state,
            lineage_refs=contract.lineage_refs,
            created_at=contract.created_at,
            replay_hash=replay_hash(replay_input),
        )
