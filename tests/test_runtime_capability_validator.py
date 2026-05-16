from sapianta_bridge.governed_runtime_capability_mapping.runtime_capability_validator import (
    validate_runtime_capability_mapping,
)


def _artifacts(operation_type="READ_STATE", primitive="GOVERNED_STATE_READER"):
    mapping = {
        "runtime_capability_mapping_id": "MAP-1",
        "runtime_operation_envelope_id": "ENV-1",
        "operation_type": operation_type,
        "executor_primitive": primitive,
    }
    return {
        "mapping": mapping,
        "contract": {"runtime_capability_contract_id": "CONTRACT-1", "runtime_capability_mapping_id": "MAP-1", "deterministic_mapping_required": True},
        "executor": {"runtime_capability_executor_id": "EXEC-1", "runtime_capability_mapping_id": "MAP-1", "executor_primitive": primitive},
        "surface": {
            "runtime_capability_surface_id": "SURFACE-1",
            "runtime_capability_mapping_id": "MAP-1",
            "raw_shell_execution_allowed": False,
            "unrestricted_subprocess_allowed": False,
            "unrestricted_network_execution_allowed": False,
        },
        "policy": {"runtime_capability_policy_id": "POLICY-1", "runtime_capability_mapping_id": "MAP-1", "bounded_executor_required": True, "dynamic_executor_generation_allowed": False},
        "operation_output": {
            "validation": {"valid": True},
            "runtime_operation_evidence": {
                "runtime_operation_envelope_id": "ENV-1",
                "runtime_operation_contract_id": "OCONTRACT-1",
                "runtime_operation_payload_id": "PAYLOAD-1",
                "runtime_operation_policy_id": "OPOLICY-1",
                "runtime_activation_gate_id": "GATE-1",
                "execution_exchange_session_id": "EX-1",
                "execution_relay_session_id": "REL-1",
                "runtime_execution_commit_id": "COMMIT-1",
                "runtime_delivery_finalization_id": "FINAL-1",
            },
        },
    }


def _validate(**overrides):
    artifacts = _artifacts(**overrides)
    return validate_runtime_capability_mapping(**artifacts)


def test_validator_accepts_valid_capability_lineage():
    assert _validate()["valid"] is True


def test_validator_rejects_forbidden_executor_requests():
    assert _validate(operation_type="RAW_SHELL", primitive="")["valid"] is False
    assert _validate(operation_type="UNRESTRICTED_SUBPROCESS", primitive="")["valid"] is False
    assert _validate(operation_type="NETWORK_EXECUTION", primitive="")["valid"] is False


def test_validator_rejects_mismatched_executor_primitive():
    assert _validate(operation_type="READ_STATE", primitive="PYTEST_VALIDATION_EXECUTOR")["valid"] is False


def test_validator_rejects_identity_change():
    artifacts = _artifacts()
    result = validate_runtime_capability_mapping(
        **artifacts,
        prior_output={"runtime_capability_mapping": {"runtime_capability_mapping_id": "OTHER"}},
    )
    assert result["valid"] is False
