from sapianta_bridge.live_governed_interaction_serving_gateway.serving_gateway_request import create_serving_gateway_request


def test_serving_gateway_request_preserves_ingress_lineage():
    request = create_serving_gateway_request(
        gateway_session={
            "serving_gateway_session_id": "GW-1",
            "ingress_id": "IN-1",
            "runtime_serving_session_id": "SERVE-1",
            "terminal_attachment_session_id": "TERM-1",
        }
    ).to_dict()
    assert request["ingress_id"] == "IN-1"
    assert request["runtime_serving_session_id"] == "SERVE-1"
