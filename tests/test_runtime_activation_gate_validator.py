from sapianta_bridge.governed_runtime_activation_gate.runtime_activation_gate_validator import (
    validate_runtime_activation_gate,
)


def _binding():
    return {
        "runtime_activation_gate_id": "GATE-1",
        "runtime_activation_boundary_id": "BOUNDARY-1",
        "operational_entry_contract_id": "CONTRACT-1",
        "operational_entry_admission_id": "ADMISSION-1",
        "execution_exchange_session_id": "EXCHANGE-1",
        "execution_relay_session_id": "RELAY-1",
        "runtime_execution_commit_id": "COMMIT-1",
        "runtime_delivery_finalization_id": "FINAL-1",
        "activation_authorized": True,
        "approved_by": "human",
        "activation_source_kind": "operational_entrypoint",
    }


def _entrypoint():
    return {
        "validation": {"valid": True},
        "activation": {"runtime_activation_boundary_id": "BOUNDARY-1"},
        "contract": {"operational_entry_contract_id": "CONTRACT-1"},
        "admission": {"operational_entry_admission_id": "ADMISSION-1", "admitted": True, "approved_by": "human"},
        "evidence": {
            "execution_exchange_session_id": "EXCHANGE-1",
            "execution_relay_session_id": "RELAY-1",
            "runtime_execution_commit_id": "COMMIT-1",
            "runtime_delivery_finalization_id": "FINAL-1",
        },
    }


def test_validator_accepts_complete_activation_authority_chain():
    result = validate_runtime_activation_gate(
        gate_session={"runtime_activation_gate_id": "GATE-1", "activation_source_id": "ENTRY-1", "activation_source_kind": "operational_entrypoint"},
        binding=_binding(),
        entrypoint_output=_entrypoint(),
    )
    assert result["valid"] is True


def test_validator_blocks_missing_execution_commit_continuity():
    binding = _binding()
    binding["runtime_execution_commit_id"] = ""
    result = validate_runtime_activation_gate(
        gate_session={"runtime_activation_gate_id": "GATE-1", "activation_source_id": "ENTRY-1", "activation_source_kind": "operational_entrypoint"},
        binding=binding,
        entrypoint_output=_entrypoint(),
    )
    assert result["valid"] is False


def test_validator_blocks_unapproved_admission():
    entrypoint = _entrypoint()
    entrypoint["admission"]["approved_by"] = "system"
    result = validate_runtime_activation_gate(
        gate_session={"runtime_activation_gate_id": "GATE-1", "activation_source_id": "ENTRY-1", "activation_source_kind": "operational_entrypoint"},
        binding=_binding(),
        entrypoint_output=entrypoint,
    )
    assert result["valid"] is False


def test_validator_blocks_implicit_reopen_of_closed_gate():
    result = validate_runtime_activation_gate(
        gate_session={"runtime_activation_gate_id": "GATE-1", "activation_source_id": "ENTRY-1", "activation_source_kind": "operational_entrypoint"},
        binding=_binding(),
        entrypoint_output=_entrypoint(),
        prior_output={"runtime_activation_gate_session": {"runtime_activation_gate_id": "GATE-1"}, "closed": True},
    )
    assert result["valid"] is False
    assert any(error["field"] == "closed" for error in result["errors"])
