from sapianta_bridge.live_governed_interaction_serving_gateway.serving_gateway_response import create_serving_gateway_response


def test_serving_gateway_response_preserves_egress_lineage():
    response = create_serving_gateway_response(
        gateway_session={"serving_gateway_session_id": "GW-1", "egress_id": "OUT-1"},
        binding={"response_return_id": "RETURN-1"},
    ).to_dict()
    assert response["egress_id"] == "OUT-1"
    assert response["serving_status"] == "SERVING_RESPONSE_EMITTED"
