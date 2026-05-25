"""Immutable runtime policy registry."""

from __future__ import annotations

from aigol.runtime.models import FailClosedRuntimeError


POLICY_SCOPES = {
    "READ_ONLY": frozenset({"read_text", "inspect_json", "analyze_text"}),
    "ANALYSIS_ONLY": frozenset({"inspect_json", "analyze_text"}),
    "PREVIEW_ONLY": frozenset({"mock_write_preview", "inspect_json", "analyze_text"}),
}
FORBIDDEN_POLICY_CLASSES = frozenset(
    {
        "SHELL_EXECUTION",
        "FILESYSTEM_WRITE",
        "SUBPROCESS_EXECUTION",
        "WORKER_SPAWN",
        "NETWORK_MUTATION",
        "RECURSIVE_DISPATCH",
    }
)
FORBIDDEN_CAPABILITIES = frozenset(
    {
        "shell_execution",
        "filesystem_write",
        "subprocess_spawn",
        "worker_spawn",
        "unrestricted_network",
        "recursive_dispatch",
        "delete_file",
        "orchestration",
    }
)


class PolicyRegistry:
    """Deterministic explicit allowlist for runtime policy scopes."""

    def capabilities_for_scope(self, policy_scope: str) -> list[str]:
        if policy_scope in FORBIDDEN_POLICY_CLASSES:
            raise FailClosedRuntimeError(f"forbidden policy scope requested: {policy_scope}")
        if policy_scope not in POLICY_SCOPES:
            raise FailClosedRuntimeError(f"unknown policy scope requested: {policy_scope}")
        return sorted(POLICY_SCOPES[policy_scope])

    def is_capability_forbidden(self, capability: str) -> bool:
        return capability in FORBIDDEN_CAPABILITIES

    def scopes(self) -> list[str]:
        return sorted(POLICY_SCOPES)

    def forbidden_scopes(self) -> list[str]:
        return sorted(FORBIDDEN_POLICY_CLASSES)

    def forbidden_capabilities(self) -> list[str]:
        return sorted(FORBIDDEN_CAPABILITIES)
