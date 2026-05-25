"""Bounded retry policy for runtime continuity."""

from __future__ import annotations

from aigol.runtime.models import FailClosedRuntimeError


DEFAULT_MAX_RETRY = 3
RETRY_ALLOWED = "RETRY_ALLOWED"
RETRY_DENIED = "RETRY_DENIED"
CONTINUATION_BLOCKED = "CONTINUATION_BLOCKED"


class RetryPolicy:
    """Deterministic bounded retry policy."""

    def evaluate(self, contract) -> dict[str, object]:
        if not isinstance(contract.retry_count, int) or contract.retry_count < 0:
            raise FailClosedRuntimeError("retry_count must be a non-negative integer")
        if not isinstance(contract.max_retry_limit, int) or contract.max_retry_limit <= 0:
            raise FailClosedRuntimeError("max_retry_limit must be positive")
        if contract.retry_count > contract.max_retry_limit:
            raise FailClosedRuntimeError("retry limit exceeded")
        if contract.max_retry_limit > DEFAULT_MAX_RETRY:
            raise FailClosedRuntimeError("max_retry_limit exceeds default bounded maximum")
        if contract.continuation_reason in {"retry_requested", "failure_retry"} and contract.retry_count < contract.max_retry_limit:
            return {
                "retry_class": RETRY_ALLOWED,
                "retry_allowed": True,
                "decision_reason": "bounded retry allowed by explicit continuation reason",
            }
        return {
            "retry_class": RETRY_DENIED,
            "retry_allowed": False,
            "decision_reason": "continuation did not request bounded retry or retry limit reached",
        }
