from sapianta_bridge.governed_execution_relay.execution_relay_request import create_execution_relay_request


def test_execution_relay_request_preserves_stdin_relay():
    request = create_execution_relay_request(
        relay_session={"execution_relay_session_id": "REL-1", "execution_exchange_session_id": "EX-1", "stdin_relay_id": "STDIN-1"}
    ).to_dict()
    assert request["stdin_relay_id"] == "STDIN-1"
