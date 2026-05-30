"""Minimal provider adapter contract for AiGOL."""

from __future__ import annotations

from typing import Any, Protocol

from aigol.provider.provider_proposal_envelope import ProviderProposalEnvelope


class ProviderAdapter(Protocol):
    provider_id: str
    provider_version: str

    def generate_proposal(self, request: Any, *, proposal_id: str, timestamp: str) -> ProviderProposalEnvelope:
        """Return a ProviderProposalEnvelope and nothing authoritative."""

