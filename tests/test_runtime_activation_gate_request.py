from sapianta_bridge.governed_runtime_activation_gate.runtime_activation_gate_request import create_runtime_activation_gate_request


def test_runtime_activation_gate_request_preserves_authorization():
    request = create_runtime_activation_gate_request(
        gate_session={"runtime_activation_gate_id": "ACT-1", "local_runtime_bridge_session_id": "BR-1", "activation_authorized": True, "approved_by": "human"}
    ).to_dict()
    assert request["activation_authorized"] is True
    assert request["approved_by"] == "human"
