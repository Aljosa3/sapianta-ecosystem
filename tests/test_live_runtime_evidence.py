from sapianta_bridge.governed_interaction_loop import create_loop_session, run_interaction_loop_turn
from sapianta_bridge.live_governed_interaction_runtime import run_live_governed_interaction_runtime
from sapianta_bridge.live_governed_interaction_runtime.live_runtime_evidence import validate_live_runtime_evidence


def test_live_runtime_evidence_preserves_lineage():
    session = create_loop_session(conversation_id="C-1", replay_identity="R-1").to_dict()
    turn = run_interaction_loop_turn("Inspect governance evidence", session=session, turn_index=1, execution_gate_id="G-1", bounded_runtime_id="RT-1", result_capture_id="CAP-1")
    evidence = run_live_governed_interaction_runtime(loop_session=session, loop_output=turn)["live_runtime_evidence"]
    assert validate_live_runtime_evidence(evidence)["valid"] is True
    assert evidence["provider_hidden_state_trusted"] is False
