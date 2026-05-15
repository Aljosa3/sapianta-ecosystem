from sapianta_bridge.interaction_transport_bridge.transport_controller import run_interaction_transport_bridge
from sapianta_bridge.interaction_transport_bridge.transport_request import validate_transport_request


def test_transport_request_is_replay_safe():
    output = run_interaction_transport_bridge("Inspect", execution_gate_id="GATE-1", bounded_runtime_id="RUNTIME-1", result_capture_id="CAPTURE-1")
    assert validate_transport_request(output["transport_request"])["valid"] is True
