from sapianta_bridge.governed_execution_relay.execution_relay_session import (
    create_execution_relay_session,
    validate_execution_relay_session,
)


def test_execution_relay_session_is_deterministic():
    exchange = {"execution_exchange_session": {"execution_exchange_session_id": "EX-1"}}
    terminal = {"terminal_attachment_binding": {"stdin_binding_id": "STDIN-1", "stdout_binding_id": "STDOUT-1"}}
    first = create_execution_relay_session(exchange_output=exchange, terminal_output=terminal).to_dict()
    second = create_execution_relay_session(exchange_output=exchange, terminal_output=terminal).to_dict()
    assert first["execution_relay_session_id"] == second["execution_relay_session_id"]
    assert validate_execution_relay_session(first)["valid"] is True
