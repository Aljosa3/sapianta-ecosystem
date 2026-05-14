from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.transport.transport_request import (
    create_transport_request,
    validate_transport_request,
)


def _envelope() -> dict:
    return create_execution_envelope(
        envelope_id="ENV-REQUEST",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-REQUEST",
        validation_requirements=["pytest"],
    ).to_dict()


def test_transport_request_is_valid_and_replay_safe() -> None:
    request = create_transport_request(_envelope()).to_dict()
    result = validate_transport_request(request)

    assert result["valid"] is True
    assert result["runtime_binding_valid"] is True
    assert result["transport_binding_valid"] is True
    assert result["immutable_after_validation"] is True
    assert request["implicit_authority_allowed"] is False


def test_transport_request_rejects_implicit_authority() -> None:
    request = create_transport_request(_envelope()).to_dict()
    request["implicit_authority_allowed"] = True
    result = validate_transport_request(request)

    assert result["valid"] is False
    assert {"field": "implicit_authority_allowed", "reason": "implicit authority is forbidden"} in result["errors"]


def test_transport_request_rejects_provider_specific_permissions() -> None:
    request = create_transport_request(_envelope()).to_dict()
    request["provider_specific_permissions_injected"] = True
    result = validate_transport_request(request)

    assert result["valid"] is False
    assert {
        "field": "provider_specific_permissions_injected",
        "reason": "provider-specific permissions are forbidden",
    } in result["errors"]


def test_transport_request_detects_runtime_binding_mismatch() -> None:
    request = create_transport_request(_envelope()).to_dict()
    request["runtime_binding"]["provider_id"] = "codex"
    request["runtime_binding"].pop("binding_sha256")
    result = validate_transport_request(request)

    assert result["valid"] is False
    assert {"field": "provider_id", "reason": "transport request/runtime binding mismatch"} in result["errors"]
