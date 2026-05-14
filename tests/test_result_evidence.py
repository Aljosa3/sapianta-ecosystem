from sapianta_bridge.active_invocation.invocation_bridge import invoke_provider
from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.result_loop.result_evidence import validate_result_evidence
from sapianta_bridge.result_loop.result_return_loop import return_invocation_result


def _invocation_output() -> dict:
    envelope = create_execution_envelope(
        envelope_id="ENV-RESULT-EVIDENCE",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-RESULT-EVIDENCE",
        validation_requirements=["pytest"],
    ).to_dict()
    return invoke_provider(envelope=envelope, provider=DeterministicMockAdapter())


def test_result_evidence_is_replay_safe_and_valid() -> None:
    output = _invocation_output()
    result = return_invocation_result(
        invocation_result=output["invocation_result"],
        invocation_evidence=output["invocation_evidence"],
    )
    evidence = result["result_evidence"]

    assert evidence["replay_safe"] is True
    assert evidence["interpretation_ready"] is True
    assert validate_result_evidence(evidence)["valid"] is True


def test_result_evidence_rejects_authority_expansion_flags() -> None:
    output = _invocation_output()
    result = return_invocation_result(
        invocation_result=output["invocation_result"],
        invocation_evidence=output["invocation_evidence"],
    )
    evidence = result["result_evidence"]
    evidence["provider_invocation_present"] = True

    assert validate_result_evidence(evidence)["valid"] is False
