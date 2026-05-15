from sapianta_bridge.governed_interaction_loop import create_loop_session, run_interaction_loop_turn
from sapianta_bridge.live_governed_interaction_runtime import run_live_governed_interaction_runtime
from sapianta_bridge.live_runtime_interaction_attachment import attach_live_runtime_interaction
from sapianta_bridge.live_governed_session_runtime import create_session_runtime_session, attach_session_runtime_turn


def _attachment(loop, idx, prior_loop_output=None):
    turn = run_interaction_loop_turn("Inspect governance evidence", session=loop, turn_index=idx, execution_gate_id=f"G-{idx}", bounded_runtime_id=f"RT-{idx}", result_capture_id=f"CAP-{idx}", prior_output=prior_loop_output)
    live = run_live_governed_interaction_runtime(loop_session=loop, loop_output=turn)
    return turn, attach_live_runtime_interaction(live_runtime_output=live)


def test_session_runtime_persists_across_turns():
    loop = create_loop_session(conversation_id="C-1", replay_identity="R-1").to_dict()
    runtime = create_session_runtime_session(interaction_loop_session_id=loop["interaction_session_id"]).to_dict()
    first_loop, first_attachment = _attachment(loop, 1)
    second_loop, second_attachment = _attachment(loop, 2, prior_loop_output=first_loop)
    first = attach_session_runtime_turn(session_runtime=runtime, attachment_output=first_attachment)
    second = attach_session_runtime_turn(session_runtime=runtime, attachment_output=second_attachment, prior_output=first)
    assert first["validation"]["valid"] is True
    assert second["validation"]["valid"] is True
    assert first["session_runtime"]["session_runtime_id"] == second["session_runtime"]["session_runtime_id"]


def test_session_runtime_blocks_changed_identity():
    loop = create_loop_session(conversation_id="C-1", replay_identity="R-1").to_dict()
    runtime = create_session_runtime_session(interaction_loop_session_id=loop["interaction_session_id"]).to_dict()
    _, first_attachment = _attachment(loop, 1)
    _, second_attachment = _attachment(loop, 2)
    first = attach_session_runtime_turn(session_runtime=runtime, attachment_output=first_attachment)
    changed = {**runtime, "session_runtime_id": "OTHER"}
    second = attach_session_runtime_turn(session_runtime=changed, attachment_output=second_attachment, prior_output=first)
    assert second["validation"]["valid"] is False
