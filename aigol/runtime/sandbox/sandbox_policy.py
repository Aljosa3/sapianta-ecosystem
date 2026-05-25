"""Sandbox policy validation for bounded execution contexts."""

from __future__ import annotations

from aigol.runtime.models import FailClosedRuntimeError

from .capability_registry import CapabilityRegistry
from .sandbox_context import ALLOWED_EXECUTION_MODES, SandboxContext


class SandboxPolicy:
    """Deterministic fail-closed sandbox policy layer."""

    def __init__(self, registry: CapabilityRegistry | None = None) -> None:
        self.registry = registry or CapabilityRegistry()

    def validate(self, context: SandboxContext) -> dict[str, object]:
        if context.execution_mode not in ALLOWED_EXECUTION_MODES:
            raise FailClosedRuntimeError("sandbox execution_mode is not allowed")
        self._validate_capabilities(context.allowed_capabilities, "allowed_capabilities")
        self._validate_denied_capabilities(context.denied_capabilities)
        self._validate_resource_limits(context.resource_limits)
        if not isinstance(context.execution_ttl_seconds, int) or context.execution_ttl_seconds <= 0:
            raise FailClosedRuntimeError("sandbox execution_ttl_seconds must be positive")
        if context.resource_limits["max_runtime_seconds"] > context.execution_ttl_seconds:
            raise FailClosedRuntimeError("sandbox max_runtime_seconds exceeds execution_ttl_seconds")
        return {
            "status": "SANDBOX_VALIDATED",
            "sandbox_id": context.sandbox_id,
            "runtime_id": context.runtime_id,
            "allowed_capabilities": sorted(context.allowed_capabilities),
            "denied_capabilities": sorted(context.denied_capabilities),
            "execution_mode": context.execution_mode,
        }

    def _validate_capabilities(self, capabilities: object, field_name: str) -> None:
        if not isinstance(capabilities, list) or not capabilities:
            raise FailClosedRuntimeError(f"sandbox {field_name} must be a non-empty list")
        if "*" in capabilities:
            raise FailClosedRuntimeError("sandbox wildcard capabilities are not allowed")
        for capability in capabilities:
            if not isinstance(capability, str) or not capability:
                raise FailClosedRuntimeError(f"sandbox {field_name} must contain strings")
            self.registry.validate_known(capability)

    def _validate_denied_capabilities(self, capabilities: object) -> None:
        if not isinstance(capabilities, list):
            raise FailClosedRuntimeError("sandbox denied_capabilities must be a list")
        if "*" in capabilities:
            raise FailClosedRuntimeError("sandbox wildcard deny capabilities are not allowed")
        for capability in capabilities:
            if not isinstance(capability, str) or not capability:
                raise FailClosedRuntimeError("sandbox denied_capabilities must contain strings")
            if not self.registry.is_forbidden(capability) and not self.registry.is_supported(capability):
                raise FailClosedRuntimeError(f"unknown sandbox denied capability: {capability}")

    def _validate_resource_limits(self, resource_limits: object) -> None:
        if not isinstance(resource_limits, dict):
            raise FailClosedRuntimeError("sandbox resource_limits must be an object")
        for field_name in ("max_memory_mb", "max_runtime_seconds"):
            value = resource_limits.get(field_name)
            if not isinstance(value, int) or value <= 0:
                raise FailClosedRuntimeError(f"sandbox {field_name} must be positive")
