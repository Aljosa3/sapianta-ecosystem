from sapianta_bridge.active_invocation.invocation_request import create_invocation_request
from sapianta_bridge.active_invocation.invocation_result import (
    create_invocation_result,
    validate_invocation_result,
)
from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.runtime.adapter_runtime import execute_adapter_runtime


def _envelope() -> dict:
    return create_execution_envelope(
        envelope_id="ENV-INV-RESULT",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-INV-RESULT",
        validation_requirements=["pytest"],
    ).to_dict()


def test_invocation_result_wraps_runtime_and_normalized_result() -> None:
    envelope = _envelope()
    request = create_invocation_request(envelope).to_dict()
    runtime_output = execute_adapter_runtime(envelope=envelope, provider=DeterministicMockAdapter())
    result = create_invocation_result(
        request=request,
        runtime_output=runtime_output,
        lifecycle=["PROPOSED", "VALIDATED", "INVOKED", "RESULT_RECEIVED", "EVIDENCE_RECORDED"],
    ).to_dict()

    assert result["invocation_status"] == "SUCCESS"
    assert result["normalized_result"]["execution_status"] == "SUCCESS"
    assert validate_invocation_result(result)["valid"] is True


def test_invocation_result_rejects_adaptive_interpretation() -> None:
    envelope = _envelope()
    request = create_invocation_request(envelope).to_dict()
    runtime_output = execute_adapter_runtime(envelope=envelope, provider=DeterministicMockAdapter())
    result = create_invocation_result(
        request=request,
        runtime_output=runtime_output,
        lifecycle=["PROPOSED", "VALIDATED", "INVOKED", "RESULT_RECEIVED", "EVIDENCE_RECORDED"],
    ).to_dict()
    result["adaptive_interpretation_present"] = True

    assert validate_invocation_result(result)["valid"] is False
