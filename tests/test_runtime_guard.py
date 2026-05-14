from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.providers.adapters.codex_adapter import CodexAdapter
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.providers.provider_contracts import ProviderContract
from sapianta_bridge.runtime.runtime_binding import create_runtime_binding
from sapianta_bridge.runtime.runtime_guard import guard_runtime


class EscalatingProvider(DeterministicMockAdapter):
    contract = ProviderContract(
        provider_id="deterministic_mock",
        provider_type="DETERMINISTIC_MOCK",
        authority_escalation_allowed=True,
    )


def _envelope(provider_id: str = "deterministic_mock") -> dict:
    return create_execution_envelope(
        envelope_id="ENV-GUARD",
        provider_id=provider_id,
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-GUARD",
        validation_requirements=["pytest"],
    ).to_dict()


def test_runtime_guard_allows_matching_valid_provider() -> None:
    envelope = _envelope()
    result = guard_runtime(
        envelope=envelope,
        provider=DeterministicMockAdapter(),
        binding=create_runtime_binding(envelope),
    )

    assert result["runtime_allowed"] is True
    assert result["provider_identity_valid"] is True
    assert result["routing_present"] is False


def test_runtime_guard_blocks_provider_identity_mismatch() -> None:
    envelope = _envelope("codex")
    result = guard_runtime(
        envelope=envelope,
        provider=DeterministicMockAdapter(),
        binding=create_runtime_binding(envelope),
    )

    assert result["runtime_allowed"] is False
    assert {"field": "provider_id", "reason": "provider identity mismatch"} in result["errors"]


def test_runtime_guard_blocks_missing_binding() -> None:
    envelope = _envelope()
    result = guard_runtime(envelope=envelope, provider=DeterministicMockAdapter(), binding=None)

    assert result["runtime_allowed"] is False
    assert {"field": "binding", "reason": "runtime binding invalid"} in result["errors"]


def test_runtime_guard_blocks_authority_escalation() -> None:
    envelope = _envelope()
    result = guard_runtime(
        envelope=envelope,
        provider=EscalatingProvider(),
        binding=create_runtime_binding(envelope),
    )

    assert result["runtime_allowed"] is False
    assert result["authority_escalation_detected"] is True


def test_runtime_guard_blocks_invalid_envelope() -> None:
    envelope = _envelope()
    envelope["authority_scope"] = ["ROOT_ACCESS"]
    result = guard_runtime(
        envelope=envelope,
        provider=CodexAdapter(),
        binding=create_runtime_binding(_envelope("codex")),
    )

    assert result["runtime_allowed"] is False
    assert {"field": "envelope", "reason": "envelope validation failed"} in result["errors"]
