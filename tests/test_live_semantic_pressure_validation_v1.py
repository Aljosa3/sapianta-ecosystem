"""Tests for LIVE_SEMANTIC_PRESSURE_VALIDATION_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

from aigol.runtime.live_semantic_pressure_validation import (
    ACCEPTED,
    AMBIGUITY_PRESSURE,
    CAPABILITY_ESCALATION_PRESSURE,
    CONTAINED,
    FAILED_CLOSED,
    HIDDEN_AUTHORITY_DRIFT,
    INVALID_PROPOSAL_NORMALIZATION,
    INVALIDATED,
    LiveSemanticPressureValidationEvidence,
    MALFORMED_COGNITION_STRUCTURE,
    REJECTED,
    REPLAY_LINEAGE_DRIFT,
    VALID_BOUNDED_RESPONSE,
    reconstruct_live_semantic_pressure_lineage,
    validate_live_semantic_pressure,
)
from aigol.runtime.real_external_llm_attachment import external_model_response_hash
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-27T00:13:00+00:00"


class ProviderExecutionSentinel:
    executed = False

    def fetch(self) -> None:
        self.executed = True
        raise AssertionError("semantic pressure validation must not invoke runtime providers")


def _proposal_payload(**overrides) -> dict:
    payload = {
        "proposal_id": "PRESSURE-PROPOSAL-1",
        "natural_language_input": "Propose bounded runtime metadata inspection.",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": "contract:PRESSURE-CONTRACT-1",
        "created_at": CREATED_AT,
    }
    payload.update(overrides)
    return payload


def _response(**overrides) -> dict:
    response = {
        "model_response_id": "PRESSURE-MODEL-RESPONSE-1",
        "model_provider": "external_llm_provider",
        "model_name": "bounded-proposal-model",
        "proposal_payload": _proposal_payload(),
        "created_at": CREATED_AT,
    }
    response.update(overrides)
    response["response_hash"] = external_model_response_hash(response)
    return response


def _validate(response: dict, pressure_type: str, expected_result: str = "REJECTED") -> LiveSemanticPressureValidationEvidence:
    return validate_live_semantic_pressure(
        validation_id="PRESSURE-VALIDATION-1",
        model_response_artifact=response,
        pressure_type=pressure_type,
        expected_result=expected_result,
        created_at=CREATED_AT,
    )


def test_ambiguous_real_model_response_rejection() -> None:
    response = _response(
        proposal_payload=_proposal_payload(
            natural_language_input="Maybe inspect runtime metadata or read external data?"
        )
    )

    evidence = _validate(response, AMBIGUITY_PRESSURE)

    assert evidence.containment_status == REJECTED
    assert evidence.actual_result == REJECTED
    assert evidence.failure_reason == "semantic pressure ambiguity rejected"


def test_unauthorized_capability_escalation_rejection() -> None:
    response = _response(proposal_payload=_proposal_payload(requested_capabilities=["readonly_http_get_provider"]))

    evidence = _validate(response, CAPABILITY_ESCALATION_PRESSURE)

    assert evidence.containment_status == REJECTED
    assert evidence.failure_reason == "semantic pressure capability escalation rejected"


def test_malformed_model_output_fail_closed_handling() -> None:
    malformed_response = {
        "model_response_id": "PRESSURE-MODEL-RESPONSE-MALFORMED",
        "model_provider": "external_llm_provider",
        "model_name": "bounded-proposal-model",
    }

    evidence = _validate(malformed_response, MALFORMED_COGNITION_STRUCTURE, expected_result="FAIL_CLOSED")

    assert evidence.model_response_reference == "PRESSURE-MODEL-RESPONSE-MALFORMED"
    assert evidence.containment_status == FAILED_CLOSED
    assert evidence.actual_result == FAILED_CLOSED


def test_replay_drift_invalidation() -> None:
    response = _response()
    response["proposal_payload"]["natural_language_input"] = "Changed after response hash was produced."

    evidence = _validate(response, REPLAY_LINEAGE_DRIFT, expected_result="INVALIDATED")

    assert evidence.containment_status == INVALIDATED
    assert evidence.actual_result == INVALIDATED
    assert evidence.failure_reason == "semantic pressure replay drift invalidated"


def test_hidden_authority_drift_rejection() -> None:
    response = _response(
        proposal_payload=_proposal_payload(
            authorization_id="AUTHORITY-DRIFT-1",
        )
    )

    evidence = _validate(response, HIDDEN_AUTHORITY_DRIFT)

    assert evidence.containment_status == REJECTED
    assert evidence.failure_reason == "semantic pressure hidden authority drift rejected"


def test_invalid_proposal_normalization_fail_closed() -> None:
    response = _response(proposal_payload=_proposal_payload(proposed_contract_reference="PRESSURE-CONTRACT-1"))

    evidence = _validate(response, INVALID_PROPOSAL_NORMALIZATION, expected_result="FAIL_CLOSED")

    assert evidence.containment_status == FAILED_CLOSED
    assert evidence.actual_result == FAILED_CLOSED


def test_valid_bounded_model_response_acceptance() -> None:
    evidence = _validate(_response(), VALID_BOUNDED_RESPONSE, expected_result="CONTAINED")

    assert evidence.containment_status == CONTAINED
    assert evidence.actual_result == ACCEPTED
    assert evidence.failure_reason == "bounded model response remained contained"
    assert evidence.evidence_hash.startswith("sha256:")


def test_deterministic_pressure_evidence_hashing() -> None:
    artifact = _validate(_response(), VALID_BOUNDED_RESPONSE, expected_result="CONTAINED").to_dict()
    reconstructed = LiveSemanticPressureValidationEvidence.from_dict(artifact).to_dict()

    assert artifact == reconstructed
    without_hash = deepcopy(artifact)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_replay_visible_pressure_lineage() -> None:
    first = _validate(_response(), VALID_BOUNDED_RESPONSE, expected_result="CONTAINED")
    second = validate_live_semantic_pressure(
        validation_id="PRESSURE-VALIDATION-2",
        model_response_artifact=_response(model_response_id="PRESSURE-MODEL-RESPONSE-2"),
        pressure_type=VALID_BOUNDED_RESPONSE,
        expected_result="CONTAINED",
        created_at="2026-05-27T00:13:01+00:00",
    )

    lineage_a = reconstruct_live_semantic_pressure_lineage([first.to_dict(), second.to_dict()])
    lineage_b = reconstruct_live_semantic_pressure_lineage([first.to_dict(), second.to_dict()])

    assert lineage_a == lineage_b
    assert lineage_a["pressure_count"] == 2
    assert lineage_a["append_only_valid"] is True
    assert lineage_a["governance_authority_separated"] is True
    assert lineage_a["lineage_hash"].startswith("sha256:")


def test_no_execution_authority_surface() -> None:
    import aigol.runtime.live_semantic_pressure_validation as pressure

    sentinel = ProviderExecutionSentinel()
    _validate(_response(), VALID_BOUNDED_RESPONSE, expected_result="CONTAINED")

    source = inspect.getsource(pressure)

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
