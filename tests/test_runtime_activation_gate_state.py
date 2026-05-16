from sapianta_bridge.governed_runtime_activation_gate.runtime_activation_gate_state import RUNTIME_ACTIVATION_GATE_STATES, SUCCESS_PATH


def test_runtime_activation_gate_states_are_bounded():
    assert SUCCESS_PATH[-1] == "RUNTIME_ACTIVATION_RESPONSE_EMITTED"
    assert "RUNTIME_ACTIVATION_BLOCKED" in RUNTIME_ACTIVATION_GATE_STATES
    assert "RUNTIME_ACTIVATION_REJECTED" in RUNTIME_ACTIVATION_GATE_STATES
