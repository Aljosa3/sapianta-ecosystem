from sapianta_bridge.governed_execution_exchange.execution_exchange_state import EXECUTION_EXCHANGE_STATES, SUCCESS_PATH


def test_execution_exchange_states_are_bounded():
    assert SUCCESS_PATH == EXECUTION_EXCHANGE_STATES[:6]
    assert EXECUTION_EXCHANGE_STATES[-2:] == ("BLOCKED", "FAILED")
