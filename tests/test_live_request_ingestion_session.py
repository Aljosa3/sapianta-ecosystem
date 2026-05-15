from sapianta_bridge.governed_live_request_ingestion.live_request_ingestion_session import (
    create_live_request_ingestion_session,
    validate_live_request_ingestion_session,
)


def test_live_request_ingestion_session_is_deterministic():
    gateway = {"serving_gateway_session": {"serving_gateway_session_id": "GW-1"}}
    first = create_live_request_ingestion_session(gateway_output=gateway, request_activation_id="ACT-1").to_dict()
    second = create_live_request_ingestion_session(gateway_output=gateway, request_activation_id="ACT-1").to_dict()
    assert first["live_request_ingestion_session_id"] == second["live_request_ingestion_session_id"]
    assert validate_live_request_ingestion_session(first)["valid"] is True
