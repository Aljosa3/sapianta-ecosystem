"""Deterministic approval registry."""

from __future__ import annotations

from aigol.runtime.models import FailClosedRuntimeError


APPROVAL_SCOPES = {
    "READ_ONLY_AUTO_ALLOWED": "LOW_RISK",
    "HUMAN_APPROVAL_REQUIRED": "HIGH_RISK",
    "RESTRICTED_BLOCKED": "RESTRICTED",
}
RISK_CLASSES = frozenset({"LOW_RISK", "MODERATE_RISK", "HIGH_RISK", "RESTRICTED"})


class ApprovalRegistry:
    """Immutable explicit approval registry."""

    def risk_for_scope(self, approval_scope: str) -> str:
        if approval_scope not in APPROVAL_SCOPES:
            raise FailClosedRuntimeError("unknown approval scope")
        return APPROVAL_SCOPES[approval_scope]

    def validate_risk(self, risk_class: str) -> None:
        if risk_class not in RISK_CLASSES:
            raise FailClosedRuntimeError("unknown approval risk class")

    def scopes(self) -> list[str]:
        return sorted(APPROVAL_SCOPES)
