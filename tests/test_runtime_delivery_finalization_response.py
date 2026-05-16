from sapianta_bridge.governed_runtime_delivery_finalization.runtime_delivery_finalization_response import create_runtime_delivery_finalization_response


def test_runtime_delivery_finalization_response_preserves_delivery_lineage():
    response = create_runtime_delivery_finalization_response(
        binding={"runtime_delivery_finalization_id": "FIN-1", "result_capture_id": "CAP-1", "response_return_id": "RETURN-1"}
    ).to_dict()
    assert response["result_capture_id"] == "CAP-1"
    assert response["finalization_status"] == "RUNTIME_DELIVERY_FINALIZATION_CLOSED"
