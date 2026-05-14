from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.real_provider_transport.provider_transport_request import create_provider_transport_request
from sapianta_bridge.real_provider_transport.provider_transport_response import create_provider_transport_response
from sapianta_bridge.real_provider_transport.provider_transport_validator import validate_provider_transport_response


def _request() -> dict:
    envelope = create_execution_envelope(
        envelope_id="ENV-TRANSPORT-RESP",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-TRANSPORT-RESP",
        validation_requirements=["pytest"],
    ).to_dict()
    return create_provider_transport_request(envelope).to_dict()


def test_provider_transport_response_preserves_identity() -> None:
    request = _request()
    response = create_provider_transport_response(request=request).to_dict()
    validation = validate_provider_transport_response(response, request=request)

    assert response["transport_id"] == request["transport_id"]
    assert response["provider_id"] == request["provider_id"]
    assert response["provider_response_is_governance_decision"] is False
    assert validation["valid"] is True


def test_provider_transport_response_rejects_identity_mismatch() -> None:
    request = _request()
    response = create_provider_transport_response(request=request).to_dict()
    response["provider_id"] = "codex"

    assert validate_provider_transport_response(response, request=request)["valid"] is False
