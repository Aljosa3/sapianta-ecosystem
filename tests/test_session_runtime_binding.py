from sapianta_bridge.live_governed_session_runtime.session_runtime_binding import create_session_runtime_binding


def test_session_runtime_binding_preserves_attachment_lineage():
    binding = create_session_runtime_binding(session_runtime={"session_runtime_id":"S"}, attachment_output={"runtime_attachment_binding":{"interaction_loop_session_id":"L","interaction_turn_id":"T","live_runtime_session_id":"LR","runtime_attachment_session_id":"A","transport_session_id":"TS","governed_session_id":"G","execution_gate_id":"EG","provider_invocation_id":"P","bounded_runtime_id":"B","result_capture_id":"C","response_return_id":"R"}}).to_dict()
    assert binding["runtime_attachment_session_id"] == "A"
