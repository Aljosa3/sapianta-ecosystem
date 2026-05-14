from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.real_provider_transport.provider_transport_request import create_provider_transport_request
from sapianta_bridge.real_provider_transport.provider_transport_response import create_provider_transport_response
from sapianta_bridge.real_provider_transport.provider_transport_validator import (
    validate_envelope_for_transport,
    validate_provider_transport_request,
    validate_provider_transport_response,
)


def _envelope() -> dict:
    return create_execution_envelope(
        envelope_id="ENV-TRANSPORT-VAL",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-TRANSPORT-VAL",
        validation_requirements=["pytest"],
    ).to_dict()


def test_provider_transport_validator_accepts_valid_chain() -> None:
    envelope = _envelope()
    request = create_provider_transport_request(envelope).to_dict()
    response = create_provider_transport_response(request=request).to_dict()

    assert validate_envelope_for_transport(envelope)["valid"] is True
    assert validate_provider_transport_request(request)["valid"] is True
    assert validate_provider_transport_response(response, request=request)["valid"] is True


def test_provider_transport_validator_rejects_malformed_request() -> None:
    validation = validate_provider_transport_request({"provider_id": "deterministic_mock"})

    assert validation["valid"] is False


def test_provider_transport_validator_rejects_response_retry_flag() -> None:
    request = create_provider_transport_request(_envelope()).to_dict()
    response = create_provider_transport_response(request=request).to_dict()
    response["retry_present"] = True

    assert validate_provider_transport_response(response, request=request)["valid"] is False
