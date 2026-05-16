from sapianta_bridge.governed_execution_relay.execution_relay_state import EXECUTION_RELAY_STATES, SUCCESS_PATH


def test_execution_relay_states_are_bounded():
    assert SUCCESS_PATH == EXECUTION_RELAY_STATES[:6]
    assert EXECUTION_RELAY_STATES[-2:] == ("BLOCKED", "FAILED")
