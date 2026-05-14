from sapianta_bridge.no_copy_paste_loop.loop_controller import run_no_copy_paste_loop
from sapianta_bridge.no_copy_paste_loop.loop_response import validate_loop_response


def test_loop_response_delivers_chatgpt_payload_deterministically() -> None:
    output = run_no_copy_paste_loop("Inspect governance evidence")
    response = output["loop_response"]

    assert response["loop_id"] == output["loop_binding"]["loop_id"]
    assert response["result_status"] == "SUCCESS"
    assert response["chatgpt_response_payload"]["interpretation_ready"] is True
    assert response["chatgpt_response_payload"]["provider_id"] == "deterministic_mock"
    assert validate_loop_response(response)["valid"] is True


def test_loop_response_rejects_malformed_response() -> None:
    assert validate_loop_response({"loop_id": "LOOP"}).get("valid") is False


def test_loop_response_rejects_hidden_execution_authority() -> None:
    response = run_no_copy_paste_loop("Inspect governance evidence")["loop_response"]
    response["autonomous_continuation_present"] = True

    assert validate_loop_response(response)["valid"] is False
