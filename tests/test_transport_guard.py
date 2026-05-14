from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.providers.adapters.codex_adapter import CodexAdapter
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.transport.transport_guard import guard_transport
from sapianta_bridge.transport.transport_request import create_transport_request


def _request(provider_id: str = "deterministic_mock") -> dict:
    envelope = create_execution_envelope(
        envelope_id="ENV-GUARD-TRANSPORT",
        provider_id=provider_id,
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-GUARD-TRANSPORT",
        validation_requirements=["pytest"],
    ).to_dict()
    return create_transport_request(envelope).to_dict()


def test_transport_guard_allows_valid_request_and_provider() -> None:
    result = guard_transport(request=_request(), provider=DeterministicMockAdapter())

    assert result["transport_allowed"] is True
    assert result["provider_identity_valid"] is True
    assert result["authority_preserved"] is True
    assert result["workspace_preserved"] is True
    assert result["routing_present"] is False


def test_transport_guard_blocks_provider_identity_mismatch() -> None:
    result = guard_transport(request=_request("codex"), provider=DeterministicMockAdapter())

    assert result["transport_allowed"] is False
    assert {"field": "provider_id", "reason": "provider identity mismatch"} in result["errors"]


def test_transport_guard_detects_authority_mutation() -> None:
    request = _request()
    request["authority_scope"] = ["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION", "RUN_TESTS"]
    result = guard_transport(request=request, provider=DeterministicMockAdapter())

    assert result["transport_allowed"] is False
    assert {"field": "authority_scope", "reason": "authority scope mutation detected"} in result["errors"]


def test_transport_guard_blocks_invalid_request() -> None:
    request = _request("codex")
    request["transport_binding"]["transport_binding_sha256"] = "bad"
    result = guard_transport(request=request, provider=CodexAdapter())

    assert result["transport_allowed"] is False
    assert {"field": "transport_request", "reason": "transport request invalid"} in result["errors"]
