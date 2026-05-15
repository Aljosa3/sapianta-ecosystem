from sapianta_bridge.governed_live_request_ingestion.live_request_ingestion_validator import validate_live_request_ingestion


def test_live_request_ingestion_validator_blocks_missing_activation():
    result = validate_live_request_ingestion(
        ingestion_session={
            "live_request_ingestion_session_id": "INGEST-1",
            "serving_gateway_session_id": "GW-1",
            "request_activation_id": "",
        },
        binding={
            "live_request_ingestion_session_id": "INGEST-1",
            "serving_gateway_session_id": "GW-1",
            "runtime_serving_session_id": "SERVE-1",
            "terminal_attachment_session_id": "TERM-1",
            "session_runtime_id": "SESSION-1",
            "interaction_loop_session_id": "LOOP-1",
            "interaction_turn_id": "TURN-1",
            "live_runtime_session_id": "LIVE-1",
            "runtime_attachment_session_id": "ATTACH-1",
            "transport_session_id": "TRANSPORT-1",
            "governed_session_id": "GOV-1",
            "execution_gate_id": "GATE-1",
            "provider_invocation_id": "PROVIDER-1",
            "bounded_runtime_id": "RUNTIME-1",
            "result_capture_id": "CAPTURE-1",
            "response_return_id": "RETURN-1",
            "request_activation_id": "",
        },
        gateway_output={"validation": {"valid": True}, "serving_gateway_binding": {"serving_gateway_session_id": "GW-1"}},
    )
    assert result["valid"] is False
    assert any(error["field"] == "request_activation_id" for error in result["errors"])
