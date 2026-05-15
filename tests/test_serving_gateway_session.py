from sapianta_bridge.live_governed_interaction_serving_gateway.serving_gateway_session import (
    create_serving_gateway_session,
    validate_serving_gateway_session,
)


def test_serving_gateway_session_is_deterministic():
    terminal = {"terminal_attachment_binding": {"runtime_serving_session_id": "SERVE-1", "terminal_attachment_session_id": "TERM-1"}}
    first = create_serving_gateway_session(terminal_output=terminal, ingress_id="IN-1", egress_id="OUT-1").to_dict()
    second = create_serving_gateway_session(terminal_output=terminal, ingress_id="IN-1", egress_id="OUT-1").to_dict()
    assert first["serving_gateway_session_id"] == second["serving_gateway_session_id"]
    assert validate_serving_gateway_session(first)["valid"] is True
