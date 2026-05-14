from sapianta_bridge.active_invocation.invocation_request import create_invocation_request
from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope


def _envelope() -> dict:
    return create_execution_envelope(
        envelope_id="ENV-INV-REQ",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-INV-REQ",
        validation_requirements=["pytest"],
    ).to_dict()


def test_invocation_request_binds_envelope_provider_and_runtime() -> None:
    request = create_invocation_request(_envelope()).to_dict()

    assert request["provider_id"] == "deterministic_mock"
    assert request["runtime_binding"]["provider_id"] == "deterministic_mock"
    assert request["invocation_binding"]["provider_id"] == "deterministic_mock"
    assert request["provider_auto_selection"] is False


def test_invocation_request_exposes_no_orchestration_flags() -> None:
    request = create_invocation_request(_envelope()).to_dict()

    assert request["routing_present"] is False
    assert request["retry_present"] is False
    assert request["fallback_present"] is False
    assert request["concurrent_execution_present"] is False
