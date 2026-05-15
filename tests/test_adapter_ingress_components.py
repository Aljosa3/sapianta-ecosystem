from sapianta_bridge.interaction_ingress_egress.ingress_binding import validate_ingress_binding
from sapianta_bridge.interaction_ingress_egress.ingress_request import create_local_ingress_request
from sapianta_bridge.interaction_ingress_egress.ingress_validator import validate_ingress_artifact


def test_local_ingress_request_is_valid():
    artifact = create_local_ingress_request("Inspect", execution_gate_id="GATE-1", bounded_runtime_id="RUNTIME-1", result_capture_id="CAPTURE-1").to_dict()
    assert validate_ingress_artifact(artifact)["valid"] is True


def test_local_ingress_request_blocks_missing_lineage():
    artifact = create_local_ingress_request("Inspect", execution_gate_id="", bounded_runtime_id="RUNTIME-1", result_capture_id="CAPTURE-1").to_dict()
    assert validate_ingress_artifact(artifact)["valid"] is False


def test_local_ingress_binding_rejects_fabricated_empty_continuity():
    assert validate_ingress_binding({})["valid"] is False
