from sapianta_bridge.interaction_transport_bridge.transport_controller import run_interaction_transport_bridge
from sapianta_bridge.interaction_transport_bridge.transport_evidence import validate_transport_evidence


def test_transport_evidence_preserves_lineage():
    output = run_interaction_transport_bridge("Inspect", execution_gate_id="GATE-1", bounded_runtime_id="RUNTIME-1", result_capture_id="CAPTURE-1")
    evidence = output["transport_evidence"]
    assert validate_transport_evidence(evidence)["valid"] is True
    assert evidence["replay_safe"] is True
