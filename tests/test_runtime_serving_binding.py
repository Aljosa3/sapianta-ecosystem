from sapianta_bridge.live_governed_runtime_serving.runtime_serving_binding import create_runtime_serving_binding


def test_runtime_serving_binding_preserves_ids():
    attachment = {"binding": {"session_runtime_id":"S","interaction_loop_session_id":"L","interaction_turn_id":"T","live_runtime_session_id":"LR","runtime_attachment_session_id":"A","transport_session_id":"TS","governed_session_id":"G","execution_gate_id":"E","provider_invocation_id":"P","bounded_runtime_id":"B","result_capture_id":"C","response_return_id":"R"}}
    assert create_runtime_serving_binding(serving_session={"runtime_serving_session_id":"RS"}, session_runtime_output=attachment).to_dict()["runtime_serving_session_id"] == "RS"
