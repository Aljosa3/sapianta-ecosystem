from sapianta_bridge.governed_execution_exchange.execution_exchange_request import create_execution_exchange_request


def test_execution_exchange_request_preserves_ingestion_identity():
    request = create_execution_exchange_request(
        exchange_session={"execution_exchange_session_id": "EX-1", "live_request_ingestion_session_id": "INGEST-1"}
    ).to_dict()
    assert request["live_request_ingestion_session_id"] == "INGEST-1"
