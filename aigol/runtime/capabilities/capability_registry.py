"""Immutable governed capability registry."""

from __future__ import annotations

from aigol.runtime.models import FailClosedRuntimeError


ALLOWED_CAPABILITIES = frozenset({"read_text", "inspect_json", "analyze_text", "mock_write_preview"})
FORBIDDEN_CAPABILITIES = frozenset(
    {
        "shell_execution",
        "subprocess_spawn",
        "filesystem_write",
        "unrestricted_network",
        "delete_file",
        "worker_spawn",
        "recursive_dispatch",
        "orchestration",
    }
)


class CapabilityRegistry:
    """Deterministic explicit allowlist for capability execution."""

    def validate(self, capability: str) -> None:
        if capability in FORBIDDEN_CAPABILITIES:
            raise FailClosedRuntimeError(f"forbidden capability requested: {capability}")
        if capability not in ALLOWED_CAPABILITIES:
            raise FailClosedRuntimeError(f"unknown capability requested: {capability}")

    def is_allowed(self, capability: str) -> bool:
        return capability in ALLOWED_CAPABILITIES

    def is_forbidden(self, capability: str) -> bool:
        return capability in FORBIDDEN_CAPABILITIES

    def allowed(self) -> list[str]:
        return sorted(ALLOWED_CAPABILITIES)

    def forbidden(self) -> list[str]:
        return sorted(FORBIDDEN_CAPABILITIES)
