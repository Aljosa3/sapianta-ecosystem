from sapianta_bridge.active_invocation.invocation_request import create_invocation_request
from sapianta_bridge.active_invocation.invocation_validator import validate_invocation_request
from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter


def _envelope(provider_id: str = "deterministic_mock") -> dict:
    return create_execution_envelope(
        envelope_id="ENV-INV-VAL",
        provider_id=provider_id,
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-INV-VAL",
        validation_requirements=["pytest"],
    ).to_dict()


def test_invocation_validator_allows_valid_explicit_provider() -> None:
    request = create_invocation_request(_envelope()).to_dict()
    validation = validate_invocation_request(
        request=request,
        provider=DeterministicMockAdapter(),
        lifecycle=["PROPOSED"],
    )

    assert validation["valid"] is True
    assert validation["provider_identity_valid"] is True


def test_invocation_validator_blocks_provider_mismatch() -> None:
    request = create_invocation_request(_envelope("codex"), "codex").to_dict()
    validation = validate_invocation_request(
        request=request,
        provider=DeterministicMockAdapter(),
        lifecycle=["PROPOSED"],
    )

    assert validation["valid"] is False
    assert {"field": "provider_id", "reason": "provider identity mismatch"} in validation["errors"]


def test_invocation_validator_blocks_orchestration_flags() -> None:
    request = create_invocation_request(_envelope()).to_dict()
    request["retry_present"] = True
    validation = validate_invocation_request(
        request=request,
        provider=DeterministicMockAdapter(),
        lifecycle=["PROPOSED"],
    )

    assert validation["valid"] is False
    assert {"field": "retry_present", "reason": "orchestration behavior is forbidden"} in validation["errors"]
