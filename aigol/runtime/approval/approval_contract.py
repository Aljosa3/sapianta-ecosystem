"""Immutable approval contract."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class ApprovalContract:
    approval_contract_id: str
    runtime_id: str
    goal_id: str
    requested_capability: str
    execution_surface: str
    approval_scope: str
    governance_state: str
    lineage_refs: list[Any]
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "approval_contract_id": self.approval_contract_id,
            "runtime_id": self.runtime_id,
            "goal_id": self.goal_id,
            "requested_capability": self.requested_capability,
            "execution_surface": self.execution_surface,
            "approval_scope": self.approval_scope,
            "governance_state": self.governance_state,
            "lineage_refs": deepcopy(self.lineage_refs),
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact

    @classmethod
    def from_routing(cls, routing_contract, route) -> "ApprovalContract":
        approval_scope = "HUMAN_APPROVAL_REQUIRED" if route.approval_required else "READ_ONLY_AUTO_ALLOWED"
        if route.capability_class == "RESTRICTED":
            approval_scope = "RESTRICTED_BLOCKED"
        contract = cls(
            approval_contract_id=f"{routing_contract.runtime_id}:{routing_contract.requested_capability}:approval",
            runtime_id=routing_contract.runtime_id,
            goal_id=routing_contract.goal_id,
            requested_capability=routing_contract.requested_capability,
            execution_surface=route.execution_surface,
            approval_scope=approval_scope,
            governance_state=routing_contract.governance_state,
            lineage_refs=deepcopy(routing_contract.lineage_refs),
            created_at=routing_contract.created_at,
        )
        replay_input = contract.to_dict()
        replay_input.pop("replay_hash", None)
        return cls(
            approval_contract_id=contract.approval_contract_id,
            runtime_id=contract.runtime_id,
            goal_id=contract.goal_id,
            requested_capability=contract.requested_capability,
            execution_surface=contract.execution_surface,
            approval_scope=contract.approval_scope,
            governance_state=contract.governance_state,
            lineage_refs=contract.lineage_refs,
            created_at=contract.created_at,
            replay_hash=replay_hash(replay_input),
        )
