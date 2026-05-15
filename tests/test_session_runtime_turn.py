from sapianta_bridge.live_governed_session_runtime.session_runtime_turn import create_session_runtime_turn


def test_session_runtime_turn_references_prior_turn():
    current = create_session_runtime_turn(session_runtime={"session_runtime_id":"S-1"}, attachment_output={"runtime_attachment_binding":{"interaction_turn_id":"T-2"}}, prior_output={"turn":{"interaction_turn_id":"T-1"}}).to_dict()
    assert current["prior_interaction_turn_id"] == "T-1"
