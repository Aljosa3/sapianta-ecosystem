from sapianta_bridge.governed_interaction_loop import create_loop_session, run_interaction_loop_turn
from sapianta_bridge.governed_interaction_loop.interaction_loop_evidence import validate_loop_evidence


def test_loop_evidence_is_replay_safe_and_non_autonomous():
    session = create_loop_session(conversation_id="C-1", replay_identity="R-1").to_dict()
    output = run_interaction_loop_turn("Inspect governance evidence", session=session, turn_index=1, execution_gate_id="G-1", bounded_runtime_id="RT-1", result_capture_id="CAP-1")
    assert validate_loop_evidence(output["evidence"])["valid"] is True
    assert output["evidence"]["implicit_memory_present"] is False
