from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.provider_connectors.connector_request import create_connector_request
from sapianta_bridge.provider_connectors.connector_validator import validate_connector_request
from sapianta_bridge.real_provider_transport.provider_transport_request import create_provider_transport_request


def _transport_request():
    envelope = create_execution_envelope(
        envelope_id="ENV-CONNECTOR-REQUEST",
        provider_id="codex",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-CONNECTOR-REQUEST",
        validation_requirements=["pytest"],
    ).to_dict()
    return create_provider_transport_request(envelope).to_dict()


def test_connector_request_preserves_transport_identity():
    transport_request = _transport_request()
    request = create_connector_request(
        provider_transport_request=transport_request,
        bounded_task_artifact_path="/tmp/task.json",
        expected_result_artifact_path="/tmp/result.json",
    ).to_dict()

    assert request["provider_id"] == transport_request["provider_id"]
    assert request["envelope_id"] == transport_request["envelope_id"]
    assert request["invocation_id"] == transport_request["invocation_id"]
    assert request["transport_id"] == transport_request["transport_id"]
    assert request["connector_mode"] == "PREPARE_ONLY"
    assert request["connector_artifact_is_execution_authority"] is False
    assert validate_connector_request(request)["valid"] is True


def test_connector_request_rejects_retry_instruction():
    transport_request = _transport_request()
    request = create_connector_request(
        provider_transport_request=transport_request,
        bounded_task_artifact_path="/tmp/task.json",
        expected_result_artifact_path="/tmp/result.json",
    ).to_dict()
    request["retry_present"] = True

    validation = validate_connector_request(request)

    assert validation["valid"] is False
    assert any(error["field"] == "retry_present" for error in validation["errors"])
