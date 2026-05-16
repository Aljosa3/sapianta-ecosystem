from sapianta_bridge.governed_runtime_activation_gate.runtime_activation_gate_session import (
    create_runtime_activation_gate_session,
    validate_runtime_activation_gate_session,
)


def test_runtime_activation_gate_session_is_deterministic():
    entrypoint = {"activation": {"operational_runtime_entrypoint_id": "ENTRY-1"}}
    first = create_runtime_activation_gate_session(entrypoint_output=entrypoint).to_dict()
    second = create_runtime_activation_gate_session(entrypoint_output=entrypoint).to_dict()
    assert first["runtime_activation_gate_id"] == second["runtime_activation_gate_id"]
    assert first["activation_source_kind"] == "operational_entrypoint"
    assert validate_runtime_activation_gate_session(first)["valid"] is True
