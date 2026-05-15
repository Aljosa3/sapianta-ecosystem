from sapianta_bridge.governed_interaction_loop.interaction_loop_session import create_loop_session, validate_loop_session


def test_loop_session_is_deterministic():
    first = create_loop_session(conversation_id="C-1", replay_identity="R-1").to_dict()
    second = create_loop_session(conversation_id="C-1", replay_identity="R-1").to_dict()
    assert first == second
    assert validate_loop_session(first)["valid"] is True
