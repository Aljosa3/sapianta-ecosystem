from sapianta_bridge.governed_interaction_loop import create_loop_session, run_interaction_loop_turn


def test_loop_controller_supports_two_explicit_turns():
    session = create_loop_session(conversation_id="C-1", replay_identity="R-1").to_dict()
    first = run_interaction_loop_turn("Inspect governance evidence", session=session, turn_index=1, execution_gate_id="G-1", bounded_runtime_id="RT-1", result_capture_id="CAP-1")
    second = run_interaction_loop_turn("Inspect governance evidence", session=session, turn_index=2, execution_gate_id="G-2", bounded_runtime_id="RT-2", result_capture_id="CAP-2", prior_output=first)
    assert first["validation"]["valid"] is True
    assert second["validation"]["valid"] is True
    assert second["binding"]["prior_turn_id"] == first["turn"]["turn_id"]
    assert second["binding"]["prior_response_id"] == first["binding"]["response_return_id"]


def test_loop_controller_blocks_missing_prior_lineage():
    session = create_loop_session(conversation_id="C-1", replay_identity="R-1").to_dict()
    second = run_interaction_loop_turn("Inspect governance evidence", session=session, turn_index=2, execution_gate_id="G-2", bounded_runtime_id="RT-2", result_capture_id="CAP-2")
    assert second["validation"]["valid"] is False
    assert second["states"] == ["BLOCKED"]
