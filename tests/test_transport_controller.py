from sapianta_bridge.interaction_transport_bridge.transport_controller import run_interaction_transport_bridge


def _run():
    return run_interaction_transport_bridge(
        "Inspect governance evidence",
        execution_gate_id="GATE-1",
        bounded_runtime_id="RUNTIME-1",
        result_capture_id="CAPTURE-1",
    )


def test_transport_controller_creates_bounded_flow():
    output = _run()
    assert output["transport_validation"]["valid"] is True
    assert output["transport_response"]["transport_state"] == "RESULT_RETURNED"


def test_transport_controller_fails_closed_for_missing_lineage():
    output = run_interaction_transport_bridge(
        "Inspect governance evidence",
        execution_gate_id="GATE-1",
        bounded_runtime_id="",
        result_capture_id="CAPTURE-1",
    )
    assert output["transport_validation"]["valid"] is False
    assert output["transport_response"]["transport_state"] == "BLOCKED"


def test_transport_controller_adds_no_forbidden_behavior():
    output = _run()
    assert output["orchestration_present"] is False
    assert output["retry_present"] is False
    assert output["fallback_present"] is False
    assert output["routing_present"] is False
    assert output["autonomous_continuation_present"] is False
