"""Sandbox context validator."""

from __future__ import annotations

from copy import deepcopy

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash

from .capability_registry import CapabilityRegistry
from .sandbox_context import SandboxContext
from .sandbox_policy import SandboxPolicy


class SandboxValidator:
    """Validates sandbox contexts before bounded execution simulation."""

    def __init__(self, policy: SandboxPolicy | None = None) -> None:
        self.policy = policy or SandboxPolicy()
        self.registry = CapabilityRegistry()

    def validate(self, context: SandboxContext) -> dict[str, object]:
        data = context.to_dict()
        replay_input = deepcopy(data)
        actual_hash = replay_input.pop("replay_hash", None)
        if actual_hash != replay_hash(replay_input):
            raise FailClosedRuntimeError("sandbox context replay_hash mismatch")
        if not context.runtime_id:
            raise FailClosedRuntimeError("sandbox runtime_id is required")
        if not context.package_id:
            raise FailClosedRuntimeError("sandbox package_id is required")
        if not context.worker_id:
            raise FailClosedRuntimeError("sandbox worker_id is required")
        if not isinstance(context.lineage_refs, list) or not context.lineage_refs:
            raise FailClosedRuntimeError("sandbox lineage_refs are required")
        for capability in context.allowed_capabilities:
            if self.registry.is_forbidden(capability):
                raise FailClosedRuntimeError(f"forbidden sandbox capability requested: {capability}")
        validation = self.policy.validate(context)
        validation["replay_hash"] = replay_hash(validation)
        return validation
