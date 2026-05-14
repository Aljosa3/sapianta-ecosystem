from sapianta_bridge.no_copy_paste_loop.loop_controller import run_no_copy_paste_loop


def test_loop_controller_runs_single_pass_no_copy_paste_flow() -> None:
    output = run_no_copy_paste_loop("Inspect governance evidence")

    assert output["loop_validation"]["valid"] is True
    assert output["loop_evidence"]["loop_status"] == "COMPLETED"
    assert output["loop_response"]["result_status"] == "SUCCESS"
    assert output["bridge_output"]["bridge_validation"]["valid"] is True


def test_loop_controller_fails_closed_for_unknown_provider() -> None:
    output = run_no_copy_paste_loop("Inspect governance evidence", requested_provider_id="unknown_provider")

    assert output["loop_validation"]["valid"] is False
    assert output["loop_evidence"]["loop_status"] == "BLOCKED"
    assert output["bridge_output"] == {}


def test_loop_controller_enforces_no_orchestration_boundaries() -> None:
    output = run_no_copy_paste_loop("Inspect governance evidence")

    assert output["orchestration_present"] is False
    assert output["retry_present"] is False
    assert output["provider_routing_present"] is False
    assert output["autonomous_execution_present"] is False
    assert output["hidden_memory_mutation_present"] is False
