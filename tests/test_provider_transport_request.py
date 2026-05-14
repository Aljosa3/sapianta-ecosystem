from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.real_provider_transport.provider_transport_request import create_provider_transport_request
from sapianta_bridge.real_provider_transport.provider_transport_validator import validate_provider_transport_request


def _envelope() -> dict:
    return create_execution_envelope(
        envelope_id="ENV-TRANSPORT-REQ",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-TRANSPORT-REQ",
        validation_requirements=["pytest"],
    ).to_dict()


def test_provider_transport_request_is_valid_and_bounded() -> None:
    request = create_provider_transport_request(_envelope()).to_dict()
    validation = validate_provider_transport_request(request)

    assert request["provider_id"] == "deterministic_mock"
    assert request["bounded_task_payload"]["allowed_actions"] == ["inspect"]
    assert request["transport_artifact_is_execution_authority"] is False
    assert validation["valid"] is True


def test_provider_transport_request_rejects_routing_or_retry_flags() -> None:
    request = create_provider_transport_request(_envelope()).to_dict()
    request["routing_present"] = True

    assert validate_provider_transport_request(request)["valid"] is False
