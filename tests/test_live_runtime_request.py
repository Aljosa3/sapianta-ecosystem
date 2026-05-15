from sapianta_bridge.governed_interaction_loop import create_loop_session, run_interaction_loop_turn
from sapianta_bridge.live_governed_interaction_runtime.live_runtime_request import create_live_runtime_request
from sapianta_bridge.live_governed_interaction_runtime.live_runtime_session import create_live_runtime_session


def test_live_runtime_request_binds_turn():
    session = create_loop_session(conversation_id="C-1", replay_identity="R-1").to_dict()
    turn = run_interaction_loop_turn("Inspect governance evidence", session=session, turn_index=1, execution_gate_id="G-1", bounded_runtime_id="RT-1", result_capture_id="CAP-1")
    runtime = create_live_runtime_session(loop_session=session).to_dict()
    request = create_live_runtime_request(session=runtime, loop_output=turn).to_dict()
    assert request["interaction_turn_id"] == turn["turn"]["turn_id"]
