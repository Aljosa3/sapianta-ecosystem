"""Tests for GOVERNANCE_FAILURE_SEMANTICS_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.governance_failure_semantics import (
    CRITICAL,
    FAIL_CLOSED,
    HIGH,
    INVALIDATE_LINEAGE,
    LOW,
    QUARANTINE_REQUIRED,
    REJECT,
    GovernanceFailureEvidence,
    classify_governance_failure,
    reconstruct_failure_lineage,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-26T00:00:00+00:00"


def _failure(**overrides) -> GovernanceFailureEvidence:
    payload = {
        "failure_id": "FAILURE-1",
        "failure_type": FAIL_CLOSED,
        "severity": HIGH,
        "related_session_id": "SESSION-1",
        "related_contract_id": "CONTRACT-1",
        "related_authorization_id": "AUTH-1",
        "reason": "authorization evidence did not match contract lineage",
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return classify_governance_failure(**payload)


def test_valid_failure_classification() -> None:
    failure = _failure()

    assert failure.failure_id == "FAILURE-1"
    assert failure.failure_type == FAIL_CLOSED
    assert failure.severity == HIGH
    assert failure.related_session_id == "SESSION-1"
    assert failure.evidence_hash.startswith("sha256:")


def test_invalid_failure_type_rejection() -> None:
    with pytest.raises(FailClosedRuntimeError, match="failure type"):
        _failure(failure_type="RECOVER")


def test_invalid_severity_rejection() -> None:
    with pytest.raises(FailClosedRuntimeError, match="severity"):
        _failure(severity="SEVERE")


def test_deterministic_failure_evidence() -> None:
    first = _failure().to_dict()
    second = _failure().to_dict()

    assert first == second
    without_hash = deepcopy(first)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_immutable_failure_evidence() -> None:
    failure = _failure()
    before = failure.to_dict()

    with pytest.raises(AttributeError):
        failure.severity = LOW

    assert failure.to_dict() == before


def test_append_only_failure_lineage() -> None:
    failures = [
        _failure(failure_id="FAILURE-1", failure_type=REJECT, severity=LOW, created_at="2026-05-26T00:00:00+00:00"),
        _failure(failure_id="FAILURE-2", failure_type=INVALIDATE_LINEAGE, severity=CRITICAL, created_at="2026-05-26T00:00:01+00:00"),
    ]

    lineage = reconstruct_failure_lineage(failures)

    assert lineage["failure_count"] == 2
    assert lineage["append_only_valid"] is True
    assert lineage["failures"][0]["failure_index"] == 0
    assert lineage["failures"][1]["failure_index"] == 1


def test_replay_visible_failure_reconstruction() -> None:
    failures = [_failure(), _failure(failure_id="FAILURE-2", failure_type=QUARANTINE_REQUIRED, created_at="2026-05-26T00:00:01+00:00")]

    first = reconstruct_failure_lineage([failure.to_dict() for failure in failures])
    second = reconstruct_failure_lineage([failure.to_dict() for failure in failures])

    assert first == second
    assert first["lineage_hash"].startswith("sha256:")


def test_fail_closed_malformed_failure_state_handling() -> None:
    artifact = _failure().to_dict()
    artifact.pop("reason")

    with pytest.raises(FailClosedRuntimeError, match="malformed"):
        GovernanceFailureEvidence.from_dict(artifact)


def test_mutated_failure_evidence_rejected() -> None:
    artifact = _failure().to_dict()
    artifact["severity"] = CRITICAL

    with pytest.raises(FailClosedRuntimeError, match="evidence hash mismatch"):
        GovernanceFailureEvidence.from_dict(artifact)


def test_duplicate_failure_lineage_rejected() -> None:
    failures = [_failure(), _failure()]

    with pytest.raises(FailClosedRuntimeError, match="duplicate"):
        reconstruct_failure_lineage(failures)


def test_out_of_order_failure_lineage_rejected() -> None:
    failures = [
        _failure(failure_id="FAILURE-1", created_at="2026-05-26T00:00:02+00:00"),
        _failure(failure_id="FAILURE-2", created_at="2026-05-26T00:00:01+00:00"),
    ]

    with pytest.raises(FailClosedRuntimeError, match="ordering"):
        reconstruct_failure_lineage(failures)


def test_no_recovery_or_provider_execution_surface() -> None:
    import aigol.runtime.governance_failure_semantics as semantics

    source = inspect.getsource(semantics)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "retry" not in source.lower()
    assert "recover" not in source.lower()
    assert "mitigat" not in source.lower()
    assert "orchestrat" not in source.lower()
    assert "autonomous" not in source.lower()
    assert "llm" not in source.lower()
    assert "async " not in source
    assert "await " not in source
