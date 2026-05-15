from sapianta_bridge.human_interaction_continuity.interaction_request import create_interaction_request
from sapianta_bridge.human_interaction_continuity.interaction_session import create_interaction_session, validate_interaction_session


def test_interaction_session_is_deterministic_and_replay_safe():
    request = create_interaction_request("Inspect", conversation_id="C-1", execution_gate_id="G-1", replay_identity="R-1").to_dict()
    session = create_interaction_session(request=request, governed_session_id="S-1").to_dict()
    assert session == create_interaction_session(request=request, governed_session_id="S-1").to_dict()
    assert validate_interaction_session(session)["valid"] is True
