"""Immutable capability route."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from aigol.runtime.transport.serialization import replay_hash


@dataclass(frozen=True)
class CapabilityRoute:
    route_id: str
    capability_name: str
    capability_class: str
    sandbox_profile: dict[str, Any]
    policy_scope: str
    execution_surface: str
    approval_required: bool
    lineage_refs: list[Any]
    created_at: str
    replay_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        artifact = {
            "route_id": self.route_id,
            "capability_name": self.capability_name,
            "capability_class": self.capability_class,
            "sandbox_profile": deepcopy(self.sandbox_profile),
            "policy_scope": self.policy_scope,
            "execution_surface": self.execution_surface,
            "approval_required": self.approval_required,
            "lineage_refs": deepcopy(self.lineage_refs),
            "created_at": self.created_at,
        }
        artifact["replay_hash"] = self.replay_hash or replay_hash(artifact)
        return artifact
