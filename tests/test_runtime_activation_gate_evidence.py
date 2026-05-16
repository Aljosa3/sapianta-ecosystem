from sapianta_bridge.governed_runtime_activation_gate.runtime_activation_gate_evidence import runtime_activation_gate_evidence


def test_evidence_records_authority_not_execution():
    evidence = runtime_activation_gate_evidence(
        binding={"activation_authorized": True, "approved_by": "human"},
        valid=True,
        states=("RUNTIME_ACTIVATION_APPROVED",),
    )
    assert evidence["runtime_activatable"] is True
    assert evidence["activation_authorized"] is True
    assert evidence["autonomous_activation_introduced"] is False
