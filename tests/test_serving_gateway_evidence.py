from sapianta_bridge.live_governed_interaction_serving_gateway.serving_gateway_evidence import serving_gateway_evidence


def test_serving_gateway_evidence_records_ingress_and_egress():
    evidence = serving_gateway_evidence(binding={"ingress_id": "IN-1", "egress_id": "OUT-1"}, valid=True, states=("SERVING_GATEWAY_CREATED",))
    assert evidence["ingress_replay_visible"] is True
    assert evidence["egress_replay_visible"] is True
    assert evidence["continuity_fabricated"] is False
