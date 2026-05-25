"""Capability request validator."""

from __future__ import annotations

from copy import deepcopy

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.sandbox import SandboxValidator
from aigol.runtime.transport.serialization import replay_hash

from .capability_policy import CapabilityPolicy
from .capability_request import CapabilityRequest


class CapabilityValidator:
    """Validates governed capability requests against sandbox context."""

    def __init__(self, policy: CapabilityPolicy | None = None) -> None:
        self.policy = policy or CapabilityPolicy()

    def validate(self, request: CapabilityRequest, sandbox_context) -> dict[str, object]:
        data = request.to_dict()
        replay_input = deepcopy(data)
        actual_hash = replay_input.pop("replay_hash", None)
        if actual_hash != replay_hash(replay_input):
            raise FailClosedRuntimeError("capability request replay_hash mismatch")
        SandboxValidator().validate(sandbox_context)
        validation = self.policy.validate(request, sandbox_context)
        validation["replay_hash"] = replay_hash(validation)
        return validation
