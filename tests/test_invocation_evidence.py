from sapianta_bridge.active_invocation.invocation_bridge import invoke_provider
from sapianta_bridge.active_invocation.invocation_evidence import validate_invocation_evidence
from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter


def _envelope() -> dict:
    return create_execution_envelope(
        envelope_id="ENV-INV-EVIDENCE",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-INV-EVIDENCE",
        validation_requirements=["pytest"],
    ).to_dict()


def test_invocation_evidence_is_replay_safe_and_valid() -> None:
    output = invoke_provider(envelope=_envelope(), provider=DeterministicMockAdapter())
    evidence = output["invocation_evidence"]

    assert evidence["replay_safe"] is True
    assert evidence["lifecycle_valid"] is True
    assert validate_invocation_evidence(evidence)["valid"] is True


def test_invocation_evidence_rejects_orchestration_flags() -> None:
    output = invoke_provider(envelope=_envelope(), provider=DeterministicMockAdapter())
    evidence = output["invocation_evidence"]
    evidence["routing_present"] = True

    assert validate_invocation_evidence(evidence)["valid"] is False
