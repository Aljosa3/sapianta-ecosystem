"""Deterministic controlled retry policy."""

from __future__ import annotations

from aigol.runtime.models import FailClosedRuntimeError


DEFAULT_MAX_RETRY = 3


class RetryPolicy:
    """Evaluates bounded retry execution eligibility."""

    def evaluate(self, contract, approval_state: str = "APPROVED") -> dict[str, object]:
        if not isinstance(contract.retry_count, int) or contract.retry_count < 0:
            raise FailClosedRuntimeError("retry_count must be a non-negative integer")
        if not isinstance(contract.max_retry_limit, int) or contract.max_retry_limit <= 0:
            raise FailClosedRuntimeError("max_retry_limit must be positive")
        if contract.max_retry_limit > DEFAULT_MAX_RETRY:
            raise FailClosedRuntimeError("max_retry_limit exceeds default bounded maximum")
        if contract.retry_count > contract.max_retry_limit:
            raise FailClosedRuntimeError("retry limit exceeded")
        if approval_state != "APPROVED":
            return {
                "retry_allowed": False,
                "retry_scope": "APPROVAL_BLOCKED",
                "decision_reason": "retry blocked by approval boundary",
            }
        if contract.retry_count >= contract.max_retry_limit:
            return {
                "retry_allowed": False,
                "retry_scope": "LIMIT_REACHED",
                "decision_reason": "retry limit reached",
            }
        if contract.retry_reason in {"retry_requested", "failure_retry"}:
            return {
                "retry_allowed": True,
                "retry_scope": "BOUNDED_LOCAL_RETRY",
                "decision_reason": "bounded governed retry execution eligible",
            }
        return {
            "retry_allowed": False,
            "retry_scope": "NOT_REQUESTED",
            "decision_reason": "retry reason does not request execution",
        }
