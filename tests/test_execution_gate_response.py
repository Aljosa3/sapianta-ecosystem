from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.provider_connectors.codex_cli_connector import prepare_codex_cli_task
from sapianta_bridge.provider_connectors.execution_gate_request import create_execution_gate_request
from sapianta_bridge.provider_connectors.execution_gate_response import create_execution_gate_response
from sapianta_bridge.provider_connectors.execution_gate_validator import validate_execution_gate_response


def _gate_request(tmp_path):
    envelope = create_execution_envelope(
        envelope_id="ENV-GATE-RESPONSE",
        provider_id="codex",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-GATE-RESPONSE",
        validation_requirements=["pytest"],
    ).to_dict()
    connector_request = prepare_codex_cli_task(envelope=envelope, connector_dir=tmp_path)["connector_request"]
    return create_execution_gate_request(
        connector_request=connector_request,
        execution_authorized=True,
        approved_by="human",
        workspace_path=str(tmp_path),
        timeout_seconds=30,
    ).to_dict()


def test_execution_gate_response_captures_result_fields(tmp_path):
    request = _gate_request(tmp_path)
    response = create_execution_gate_response(
        request=request,
        status="SUCCESS",
        stdout="captured",
        stderr="",
        exit_code=0,
        result_metadata={"operation": "CAPTURE_CONNECTOR_TASK"},
    ).to_dict()

    assert response["stdout"] == "captured"
    assert response["stderr"] == ""
    assert response["exit_code"] == 0
    assert response["execution_started_at"] == "1970-01-01T00:00:00Z"
    assert validate_execution_gate_response(response, request=request)["valid"] is True


def test_execution_gate_response_rejects_provider_mismatch(tmp_path):
    request = _gate_request(tmp_path)
    response = create_execution_gate_response(request=request, status="SUCCESS").to_dict()
    response["provider_id"] = "claude"

    validation = validate_execution_gate_response(response, request=request)

    assert validation["valid"] is False
    assert validation["identity_continuity_valid"] is False
