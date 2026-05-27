"""Tests for LIVE_RUNTIME_OBSERVATION_PHASE_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

from aigol.runtime.live_runtime_observation_phase import (
    AMBIGUITY_TELEMETRY,
    COGNITION_DRIFT,
    GOVERNANCE_PRESSURE,
    OBSERVED,
    REPLAY_CONTINUITY,
    LiveRuntimeObservationArtifact,
    observe_ambiguity_telemetry,
    observe_cognition_drift,
    observe_governance_pressure,
    observe_replay_continuity,
    reconstruct_live_runtime_observation_lineage,
)
from aigol.runtime.live_semantic_pressure_validation import (
    AMBIGUITY_PRESSURE,
    HIDDEN_AUTHORITY_DRIFT,
    VALID_BOUNDED_RESPONSE,
    reconstruct_live_semantic_pressure_lineage,
    validate_live_semantic_pressure,
)
from aigol.runtime.real_external_llm_attachment import external_model_response_hash
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-27T00:15:00+00:00"


class ProviderExecutionSentinel:
    executed = False

    def fetch(self) -> None:
        self.executed = True
        raise AssertionError("runtime observation must not invoke providers")


def _proposal_payload(**overrides) -> dict:
    payload = {
        "proposal_id": "OBSERVATION-PROPOSAL-1",
        "natural_language_input": "Propose bounded runtime metadata inspection.",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": "contract:OBSERVATION-CONTRACT-1",
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return payload


def _response(**overrides) -> dict:
    response = {
        "model_response_id": "OBSERVATION-MODEL-RESPONSE-1",
        "model_provider": "external_llm_provider",
        "model_name": "bounded-proposal-model",
        "proposal_payload": _proposal_payload(),
        "created_at": CREATED_AT,
    }
    response.update(overrides)
    response["response_hash"] = external_model_response_hash(response)
    return response


def _pressure(pressure_type: str = VALID_BOUNDED_RESPONSE, **payload_overrides):
    response = _response(proposal_payload=_proposal_payload(**payload_overrides))
    return validate_live_semantic_pressure(
        validation_id=f"PRESSURE-{pressure_type}",
        model_response_artifact=response,
        pressure_type=pressure_type,
        expected_result="CONTAINED",
        created_at=CREATED_AT,
    )


def test_cognition_drift_observation() -> None:
    pressure = _pressure(HIDDEN_AUTHORITY_DRIFT, authorization_id="AUTHORITY-DRIFT-1")

    observation = observe_cognition_drift(
        observation_id="OBSERVATION-DRIFT-1",
        pressure_evidence=pressure,
        created_at=CREATED_AT,
    )

    assert observation.observation_type == COGNITION_DRIFT
    assert observation.observation_status == OBSERVED
    assert observation.telemetry["drift_detected"] is True
    assert observation.telemetry["source_evidence_hash"] == pressure.evidence_hash


def test_ambiguity_telemetry_generation() -> None:
    pressure = _pressure(
        AMBIGUITY_PRESSURE,
        natural_language_input="Maybe inspect runtime metadata or read external data?",
    )

    observation = observe_ambiguity_telemetry(
        observation_id="OBSERVATION-AMBIGUITY-1",
        pressure_evidence=pressure.to_dict(),
        created_at=CREATED_AT,
    )

    assert observation.observation_type == AMBIGUITY_TELEMETRY
    assert observation.telemetry["ambiguity_detected"] is True
    assert observation.telemetry["ambiguity_rejected"] is True


def test_replay_continuity_observation() -> None:
    pressure = _pressure()
    lineage = reconstruct_live_semantic_pressure_lineage([pressure])

    observation = observe_replay_continuity(
        observation_id="OBSERVATION-REPLAY-1",
        lineage_evidence=lineage,
        created_at=CREATED_AT,
    )

    assert observation.observation_type == REPLAY_CONTINUITY
    assert observation.telemetry["replay_continuous"] is True
    assert observation.telemetry["append_only_valid"] is True
    assert observation.telemetry["lineage_hash"] == lineage["lineage_hash"]


def test_governance_pressure_evidence() -> None:
    contained = _pressure()
    ambiguous = _pressure(
        AMBIGUITY_PRESSURE,
        natural_language_input="Maybe inspect runtime metadata or read external data?",
    )

    observation = observe_governance_pressure(
        observation_id="OBSERVATION-PRESSURE-1",
        pressure_evidence=[contained, ambiguous.to_dict()],
        created_at=CREATED_AT,
    )

    assert observation.observation_type == GOVERNANCE_PRESSURE
    assert observation.telemetry["pressure_count"] == 2
    assert observation.telemetry["contained_count"] == 1
    assert observation.telemetry["rejected_count"] == 1
    assert observation.evidence_hash.startswith("sha256:")


def test_deterministic_observation_hashing() -> None:
    observation = observe_cognition_drift(
        observation_id="OBSERVATION-HASH-1",
        pressure_evidence=_pressure(),
        created_at=CREATED_AT,
    )
    artifact = observation.to_dict()
    reconstructed = LiveRuntimeObservationArtifact.from_dict(artifact).to_dict()

    assert artifact == reconstructed
    without_hash = deepcopy(artifact)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_append_only_telemetry_lineage() -> None:
    first = observe_cognition_drift(
        observation_id="OBSERVATION-LINEAGE-1",
        pressure_evidence=_pressure(),
        created_at=CREATED_AT,
    )
    second = observe_ambiguity_telemetry(
        observation_id="OBSERVATION-LINEAGE-2",
        pressure_evidence=_pressure(
            AMBIGUITY_PRESSURE,
            natural_language_input="Maybe inspect runtime metadata or read external data?",
        ),
        created_at="2026-05-27T00:15:01+00:00",
    )

    lineage_a = reconstruct_live_runtime_observation_lineage([first.to_dict(), second.to_dict()])
    lineage_b = reconstruct_live_runtime_observation_lineage([first.to_dict(), second.to_dict()])

    assert lineage_a == lineage_b
    assert lineage_a["observation_count"] == 2
    assert lineage_a["append_only_valid"] is True
    assert lineage_a["governance_authority_separated"] is True


def test_no_execution_authority_surface() -> None:
    import aigol.runtime.live_runtime_observation_phase as observation_phase

    sentinel = ProviderExecutionSentinel()
    observe_cognition_drift(
        observation_id="OBSERVATION-SURFACE-1",
        pressure_evidence=_pressure(),
        created_at=CREATED_AT,
    )

    source = inspect.getsource(observation_phase)

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
    assert "authorize_" not in source
    assert "route_authorized" not in source
    assert "attach_to_session" not in source
    assert "execute_minimal_governed_path" not in source
    assert "open(" not in source
    assert "Path(" not in source
