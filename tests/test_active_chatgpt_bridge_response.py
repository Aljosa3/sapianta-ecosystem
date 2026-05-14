from sapianta_bridge.active_chatgpt_bridge.bridge_controller import run_active_chatgpt_bridge
from sapianta_bridge.active_chatgpt_bridge.bridge_response import validate_bridge_response


def test_active_chatgpt_bridge_response_preserves_lineage() -> None:
    output = run_active_chatgpt_bridge("Inspect governance evidence")
    response = output["bridge_response"]

    assert response["bridge_id"] == output["bridge_binding"]["bridge_id"]
    assert response["session_id"] == output["session_output"]["session_identity"]["session_id"]
    assert response["invocation_id"] == output["invocation_output"]["invocation_result"]["invocation_id"]
    assert response["provider_id"] == "deterministic_mock"
    assert response["interpretation_ready_payload"]["interpretation_ready"] is True
    assert validate_bridge_response(response)["valid"] is True


def test_active_chatgpt_bridge_response_grants_no_authority() -> None:
    response = run_active_chatgpt_bridge("Inspect governance evidence")["bridge_response"]

    assert response["follow_up_tasks_executed"] is False
    assert response["autonomous_interpretation_present"] is False
    assert response["provider_output_hidden"] is False
    assert response["result_lineage_mutated"] is False
    assert response["execution_authority_granted"] is False


def test_active_chatgpt_bridge_response_rejects_hidden_follow_up_execution() -> None:
    response = run_active_chatgpt_bridge("Inspect governance evidence")["bridge_response"]
    response["follow_up_tasks_executed"] = True

    assert validate_bridge_response(response)["valid"] is False
