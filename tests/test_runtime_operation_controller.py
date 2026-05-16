from sapianta_bridge.governed_runtime_operation_envelope import create_runtime_operation_envelope
from sapianta_bridge.governed_runtime_operation_envelope.runtime_operation_boundary import ALLOWED_OPERATION_TYPES


def _activation():
    return {
        "validation": {"valid": True},
        "runtime_activation_gate_binding": {
            "runtime_activation_gate_id": "GATE-1",
            "runtime_activation_boundary_id": "BOUNDARY-1",
            "operational_entry_contract_id": "CONTRACT-1",
            "operational_entry_admission_id": "ADMISSION-1",
            "operational_runtime_entrypoint_id": "ENTRY-1",
            "execution_exchange_session_id": "EXCHANGE-1",
            "execution_relay_session_id": "RELAY-1",
            "runtime_execution_commit_id": "COMMIT-1",
            "runtime_delivery_finalization_id": "FINAL-1",
            "response_return_id": "RETURN-1",
            "activation_authorized": True,
            "approved_by": "human",
        },
    }


def _lineage():
    return {
        "runtime_persistent_channel_id": "CHANNEL-1",
        "direct_runtime_interaction_session_id": "DIRECT-1",
        "runtime_surface_session_id": "SURFACE-1",
        "local_runtime_bridge_session_id": "BRIDGE-1",
        "governed_session_id": "GOV-1",
        "execution_gate_id": "EXEC-GATE-1",
        "provider_invocation_id": "PROVIDER-1",
        "bounded_runtime_id": "RUNTIME-1",
        "result_capture_id": "CAPTURE-1",
    }


def _create(**overrides):
    params = {
        "activation_output": _activation(),
        "upstream_lineage": _lineage(),
        "operation_type": "READ_STATE",
        "operation_intent": "read bounded state",
        "target_scope": {"kind": "path", "value": "runtime/state.json"},
        "allowed_inputs": ["state_ref"],
        "expected_outputs": ["state_snapshot"],
        "risk_class": "LOW",
        "requires_human_approval": True,
        "approved_by": "human",
    }
    params.update(overrides)
    return create_runtime_operation_envelope(**params)


def test_controller_authorizes_allowed_operation():
    result = _create()
    assert result["validation"]["valid"] is True
    assert result["states"][-1] == "OPERATION_AUTHORIZED"


def test_controller_authorizes_every_allowed_operation_type():
    assert all(_create(operation_type=operation_type)["validation"]["valid"] for operation_type in ALLOWED_OPERATION_TYPES)


def test_controller_rejects_raw_shell():
    result = _create(operation_type="RAW_SHELL")
    assert result["validation"]["valid"] is False
    assert result["states"] == ["OPERATION_REJECTED"]


def test_controller_rejects_unrestricted_subprocess():
    result = _create(operation_type="UNRESTRICTED_SUBPROCESS")
    assert result["states"] == ["OPERATION_REJECTED"]
