from sapianta_bridge.governed_interaction_loop import create_loop_session, run_interaction_loop_turn
from sapianta_bridge.live_governed_interaction_runtime import run_live_governed_interaction_runtime
from sapianta_bridge.live_runtime_interaction_attachment import attach_live_runtime_interaction
from sapianta_bridge.live_governed_session_runtime import create_session_runtime_session, attach_session_runtime_turn
from sapianta_bridge.live_governed_runtime_serving import create_runtime_serving_session, attach_runtime_serving_turn


def _session_output(loop, runtime, idx, prior_loop=None, prior_session=None):
    turn = run_interaction_loop_turn("Inspect governance evidence", session=loop, turn_index=idx, execution_gate_id=f"G-{idx}", bounded_runtime_id=f"RT-{idx}", result_capture_id=f"CAP-{idx}", prior_output=prior_loop)
    live = run_live_governed_interaction_runtime(loop_session=loop, loop_output=turn)
    attachment = attach_live_runtime_interaction(live_runtime_output=live)
    return turn, attach_session_runtime_turn(session_runtime=runtime, attachment_output=attachment, prior_output=prior_session)


def test_runtime_serving_reuses_serving_identity():
    loop = create_loop_session(conversation_id="C-1", replay_identity="R-1").to_dict()
    runtime = create_session_runtime_session(interaction_loop_session_id=loop["interaction_session_id"]).to_dict()
    serving = create_runtime_serving_session(session_runtime=runtime).to_dict()
    first_loop, first_session = _session_output(loop, runtime, 1)
    _, second_session = _session_output(loop, runtime, 2, prior_loop=first_loop, prior_session=first_session)
    first = attach_runtime_serving_turn(serving_session=serving, session_runtime_output=first_session)
    second = attach_runtime_serving_turn(serving_session=serving, session_runtime_output=second_session, prior_output=first)
    assert first["validation"]["valid"] is True
    assert second["validation"]["valid"] is True
    assert first["runtime_serving_session"]["runtime_serving_session_id"] == second["runtime_serving_session"]["runtime_serving_session_id"]
