"""Tests for SYNTHETIC_COGNITION_PRESSURE_SIMULATOR_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

import pytest

from aigol.runtime.governance_failure_semantics import (
    FAIL_CLOSED,
    HIGH,
    INVALIDATE_LINEAGE,
    QUARANTINE_REQUIRED,
    REJECT,
    classify_governance_failure,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.synthetic_cognition_pressure_simulator import (
    AMBIGUOUS_CONTRACT,
    AUTHORITY_DRIFT_ATTEMPT,
    LONG_CHAIN_ENTROPY_SEQUENCE,
    PROVIDER_ESCALATION_ATTEMPT,
    REPLAY_CORRUPTION_ATTEMPT,
    SyntheticCognitionPressureArtifact,
    generate_ambiguous_contract,
    generate_authority_drift_attempt,
    generate_long_chain_entropy_sequence,
    generate_provider_escalation_attempt,
    generate_replay_corruption_attempt,
    reconstruct_simulation_lineage,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-26T00:00:00+00:00"


class ProviderExecutionSentinel:
    executed = False

    def fetch(self) -> None:
        self.executed = True
        raise AssertionError("simulator must not invoke providers")


def test_ambiguous_contract_generation() -> None:
    simulation = generate_ambiguous_contract(created_at=CREATED_AT)
    artifact = simulation.to_dict()["generated_artifact"]

    assert simulation.simulation_type == AMBIGUOUS_CONTRACT
    assert simulation.expected_governance_result == REJECT
    assert artifact["requested_operations"][0]["operation_id"] == artifact["requested_operations"][1]["operation_id"]


def test_provider_escalation_generation() -> None:
    simulation = generate_provider_escalation_attempt(created_at=CREATED_AT)
    artifact = simulation.to_dict()["generated_artifact"]

    assert simulation.simulation_type == PROVIDER_ESCALATION_ATTEMPT
    assert simulation.expected_governance_result == FAIL_CLOSED
    assert artifact["requested_provider"] not in artifact["authorized_provider_boundary"]


def test_replay_corruption_generation() -> None:
    simulation = generate_replay_corruption_attempt(created_at=CREATED_AT)
    artifact = simulation.to_dict()["generated_artifact"]

    assert simulation.simulation_type == REPLAY_CORRUPTION_ATTEMPT
    assert simulation.expected_governance_result == INVALIDATE_LINEAGE
    assert artifact["original_evidence"]["evidence_hash"] == artifact["corrupted_evidence"]["evidence_hash"]
    assert artifact["original_evidence"]["operation"] != artifact["corrupted_evidence"]["operation"]


def test_authority_drift_simulation() -> None:
    simulation = generate_authority_drift_attempt(created_at=CREATED_AT)
    artifact = simulation.to_dict()["generated_artifact"]

    assert simulation.simulation_type == AUTHORITY_DRIFT_ATTEMPT
    assert simulation.expected_governance_result == QUARANTINE_REQUIRED
    assert set(artifact["later_requested_providers"]) > set(artifact["declared_allowed_providers"])


def test_long_chain_entropy_generation() -> None:
    simulation = generate_long_chain_entropy_sequence(created_at=CREATED_AT, length=8)
    artifact = simulation.to_dict()["generated_artifact"]

    assert simulation.simulation_type == LONG_CHAIN_ENTROPY_SEQUENCE
    assert simulation.expected_governance_result == INVALIDATE_LINEAGE
    assert artifact["lineage_length"] == 9
    assert artifact["operations"][-1]["operation_id"] == artifact["operations"][-2]["operation_id"]


def test_deterministic_replay_visibility() -> None:
    simulations = [
        generate_ambiguous_contract(simulation_id="SIM-1", created_at="2026-05-26T00:00:00+00:00"),
        generate_provider_escalation_attempt(simulation_id="SIM-2", created_at="2026-05-26T00:00:01+00:00"),
    ]

    first = reconstruct_simulation_lineage([simulation.to_dict() for simulation in simulations])
    second = reconstruct_simulation_lineage([simulation.to_dict() for simulation in simulations])

    assert first == second
    assert first["simulation_count"] == 2
    assert first["lineage_hash"].startswith("sha256:")


def test_append_only_evidence_generation() -> None:
    lineage = reconstruct_simulation_lineage(
        [
            generate_ambiguous_contract(simulation_id="SIM-1", created_at="2026-05-26T00:00:00+00:00"),
            generate_replay_corruption_attempt(simulation_id="SIM-2", created_at="2026-05-26T00:00:01+00:00"),
        ]
    )

    assert lineage["append_only_valid"] is True
    assert lineage["simulations"][0]["simulation_index"] == 0
    assert lineage["simulations"][1]["simulation_index"] == 1


def test_fail_closed_governance_expectation_generation() -> None:
    expectations = {
        generate_ambiguous_contract().expected_governance_result,
        generate_provider_escalation_attempt().expected_governance_result,
        generate_replay_corruption_attempt().expected_governance_result,
        generate_authority_drift_attempt().expected_governance_result,
        generate_long_chain_entropy_sequence().expected_governance_result,
    }

    assert expectations == {REJECT, FAIL_CLOSED, INVALIDATE_LINEAGE, QUARANTINE_REQUIRED}


def test_deterministic_evidence_hashing() -> None:
    first = generate_long_chain_entropy_sequence(created_at=CREATED_AT, length=6).to_dict()
    second = generate_long_chain_entropy_sequence(created_at=CREATED_AT, length=6).to_dict()

    assert first == second
    without_hash = deepcopy(first)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_immutable_simulation_evidence() -> None:
    simulation = generate_ambiguous_contract(created_at=CREATED_AT)
    before = simulation.to_dict()

    with pytest.raises(TypeError):
        simulation.generated_artifact["contract_id"] = "CHANGED"
    with pytest.raises(AttributeError):
        simulation.simulation_type = PROVIDER_ESCALATION_ATTEMPT

    assert simulation.to_dict() == before


def test_deterministic_governance_failure_classification() -> None:
    simulation = generate_provider_escalation_attempt(created_at=CREATED_AT)
    first = classify_governance_failure(
        failure_id="FAILURE-FROM-SIM-1",
        failure_type=simulation.expected_governance_result,
        severity=HIGH,
        related_session_id="SESSION-SYNTH-1",
        related_contract_id="CONTRACT-SYNTH-1",
        related_authorization_id="AUTH-SYNTH-1",
        reason="synthetic provider boundary pressure expected fail-closed handling",
        created_at=CREATED_AT,
    ).to_dict()
    second = classify_governance_failure(
        failure_id="FAILURE-FROM-SIM-1",
        failure_type=simulation.expected_governance_result,
        severity=HIGH,
        related_session_id="SESSION-SYNTH-1",
        related_contract_id="CONTRACT-SYNTH-1",
        related_authorization_id="AUTH-SYNTH-1",
        reason="synthetic provider boundary pressure expected fail-closed handling",
        created_at=CREATED_AT,
    ).to_dict()

    assert first == second


def test_mutated_simulation_evidence_rejected() -> None:
    artifact = generate_ambiguous_contract(created_at=CREATED_AT).to_dict()
    artifact["generated_artifact"]["contract_id"] = "CHANGED"

    with pytest.raises(FailClosedRuntimeError, match="evidence hash mismatch"):
        SyntheticCognitionPressureArtifact.from_dict(artifact)


def test_malformed_simulation_rejected() -> None:
    artifact = generate_ambiguous_contract(created_at=CREATED_AT).to_dict()
    artifact.pop("generated_artifact")

    with pytest.raises(FailClosedRuntimeError, match="malformed"):
        SyntheticCognitionPressureArtifact.from_dict(artifact)


def test_duplicate_simulation_lineage_rejected() -> None:
    simulations = [
        generate_ambiguous_contract(simulation_id="SIM-1", created_at="2026-05-26T00:00:00+00:00"),
        generate_provider_escalation_attempt(simulation_id="SIM-1", created_at="2026-05-26T00:00:01+00:00"),
    ]

    with pytest.raises(FailClosedRuntimeError, match="duplicate"):
        reconstruct_simulation_lineage(simulations)


def test_out_of_order_simulation_lineage_rejected() -> None:
    simulations = [
        generate_ambiguous_contract(simulation_id="SIM-1", created_at="2026-05-26T00:00:02+00:00"),
        generate_provider_escalation_attempt(simulation_id="SIM-2", created_at="2026-05-26T00:00:01+00:00"),
    ]

    with pytest.raises(FailClosedRuntimeError, match="ordering"):
        reconstruct_simulation_lineage(simulations)


def test_no_provider_runtime_or_cognition_surface() -> None:
    import aigol.runtime.synthetic_cognition_pressure_simulator as simulator

    sentinel = ProviderExecutionSentinel()
    generate_ambiguous_contract()
    generate_provider_escalation_attempt()
    generate_replay_corruption_attempt()
    generate_authority_drift_attempt()
    generate_long_chain_entropy_sequence(length=4)

    source = inspect.getsource(simulator)

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
    assert "workflow" not in source.lower()
    assert "llm" not in source.lower()
    assert "open(" not in source
    assert "Path(" not in source
