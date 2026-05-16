from sapianta_bridge.governed_runtime_activation_gate.runtime_activation_gate_session import (
    create_runtime_activation_gate_session,
    validate_runtime_activation_gate_session,
)


def test_runtime_activation_gate_session_is_deterministic():
    bridge = {"local_runtime_bridge_session": {"local_runtime_bridge_session_id": "BR-1"}}
    first = create_runtime_activation_gate_session(bridge_output=bridge, activation_authorized=True, approved_by="human").to_dict()
    second = create_runtime_activation_gate_session(bridge_output=bridge, activation_authorized=True, approved_by="human").to_dict()
    assert first["runtime_activation_gate_id"] == second["runtime_activation_gate_id"]
    assert validate_runtime_activation_gate_session(first)["valid"] is True
