from sapianta_bridge.governed_terminal_runtime_attachment.terminal_attachment_response import create_terminal_attachment_response


def test_terminal_attachment_response_preserves_return_identity():
    response = create_terminal_attachment_response(
        binding={"terminal_attachment_session_id": "TERM-1", "response_return_id": "RETURN-1"}
    ).to_dict()
    assert response["response_return_id"] == "RETURN-1"
    assert response["terminal_status"] == "TERMINAL_RESPONSE_EMITTED"
