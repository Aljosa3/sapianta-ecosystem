from sapianta_bridge.governed_runtime_operation_envelope.runtime_operation_envelope import (
    create_runtime_operation_envelope_record,
)


def test_operation_envelope_identity_is_deterministic():
    binding = {"runtime_activation_gate_id": "GATE-1"}
    first = create_runtime_operation_envelope_record(
        activation_binding=binding, operation_type="READ_STATE", operation_intent="read bounded state"
    )
    second = create_runtime_operation_envelope_record(
        activation_binding=binding, operation_type="READ_STATE", operation_intent="read bounded state"
    )
    assert first == second
