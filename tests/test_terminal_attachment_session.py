from sapianta_bridge.governed_terminal_runtime_attachment.terminal_attachment_session import (
    create_terminal_attachment_session,
    validate_terminal_attachment_session,
)


def test_terminal_attachment_session_is_deterministic():
    serving = {"runtime_serving_session_id": "SERVE-1"}
    first = create_terminal_attachment_session(runtime_serving_session=serving, stdin_binding_id="STDIN-1", stdout_binding_id="STDOUT-1").to_dict()
    second = create_terminal_attachment_session(runtime_serving_session=serving, stdin_binding_id="STDIN-1", stdout_binding_id="STDOUT-1").to_dict()
    assert first["terminal_attachment_session_id"] == second["terminal_attachment_session_id"]
    assert validate_terminal_attachment_session(first)["valid"] is True
