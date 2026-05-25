"""Governance gate for provider activation."""

from __future__ import annotations

from typing import Iterable

from aigol.runtime.models import AUTHORIZED, FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash

from .provider_envelope import ProviderEnvelope, provider_boundary_guarantees


class ProviderActivationGate:
    """Validates explicit provider activation evidence before invocation."""

    def __init__(
        self,
        registered_providers: Iterable[str],
        allowed_invocation_types: Iterable[str] = ("prompt_response",),
    ) -> None:
        self.registered_providers = set(registered_providers)
        self.allowed_invocation_types = set(allowed_invocation_types)

    def validate(self, envelope: ProviderEnvelope) -> None:
        data = envelope.to_dict()
        replay_input = dict(data)
        actual_hash = replay_input.pop("replay_hash", None)
        if actual_hash != replay_hash(replay_input):
            raise FailClosedRuntimeError("provider envelope replay_hash mismatch")
        if envelope.governance_state != AUTHORIZED:
            raise FailClosedRuntimeError("provider activation requires AUTHORIZED governance_state")
        if not envelope.provider or envelope.provider not in self.registered_providers:
            raise FailClosedRuntimeError("provider must be explicitly registered")
        if envelope.invocation_type not in self.allowed_invocation_types:
            raise FailClosedRuntimeError("provider invocation_type is not allowed")
        if not envelope.runtime_id:
            raise FailClosedRuntimeError("runtime_id is required")
        if not envelope.package_id:
            raise FailClosedRuntimeError("package_id is required")
        if not envelope.provider_request_id:
            raise FailClosedRuntimeError("provider_request_id is required")
        if not isinstance(envelope.lineage_refs, list) or not envelope.lineage_refs:
            raise FailClosedRuntimeError("provider activation lineage_refs are required")
        if envelope.request_payload is None:
            raise FailClosedRuntimeError("provider request_payload is required")
        if data["boundary_guarantees"] != provider_boundary_guarantees():
            raise FailClosedRuntimeError("provider boundary guarantees are malformed")
