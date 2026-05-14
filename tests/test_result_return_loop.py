from sapianta_bridge.active_invocation.invocation_bridge import invoke_provider
from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.result_loop.result_return_loop import return_invocation_result


def _invocation_output() -> dict:
    envelope = create_execution_envelope(
        envelope_id="ENV-RESULT-LOOP",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-RESULT-LOOP",
        validation_requirements=["pytest"],
    ).to_dict()
    return invoke_provider(envelope=envelope, provider=DeterministicMockAdapter())


def test_result_return_loop_produces_interpretation_ready_payload() -> None:
    output = _invocation_output()
    result = return_invocation_result(
        invocation_result=output["invocation_result"],
        invocation_evidence=output["invocation_evidence"],
    )

    assert result["result_validation"]["valid"] is True
    assert result["result_payload"]["interpretation_ready"] is True
    assert result["result_evidence"]["result_returned"] is True


def test_result_return_loop_fails_closed_on_missing_evidence() -> None:
    output = _invocation_output()
    result = return_invocation_result(invocation_result=output["invocation_result"], invocation_evidence={})

    assert result["result_payload"]["interpretation_ready"] is False
    assert result["result_validation"]["valid"] is False
    assert result["result_evidence"]["result_returned"] is False


def test_result_return_loop_does_not_invoke_or_orchestrate() -> None:
    output = _invocation_output()
    result = return_invocation_result(
        invocation_result=output["invocation_result"],
        invocation_evidence=output["invocation_evidence"],
    )

    assert result["provider_invocation_present"] is False
    assert result["retry_present"] is False
    assert result["orchestration_present"] is False
    assert result["autonomous_interpretation_present"] is False
