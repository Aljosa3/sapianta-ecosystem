from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.envelopes.envelope_validator import validate_execution_envelope
from sapianta_bridge.providers.normalized_result import NormalizedExecutionResult
from sapianta_bridge.runtime.runtime_evidence import runtime_evidence
from sapianta_bridge.runtime.runtime_result import create_runtime_result


def _envelope() -> dict:
    return create_execution_envelope(
        envelope_id="ENV-EVIDENCE",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-EVIDENCE",
        validation_requirements=["pytest"],
    ).to_dict()


def test_runtime_evidence_is_replay_safe_and_deterministic() -> None:
    envelope = _envelope()
    guard = {"runtime_allowed": True, "provider_identity_valid": True}
    runtime_result = create_runtime_result(
        envelope=envelope,
        normalized_result=NormalizedExecutionResult(
            provider_id="deterministic_mock",
            execution_status="SUCCESS",
        ),
        guard_status=guard,
    )

    first = runtime_evidence(
        runtime_result=runtime_result,
        envelope_validation=validate_execution_envelope(envelope),
        guard_status=guard,
    )
    second = runtime_evidence(
        runtime_result=runtime_result,
        envelope_validation=validate_execution_envelope(envelope),
        guard_status=guard,
    )

    assert first == second
    assert first["runtime_executed"] is True
    assert first["normalized_result_valid"] is True
    assert first["routing_present"] is False
    assert first["external_api_calls_present"] is False
