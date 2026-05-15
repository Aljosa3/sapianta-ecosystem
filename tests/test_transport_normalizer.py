from sapianta_bridge.interaction_transport_bridge.transport_controller import run_interaction_transport_bridge
from sapianta_bridge.interaction_transport_bridge.transport_normalizer import validate_transport_normalization


def test_transport_normalization_is_deterministic_and_non_mutating():
    output = run_interaction_transport_bridge("Inspect", execution_gate_id="GATE-1", bounded_runtime_id="RUNTIME-1", result_capture_id="CAPTURE-1")
    normalized = output["normalized_result"]
    assert validate_transport_normalization(normalized)["valid"] is True
    assert normalized["missing_output_synthesized"] is False
    assert normalized["provider_success_fabricated"] is False
    assert normalized["execution_evidence_altered"] is False
