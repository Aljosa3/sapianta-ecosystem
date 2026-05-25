"""Governed capability policy."""

from __future__ import annotations

from aigol.runtime.models import AUTHORIZED, FailClosedRuntimeError

from .capability_registry import CapabilityRegistry
from .capability_request import CapabilityRequest, capability_boundary_guarantees


class CapabilityPolicy:
    """Deterministic fail-closed capability policy."""

    def __init__(self, registry: CapabilityRegistry | None = None) -> None:
        self.registry = registry or CapabilityRegistry()

    def validate(self, request: CapabilityRequest, sandbox_context) -> dict[str, object]:
        if request.governance_state != AUTHORIZED:
            raise FailClosedRuntimeError("capability execution requires AUTHORIZED governance_state")
        if not request.runtime_id or not request.package_id or not request.worker_id:
            raise FailClosedRuntimeError("capability request runtime identifiers are required")
        if not request.sandbox_id or request.sandbox_id != sandbox_context.sandbox_id:
            raise FailClosedRuntimeError("capability request sandbox mismatch")
        if not request.target:
            raise FailClosedRuntimeError("capability target is required")
        if not isinstance(request.lineage_refs, list) or not request.lineage_refs:
            raise FailClosedRuntimeError("capability lineage_refs are required")
        if request.boundary_guarantees != capability_boundary_guarantees():
            raise FailClosedRuntimeError("capability boundary guarantees are malformed")
        self.registry.validate(request.capability)
        if request.capability not in sandbox_context.allowed_capabilities:
            raise FailClosedRuntimeError("sandbox does not allow requested capability")
        if request.capability in sandbox_context.denied_capabilities:
            raise FailClosedRuntimeError("sandbox denies requested capability")
        if "*" in sandbox_context.allowed_capabilities:
            raise FailClosedRuntimeError("sandbox wildcard capability is not allowed")
        return {
            "status": "CAPABILITY_VALIDATED",
            "capability_request_id": request.capability_request_id,
            "runtime_id": request.runtime_id,
            "sandbox_id": request.sandbox_id,
            "capability": request.capability,
        }
