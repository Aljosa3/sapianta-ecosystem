from sapianta_bridge.governed_interaction_loop import create_loop_session, run_interaction_loop_turn
from sapianta_bridge.live_governed_interaction_runtime import run_live_governed_interaction_runtime
from sapianta_bridge.live_runtime_interaction_attachment import attach_live_runtime_interaction
from sapianta_bridge.live_runtime_interaction_attachment.runtime_attachment_evidence import validate_runtime_attachment_evidence


def test_runtime_attachment_evidence_is_valid():
    loop = create_loop_session(conversation_id="C-1", replay_identity="R-1").to_dict()
    turn = run_interaction_loop_turn("Inspect governance evidence", session=loop, turn_index=1, execution_gate_id="G-1", bounded_runtime_id="RT-1", result_capture_id="CAP-1")
    evidence = attach_live_runtime_interaction(live_runtime_output=run_live_governed_interaction_runtime(loop_session=loop, loop_output=turn))["runtime_attachment_evidence"]
    assert validate_runtime_attachment_evidence(evidence)["valid"] is True
