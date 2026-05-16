from sapianta_bridge.governed_local_runtime_bridge.local_runtime_bridge_state import LOCAL_RUNTIME_BRIDGE_STATES, SUCCESS_PATH


def test_local_runtime_bridge_states_are_bounded():
    assert SUCCESS_PATH == LOCAL_RUNTIME_BRIDGE_STATES[:6]
    assert LOCAL_RUNTIME_BRIDGE_STATES[-2:] == ("BLOCKED", "FAILED")
