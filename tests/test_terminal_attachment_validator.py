from sapianta_bridge.governed_terminal_runtime_attachment.terminal_attachment_validator import validate_terminal_attachment


def test_terminal_attachment_validator_blocks_missing_stdout():
    result = validate_terminal_attachment(
        terminal_session={
            "terminal_attachment_session_id": "TERM-1",
            "runtime_serving_session_id": "SERVE-1",
            "stdin_binding_id": "STDIN-1",
            "stdout_binding_id": "",
        },
        binding={
            "terminal_attachment_session_id": "TERM-1",
            "runtime_serving_session_id": "SERVE-1",
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
            "stdin_binding_id": "STDIN-1",
            "stdout_binding_id": "",
        },
        runtime_serving_output={"validation": {"valid": True}},
    )
    assert result["valid"] is False
    assert any(error["field"] == "stdout_binding_id" for error in result["errors"])
