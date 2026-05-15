from sapianta_bridge.live_governed_session_runtime.session_runtime_session import create_session_runtime_session, validate_session_runtime_session


def test_session_runtime_session_is_deterministic():
    session = create_session_runtime_session(interaction_loop_session_id="L-1").to_dict()
    assert validate_session_runtime_session(session)["valid"] is True
