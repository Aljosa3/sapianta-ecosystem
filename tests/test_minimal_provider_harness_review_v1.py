"""Tests for MINIMAL_PROVIDER_HARNESS_REVIEW_V1."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from aigol.runtime import FailClosedRuntimeError
from aigol.runtime.review import ProviderHarnessReview, ReviewContract, ReviewValidator


def _scope(**overrides):
    scope = {
        "registered_providers": ["mock"],
        "routing_compatible": True,
        "approval_state": "APPROVED",
        "replay_persistence_available": True,
        "sandbox_compatible": True,
        "policy_compatible": True,
    }
    scope.update(overrides)
    return scope


def _contract(**overrides) -> ReviewContract:
    values = {
        "runtime_id": "review-v1",
        "provider_name": "mock",
        "review_scope": _scope(),
        "governance_state": "AUTHORIZED",
        "created_at": "1970-01-01T00:00:00Z",
    }
    values.update(overrides)
    return ReviewContract.create(**values)


def test_valid_readiness_evaluation() -> None:
    result, validation = ProviderHarnessReview().evaluate(_contract())

    assert validation["status"] == "REVIEW_CONTRACT_VALIDATED"
    assert result.readiness_state == "READY"
    assert all(finding["provider_invoked"] is False for finding in result.findings)


def test_missing_provider_blocked() -> None:
    result, _ = ProviderHarnessReview().evaluate(_contract(review_scope=_scope(registered_providers=[])))

    assert result.readiness_state == "BLOCKED"


def test_routing_mismatch_blocked() -> None:
    result, _ = ProviderHarnessReview().evaluate(_contract(review_scope=_scope(routing_compatible=False)))

    assert result.readiness_state == "BLOCKED"


def test_replay_compatibility_checks() -> None:
    result, _ = ProviderHarnessReview().evaluate(_contract(review_scope=_scope(replay_persistence_available=False)))

    assert result.readiness_state == "BLOCKED"
    assert any(finding["check"] == "replay_persistence_compatibility" for finding in result.findings)


def test_policy_not_ready_without_execution() -> None:
    result, _ = ProviderHarnessReview().evaluate(_contract(review_scope=_scope(policy_compatible=False)))

    assert result.readiness_state == "NOT_READY"
    assert all(finding["execution_performed"] is False for finding in result.findings)


def test_invalid_replay_hash_blocked() -> None:
    contract = _contract()
    broken = ReviewContract(
        review_id=contract.review_id,
        runtime_id=contract.runtime_id,
        provider_name=contract.provider_name,
        review_scope=contract.review_scope,
        governance_state=contract.governance_state,
        created_at=contract.created_at,
        replay_hash="sha256:bad",
    )

    with pytest.raises(FailClosedRuntimeError):
        ReviewValidator().validate(broken)


def test_deterministic_hashing() -> None:
    first, _ = ProviderHarnessReview().evaluate(_contract())
    second, _ = ProviderHarnessReview().evaluate(_contract())

    assert _contract().to_dict()["replay_hash"] == _contract().to_dict()["replay_hash"]
    assert first.to_dict()["replay_hash"] == second.to_dict()["replay_hash"]


def test_immutable_review_guarantees() -> None:
    contract = _contract()
    result, _ = ProviderHarnessReview().evaluate(contract)

    with pytest.raises(FrozenInstanceError):
        contract.provider_name = "openai"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.readiness_state = "BLOCKED"  # type: ignore[misc]
