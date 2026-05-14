from sapianta_bridge.active_invocation.invocation_bridge import invoke_provider
from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.result_loop.result_binding import create_result_binding, validate_result_binding


def _invocation_output() -> dict:
    envelope = create_execution_envelope(
        envelope_id="ENV-RESULT-BIND",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-RESULT-BIND",
        validation_requirements=["pytest"],
    ).to_dict()
    return invoke_provider(envelope=envelope, provider=DeterministicMockAdapter())


def test_result_binding_is_replay_safe_and_valid() -> None:
    output = _invocation_output()
    binding = create_result_binding(output["invocation_result"], output["invocation_evidence"]).to_dict()
    validation = validate_result_binding(binding)

    assert validation["valid"] is True
    assert binding["replay_safe"] is True


def test_result_binding_rejects_invalid_replay_binding() -> None:
    output = _invocation_output()
    binding = create_result_binding(output["invocation_result"], output["invocation_evidence"]).to_dict()
    binding["binding_sha256"] = "bad-hash"
    validation = validate_result_binding(binding)

    assert validation["valid"] is False
    assert {"field": "binding_sha256", "reason": "result binding hash mismatch"} in validation["errors"]
