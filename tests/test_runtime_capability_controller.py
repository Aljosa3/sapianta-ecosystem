from sapianta_bridge.governed_runtime_capability_mapping import create_runtime_capability_mapping


def _operation(operation_type="RUN_VALIDATION"):
    return {
        "validation": {"valid": True},
        "runtime_operation_evidence": {
            "runtime_operation_envelope_id": "ENV-1",
            "runtime_operation_contract_id": "CONTRACT-1",
            "runtime_operation_payload_id": "PAYLOAD-1",
            "runtime_operation_policy_id": "POLICY-1",
            "runtime_activation_gate_id": "GATE-1",
            "execution_exchange_session_id": "EXCHANGE-1",
            "execution_relay_session_id": "RELAY-1",
            "runtime_execution_commit_id": "COMMIT-1",
            "runtime_delivery_finalization_id": "FINAL-1",
            "operation_type": operation_type,
        },
    }


def test_controller_authorizes_allowed_mapping():
    result = create_runtime_capability_mapping(operation_output=_operation())
    assert result["validation"]["valid"] is True
    assert result["states"][-1] == "CAPABILITY_AUTHORIZED"


def test_controller_rejects_unknown_mapping():
    result = create_runtime_capability_mapping(operation_output=_operation("UNKNOWN"))
    assert result["states"] == ["CAPABILITY_REJECTED"]


def test_controller_rejects_raw_shell_subprocess_and_network():
    for operation_type in ("RAW_SHELL", "UNRESTRICTED_SUBPROCESS", "NETWORK_EXECUTION"):
        assert create_runtime_capability_mapping(operation_output=_operation(operation_type))["states"] == ["CAPABILITY_REJECTED"]
