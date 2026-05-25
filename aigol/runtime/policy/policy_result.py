"""Deterministic runtime policy result."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class PolicyResult:
    policy_result_id: str
    runtime_id: str
    capability_request_id: str
    decision: str
    decision_reason: str
    allowed_capabilities: list[str]
    denied_capabilities: list[str]
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "policy_result_id": self.policy_result_id,
            "runtime_id": self.runtime_id,
            "capability_request_id": self.capability_request_id,
            "decision": self.decision,
            "decision_reason": self.decision_reason,
            "allowed_capabilities": deepcopy(self.allowed_capabilities),
            "denied_capabilities": deepcopy(self.denied_capabilities),
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact
