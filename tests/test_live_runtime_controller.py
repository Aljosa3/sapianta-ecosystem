from sapianta_bridge.governed_interaction_loop import create_loop_session, run_interaction_loop_turn
from sapianta_bridge.live_governed_interaction_runtime import run_live_governed_interaction_runtime


def _loop():
    session = create_loop_session(conversation_id="C-1", replay_identity="R-1").to_dict()
    turn = run_interaction_loop_turn("Inspect governance evidence", session=session, turn_index=1, execution_gate_id="G-1", bounded_runtime_id="RT-1", result_capture_id="CAP-1")
    return session, turn


def test_live_runtime_emits_one_response():
    session, turn = _loop()
    output = run_live_governed_interaction_runtime(loop_session=session, loop_output=turn)
    assert output["validation"]["valid"] is True
    assert output["live_runtime_response"]["runtime_status"] == "LIVE_RESPONSE_EMITTED"


def test_live_runtime_blocks_incomplete_loop_lineage():
    session, _ = _loop()
    output = run_live_governed_interaction_runtime(loop_session=session, loop_output={"turn": {"turn_id": "T-1"}})
    assert output["validation"]["valid"] is False
    assert output["states"] == ["BLOCKED"]
