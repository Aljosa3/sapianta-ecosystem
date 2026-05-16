from sapianta_bridge.governed_execution_relay.execution_relay_binding import create_execution_relay_binding


def test_execution_relay_binding_preserves_exchange_and_relay_lineage():
    binding = create_execution_relay_binding(
        relay_session={"execution_relay_session_id": "REL-1", "stdin_relay_id": "STDIN-1", "stdout_relay_id": "STDOUT-1"},
        exchange_output={
            "execution_exchange_binding": {
                "execution_exchange_session_id": "EX-1",
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
            }
        },
    ).to_dict()
    assert binding["execution_exchange_session_id"] == "EX-1"
    assert binding["stdin_relay_id"] == "STDIN-1"
