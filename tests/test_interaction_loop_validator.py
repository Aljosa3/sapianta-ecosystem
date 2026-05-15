from sapianta_bridge.governed_interaction_loop import create_loop_session, run_interaction_loop_turn
from sapianta_bridge.governed_interaction_loop.interaction_loop_validator import validate_turn_continuity


def test_loop_validator_blocks_invalid_prior_response_link():
    session = create_loop_session(conversation_id="C-1", replay_identity="R-1").to_dict()
    first = run_interaction_loop_turn("Inspect governance evidence", session=session, turn_index=1, execution_gate_id="G-1", bounded_runtime_id="RT-1", result_capture_id="CAP-1")
    bad_prior = {**first, "binding": {**first["binding"], "response_return_id": "WRONG"}}
    second = run_interaction_loop_turn("Inspect governance evidence", session=session, turn_index=2, execution_gate_id="G-2", bounded_runtime_id="RT-2", result_capture_id="CAP-2", prior_output=bad_prior)
    # Controller uses explicit given prior; it remains self-consistent. Tamper after construction to exercise validator directly.
    tampered_turn = {**second["turn"], "prior_response_id": "NOT-THE-PRIOR"}
    result = validate_turn_continuity(session=session, turn=tampered_turn, prior_output=first, binding=second["binding"], transport_output=second["transport_output"])
    assert result["valid"] is False
