from sapianta_bridge.governed_runtime_operation_envelope.runtime_operation_evidence import runtime_operation_evidence


def test_evidence_distinguishes_activation_from_operation_authorization():
    evidence = runtime_operation_evidence(
        envelope={"runtime_operation_envelope_id": "ENV-1"},
        contract={"runtime_operation_contract_id": "CONTRACT-1"},
        payload={"runtime_operation_payload_id": "PAYLOAD-1", "operation_type": "READ_STATE"},
        policy={"runtime_operation_policy_id": "POLICY-1"},
        boundary={"runtime_operation_boundary_id": "BOUNDARY-1"},
        lineage={},
        valid=True,
        states=("OPERATION_AUTHORIZED",),
    )
    assert evidence["activation_authorization_is_operation_authorization"] is False
    assert evidence["raw_prompt_to_shell_forbidden"] is True
