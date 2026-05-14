"""Replay-safe provider capability declaration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .capability_model import modality_for_capability


@dataclass(frozen=True)
class CapabilityDeclaration:
    provider_id: str
    capability_class: str
    modality_class: str
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    replay_safe: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "capability_class": self.capability_class,
            "modality_class": self.modality_class,
            "evidence_refs": list(self.evidence_refs),
            "replay_safe": self.replay_safe,
            "execution_authority_granted": False,
            "envelope_bypass_allowed": False,
            "provider_abstraction_bypass_allowed": False,
            "routing_enabled": False,
            "orchestration_enabled": False,
            "autonomous_provider_selection_enabled": False,
        }


def create_capability_declaration(
    *,
    provider_id: str,
    capability_class: str,
    modality_class: str | None = None,
    evidence_refs: list[str] | None = None,
) -> CapabilityDeclaration:
    return CapabilityDeclaration(
        provider_id=provider_id,
        capability_class=capability_class,
        modality_class=modality_class or modality_for_capability(capability_class),
        evidence_refs=tuple(sorted(evidence_refs or ())),
    )
