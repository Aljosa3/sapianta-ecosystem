from sapianta_bridge.governed_live_request_ingestion.live_request_ingestion_response import create_live_request_ingestion_response


def test_live_request_ingestion_response_preserves_return_identity():
    response = create_live_request_ingestion_response(
        binding={"live_request_ingestion_session_id": "INGEST-1", "response_return_id": "RETURN-1"}
    ).to_dict()
    assert response["response_return_id"] == "RETURN-1"
    assert response["ingestion_status"] == "LIVE_RESPONSE_CONTINUITY_READY"
