from sapianta_system.runtime.mcp_wrapper import SAPIANTA_GOVERNED_INVOKE_TOOL, handle_sapianta_governed_invoke
from sapianta_system.runtime.mcp_wrapper.sapianta_mcp_server import call_tool, list_tools


def _bridge_response():
    return {
        "status": "RETURNED",
        "closure": "PASS",
        "request_id": "REQ-1",
        "response_id": "RESP-1",
        "replay_identity": "REPLAY-1",
        "evidence": {"localhost_only": True, "response_returned": True, "replay_safe": True},
    }


def _bridge(*args, **kwargs):
    assert args == ("TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1",)
    assert kwargs == {"host": "127.0.0.1", "port": 8110}
    return _bridge_response()


def test_tool_schema_exists_and_registry_exposes_exactly_one_tool():
    assert SAPIANTA_GOVERNED_INVOKE_TOOL["name"] == "sapianta_governed_invoke"
    assert list_tools() == [SAPIANTA_GOVERNED_INVOKE_TOOL]


def test_valid_mcp_input_calls_existing_bridge():
    result = handle_sapianta_governed_invoke(
        {"artifact": "TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1"},
        bridge=_bridge,
    )
    assert result == _bridge_response()


def test_returned_response_is_deterministic():
    first = handle_sapianta_governed_invoke(
        {"artifact": "TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1"},
        bridge=_bridge,
    )
    second = handle_sapianta_governed_invoke(
        {"artifact": "TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1"},
        bridge=_bridge,
    )
    assert first == second


def test_non_localhost_target_is_rejected():
    assert handle_sapianta_governed_invoke(
        {"artifact": "TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1", "host": "0.0.0.0"},
        bridge=_bridge,
    )["status"] == "BLOCKED"


def test_empty_artifact_is_rejected():
    assert handle_sapianta_governed_invoke({"artifact": ""}, bridge=_bridge)["status"] == "BLOCKED"


def test_malformed_bridge_response_is_rejected():
    def malformed_bridge(*args, **kwargs):
        return {"status": "RETURNED", "closure": "PASS"}

    assert handle_sapianta_governed_invoke(
        {"artifact": "TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1"},
        bridge=malformed_bridge,
    )["status"] == "BLOCKED"


def test_missing_replay_evidence_is_rejected():
    def no_evidence_bridge(*args, **kwargs):
        response = _bridge_response()
        response["evidence"] = {}
        return response

    assert handle_sapianta_governed_invoke(
        {"artifact": "TEST_REAL_OPERATIONAL_NO_COPY_PASTE_PROOF_V1"},
        bridge=no_evidence_bridge,
    )["status"] == "BLOCKED"


def test_wrapper_has_no_retry_fallback_or_orchestration_surface():
    schema_text = str(SAPIANTA_GOVERNED_INVOKE_TOOL)
    assert "retry" not in schema_text.lower()
    assert "fallback" not in schema_text.lower()
    assert call_tool("unknown", {})["status"] == "BLOCKED"
