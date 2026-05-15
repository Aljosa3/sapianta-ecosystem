from sapianta_bridge.governed_interaction_loop import create_loop_session
from sapianta_bridge.live_governed_interaction_runtime.live_runtime_session import create_live_runtime_session, validate_live_runtime_session


def test_live_runtime_session_is_deterministic():
    loop = create_loop_session(conversation_id="C-1", replay_identity="R-1").to_dict()
    assert validate_live_runtime_session(create_live_runtime_session(loop_session=loop).to_dict())["valid"] is True
