"""Immutable approval request."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class ApprovalRequest:
    approval_request_id: str
    runtime_id: str
    requested_action: str
    risk_class: str
    approval_required: bool
    requested_by: str
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "approval_request_id": self.approval_request_id,
            "runtime_id": self.runtime_id,
            "requested_action": self.requested_action,
            "risk_class": self.risk_class,
            "approval_required": self.approval_required,
            "requested_by": self.requested_by,
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact

    @classmethod
    def from_contract(cls, contract, risk_class: str, approval_required: bool) -> "ApprovalRequest":
        request = cls(
            approval_request_id=f"{contract.approval_contract_id}:request",
            runtime_id=contract.runtime_id,
            requested_action=f"{contract.requested_capability}:{contract.execution_surface}",
            risk_class=risk_class,
            approval_required=approval_required,
            requested_by="runtime_governance",
            created_at=contract.created_at,
        )
        replay_input = request.to_dict()
        replay_input.pop("replay_hash", None)
        return cls(
            approval_request_id=request.approval_request_id,
            runtime_id=request.runtime_id,
            requested_action=request.requested_action,
            risk_class=request.risk_class,
            approval_required=request.approval_required,
            requested_by=request.requested_by,
            created_at=request.created_at,
            replay_hash=replay_hash(replay_input),
        )
