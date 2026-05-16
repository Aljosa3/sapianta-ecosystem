from sapianta_bridge.governed_runtime_delivery_finalization.runtime_delivery_finalization_state import RUNTIME_DELIVERY_FINALIZATION_STATES, SUCCESS_PATH


def test_runtime_delivery_finalization_states_are_explicit():
    assert SUCCESS_PATH[-1] == "RUNTIME_DELIVERY_FINALIZATION_CLOSED"
    assert "RUNTIME_DELIVERY_FINALIZATION_BLOCKED" in RUNTIME_DELIVERY_FINALIZATION_STATES
    assert "RUNTIME_DELIVERY_FINALIZATION_REJECTED" in RUNTIME_DELIVERY_FINALIZATION_STATES
