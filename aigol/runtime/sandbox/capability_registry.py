"""Deterministic sandbox capability registry."""

from __future__ import annotations

from aigol.runtime.models import FailClosedRuntimeError


SUPPORTED_CAPABILITIES = frozenset({"read_text", "analyze_text", "inspect_json", "mock_execute"})
FORBIDDEN_CAPABILITIES = frozenset(
    {
        "shell_execution",
        "subprocess_spawn",
        "filesystem_write",
        "unrestricted_network",
        "worker_spawn",
        "recursive_dispatch",
    }
)


class CapabilityRegistry:
    """Explicit allowlist registry for bounded sandbox capabilities."""

    def is_supported(self, capability: str) -> bool:
        return capability in SUPPORTED_CAPABILITIES

    def is_forbidden(self, capability: str) -> bool:
        return capability in FORBIDDEN_CAPABILITIES

    def validate_known(self, capability: str) -> None:
        if self.is_forbidden(capability):
            raise FailClosedRuntimeError(f"forbidden sandbox capability requested: {capability}")
        if not self.is_supported(capability):
            raise FailClosedRuntimeError(f"unknown sandbox capability requested: {capability}")

    def supported_capabilities(self) -> list[str]:
        return sorted(SUPPORTED_CAPABILITIES)

    def forbidden_capabilities(self) -> list[str]:
        return sorted(FORBIDDEN_CAPABILITIES)
