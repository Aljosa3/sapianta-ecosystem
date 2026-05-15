from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.provider_connectors.connector_request import create_connector_request
from sapianta_bridge.provider_connectors.connector_response import create_connector_response
from sapianta_bridge.provider_connectors.connector_validator import validate_connector_request, validate_connector_response
from sapianta_bridge.real_provider_transport.provider_transport_request import create_provider_transport_request
from sapianta_bridge.real_provider_transport.provider_transport_response import create_provider_transport_response


def _valid_chain():
    envelope = create_execution_envelope(
        envelope_id="ENV-CONNECTOR-VALIDATOR",
        provider_id="codex",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-CONNECTOR-VALIDATOR",
        validation_requirements=["pytest"],
    ).to_dict()
    transport_request = create_provider_transport_request(envelope).to_dict()
    connector_request = create_connector_request(
        provider_transport_request=transport_request,
        bounded_task_artifact_path="/tmp/task.json",
        expected_result_artifact_path="/tmp/result.json",
    ).to_dict()
    transport_response = create_provider_transport_response(request=transport_request).to_dict()
    connector_response = create_connector_response(
        connector_request=connector_request,
        provider_transport_response=transport_response,
        result_artifact_path="/tmp/result.json",
    ).to_dict()
    return connector_request, connector_response


def test_connector_validator_accepts_valid_request_and_response():
    connector_request, connector_response = _valid_chain()

    assert validate_connector_request(connector_request)["valid"] is True
    assert validate_connector_response(connector_response, request=connector_request)["valid"] is True


def test_connector_validator_rejects_malformed_request():
    validation = validate_connector_request({"provider_id": "codex"})

    assert validation["valid"] is False
    assert any(error["field"] == "connector_id" for error in validation["errors"])


def test_connector_validator_rejects_replay_mismatch():
    connector_request, connector_response = _valid_chain()
    connector_response["replay_identity"] = "REPLAY-MUTATED"

    validation = validate_connector_response(connector_response, request=connector_request)

    assert validation["valid"] is False
    assert validation["identity_continuity_valid"] is False
