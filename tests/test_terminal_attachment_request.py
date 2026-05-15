from sapianta_bridge.governed_terminal_runtime_attachment.terminal_attachment_request import create_terminal_attachment_request


def test_terminal_attachment_request_preserves_terminal_bindings():
    request = create_terminal_attachment_request(
        terminal_session={
            "terminal_attachment_session_id": "TERM-1",
            "runtime_serving_session_id": "SERVE-1",
            "stdin_binding_id": "STDIN-1",
            "stdout_binding_id": "STDOUT-1",
        }
    ).to_dict()
    assert request == {
        "terminal_attachment_session_id": "TERM-1",
        "runtime_serving_session_id": "SERVE-1",
        "stdin_binding_id": "STDIN-1",
        "stdout_binding_id": "STDOUT-1",
    }
