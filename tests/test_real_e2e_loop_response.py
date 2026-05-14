from sapianta_bridge.real_e2e_codex_loop.e2e_loop_binding import RealE2ELoopBinding
from sapianta_bridge.real_e2e_codex_loop.e2e_loop_response import create_e2e_loop_response
from sapianta_bridge.real_e2e_codex_loop.e2e_loop_validator import validate_e2e_loop_response


def _response():
    request = {"loop_id": "LOOP-1", "provider_id": "codex_cli", "replay_identity": "REPLAY-1"}
    result_payload = {
        "result_return_id": "RESULT-1",
        "invocation_id": "INV-1",
        "provider_id": "codex_cli",
        "envelope_id": "ENV-1",
        "execution_status": "SUCCESS",
        "normalized_provider_result": {"execution_status": "SUCCESS"},
        "replay_identity": "REPLAY-1",
        "interpretation_ready": True,
    }
    binding = RealE2ELoopBinding(
        loop_id="LOOP-1",
        ingress_request_id="INGRESS-1",
        semantic_request_id="SEM-1",
        envelope_id="ENV-1",
        connector_id="CONN-1",
        execution_gate_id="GATE-1",
        invocation_id="INV-1",
        result_return_id="RESULT-1",
        provider_id="codex_cli",
        replay_identity="REPLAY-1",
    ).to_dict()
    return request, create_e2e_loop_response(
        request=request,
        result_payload=result_payload,
        loop_binding=binding,
        evidence_references={"execution_gate_id": "GATE-1"},
    ).to_dict()


def test_real_e2e_loop_response_is_chatgpt_facing():
    request, response = _response()

    assert response["chatgpt_response_payload"]["interpretation_ready"] is True
    assert response["manual_copy_paste_required"] is False
    assert validate_e2e_loop_response(response, request=request)["valid"] is True


def test_real_e2e_loop_response_rejects_retry_flag():
    request, response = _response()
    response["retry_present"] = True

    validation = validate_e2e_loop_response(response, request=request)

    assert validation["valid"] is False
    assert any(error["field"] == "retry_present" for error in validation["errors"])
