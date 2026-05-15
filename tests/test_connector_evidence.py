from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.provider_connectors.connector_evidence import connector_evidence, validate_connector_evidence
from sapianta_bridge.provider_connectors.connector_request import create_connector_request
from sapianta_bridge.provider_connectors.connector_validator import validate_connector_request
from sapianta_bridge.real_provider_transport.provider_transport_request import create_provider_transport_request


def _connector_request():
    envelope = create_execution_envelope(
        envelope_id="ENV-CONNECTOR-EVIDENCE",
        provider_id="codex",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-CONNECTOR-EVIDENCE",
        validation_requirements=["pytest"],
    ).to_dict()
    transport_request = create_provider_transport_request(envelope).to_dict()
    return create_connector_request(
        provider_transport_request=transport_request,
        bounded_task_artifact_path="/tmp/task.json",
        expected_result_artifact_path="/tmp/result.json",
    ).to_dict()


def test_connector_evidence_is_replay_safe_for_prepare_only_request():
    request = _connector_request()
    validation = validate_connector_request(request)
    evidence = connector_evidence(
        connector_request=request,
        request_validation=validation,
        task_artifact_written=True,
    )

    assert evidence["connector_mode"] == "PREPARE_ONLY"
    assert evidence["codex_cli_invoked"] is False
    assert evidence["connector_request_valid"] is True
    assert evidence["replay_safe"] is True
    assert validate_connector_evidence(evidence)["valid"] is True


def test_connector_evidence_rejects_shell_execution():
    request = _connector_request()
    validation = validate_connector_request(request)
    evidence = connector_evidence(
        connector_request=request,
        request_validation=validation,
        task_artifact_written=True,
    )
    evidence["shell_execution_present"] = True

    validation = validate_connector_evidence(evidence)

    assert validation["valid"] is False
    assert any(error["field"] == "shell_execution_present" for error in validation["errors"])
