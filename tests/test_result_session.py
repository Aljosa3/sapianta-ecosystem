from sapianta_bridge.active_invocation.invocation_bridge import invoke_provider
from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.result_loop.result_session import create_result_session


def _invocation_output() -> dict:
    envelope = create_execution_envelope(
        envelope_id="ENV-RESULT-SESSION",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-RESULT-SESSION",
        validation_requirements=["pytest"],
    ).to_dict()
    return invoke_provider(envelope=envelope, provider=DeterministicMockAdapter())


def test_result_session_identity_is_deterministic() -> None:
    output = _invocation_output()
    first = create_result_session(output["invocation_result"], output["invocation_evidence"]).to_dict()
    second = create_result_session(output["invocation_result"], output["invocation_evidence"]).to_dict()

    assert first["result_return_id"] == second["result_return_id"]
    assert first["result_return_id"].startswith("RESULT-")
    assert first["mutable_state_present"] is False


def test_result_session_preserves_lineage() -> None:
    output = _invocation_output()
    session = create_result_session(output["invocation_result"], output["invocation_evidence"]).to_dict()

    assert session["invocation_id"] == output["invocation_result"]["invocation_id"]
    assert session["provider_id"] == "deterministic_mock"
    assert session["envelope_id"] == "ENV-RESULT-SESSION"
    assert session["replay_identity"] == "REPLAY-RESULT-SESSION"
