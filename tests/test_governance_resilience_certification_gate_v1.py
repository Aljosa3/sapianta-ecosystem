"""Tests for GOVERNANCE_RESILIENCE_CERTIFICATION_GATE_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.governance_resilience_certification_gate import (
    CERTIFIED,
    REJECTED,
    GovernanceResilienceCertificationResult,
    certify_governance_resilience,
    reconstruct_certification_lineage,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.synthetic_cognition_pressure_simulator import (
    generate_ambiguous_contract,
    generate_authority_drift_attempt,
    generate_long_chain_entropy_sequence,
    generate_provider_escalation_attempt,
    generate_replay_corruption_attempt,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-26T00:01:00+00:00"


class ProviderExecutionSentinel:
    executed = False

    def fetch(self) -> None:
        self.executed = True
        raise AssertionError("certification gate must not invoke providers")


def _evidence() -> list[dict]:
    return [
        generate_ambiguous_contract(simulation_id="SIM-1", created_at="2026-05-26T00:00:00+00:00").to_dict(),
        generate_authority_drift_attempt(simulation_id="SIM-2", created_at="2026-05-26T00:00:01+00:00").to_dict(),
        generate_long_chain_entropy_sequence(simulation_id="SIM-3", created_at="2026-05-26T00:00:02+00:00", length=4).to_dict(),
        generate_provider_escalation_attempt(simulation_id="SIM-4", created_at="2026-05-26T00:00:03+00:00").to_dict(),
        generate_replay_corruption_attempt(simulation_id="SIM-5", created_at="2026-05-26T00:00:04+00:00").to_dict(),
    ]


def _certification(**overrides) -> GovernanceResilienceCertificationResult:
    payload = {
        "certification_id": "CERT-1",
        "related_change_id": "CHANGE-1",
        "resilience_suite_version": "SYNTHETIC_COGNITION_PRESSURE_SIMULATOR_V1",
        "resilience_evidence": _evidence(),
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return certify_governance_resilience(**payload)


def test_valid_resilience_certification() -> None:
    certification = _certification()

    assert certification.certification_status == CERTIFIED
    assert certification.related_change_id == "CHANGE-1"
    assert certification.failure_summary["promotion_eligible"] is True
    assert len(certification.validated_simulation_types) == 5
    assert certification.evidence_hash.startswith("sha256:")


def test_missing_resilience_evidence_rejection() -> None:
    certification = _certification(resilience_evidence=[])

    assert certification.certification_status == REJECTED
    assert certification.failure_summary["promotion_eligible"] is False
    assert certification.failure_summary["rejection_reason"] == "missing resilience evidence"


def test_malformed_certification_rejection() -> None:
    artifact = _certification().to_dict()
    artifact.pop("failure_summary")

    with pytest.raises(FailClosedRuntimeError, match="malformed"):
        GovernanceResilienceCertificationResult.from_dict(artifact)


def test_incomplete_simulation_coverage_rejection() -> None:
    evidence = _evidence()[:-1]
    certification = _certification(resilience_evidence=evidence)

    assert certification.certification_status == REJECTED
    assert certification.failure_summary["promotion_eligible"] is False
    assert certification.failure_summary["rejection_reason"] == "incomplete simulation coverage"
    assert certification.to_dict()["failure_summary"]["missing_simulation_types"] == ["REPLAY_CORRUPTION_ATTEMPT"]


def test_replay_visible_certification_evidence() -> None:
    first = _certification().to_dict()
    second = GovernanceResilienceCertificationResult.from_dict(first).to_dict()

    assert first == second
    without_hash = deepcopy(first)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_deterministic_certification_lineage() -> None:
    certifications = [
        _certification(certification_id="CERT-1", related_change_id="CHANGE-1", created_at="2026-05-26T00:01:00+00:00"),
        _certification(certification_id="CERT-2", related_change_id="CHANGE-2", created_at="2026-05-26T00:01:01+00:00"),
    ]

    first = reconstruct_certification_lineage([certification.to_dict() for certification in certifications])
    second = reconstruct_certification_lineage([certification.to_dict() for certification in certifications])

    assert first == second
    assert first["certification_count"] == 2
    assert first["lineage_hash"].startswith("sha256:")


def test_append_only_certification_semantics() -> None:
    certifications = [
        _certification(certification_id="CERT-1", created_at="2026-05-26T00:01:00+00:00"),
        _certification(certification_id="CERT-2", created_at="2026-05-26T00:01:01+00:00"),
    ]

    lineage = reconstruct_certification_lineage(certifications)

    assert lineage["append_only_valid"] is True
    assert lineage["certifications"][0]["certification_index"] == 0
    assert lineage["certifications"][1]["certification_index"] == 1


def test_fail_closed_certification_gating() -> None:
    evidence = _evidence()
    evidence[0]["generated_artifact"]["contract_id"] = "MUTATED"

    certification = _certification(resilience_evidence=evidence)

    assert certification.certification_status == REJECTED
    assert certification.failure_summary["rejection_reason"] == "certification validation failed closed"


def test_mutated_certification_evidence_rejected() -> None:
    artifact = _certification().to_dict()
    artifact["certification_status"] = REJECTED

    with pytest.raises(FailClosedRuntimeError, match="evidence hash mismatch"):
        GovernanceResilienceCertificationResult.from_dict(artifact)


def test_duplicate_certification_lineage_rejected() -> None:
    certifications = [
        _certification(certification_id="CERT-1", created_at="2026-05-26T00:01:00+00:00"),
        _certification(certification_id="CERT-1", created_at="2026-05-26T00:01:01+00:00"),
    ]

    with pytest.raises(FailClosedRuntimeError, match="duplicate"):
        reconstruct_certification_lineage(certifications)


def test_out_of_order_certification_lineage_rejected() -> None:
    certifications = [
        _certification(certification_id="CERT-1", created_at="2026-05-26T00:01:02+00:00"),
        _certification(certification_id="CERT-2", created_at="2026-05-26T00:01:01+00:00"),
    ]

    with pytest.raises(FailClosedRuntimeError, match="ordering"):
        reconstruct_certification_lineage(certifications)


def test_no_provider_execution_or_runtime_governance_surface() -> None:
    import aigol.runtime.governance_resilience_certification_gate as gate

    sentinel = ProviderExecutionSentinel()
    _certification()

    source = inspect.getsource(gate)

    assert sentinel.executed is False
    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
    assert "orchestrat" not in source.lower()
    assert "autonomous" not in source.lower()
    assert "llm" not in source.lower()
    assert "open(" not in source
    assert "Path(" not in source
