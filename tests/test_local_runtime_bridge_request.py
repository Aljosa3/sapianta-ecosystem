from sapianta_bridge.governed_local_runtime_bridge.local_runtime_bridge_request import create_local_runtime_bridge_request


def test_local_runtime_bridge_request_preserves_transport_id():
    request = create_local_runtime_bridge_request(
        bridge_session={"local_runtime_bridge_session_id": "BR-1", "execution_relay_session_id": "REL-1", "runtime_transport_bridge_id": "RTB-1"}
    ).to_dict()
    assert request["runtime_transport_bridge_id"] == "RTB-1"
