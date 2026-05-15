from sapianta_bridge.interaction_transport_bridge.transport_state import SUCCESS_PATH, validate_transport_state_chain


def test_transport_state_success_path_is_valid():
    assert validate_transport_state_chain(list(SUCCESS_PATH))["valid"] is True
