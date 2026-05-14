from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.providers.adapters.deterministic_mock_adapter import DeterministicMockAdapter
from sapianta_bridge.runtime.adapter_runtime import execute_adapter_runtime
from sapianta_bridge.transport.transport_evidence import transport_evidence
from sapianta_bridge.transport.transport_guard import guard_transport
from sapianta_bridge.transport.transport_request import create_transport_request
from sapianta_bridge.transport.transport_response import (
    create_transport_response,
    validate_transport_response,
)


def _request_and_runtime() -> tuple[dict, dict, dict]:
    envelope = create_execution_envelope(
        envelope_id="ENV-RESPONSE",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-RESPONSE",
        validation_requirements=["pytest"],
    ).to_dict()
    request = create_transport_request(envelope).to_dict()
    guard = guard_transport(request=request, provider=DeterministicMockAdapter())
    runtime = execute_adapter_runtime(envelope=envelope, provider=DeterministicMockAdapter())
    evidence = transport_evidence(request=request, runtime_output=runtime, guard_status=guard)
    return request, runtime, evidence


def test_transport_response_wraps_runtime_and_normalized_result() -> None:
    request, runtime, evidence = _request_and_runtime()
    response = create_transport_response(request=request, runtime_output=runtime, evidence=evidence)

    assert response.transport_status == "SUCCESS"
    assert response.provider_id == "deterministic_mock"
    assert response.normalized_result["execution_status"] == "SUCCESS"
    assert validate_transport_response(response)["valid"] is True


def test_transport_response_rejects_unknown_status() -> None:
    request, runtime, evidence = _request_and_runtime()
    response = create_transport_response(request=request, runtime_output=runtime, evidence=evidence).to_dict()
    response["transport_status"] = "ROUTED"

    validation = validate_transport_response(response)

    assert validation["valid"] is False
    assert {"field": "transport_status", "reason": "unsupported transport status"} in validation["errors"]
