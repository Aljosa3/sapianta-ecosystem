from sapianta_bridge.governed_runtime_activation_gate.runtime_activation_gate_evidence import runtime_activation_gate_evidence


def test_runtime_activation_gate_evidence_records_authorization():
    evidence = runtime_activation_gate_evidence(binding={"activation_authorized": True, "approved_by": "human"}, valid=True, states=("RUNTIME_ACTIVATION_CREATED",))
    assert evidence["activation_authorized"] is True
    assert evidence["approved_by"] == "human"
