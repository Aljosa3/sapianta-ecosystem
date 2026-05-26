"""Immutable approval result."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class ApprovalResult:
    approval_result_id: str
    runtime_id: str
    approval_state: str
    approval_reason: str
    risk_class: str
    execution_allowed: bool
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "approval_result_id": self.approval_result_id,
            "runtime_id": self.runtime_id,
            "approval_state": self.approval_state,
            "approval_reason": self.approval_reason,
            "risk_class": self.risk_class,
            "execution_allowed": self.execution_allowed,
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact
