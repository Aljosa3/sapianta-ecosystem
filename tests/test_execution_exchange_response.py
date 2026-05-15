from sapianta_bridge.governed_execution_exchange.execution_exchange_response import create_execution_exchange_response


def test_execution_exchange_response_pairs_result_and_return():
    response = create_execution_exchange_response(
        binding={"execution_exchange_session_id": "EX-1", "result_capture_id": "CAP-1", "response_return_id": "RETURN-1"}
    ).to_dict()
    assert response["result_capture_id"] == "CAP-1"
    assert response["response_return_id"] == "RETURN-1"
