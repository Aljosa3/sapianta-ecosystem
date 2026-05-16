from sapianta_bridge.governed_runtime_activation_gate.runtime_activation_gate_request import (
    create_runtime_activation_gate_request,
)


def test_request_preserves_activation_source():
    request = create_runtime_activation_gate_request(
        gate_session={
            "runtime_activation_gate_id": "GATE-1",
            "activation_source_id": "ENTRY-1",
            "activation_source_kind": "operational_entrypoint",
        }
    ).to_dict()
    assert request["activation_source_id"] == "ENTRY-1"
    assert request["activation_source_kind"] == "operational_entrypoint"
