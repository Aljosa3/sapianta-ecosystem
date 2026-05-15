from sapianta_bridge.governed_interaction_loop import create_loop_session, run_interaction_loop_turn


def test_loop_binding_preserves_required_lineage():
    session = create_loop_session(conversation_id="C-1", replay_identity="R-1").to_dict()
    output = run_interaction_loop_turn("Inspect governance evidence", session=session, turn_index=1, execution_gate_id="G-1", bounded_runtime_id="RT-1", result_capture_id="CAP-1")
    binding = output["binding"]
    assert binding["interaction_session_id"] == session["interaction_session_id"]
    assert binding["transport_session_id"]
    assert binding["response_return_id"]
