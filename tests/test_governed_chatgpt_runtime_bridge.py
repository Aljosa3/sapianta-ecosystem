from sapianta_system.runtime.chatgpt_bridge import invoke_from_chatgpt_bridge
from sapianta_system.runtime.chatgpt_bridge.governed_chatgpt_bridge_evidence import governed_chatgpt_bridge_evidence
from sapianta_system.runtime.chatgpt_bridge.governed_chatgpt_bridge_request import create_chatgpt_bridge_request
from sapianta_system.runtime.chatgpt_bridge.governed_chatgpt_bridge_replay import validate_chatgpt_bridge_replay
from sapianta_system.runtime.operator.governed_operator_request import build_operator_request


def _response(request):
    return {
        "preview_runtime_request_id": request["preview_runtime_request_id"],
        "runtime_invocation_response_id": "INVOCATION-RESP-1",
        "invocation_replay_identity": "REPLAY-1",
        "lineage": request["lineage"],
        "evidence": {
            "localhost_only": True,
            "response_returned": True,
            "replay_safe": True,
            "orchestration_present": False,
            "hidden_continuation_present": False,
            "hidden_execution_present": False,
            "hidden_mutable_state_present": False,
        },
        "closure_id": "CLOSURE-1",
        "preview_runtime_response_id": "PREVIEW-RESP-1",
        "response_sha256": "HASH",
        "status": "RETURNED",
        "closure": "PASS",
    }


def _transport(request, host, port):
    assert request == build_operator_request(artifact="TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1")
    assert host == "127.0.0.1"
    assert port == 8110
    return _response(request)


def test_valid_bridge_request_produces_governed_request():
    request = create_chatgpt_bridge_request(
        artifact="TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1",
        host="127.0.0.1",
        port=8110,
    )
    assert request["tool_name"] == "sapianta_governed_invoke"
    assert validate_chatgpt_bridge_replay(request)["valid"] is True


def test_non_localhost_target_rejected():
    assert invoke_from_chatgpt_bridge(
        "TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1",
        host="0.0.0.0",
        transport=_transport,
    )["status"] == "BLOCKED"


def test_empty_artifact_rejected():
    assert invoke_from_chatgpt_bridge("", transport=_transport)["status"] == "BLOCKED"


def test_malformed_runtime_response_rejected():
    def malformed_transport(request, host, port):
        response = _response(request)
        response["evidence"] = {}
        return response

    assert invoke_from_chatgpt_bridge(
        "TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1",
        transport=malformed_transport,
    )["status"] == "BLOCKED"


def test_blocked_runtime_response_rejected():
    def blocked_transport(request, host, port):
        response = _response(request)
        response["status"] = "BLOCKED"
        response["closure"] = "BLOCKED"
        return response

    assert invoke_from_chatgpt_bridge(
        "TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1",
        transport=blocked_transport,
    )["status"] == "BLOCKED"


def test_returned_runtime_response_accepted_and_summary_preserved():
    result = invoke_from_chatgpt_bridge(
        "TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1",
        transport=_transport,
    )
    assert result == {
        "status": "RETURNED",
        "closure": "PASS",
        "request_id": build_operator_request(artifact="TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1")["preview_runtime_request_id"],
        "response_id": "PREVIEW-RESP-1",
        "replay_identity": "REPLAY-1",
        "evidence": {"localhost_only": True, "response_returned": True, "replay_safe": True},
        "chatgpt_bridge_request_id": create_chatgpt_bridge_request(
            artifact="TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1",
            host="127.0.0.1",
            port=8110,
        )["chatgpt_bridge_request_id"],
    }


def test_bridge_evidence_preserves_replay_without_retry_or_fallback():
    request = create_chatgpt_bridge_request(
        artifact="TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1",
        host="127.0.0.1",
        port=8110,
    )
    response = invoke_from_chatgpt_bridge(
        "TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1",
        transport=_transport,
    )
    evidence = governed_chatgpt_bridge_evidence(request=request, response=response)
    assert evidence["localhost_only"] is True
    assert evidence["retry_present"] is False
    assert evidence["fallback_present"] is False
    assert evidence["orchestration_present"] is False


def test_bridge_output_is_deterministic_for_same_input():
    first = invoke_from_chatgpt_bridge("TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1", transport=_transport)
    second = invoke_from_chatgpt_bridge("TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1", transport=_transport)
    assert first == second
