from sapianta_bridge.live_governed_interaction_serving_gateway.serving_gateway_validator import validate_serving_gateway


def _binding():
    return {
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
        "ingress_id": "IN-1",
        "egress_id": "",
    }


def test_serving_gateway_validator_blocks_missing_egress():
    result = validate_serving_gateway(
        gateway_session={
            "serving_gateway_session_id": "GW-1",
            "runtime_serving_session_id": "SERVE-1",
            "terminal_attachment_session_id": "TERM-1",
            "ingress_id": "IN-1",
            "egress_id": "",
        },
        binding=_binding(),
        terminal_output={
            "validation": {"valid": True},
            "terminal_attachment_binding": {"runtime_serving_session_id": "SERVE-1", "terminal_attachment_session_id": "TERM-1"},
        },
    )
    assert result["valid"] is False
    assert any(error["field"] == "egress_id" for error in result["errors"])
