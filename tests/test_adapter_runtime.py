from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.providers.adapters.codex_adapter import CodexAdapter
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.runtime.adapter_runtime import execute_adapter_runtime


def _envelope(provider_id: str = "deterministic_mock") -> dict:
    return create_execution_envelope(
        envelope_id="ENV-ADAPTER",
        provider_id=provider_id,
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-ADAPTER",
        validation_requirements=["pytest"],
    ).to_dict()


def test_valid_envelope_reaches_deterministic_adapter() -> None:
    result = execute_adapter_runtime(envelope=_envelope(), provider=DeterministicMockAdapter())

    assert result["runtime_result"]["runtime_status"] == "SUCCESS"
    assert result["runtime_result"]["provider_id"] == "deterministic_mock"
    assert result["runtime_evidence"]["runtime_executed"] is True
    assert result["runtime_evidence"]["normalized_result_valid"] is True


def test_invalid_envelope_is_blocked_before_adapter_execution() -> None:
    envelope = _envelope()
    envelope["authority_scope"] = ["ROOT_ACCESS"]
    result = execute_adapter_runtime(envelope=envelope, provider=DeterministicMockAdapter())

    assert result["runtime_result"]["runtime_status"] == "BLOCKED"
    assert result["runtime_evidence"]["runtime_executed"] is False
    assert result["envelope_validation"]["valid"] is False


def test_provider_identity_mismatch_is_blocked() -> None:
    result = execute_adapter_runtime(envelope=_envelope("codex"), provider=DeterministicMockAdapter())

    assert result["runtime_result"]["runtime_status"] == "BLOCKED"
    assert result["runtime_guard"]["provider_identity_valid"] is False


def test_placeholder_codex_adapter_returns_needs_review_not_real_execution() -> None:
    result = execute_adapter_runtime(envelope=_envelope("codex"), provider=CodexAdapter())

    assert result["runtime_result"]["runtime_status"] == "NEEDS_REVIEW"
    assert result["runtime_result"]["normalized_result"]["execution_status"] == "NOT_EXECUTED"
    assert result["runtime_evidence"]["external_api_calls_present"] is False


def test_runtime_exposes_no_routing_or_orchestration() -> None:
    result = execute_adapter_runtime(envelope=_envelope(), provider=DeterministicMockAdapter())

    assert result["routing_present"] is False
    assert result["orchestration_present"] is False
    assert result["runtime_evidence"]["fallback_present"] is False
    assert result["runtime_evidence"]["retry_present"] is False
