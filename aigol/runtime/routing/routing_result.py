"""Immutable routing result."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class RoutingResult:
    routing_result_id: str
    runtime_id: str
    requested_capability: str
    routing_decision: str
    execution_surface: str
    approval_required: bool
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "routing_result_id": self.routing_result_id,
            "runtime_id": self.runtime_id,
            "requested_capability": self.requested_capability,
            "routing_decision": self.routing_decision,
            "execution_surface": self.execution_surface,
            "approval_required": self.approval_required,
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact
