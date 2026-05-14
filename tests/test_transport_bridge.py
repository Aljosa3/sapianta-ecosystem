from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.providers.adapters.codex_adapter import CodexAdapter
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.transport.transport_bridge import execute_transport_bridge


def _envelope(provider_id: str = "deterministic_mock") -> dict:
    return create_execution_envelope(
        envelope_id="ENV-BRIDGE",
        provider_id=provider_id,
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-BRIDGE",
        validation_requirements=["pytest"],
    ).to_dict()


def test_transport_bridge_delivers_valid_envelope_to_runtime() -> None:
    result = execute_transport_bridge(envelope=_envelope(), provider=DeterministicMockAdapter())

    assert result["transport_response"]["transport_status"] == "SUCCESS"
    assert result["transport_evidence"]["transport_executed"] is True
    assert result["transport_evidence"]["authority_preserved"] is True
    assert result["transport_evidence"]["workspace_preserved"] is True


def test_transport_bridge_blocks_invalid_envelope() -> None:
    envelope = _envelope()
    envelope["authority_scope"] = ["ROOT_ACCESS"]
    result = execute_transport_bridge(envelope=envelope, provider=DeterministicMockAdapter())

    assert result["transport_response"]["transport_status"] == "BLOCKED"
    assert result["transport_response"]["transport_evidence"]["transport_executed"] is False
    assert result["envelope_validation"]["valid"] is False


def test_transport_bridge_blocks_provider_mismatch() -> None:
    result = execute_transport_bridge(envelope=_envelope("codex"), provider=DeterministicMockAdapter())

    assert result["transport_response"]["transport_status"] == "BLOCKED"
    assert result["transport_guard"]["provider_identity_valid"] is False


def test_transport_bridge_preserves_placeholder_adapter_semantics() -> None:
    result = execute_transport_bridge(envelope=_envelope("codex"), provider=CodexAdapter())

    assert result["transport_response"]["transport_status"] == "NEEDS_REVIEW"
    assert result["transport_response"]["normalized_result"]["execution_status"] == "NOT_EXECUTED"


def test_transport_bridge_exposes_no_orchestration_or_retry() -> None:
    result = execute_transport_bridge(envelope=_envelope(), provider=DeterministicMockAdapter())

    assert result["routing_present"] is False
    assert result["orchestration_present"] is False
    assert result["transport_evidence"]["fallback_present"] is False
    assert result["transport_evidence"]["retry_present"] is False
