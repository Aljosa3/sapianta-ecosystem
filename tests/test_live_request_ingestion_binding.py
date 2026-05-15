from sapianta_bridge.governed_live_request_ingestion.live_request_ingestion_binding import create_live_request_ingestion_binding


def test_live_request_ingestion_binding_preserves_gateway_lineage():
    binding = create_live_request_ingestion_binding(
        ingestion_session={"live_request_ingestion_session_id": "INGEST-1", "request_activation_id": "ACT-1"},
        gateway_output={
            "serving_gateway_binding": {
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
            }
        },
    ).to_dict()
    assert binding["serving_gateway_session_id"] == "GW-1"
    assert binding["request_activation_id"] == "ACT-1"
