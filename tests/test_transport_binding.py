from sapianta_bridge.interaction_transport_bridge.transport_binding import validate_transport_binding
from sapianta_bridge.interaction_transport_bridge.transport_controller import run_interaction_transport_bridge


def test_transport_binding_preserves_explicit_lineage():
    output = run_interaction_transport_bridge("Inspect", execution_gate_id="GATE-1", bounded_runtime_id="RUNTIME-1", result_capture_id="CAPTURE-1")
    binding = output["transport_binding"]
    assert validate_transport_binding(binding)["valid"] is True
    assert binding["execution_gate_id"] == "GATE-1"
    assert binding["bounded_runtime_id"] == "RUNTIME-1"
    assert binding["result_capture_id"] == "CAPTURE-1"
