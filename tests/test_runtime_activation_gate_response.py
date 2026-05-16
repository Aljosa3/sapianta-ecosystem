from sapianta_bridge.governed_runtime_activation_gate.runtime_activation_gate_response import (
    create_runtime_activation_gate_response,
)


def test_response_marks_activation_approved():
    response = create_runtime_activation_gate_response(
        binding={"runtime_activation_gate_id": "GATE-1", "response_return_id": "RETURN-1"}
    ).to_dict()
    assert response["response_return_id"] == "RETURN-1"
    assert response["activation_status"] == "RUNTIME_ACTIVATION_APPROVED"
