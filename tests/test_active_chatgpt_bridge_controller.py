from sapianta_bridge.active_chatgpt_bridge.bridge_controller import run_active_chatgpt_bridge


def test_active_chatgpt_bridge_controller_completes_single_provider_flow() -> None:
    output = run_active_chatgpt_bridge("Inspect governance evidence", requested_provider_id="deterministic_mock")

    assert output["bridge_validation"]["valid"] is True
    assert output["bridge_evidence"]["bridge_status"] == "COMPLETED"
    assert output["bridge_response"]["result_status"] == "SUCCESS"
    assert output["session_output"]["session_validation"]["valid"] is True


def test_active_chatgpt_bridge_controller_fails_closed_for_unknown_provider() -> None:
    output = run_active_chatgpt_bridge("Inspect governance evidence", requested_provider_id="unknown_provider")

    assert output["bridge_validation"]["valid"] is False
    assert output["bridge_evidence"]["bridge_status"] == "BLOCKED"
    assert output["invocation_output"] == {}


def test_active_chatgpt_bridge_controller_exposes_no_orchestration_or_routing() -> None:
    output = run_active_chatgpt_bridge("Inspect governance evidence")

    assert output["orchestration_present"] is False
    assert output["retry_present"] is False
    assert output["provider_routing_present"] is False
    assert output["autonomous_execution_present"] is False
    assert output["hidden_memory_mutation_present"] is False
