from sapianta_bridge.governed_local_runtime_bridge.local_runtime_bridge_response import create_local_runtime_bridge_response


def test_local_runtime_bridge_response_preserves_return_identity():
    response = create_local_runtime_bridge_response(
        binding={"local_runtime_bridge_session_id": "BR-1", "runtime_transport_bridge_id": "RTB-1", "response_return_id": "RETURN-1"}
    ).to_dict()
    assert response["bridge_status"] == "LOCAL_RUNTIME_BRIDGE_RESPONSE_EMITTED"
    assert response["response_return_id"] == "RETURN-1"
