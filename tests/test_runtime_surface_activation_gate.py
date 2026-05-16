from sapianta_bridge.governed_runtime_surface_activation.runtime_surface_activation_gate import (
    OPERATIONAL_PATH,
    validate_activation_transitions,
)


def test_operational_path_is_deterministic():
    assert validate_activation_transitions(OPERATIONAL_PATH)["valid"] is True


def test_invalid_transition_is_rejected():
    assert validate_activation_transitions(("SURFACE_REGISTERED", "SURFACE_VALIDATED"))["valid"] is False
