from sapianta_bridge.active_invocation.invocation_bridge import invoke_provider
from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.result_loop.result_payload import create_result_payload


def _invocation_output() -> dict:
    envelope = create_execution_envelope(
        envelope_id="ENV-RESULT-PAYLOAD",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-RESULT-PAYLOAD",
        validation_requirements=["pytest"],
    ).to_dict()
    return invoke_provider(envelope=envelope, provider=DeterministicMockAdapter())


def test_result_payload_preserves_normalized_provider_result() -> None:
    output = _invocation_output()
    payload = create_result_payload(output["invocation_result"], output["invocation_evidence"]).to_dict()

    assert payload["invocation_id"] == output["invocation_result"]["invocation_id"]
    assert payload["provider_id"] == "deterministic_mock"
    assert payload["execution_status"] == "SUCCESS"
    assert payload["normalized_provider_result"]["execution_status"] == "SUCCESS"
    assert payload["interpretation_ready"] is True


def test_result_payload_grants_no_hidden_authority() -> None:
    output = _invocation_output()
    payload = create_result_payload(output["invocation_result"], output["invocation_evidence"]).to_dict()

    assert payload["autonomous_interpretation_present"] is False
    assert payload["hidden_instructions_generated"] is False
    assert payload["provider_invocation_present"] is False
    assert payload["execution_authority_granted"] is False
