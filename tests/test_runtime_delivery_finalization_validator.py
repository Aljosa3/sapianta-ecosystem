from sapianta_bridge.governed_runtime_delivery_finalization.runtime_delivery_finalization_validator import validate_runtime_delivery_finalization


def _binding():
    return {
        "runtime_delivery_finalization_id": "FIN-1",
        "runtime_execution_commit_id": "COMMIT-1",
        "runtime_activation_gate_id": "ACT-1",
        "local_runtime_bridge_session_id": "BR-1",
        "execution_relay_session_id": "REL-1",
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
        "response_return_id": "",
        "stdin_relay_id": "STDIN-1",
        "stdout_relay_id": "STDOUT-1",
        "runtime_transport_bridge_id": "RTB-1",
        "activation_authorized": True,
        "approved_by": "human",
    }


def test_runtime_delivery_finalization_validator_blocks_missing_response_return():
    result = validate_runtime_delivery_finalization(
        finalization_session={"runtime_delivery_finalization_id": "FIN-1", "runtime_execution_commit_id": "COMMIT-1"},
        binding=_binding(),
        commit_output={"validation": {"valid": True}, "runtime_execution_commit_binding": {"runtime_execution_commit_id": "COMMIT-1"}},
    )
    assert result["valid"] is False
    assert any(error["field"] == "response_return_id" for error in result["errors"])
