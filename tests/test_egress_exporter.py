from sapianta_bridge.interaction_ingress_egress.egress_exporter import export_egress_artifact, load_egress_artifact


def test_egress_exporter_is_deterministic(tmp_path):
    payload = {"status": "RESULT_RETURNED", "provider_output_rewritten": False}
    path = export_egress_artifact(payload, tmp_path / "egress.json")
    assert load_egress_artifact(path) == payload
