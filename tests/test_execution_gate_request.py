from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.provider_connectors.codex_cli_connector import prepare_codex_cli_task
from sapianta_bridge.provider_connectors.execution_gate_request import create_execution_gate_request
from sapianta_bridge.provider_connectors.execution_gate_validator import validate_execution_gate_request


def _connector_request(tmp_path):
    envelope = create_execution_envelope(
        envelope_id="ENV-GATE-REQUEST",
        provider_id="codex",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-GATE-REQUEST",
        validation_requirements=["pytest"],
    ).to_dict()
    return prepare_codex_cli_task(envelope=envelope, connector_dir=tmp_path)["connector_request"]


def test_execution_gate_request_requires_explicit_authorization(tmp_path):
    connector_request = _connector_request(tmp_path)
    request = create_execution_gate_request(
        connector_request=connector_request,
        execution_authorized=True,
        approved_by="human",
        workspace_path=str(tmp_path),
        timeout_seconds=30,
    ).to_dict()

    assert request["execution_authorized"] is True
    assert request["approved_by"] == "human"
    assert request["prepared_artifact_is_execution_authority"] is False
    assert validate_execution_gate_request(request)["valid"] is True


def test_execution_gate_request_blocks_unauthorized_execution(tmp_path):
    request = create_execution_gate_request(
        connector_request=_connector_request(tmp_path),
        execution_authorized=False,
        approved_by="human",
        workspace_path=str(tmp_path),
        timeout_seconds=30,
    ).to_dict()

    validation = validate_execution_gate_request(request)

    assert validation["valid"] is False
    assert validation["authorization_valid"] is False
    assert any(error["field"] == "execution_authorized" for error in validation["errors"])


def test_execution_gate_request_requires_timeout(tmp_path):
    request = create_execution_gate_request(
        connector_request=_connector_request(tmp_path),
        execution_authorized=True,
        approved_by="human",
        workspace_path=str(tmp_path),
        timeout_seconds=30,
    ).to_dict()
    del request["timeout_seconds"]

    validation = validate_execution_gate_request(request)

    assert validation["valid"] is False
    assert any(error["field"] == "timeout_seconds" for error in validation["errors"])
