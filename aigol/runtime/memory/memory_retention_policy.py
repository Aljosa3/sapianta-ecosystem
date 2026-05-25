"""Deterministic bounded memory retention policy."""

from __future__ import annotations

from aigol.runtime.models import FailClosedRuntimeError


RETENTION_CLASSES = {
    "TRANSIENT": {"expires_after_runtime": True, "bounded": True},
    "SESSION": {"expires_after_session": True, "bounded": True},
    "GOVERNED_PERSISTENT": {"requires_governance": True, "bounded": True},
}


class MemoryRetentionPolicy:
    """Validates bounded memory retention classes."""

    def validate(self, retention_policy: str) -> dict[str, object]:
        if retention_policy not in RETENTION_CLASSES:
            raise FailClosedRuntimeError("memory retention_policy is invalid")
        decision = {
            "retention_policy": retention_policy,
            "retention_class": retention_policy,
            "bounded": True,
            "unlimited_retention": False,
        }
        decision.update(RETENTION_CLASSES[retention_policy])
        return decision

    def allowed(self) -> list[str]:
        return sorted(RETENTION_CLASSES)
