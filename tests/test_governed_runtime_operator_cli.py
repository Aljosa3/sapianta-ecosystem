from sapianta_system.runtime.operator.cli import invoke_preview_runtime
from sapianta_system.runtime.operator.governed_operator_request import build_operator_request
from sapianta_system.runtime.operator.governed_operator_response import summarize_operator_response
from sapianta_system.runtime.operator.governed_operator_validator import validate_operator_target


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
    assert host == "127.0.0.1"
    assert port == 8010
    return _response(request)


def test_cli_builds_deterministic_payload():
    first = build_operator_request(artifact="TEST_OPERATIONAL_RUNTIME_PROOF_V1")
    second = build_operator_request(artifact="TEST_OPERATIONAL_RUNTIME_PROOF_V1")
    assert first == second


def test_cli_rejects_non_localhost_target():
    assert validate_operator_target(host="0.0.0.0")["valid"] is False
    assert invoke_preview_runtime(
        artifact="TEST_OPERATIONAL_RUNTIME_PROOF_V1",
        host="0.0.0.0",
        transport=_transport,
    )["status"] == "BLOCKED"


def test_cli_rejects_empty_artifact_name():
    assert invoke_preview_runtime(artifact="", transport=_transport)["status"] == "BLOCKED"


def test_cli_handles_returned_response_and_exposes_summary():
    result = invoke_preview_runtime(
        artifact="TEST_OPERATIONAL_RUNTIME_PROOF_V1",
        transport=_transport,
    )
    assert result["status"] == "RETURNED"
    assert result["summary"] == summarize_operator_response(_response(build_operator_request(artifact="TEST_OPERATIONAL_RUNTIME_PROOF_V1")))


def test_cli_fails_closed_on_blocked_response():
    def blocked_transport(request, host, port):
        response = _response(request)
        response["status"] = "BLOCKED"
        response["closure"] = "BLOCKED"
        return response

    assert invoke_preview_runtime(
        artifact="TEST_OPERATIONAL_RUNTIME_PROOF_V1",
        transport=blocked_transport,
    )["status"] == "BLOCKED"


def test_cli_fails_closed_when_replay_evidence_missing():
    def malformed_transport(request, host, port):
        response = _response(request)
        response["evidence"] = {}
        return response

    assert invoke_preview_runtime(
        artifact="TEST_OPERATIONAL_RUNTIME_PROOF_V1",
        transport=malformed_transport,
    )["status"] == "BLOCKED"


def test_cli_does_not_introduce_retries_or_fallbacks():
    request = build_operator_request(artifact="TEST_OPERATIONAL_RUNTIME_PROOF_V1")
    assert request["request_payload"]["interaction_payload"]["orchestration_present"] is False
    assert request["request_payload"]["interaction_payload"]["hidden_routing_present"] is False


def test_cli_output_is_deterministic_for_same_input():
    first = invoke_preview_runtime(artifact="TEST_OPERATIONAL_RUNTIME_PROOF_V1", transport=_transport)
    second = invoke_preview_runtime(artifact="TEST_OPERATIONAL_RUNTIME_PROOF_V1", transport=_transport)
    assert first == second
