from sapianta_bridge.governed_runtime_activation_gate import create_runtime_activation_gate


def _entrypoint():
    return {
        "validation": {"valid": True},
        "activation": {
            "operational_runtime_entrypoint_id": "ENTRY-1",
            "runtime_activation_boundary_id": "BOUNDARY-1",
            "operational_entry_contract_id": "CONTRACT-1",
            "operational_entry_admission_id": "ADMISSION-1",
        },
        "contract": {"operational_entry_contract_id": "CONTRACT-1"},
        "admission": {"operational_entry_admission_id": "ADMISSION-1", "admitted": True, "approved_by": "human"},
        "evidence": {
            "execution_exchange_session_id": "EXCHANGE-1",
            "execution_relay_session_id": "RELAY-1",
            "runtime_execution_commit_id": "COMMIT-1",
            "runtime_delivery_finalization_id": "FINAL-1",
            "response_return_id": "RETURN-1",
        },
    }


def test_controller_approves_complete_entrypoint_authority_chain():
    result = create_runtime_activation_gate(entrypoint_output=_entrypoint())
    assert result["validation"]["valid"] is True
    assert result["states"][-1] == "RUNTIME_ACTIVATION_APPROVED"


def test_controller_blocks_incomplete_entrypoint():
    result = create_runtime_activation_gate(entrypoint_output={})
    assert result["states"] == ["BLOCKED"]


def test_controller_blocks_invalid_admission():
    entrypoint = _entrypoint()
    entrypoint["admission"]["admitted"] = False
    result = create_runtime_activation_gate(entrypoint_output=entrypoint)
    assert result["states"] == ["BLOCKED"]
