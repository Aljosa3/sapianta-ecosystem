from copy import deepcopy

from sapianta_system.runtime.ux import (
    close_governed_interaction_session,
    create_governed_interaction_session,
    perform_governed_interaction,
)
from sapianta_system.runtime.ux.governed_interaction_evidence import governed_interaction_evidence
from sapianta_system.runtime.ux.governed_interaction_replay import validate_interaction_replay
from sapianta_system.runtime.ux.governed_interaction_validator import validate_interaction_session


def _lineage():
    return {
        "governed_session_id": "GOV-1",
        "runtime_activation_gate_id": "GATE-1",
        "runtime_operation_envelope_id": "ENV-1",
        "runtime_execution_surface_id": "SURFACE-1",
    }


def _transport_lineage():
    return {
        "runtime_activation_gate_id": "GATE-1",
        "runtime_operation_envelope_id": "ENV-1",
        "runtime_execution_surface_id": "SURFACE-1",
        "execution_exchange_session_id": "EXCHANGE-1",
        "execution_relay_session_id": "RELAY-1",
        "runtime_execution_commit_id": "COMMIT-1",
        "response_return_id": "RETURN-1",
    }


def _activation():
    return {
        "validation": {"valid": True},
        "runtime_activation_gate_binding": {
            "runtime_activation_gate_id": "GATE-1",
            "activation_authorized": True,
        },
    }


def _operation():
    return {
        "validation": {"valid": True},
        "runtime_operation_evidence": {"runtime_operation_envelope_id": "ENV-1"},
    }


def _surface():
    return {
        "validation": {"valid": True},
        "runtime_execution_surface_evidence": {
            "runtime_execution_surface_id": "SURFACE-1",
            "runtime_surface": "GOVERNED_PYTEST_RUNTIME_SURFACE",
        },
    }


def _payload(**overrides):
    value = {
        "interaction_intent": "run bounded validation",
        "connector_name": "local_execution",
        "request_payload": {"operation_intent": "run bounded validation", "authorized_execution": True},
        "hidden_continuation_present": False,
        "orchestration_present": False,
        "hidden_routing_present": False,
        "hidden_execution_present": False,
        "hidden_mutable_state_present": False,
    }
    value.update(overrides)
    return value


def _session():
    return create_governed_interaction_session(interaction_seed={"user_id": "U-1"}, lineage=_lineage())


def _perform(session=None, payload=None):
    return perform_governed_interaction(
        session=session or _session(),
        interaction_payload=payload or _payload(),
        transport_lineage=_transport_lineage(),
        activation_output=_activation(),
        operation_output=_operation(),
        surface_output=_surface(),
    )


def test_interaction_identity_is_deterministic():
    assert _session() == _session()


def test_governed_interaction_returns_replay_visible_response():
    first = _perform()
    second = _perform()
    assert first["interaction_status"] == "RETURNED"
    assert first["response"]["governed_interaction_response_id"] == second["response"]["governed_interaction_response_id"]
    assert first["response"]["operational_evidence"]["lineage_preserved"] is True
    assert validate_interaction_session(first["session"])["valid"] is True


def test_interaction_continuity_is_hash_linked():
    first = _perform()
    second = _perform(session=first["session"])
    interactions = second["session"]["interactions"]
    assert second["session"]["interaction_count"] == 2
    assert interactions[1]["request"]["previous_interaction_hash"] == interactions[0]["response"]["response_hash"]


def test_replay_mismatch_fails_closed():
    result = _perform()
    session = deepcopy(result["session"])
    session["interactions"][0]["response"]["response_hash"] = "MISMATCH"
    assert validate_interaction_replay(session)["valid"] is False


def test_invalid_payload_and_hidden_behavior_fail_closed():
    assert _perform(payload=_payload(interaction_intent=""))["interaction_status"] == "BLOCKED"
    assert _perform(payload=_payload(hidden_routing_present=True))["interaction_status"] == "BLOCKED"


def test_invalid_runtime_flow_fails_closed_without_session_mutation():
    session = _session()
    before = deepcopy(session)
    result = perform_governed_interaction(
        session=session,
        interaction_payload=_payload(),
        transport_lineage=_transport_lineage(),
        activation_output={
            "validation": {"valid": True},
            "runtime_activation_gate_binding": {"runtime_activation_gate_id": "GATE-1", "activation_authorized": False},
        },
        operation_output=_operation(),
        surface_output=_surface(),
    )
    assert result["interaction_status"] == "BLOCKED"
    assert session == before


def test_evidence_declares_no_orchestration_or_hidden_execution():
    result = _perform()
    evidence = governed_interaction_evidence(session=result["session"], response=result["response"])
    assert evidence["interaction_continuity_preserved"] is True
    assert evidence["orchestration_present"] is False
    assert evidence["hidden_execution_present"] is False
    assert evidence["hidden_routing_present"] is False


def test_interaction_closure_is_deterministic_and_prevents_continuation():
    result = _perform()
    first = close_governed_interaction_session(session=result["session"])
    second = close_governed_interaction_session(session=result["session"])
    assert first["validation"]["valid"] is True
    assert first["closure"]["governed_interaction_closure_id"] == second["closure"]["governed_interaction_closure_id"]
    assert _perform(session=first["session"])["interaction_status"] == "BLOCKED"
