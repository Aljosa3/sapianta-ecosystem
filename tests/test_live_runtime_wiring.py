from copy import deepcopy

from sapianta_system.runtime.ux import create_governed_interaction_session
from sapianta_system.runtime.wiring import (
    close_runtime_invocation_session,
    create_runtime_invocation_session,
    invoke_governed_runtime,
)
from sapianta_system.runtime.wiring.governed_runtime_endpoint_validator import validate_invocation_session
from sapianta_system.runtime.wiring.governed_runtime_invocation_evidence import governed_runtime_invocation_evidence
from sapianta_system.runtime.wiring.governed_runtime_invocation_replay import validate_invocation_replay


def _ux_lineage():
    return {
        "governed_session_id": "GOV-1",
        "runtime_activation_gate_id": "GATE-1",
        "runtime_operation_envelope_id": "ENV-1",
        "runtime_execution_surface_id": "SURFACE-1",
    }


def _invocation_lineage(ux_session):
    return {
        "governed_interaction_session_id": ux_session["governed_interaction_session_id"],
        "governed_session_id": "GOV-1",
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


def _activation(authorized=True):
    return {
        "validation": {"valid": True},
        "runtime_activation_gate_binding": {"runtime_activation_gate_id": "GATE-1", "activation_authorized": authorized},
    }


def _operation():
    return {"validation": {"valid": True}, "runtime_operation_evidence": {"runtime_operation_envelope_id": "ENV-1"}}


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


def _sessions():
    ux_session = create_governed_interaction_session(interaction_seed={"user_id": "U-1"}, lineage=_ux_lineage())
    invocation_session = create_runtime_invocation_session(
        interaction_identity="CHATGPT-INTERACTION-1",
        lineage=_invocation_lineage(ux_session),
    )
    return ux_session, invocation_session


def _invoke(ux_session=None, invocation_session=None, payload=None, activation_output=None):
    default_ux, default_invocation = _sessions()
    return invoke_governed_runtime(
        invocation_session=invocation_session or default_invocation,
        ux_session=ux_session or default_ux,
        interaction_payload=payload or _payload(),
        transport_lineage=_transport_lineage(),
        activation_output=activation_output or _activation(),
        operation_output=_operation(),
        surface_output=_surface(),
    )


def test_invocation_identity_is_deterministic():
    ux_session, _ = _sessions()
    assert create_runtime_invocation_session(
        interaction_identity="CHATGPT-INTERACTION-1",
        lineage=_invocation_lineage(ux_session),
    ) == create_runtime_invocation_session(
        interaction_identity="CHATGPT-INTERACTION-1",
        lineage=_invocation_lineage(ux_session),
    )


def test_wiring_returns_replay_visible_response():
    first = _invoke()
    second = _invoke()
    assert first["invocation_status"] == "RETURNED"
    assert first["response_envelope"]["runtime_invocation_response_id"] == second["response_envelope"]["runtime_invocation_response_id"]
    assert first["response_envelope"]["operational_evidence"]["lineage_preserved"] is True
    assert validate_invocation_session(first["invocation_session"])["valid"] is True


def test_invocation_continuity_is_hash_linked():
    ux_session, invocation_session = _sessions()
    first = _invoke(ux_session=ux_session, invocation_session=invocation_session)
    second = _invoke(ux_session=first["ux_session"], invocation_session=first["invocation_session"])
    invocations = second["invocation_session"]["invocations"]
    assert second["invocation_session"]["invocation_count"] == 2
    assert invocations[1]["request"]["previous_invocation_hash"] == invocations[0]["response"]["invocation_response_hash"]


def test_replay_mismatch_fails_closed():
    result = _invoke()
    session = deepcopy(result["invocation_session"])
    session["invocations"][0]["response"]["invocation_response_hash"] = "MISMATCH"
    assert validate_invocation_replay(session)["valid"] is False


def test_invalid_payload_and_hidden_behavior_fail_closed():
    assert _invoke(payload=_payload(interaction_intent=""))["invocation_status"] == "BLOCKED"
    assert _invoke(payload=_payload(hidden_execution_present=True))["invocation_status"] == "BLOCKED"


def test_invalid_runtime_flow_fails_closed_without_invocation_mutation():
    ux_session, invocation_session = _sessions()
    before = deepcopy(invocation_session)
    result = _invoke(
        ux_session=ux_session,
        invocation_session=invocation_session,
        activation_output=_activation(False),
    )
    assert result["invocation_status"] == "BLOCKED"
    assert invocation_session == before


def test_evidence_declares_no_orchestration_or_hidden_execution():
    result = _invoke()
    evidence = governed_runtime_invocation_evidence(
        session=result["invocation_session"],
        response=result["response_envelope"],
    )
    assert evidence["invocation_continuity_preserved"] is True
    assert evidence["orchestration_present"] is False
    assert evidence["hidden_execution_present"] is False
    assert evidence["hidden_routing_present"] is False


def test_invocation_closure_is_deterministic_and_prevents_continuation():
    result = _invoke()
    first = close_runtime_invocation_session(session=result["invocation_session"])
    second = close_runtime_invocation_session(session=result["invocation_session"])
    assert first["validation"]["valid"] is True
    assert first["closure"]["runtime_invocation_closure_id"] == second["closure"]["runtime_invocation_closure_id"]
    assert _invoke(ux_session=result["ux_session"], invocation_session=first["session"])["invocation_status"] == "BLOCKED"
