"""Tests for REAL_GOVERNED_EXECUTION_RESILIENCE_SUITE_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.real_governed_execution_resilience_suite import (
    DUPLICATE_EXECUTION_ATTEMPT,
    INVALID_SESSION_LINEAGE_CONTINUATION,
    MALFORMED_PROPOSAL_LINEAGE,
    PASSED,
    PROVIDER_BOUNDARY_VIOLATION,
    REPLAY_CORRUPTION_ATTEMPT,
    ROUTING_MISMATCH_ATTEMPT,
    UNAUTHORIZED_CAPABILITY_ESCALATION,
    RealGovernedExecutionResilienceEvidence,
    reconstruct_real_governed_execution_resilience_lineage,
    run_real_governed_execution_resilience_suite,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-26T00:08:00+00:00"


def _suite(**overrides):
    payload = {
        "suite_id": "RESILIENCE-SUITE-1",
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return run_real_governed_execution_resilience_suite(**payload)


def test_malformed_cognition_rejection() -> None:
    result = _suite()
    evidence = {item.pressure_type: item for item in result["resilience_evidence"]}

    assert evidence[MALFORMED_PROPOSAL_LINEAGE].status == PASSED
    assert evidence[MALFORMED_PROPOSAL_LINEAGE].observed_result == "REJECTED"


def test_authorization_failure_containment() -> None:
    result = _suite()
    evidence = {item.pressure_type: item for item in result["resilience_evidence"]}

    assert evidence[UNAUTHORIZED_CAPABILITY_ESCALATION].status == PASSED
    assert evidence[UNAUTHORIZED_CAPABILITY_ESCALATION].observed_result == "REJECTED"


def test_replay_corruption_invalidation() -> None:
    result = _suite()
    evidence = {item.pressure_type: item for item in result["resilience_evidence"]}

    assert evidence[REPLAY_CORRUPTION_ATTEMPT].status == PASSED
    assert evidence[REPLAY_CORRUPTION_ATTEMPT].observed_result == "REJECTED"


def test_routing_mismatch_rejection() -> None:
    result = _suite()
    evidence = {item.pressure_type: item for item in result["resilience_evidence"]}

    assert evidence[ROUTING_MISMATCH_ATTEMPT].status == PASSED
    assert evidence[ROUTING_MISMATCH_ATTEMPT].observed_result == "REJECTED"


def test_provider_boundary_enforcement() -> None:
    result = _suite()
    evidence = {item.pressure_type: item for item in result["resilience_evidence"]}

    assert evidence[PROVIDER_BOUNDARY_VIOLATION].status == PASSED
    assert evidence[PROVIDER_BOUNDARY_VIOLATION].observed_result == "REJECTED"


def test_deterministic_fail_closed_execution() -> None:
    result = _suite()
    evidence = {item.pressure_type: item for item in result["resilience_evidence"]}

    assert evidence[DUPLICATE_EXECUTION_ATTEMPT].status == PASSED
    assert evidence[INVALID_SESSION_LINEAGE_CONTINUATION].status == PASSED
    assert result["suite_result"]["status"] == PASSED


def test_replay_visible_resilience_evidence() -> None:
    first = _suite()["resilience_evidence"][0].to_dict()
    second = RealGovernedExecutionResilienceEvidence.from_dict(first).to_dict()

    assert first == second
    without_hash = deepcopy(first)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_append_only_resilience_lineage() -> None:
    evidence = list(_suite()["resilience_evidence"])

    first = reconstruct_real_governed_execution_resilience_lineage([item.to_dict() for item in evidence])
    second = reconstruct_real_governed_execution_resilience_lineage([item.to_dict() for item in evidence])

    assert first == second
    assert first["resilience_count"] == 7
    assert first["append_only_valid"] is True
    assert first["lineage_hash"].startswith("sha256:")


def test_mutated_resilience_evidence_rejected() -> None:
    artifact = _suite()["resilience_evidence"][0].to_dict()
    artifact["status"] = "FAILED"

    with pytest.raises(FailClosedRuntimeError, match="evidence hash mismatch"):
        RealGovernedExecutionResilienceEvidence.from_dict(artifact)


def test_duplicate_resilience_lineage_rejected() -> None:
    evidence = list(_suite()["resilience_evidence"])

    with pytest.raises(FailClosedRuntimeError, match="duplicate"):
        reconstruct_real_governed_execution_resilience_lineage([evidence[0], evidence[0]])


def test_no_disallowed_runtime_surface() -> None:
    import aigol.runtime.real_governed_execution_resilience_suite as suite

    source = inspect.getsource(suite)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
    assert "orchestrat" not in source.lower()
    assert "autonomous" not in source.lower()
    assert "retry" not in source.lower()
    assert "open(" not in source
    assert "Path(" not in source
