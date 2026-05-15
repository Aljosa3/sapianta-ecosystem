from sapianta_bridge.human_interaction_continuity.interaction_controller import run_human_interaction_continuity


def test_interaction_controller_creates_continuous_view():
    output = run_human_interaction_continuity("Inspect governance evidence", execution_gate_id="GATE-1")
    assert output["interaction_validation"]["valid"] is True
    assert output["interaction_evidence"]["request_result_associated"] is True
    assert output["interaction_response"]["current_state"] == "RESULT_RETURNED"


def test_interaction_controller_fails_closed_without_gate_lineage():
    output = run_human_interaction_continuity("Inspect governance evidence", execution_gate_id="")
    assert output["interaction_validation"]["valid"] is False
    assert output["interaction_response"]["current_state"] == "BLOCKED"


def test_interaction_controller_does_not_orchestrate():
    output = run_human_interaction_continuity("Inspect governance evidence", execution_gate_id="GATE-1")
    assert output["orchestration_present"] is False
    assert output["autonomous_continuation_present"] is False
    assert output["retry_present"] is False
    assert output["routing_present"] is False
