"""Deterministic routing registry."""

from __future__ import annotations

from copy import deepcopy

from aigol.runtime.models import FailClosedRuntimeError


ROUTES = {
    "read_text": {
        "capability_class": "READ_ONLY",
        "execution_surface": "LOCAL_READ",
        "policy_scope": "READ_ONLY",
        "sandbox_profile": {"execution_mode": "READ_ONLY", "required_capabilities": ["read_text"]},
        "approval_required": False,
    },
    "inspect_json": {
        "capability_class": "ANALYSIS",
        "execution_surface": "SANDBOX_ONLY",
        "policy_scope": "ANALYSIS_ONLY",
        "sandbox_profile": {"execution_mode": "ANALYSIS_ONLY", "required_capabilities": ["inspect_json"]},
        "approval_required": False,
    },
    "analyze_text": {
        "capability_class": "ANALYSIS",
        "execution_surface": "SANDBOX_ONLY",
        "policy_scope": "ANALYSIS_ONLY",
        "sandbox_profile": {"execution_mode": "ANALYSIS_ONLY", "required_capabilities": ["analyze_text"]},
        "approval_required": False,
    },
    "mock_write_preview": {
        "capability_class": "PREVIEW",
        "execution_surface": "HUMAN_APPROVAL_REQUIRED",
        "policy_scope": "PREVIEW_ONLY",
        "sandbox_profile": {"execution_mode": "MOCK_EXECUTION", "required_capabilities": ["mock_write_preview"]},
        "approval_required": True,
    },
}
CAPABILITY_CLASSES = frozenset({"READ_ONLY", "ANALYSIS", "PREVIEW", "RESTRICTED"})
EXECUTION_SURFACES = frozenset({"LOCAL_READ", "SANDBOX_ONLY", "GOVERNED_PROVIDER", "HUMAN_APPROVAL_REQUIRED"})


class RoutingRegistry:
    """Immutable explicit capability routing registry."""

    def get(self, capability: str) -> dict:
        if capability not in ROUTES:
            raise FailClosedRuntimeError(f"unknown routable capability: {capability}")
        return deepcopy(ROUTES[capability])

    def validate_surface(self, execution_surface: str) -> None:
        if execution_surface not in EXECUTION_SURFACES:
            raise FailClosedRuntimeError("routing execution_surface is invalid")

    def capabilities(self) -> list[str]:
        return sorted(ROUTES)
