"""Minimal read-only provider harness readiness review."""

from __future__ import annotations

from aigol.runtime.transport.serialization import replay_hash

from .review_result import ReviewResult
from .review_validator import ReviewValidator


class ProviderHarnessReview:
    """Evaluates provider activation readiness without executing providers."""

    def __init__(self, validator: ReviewValidator | None = None) -> None:
        self.validator = validator or ReviewValidator()

    def evaluate(self, contract) -> tuple[ReviewResult, dict[str, object]]:
        validation = self.validator.validate(contract)
        scope = contract.review_scope
        findings = [
            self._finding(
                "provider_registration",
                contract.provider_name in set(scope.get("registered_providers", [])),
                "provider is explicitly registered",
                "provider missing from explicit registration evidence",
            ),
            self._finding(
                "routing_compatibility",
                scope.get("routing_compatible") is True,
                "routing compatibility evidence is present",
                "routing compatibility unresolved or incompatible",
            ),
            self._finding(
                "approval_compatibility",
                scope.get("approval_state") == "APPROVED",
                "approval path is resolved",
                "approval path unresolved or not approved",
            ),
            self._finding(
                "replay_persistence_compatibility",
                scope.get("replay_persistence_available") is True,
                "replay persistence compatibility evidence is present",
                "replay persistence compatibility unavailable",
            ),
            self._finding(
                "sandbox_compatibility",
                scope.get("sandbox_compatible") is True,
                "sandbox compatibility evidence is present",
                "sandbox unresolved or incompatible",
            ),
            self._finding(
                "policy_compatibility",
                scope.get("policy_compatible") is True,
                "policy compatibility evidence is present",
                "policy compatibility unresolved or incompatible",
            ),
        ]
        blocked_checks = {
            "provider_registration",
            "routing_compatibility",
            "approval_compatibility",
            "replay_persistence_compatibility",
            "sandbox_compatibility",
        }
        failed = [finding for finding in findings if finding["status"] != "PASS"]
        if not failed:
            state = "READY"
        elif any(finding["check"] in blocked_checks for finding in failed):
            state = "BLOCKED"
        else:
            state = "NOT_READY"
        result = ReviewResult(
            review_result_id=f"{contract.review_id}:result",
            runtime_id=contract.runtime_id,
            readiness_state=state,
            findings=findings,
            created_at=contract.created_at,
        )
        replay_input = result.to_dict()
        replay_input.pop("replay_hash", None)
        result = ReviewResult(
            review_result_id=result.review_result_id,
            runtime_id=result.runtime_id,
            readiness_state=result.readiness_state,
            findings=result.findings,
            created_at=result.created_at,
            replay_hash=replay_hash(replay_input),
        )
        return result, validation

    def _finding(self, check: str, passed: bool, pass_reason: str, fail_reason: str) -> dict[str, object]:
        return {
            "check": check,
            "status": "PASS" if passed else "FAIL",
            "reason": pass_reason if passed else fail_reason,
            "execution_performed": False,
            "provider_invoked": False,
            "orchestration": False,
        }
