from sapianta_bridge.governed_interaction_loop.interaction_loop_session import create_loop_session
from sapianta_bridge.governed_interaction_loop.interaction_loop_turn import create_loop_turn


def test_loop_turn_carries_explicit_prior_links():
    session = create_loop_session(conversation_id="C-1", replay_identity="R-1").to_dict()
    turn = create_loop_turn(session=session, turn_index=2, human_input="next", prior_turn_id="T-1", prior_response_id="RSP-1").to_dict()
    assert turn["prior_turn_id"] == "T-1"
    assert turn["prior_response_id"] == "RSP-1"
