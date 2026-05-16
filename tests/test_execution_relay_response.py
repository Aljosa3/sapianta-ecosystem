from sapianta_bridge.governed_execution_relay.execution_relay_response import create_execution_relay_response


def test_execution_relay_response_preserves_stdout_relay():
    response = create_execution_relay_response(
        binding={"execution_relay_session_id": "REL-1", "stdout_relay_id": "STDOUT-1", "response_return_id": "RETURN-1"}
    ).to_dict()
    assert response["stdout_relay_id"] == "STDOUT-1"
    assert response["relay_status"] == "EXECUTION_RELAY_RESPONSE_EMITTED"
