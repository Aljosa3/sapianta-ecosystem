from sapianta_bridge.governed_execution_exchange.execution_exchange_session import (
    create_execution_exchange_session,
    validate_execution_exchange_session,
)


def test_execution_exchange_session_is_deterministic():
    ingestion = {"live_request_ingestion_session": {"live_request_ingestion_session_id": "INGEST-1"}}
    first = create_execution_exchange_session(ingestion_output=ingestion).to_dict()
    second = create_execution_exchange_session(ingestion_output=ingestion).to_dict()
    assert first["execution_exchange_session_id"] == second["execution_exchange_session_id"]
    assert validate_execution_exchange_session(first)["valid"] is True
