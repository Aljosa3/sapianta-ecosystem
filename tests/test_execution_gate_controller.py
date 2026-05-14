import json

from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.provider_connectors.codex_cli_connector import prepare_codex_cli_task
from sapianta_bridge.provider_connectors.execution_gate_controller import execute_through_execution_gate
from sapianta_bridge.provider_connectors.execution_gate_request import create_execution_gate_request


def _gate_request(tmp_path, *, authorized=True):
    envelope = create_execution_envelope(
        envelope_id="ENV-GATE-CONTROLLER",
        provider_id="codex",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-GATE-CONTROLLER",
        validation_requirements=["pytest"],
    ).to_dict()
    connector_request = prepare_codex_cli_task(envelope=envelope, connector_dir=tmp_path)["connector_request"]
    return create_execution_gate_request(
        connector_request=connector_request,
        execution_authorized=authorized,
        approved_by="human",
        workspace_path=str(tmp_path),
        timeout_seconds=30,
    ).to_dict()


def test_execution_gate_controller_captures_deterministic_result(tmp_path):
    request = _gate_request(tmp_path)

    result = execute_through_execution_gate(request=request)

    assert result["execution_gate_status"] == "SUCCESS"
    response = result["execution_gate_response"]
    stdout = json.loads(response["stdout"])
    assert response["exit_code"] == 0
    assert response["stderr"] == ""
    assert stdout["captured_provider_id"] == "codex"
    assert stdout["captured_envelope_id"] == request["envelope_id"]
    assert result["execution_gate_evidence"]["orchestration_present"] is False
    assert result["execution_gate_evidence"]["retry_present"] is False
    assert result["execution_gate_evidence"]["routing_present"] is False


def test_execution_gate_controller_blocks_unauthorized_execution(tmp_path):
    request = _gate_request(tmp_path, authorized=False)

    result = execute_through_execution_gate(request=request)

    assert result["execution_gate_status"] == "BLOCKED"
    assert result["execution_gate_response"]["status"] == "BLOCKED"
    assert result["execution_gate_evidence"]["request_valid"] is False
    assert result["execution_gate_evidence"]["replay_safe"] is False
