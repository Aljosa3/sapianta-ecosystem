import json

from sapianta_bridge.interaction_ingress_egress.egress_exporter import load_egress_artifact
from sapianta_bridge.interaction_ingress_egress.ingress_controller import run_local_ingress_egress
from sapianta_bridge.interaction_ingress_egress.ingress_request import create_local_ingress_request
from sapianta_bridge.interaction_ingress_egress.ingress_evidence import validate_ingress_evidence


def _artifact(tmp_path):
    artifact = create_local_ingress_request(
        "Inspect governance evidence",
        execution_gate_id="GATE-1",
        bounded_runtime_id="RUNTIME-1",
        result_capture_id="CAPTURE-1",
    ).to_dict()
    path = tmp_path / "ingress.json"
    path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")
    return path


def test_local_ingress_egress_exports_deterministic_response(tmp_path):
    egress = tmp_path / "egress.json"
    output = run_local_ingress_egress(ingress_path=_artifact(tmp_path), egress_path=egress)
    exported = load_egress_artifact(egress)
    assert output["ingress_validation"]["valid"] is True
    assert exported == output["ingress_response"]
    assert output["states"][-1] == "EGRESS_EXPORTED"


def test_local_ingress_egress_preserves_continuity(tmp_path):
    output = run_local_ingress_egress(ingress_path=_artifact(tmp_path), egress_path=tmp_path / "egress.json")
    evidence = output["ingress_evidence"]
    assert validate_ingress_evidence(evidence)["valid"] is True
    assert evidence["transport_session_id"]
    assert evidence["result_capture_id"] == "CAPTURE-1"


def test_local_ingress_egress_fails_closed_on_malformed_json(tmp_path):
    ingress = tmp_path / "bad.json"
    ingress.write_text("{", encoding="utf-8")
    output = run_local_ingress_egress(ingress_path=ingress, egress_path=tmp_path / "egress.json")
    assert output["ingress_validation"]["valid"] is False
    assert output["ingress_response"]["state"] == "BLOCKED"
