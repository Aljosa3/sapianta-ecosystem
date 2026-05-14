from sapianta_bridge.active_invocation.invocation_bridge import invoke_provider
from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter


def _envelope(provider_id: str = "deterministic_mock") -> dict:
    return create_execution_envelope(
        envelope_id="ENV-INV-BRIDGE",
        provider_id=provider_id,
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-INV-BRIDGE",
        validation_requirements=["pytest"],
    ).to_dict()


def test_invocation_bridge_invokes_single_explicit_provider() -> None:
    output = invoke_provider(envelope=_envelope(), provider=DeterministicMockAdapter())

    assert output["invocation_result"]["invocation_status"] == "SUCCESS"
    assert output["invocation_evidence"]["invocation_executed"] is True
    assert output["invocation_evidence"]["provider_identity_valid"] is True
    assert output["invocation_evidence"]["normalized_result_bound"] is True


def test_invocation_bridge_blocks_invalid_envelope_without_runtime_delivery() -> None:
    envelope = _envelope()
    envelope["authority_scope"] = ["ROOT_ACCESS"]
    output = invoke_provider(envelope=envelope, provider=DeterministicMockAdapter())

    assert output["invocation_result"]["invocation_status"] == "BLOCKED"
    assert output["invocation_evidence"]["invocation_executed"] is False
    assert output["runtime_output"] == {}


def test_invocation_bridge_fails_closed_on_malformed_envelope() -> None:
    output = invoke_provider(envelope={"provider_id": "deterministic_mock"}, provider=DeterministicMockAdapter())

    assert output["invocation_result"]["invocation_status"] == "BLOCKED"
    assert output["invocation_validation"]["valid"] is False
    assert output["runtime_output"] == {}


def test_invocation_bridge_blocks_provider_mismatch() -> None:
    output = invoke_provider(envelope=_envelope("codex"), provider=DeterministicMockAdapter(), provider_id="codex")

    assert output["invocation_result"]["invocation_status"] == "BLOCKED"
    assert output["invocation_validation"]["provider_identity_valid"] is False


def test_invocation_bridge_exposes_no_orchestration_retry_or_routing() -> None:
    output = invoke_provider(envelope=_envelope(), provider=DeterministicMockAdapter())

    assert output["routing_present"] is False
    assert output["retry_present"] is False
    assert output["fallback_present"] is False
    assert output["orchestration_present"] is False
    assert output["invocation_evidence"]["adaptive_provider_selection_present"] is False
