from sapianta_bridge.governed_runtime_capability_mapping.runtime_capability_evidence import runtime_capability_evidence


def test_evidence_preserves_lineage_and_executor():
    evidence = runtime_capability_evidence(
        mapping={"runtime_capability_mapping_id": "MAP-1", "operation_type": "READ_STATE"},
        contract={"runtime_capability_contract_id": "CONTRACT-1"},
        executor={"runtime_capability_executor_id": "EXEC-1", "executor_primitive": "GOVERNED_STATE_READER"},
        surface={"runtime_capability_surface_id": "SURFACE-1"},
        policy={"runtime_capability_policy_id": "POLICY-1"},
        operation_evidence={"runtime_operation_envelope_id": "ENV-1"},
        valid=True,
        states=("CAPABILITY_AUTHORIZED",),
    )
    assert evidence["runtime_operation_envelope_id"] == "ENV-1"
    assert evidence["executor_primitive"] == "GOVERNED_STATE_READER"
