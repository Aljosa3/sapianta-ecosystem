from sapianta_bridge.governed_runtime_activation_gate.runtime_activation_gate_state import (
    RUNTIME_ACTIVATION_GATE_STATES,
    SUCCESS_PATH,
)


def test_states_distinguish_authority_from_continuity():
    assert SUCCESS_PATH[-1] == "RUNTIME_ACTIVATION_APPROVED"
    assert "RUNTIME_ACTIVATION_ADMISSION_VALIDATED" in RUNTIME_ACTIVATION_GATE_STATES
    assert "BLOCKED" in RUNTIME_ACTIVATION_GATE_STATES
