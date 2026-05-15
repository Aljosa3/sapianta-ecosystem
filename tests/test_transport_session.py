from sapianta_bridge.interaction_transport_bridge.transport_controller import run_interaction_transport_bridge
from sapianta_bridge.interaction_transport_bridge.transport_session import validate_transport_session


def test_transport_session_is_deterministic():
    output = run_interaction_transport_bridge("Inspect", execution_gate_id="GATE-1", bounded_runtime_id="RUNTIME-1", result_capture_id="CAPTURE-1")
    assert validate_transport_session(output["transport_session"])["valid"] is True
