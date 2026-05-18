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


def _transport_lineage(**overrides):
    value = {
        "runtime_activation_gate_id": "GATE-1",
        "runtime_operation_envelope_id": "ENV-1",
        "runtime_execution_surface_id": "SURFACE-1",
        "execution_exchange_session_id": "EXCHANGE-1",
        "execution_relay_session_id": "RELAY-1",
        "runtime_execution_commit_id": "COMMIT-1",
        "response_return_id": "RETURN-1",
    }
    value.update(overrides)
    return value


def _activation(authorized=True):
    return {
        "validation": {"valid": True},
        "runtime_activation_gate_binding": {"runtime_activation_gate_id": "GATE-1", "activation_authorized": authorized},
    }


def _operation(valid=True):
    return {
        "validation": {"valid": valid},
        "runtime_operation_evidence": {"runtime_operation_envelope_id": "ENV-1"},
    }


def _surface(runtime_surface="GOVERNED_PYTEST_RUNTIME_SURFACE", valid=True):
    return {
        "validation": {"valid": valid},
        "runtime_execution_surface_evidence": {
            "runtime_execution_surface_id": "SURFACE-1",
            "runtime_surface": runtime_surface,
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


def _sessions(lineage_override=None):
    ux_session = create_governed_interaction_session(interaction_seed={"user_id": "U-1"}, lineage=_ux_lineage())
    lineage = _invocation_lineage(ux_session)
    if lineage_override:
        lineage.update(lineage_override)
    invocation_session = create_runtime_invocation_session(
        interaction_identity="CHATGPT-INTERACTION-1",
        lineage=lineage,
    )
    return ux_session, invocation_session


def _invoke(
    *,
    ux_session=None,
    invocation_session=None,
    payload=None,
    transport_lineage=None,
    activation_output=None,
    operation_output=None,
    surface_output=None,
):
    default_ux, default_invocation = _sessions()
    return invoke_governed_runtime(
        invocation_session=invocation_session or default_invocation,
        ux_session=ux_session or default_ux,
        interaction_payload=payload or _payload(),
        transport_lineage=transport_lineage or _transport_lineage(),
        activation_output=activation_output or _activation(),
        operation_output=operation_output or _operation(),
        surface_output=surface_output or _surface(),
    )


def test_successful_full_invocation_traverses_existing_chain():
    result = _invoke()
    assert result["invocation_status"] == "RETURNED"
    assert result["ux_output"]["interaction_status"] == "RETURNED"
    assert result["ux_output"]["transport"]["transport_status"] == "COMPLETED"
    assert result["ux_output"]["connector"]["connector_status"] == "COMPLETED"
    assert result["response_envelope"]["operational_evidence"]["lineage_preserved"] is True
    assert validate_invocation_session(result["invocation_session"])["valid"] is True


def test_malformed_invocation_lineage_fails_closed():
    ux_session, invocation_session = _sessions(lineage_override={"governed_session_id": ""})
    assert _invoke(ux_session=ux_session, invocation_session=invocation_session)["invocation_status"] == "BLOCKED"


def test_replay_mismatch_fails_closed():
    result = _invoke()
    broken = deepcopy(result["invocation_session"])
    broken["invocations"][0]["response"]["invocation_response_hash"] = "MISMATCH"
    assert validate_invocation_replay(broken)["valid"] is False


def test_unauthorized_execution_fails_closed():
    payload = _payload(request_payload={"operation_intent": "run bounded validation", "authorized_execution": False})
    assert _invoke(payload=payload)["invocation_status"] == "BLOCKED"


def test_invalid_transport_continuity_fails_closed():
    assert _invoke(transport_lineage=_transport_lineage(response_return_id=""))["invocation_status"] == "BLOCKED"


def test_closure_corruption_fails_closed():
    result = _invoke()
    closed = close_runtime_invocation_session(session=result["invocation_session"])["session"]
    corrupted = deepcopy(closed)
    corrupted["invocation_head_hash"] = "MISMATCH"
    assert close_runtime_invocation_session(session=corrupted)["states"] == ["BLOCKED"]


def test_hidden_continuation_routing_and_execution_flags_fail_closed():
    assert _invoke(payload=_payload(hidden_continuation_present=True))["invocation_status"] == "BLOCKED"
    assert _invoke(payload=_payload(hidden_routing_present=True))["invocation_status"] == "BLOCKED"
    assert _invoke(payload=_payload(hidden_execution_present=True))["invocation_status"] == "BLOCKED"


def test_invalid_connector_surface_fails_closed():
    assert _invoke(surface_output=_surface(runtime_surface="GOVERNED_ARTIFACT_WRITE_SURFACE"))["invocation_status"] == "BLOCKED"


def test_invalid_response_continuity_fails_validation():
    result = _invoke()
    broken = deepcopy(result["invocation_session"])
    broken["invocations"][0]["response"]["runtime_invocation_request_id"] = "WRONG"
    assert validate_invocation_session(broken)["valid"] is False


def test_multi_invocation_continuity_is_deterministic_and_ordered():
    ux_session, invocation_session = _sessions()
    first = _invoke(ux_session=ux_session, invocation_session=invocation_session)
    second = _invoke(ux_session=first["ux_session"], invocation_session=first["invocation_session"])
    third = _invoke(ux_session=second["ux_session"], invocation_session=second["invocation_session"])
    invocations = third["invocation_session"]["invocations"]
    assert third["invocation_session"]["invocation_count"] == 3
    assert invocations[1]["request"]["previous_invocation_hash"] == invocations[0]["response"]["invocation_response_hash"]
    assert invocations[2]["request"]["previous_invocation_hash"] == invocations[1]["response"]["invocation_response_hash"]
    assert third["invocation_session"]["invocation_head_hash"] == invocations[2]["response"]["invocation_response_hash"]


def test_closure_prevents_continuation_and_stale_state_reuse():
    first = _invoke()
    closed = close_runtime_invocation_session(session=first["invocation_session"])["session"]
    assert _invoke(ux_session=first["ux_session"], invocation_session=closed)["invocation_status"] == "BLOCKED"
    stale = deepcopy(first["invocation_session"])
    stale["invocation_head_hash"] = ""
    assert validate_invocation_session(stale)["valid"] is False


def test_replay_evidence_is_deterministic_and_read_only():
    first = _invoke()
    second = _invoke()
    first_evidence = governed_runtime_invocation_evidence(
        session=first["invocation_session"],
        response=first["response_envelope"],
    )
    second_evidence = governed_runtime_invocation_evidence(
        session=second["invocation_session"],
        response=second["response_envelope"],
    )
    assert first["response_envelope"]["runtime_invocation_response_id"] == second["response_envelope"]["runtime_invocation_response_id"]
    assert first_evidence == second_evidence
    assert validate_invocation_replay(first["invocation_session"])["read_only"] is True
