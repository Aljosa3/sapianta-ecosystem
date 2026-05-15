from sapianta_bridge.live_governed_interaction_serving_gateway.serving_gateway_state import SERVING_GATEWAY_STATES, SUCCESS_PATH


def test_serving_gateway_states_are_bounded():
    assert SUCCESS_PATH == SERVING_GATEWAY_STATES[:7]
    assert SERVING_GATEWAY_STATES[-2:] == ("BLOCKED", "FAILED")
