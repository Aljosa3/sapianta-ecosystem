from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.runtime.adapter_runtime import execute_adapter_runtime
from sapianta_bridge.transport.transport_evidence import transport_evidence
from sapianta_bridge.transport.transport_guard import guard_transport
from sapianta_bridge.transport.transport_request import create_transport_request


def test_transport_evidence_is_deterministic_and_replay_safe() -> None:
    envelope = create_execution_envelope(
        envelope_id="ENV-EVIDENCE-TRANSPORT",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-EVIDENCE-TRANSPORT",
        validation_requirements=["pytest"],
    ).to_dict()
    request = create_transport_request(envelope).to_dict()
    guard = guard_transport(request=request, provider=DeterministicMockAdapter())
    runtime = execute_adapter_runtime(envelope=envelope, provider=DeterministicMockAdapter())

    first = transport_evidence(request=request, runtime_output=runtime, guard_status=guard)
    second = transport_evidence(request=request, runtime_output=runtime, guard_status=guard)

    assert first == second
    assert first["transport_executed"] is True
    assert first["transport_binding_valid"] is True
    assert first["runtime_binding_valid"] is True
    assert first["routing_present"] is False
    assert first["fallback_present"] is False
