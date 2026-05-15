from sapianta_bridge.governed_live_request_ingestion.live_request_ingestion_request import create_live_request_ingestion_request


def test_live_request_ingestion_request_preserves_activation_identity():
    request = create_live_request_ingestion_request(
        ingestion_session={
            "live_request_ingestion_session_id": "INGEST-1",
            "serving_gateway_session_id": "GW-1",
            "request_activation_id": "ACT-1",
        }
    ).to_dict()
    assert request["request_activation_id"] == "ACT-1"
