"""Deterministic models for governed bounded capability memory."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CapabilityStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class CapabilityDecision(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"


@dataclass(frozen=True)
class CapabilityScope:
    host: str
    port: int
    runtime: str
    lifecycle: tuple[str, ...]
    temporary: bool
    visual_validation: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "host": self.host,
            "lifecycle": list(self.lifecycle),
            "port": self.port,
            "runtime": self.runtime,
            "temporary": self.temporary,
            "visual_validation": self.visual_validation,
        }


@dataclass(frozen=True)
class GovernedCapability:
    capability_id: str
    status: CapabilityStatus
    allowed_scope: CapabilityScope
    forbidden_scope: tuple[str, ...]
    approval_semantics: tuple[str, ...]
    replay_visibility: tuple[str, ...]
    revocation_semantics: tuple[str, ...]
    escalation_conditions: tuple[str, ...]
    lineage_references: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed_scope": self.allowed_scope.to_dict(),
            "approval_semantics": list(self.approval_semantics),
            "capability_id": self.capability_id,
            "escalation_conditions": list(self.escalation_conditions),
            "forbidden_scope": list(self.forbidden_scope),
            "lineage_references": list(self.lineage_references),
            "replay_visibility": list(self.replay_visibility),
            "revocation_semantics": list(self.revocation_semantics),
            "status": self.status.value,
        }


@dataclass(frozen=True)
class CapabilityEvaluation:
    capability_id: str
    decision: CapabilityDecision
    reason: str
    replay_visible: bool
    scope_locked: bool
    escalation_required: bool
    deterministic_hash: str

    def to_dict(self, include_hash: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "capability_id": self.capability_id,
            "decision": self.decision.value,
            "escalation_required": self.escalation_required,
            "reason": self.reason,
            "replay_visible": self.replay_visible,
            "scope_locked": self.scope_locked,
        }
        if include_hash:
            data["deterministic_hash"] = self.deterministic_hash
        return data

