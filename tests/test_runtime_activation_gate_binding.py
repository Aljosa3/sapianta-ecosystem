from sapianta_bridge.governed_runtime_activation_gate.runtime_activation_gate_binding import (
    create_runtime_activation_gate_binding,
)


def test_binding_preserves_activation_authority_artifacts():
    binding = create_runtime_activation_gate_binding(
        gate_session={"runtime_activation_gate_id": "GATE-1"},
        entrypoint_output={
            "activation": {
                "operational_runtime_entrypoint_id": "ENTRY-1",
                "runtime_activation_boundary_id": "BOUNDARY-1",
                "operational_entry_contract_id": "CONTRACT-1",
                "operational_entry_admission_id": "ADMISSION-1",
            },
            "admission": {"admitted": True, "approved_by": "human"},
            "evidence": {
                "execution_exchange_session_id": "EXCHANGE-1",
                "execution_relay_session_id": "RELAY-1",
                "runtime_execution_commit_id": "COMMIT-1",
                "runtime_delivery_finalization_id": "FINAL-1",
                "response_return_id": "RETURN-1",
            },
        },
    ).to_dict()
    assert binding["runtime_activation_boundary_id"] == "BOUNDARY-1"
    assert binding["operational_entry_admission_id"] == "ADMISSION-1"
    assert binding["activation_authorized"] is True
