from sapianta_bridge.governed_interaction_loop import create_loop_session, run_interaction_loop_turn
from sapianta_bridge.live_governed_interaction_runtime import run_live_governed_interaction_runtime


def test_live_runtime_binding_preserves_loop_lineage():
    session = create_loop_session(conversation_id="C-1", replay_identity="R-1").to_dict()
    turn = run_interaction_loop_turn("Inspect governance evidence", session=session, turn_index=1, execution_gate_id="G-1", bounded_runtime_id="RT-1", result_capture_id="CAP-1")
    binding = run_live_governed_interaction_runtime(loop_session=session, loop_output=turn)["live_runtime_binding"]
    assert binding["interaction_turn_id"] == turn["turn"]["turn_id"]
    assert binding["result_capture_id"] == turn["binding"]["result_capture_id"]
