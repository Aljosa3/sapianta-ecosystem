from sapianta_bridge.human_interaction_continuity.interaction_controller import run_human_interaction_continuity
from sapianta_bridge.human_interaction_continuity.interaction_response import validate_interaction_response


def test_interaction_response_exposes_human_execution_view():
    output = run_human_interaction_continuity("Inspect governance evidence", execution_gate_id="GATE-1")
    response = output["interaction_response"]
    assert validate_interaction_response(response)["valid"] is True
    assert response["current_state"] == "RESULT_RETURNED"
    assert response["result_payload"]["interpretation_ready"] is True
