from copy import deepcopy

from sapianta_system.runtime.transport import execute_governed_live_execution_transport


def _lineage():
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
        "runtime_activation_gate_binding": {
            "runtime_activation_gate_id": "GATE-1",
            "activation_authorized": authorized,
        },
    }


def _operation(valid=True):
    return {
        "validation": {"valid": valid},
        "runtime_operation_evidence": {"runtime_operation_envelope_id": "ENV-1"},
    }


def _surface(valid=True):
    return {
        "validation": {"valid": valid},
        "runtime_execution_surface_evidence": {
            "runtime_execution_surface_id": "SURFACE-1",
            "runtime_surface": "GOVERNED_PYTEST_RUNTIME_SURFACE",
        },
    }


def _payload(**overrides):
    value = {
        "operation_intent": "run bounded validation",
        "authorized_execution": True,
    }
    value.update(overrides)
    return value


def _execute(**overrides):
    params = {
        "request_payload": _payload(),
        "lineage": _lineage(),
        "activation_output": _activation(),
        "operation_output": _operation(),
        "surface_output": _surface(),
    }
    params.update(overrides)
    return execute_governed_live_execution_transport(**params)


def test_transport_is_deterministic_and_returns_result():
    first = _execute()
    second = _execute()
    assert first["transport_status"] == "COMPLETED"
    assert first["request"]["replay_identity"] == second["request"]["replay_identity"]
    assert first["response"]["result_replay_identity"] == second["response"]["result_replay_identity"]
    assert first["evidence"]["transport_completed"] is True


def test_transport_preserves_lineage_and_closure():
    result = _execute()
    assert result["request"]["lineage"] == _lineage()
    assert result["evidence"]["lineage_preserved"] is True
    assert result["states"] == ["TRANSPORT_COMPLETED"]


def test_transport_blocks_invalid_request():
    result = _execute(request_payload=_payload(operation_intent=""))
    assert result["transport_status"] == "BLOCKED"


def test_transport_blocks_missing_activation_approval():
    result = _execute(activation_output=_activation(False))
    assert result["transport_status"] == "BLOCKED"


def test_transport_blocks_invalid_operation_envelope_and_surface():
    assert _execute(operation_output=_operation(False))["transport_status"] == "BLOCKED"
    assert _execute(surface_output=_surface(False))["transport_status"] == "BLOCKED"


def test_transport_blocks_replay_mismatch():
    result = _execute()
    broken = deepcopy(result["request"])
    broken["replay_identity"] = "MISMATCH"
    from sapianta_system.runtime.transport.governed_transport_validator import validate_governed_transport_request

    assert validate_governed_transport_request(broken)["valid"] is False


def test_transport_exposes_no_retry_fallback_or_orchestration():
    evidence = _execute()["evidence"]
    assert evidence["retry_present"] is False
    assert evidence["fallback_present"] is False
    assert evidence["orchestration_present"] is False
    assert evidence["hidden_execution_present"] is False
