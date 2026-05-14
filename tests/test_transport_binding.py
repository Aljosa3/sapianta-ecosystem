from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.runtime.runtime_binding import create_runtime_binding
from sapianta_bridge.transport.transport_binding import (
    create_transport_binding,
    validate_transport_binding,
)


def _envelope() -> dict:
    return create_execution_envelope(
        envelope_id="ENV-TRANSPORT",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-TRANSPORT",
        validation_requirements=["pytest"],
    ).to_dict()


def test_transport_binding_is_deterministic_and_valid() -> None:
    envelope = _envelope()
    runtime = create_runtime_binding(envelope).to_dict()
    first = create_transport_binding(envelope=envelope, runtime_binding=runtime).to_dict()
    second = create_transport_binding(envelope=envelope, runtime_binding=runtime).to_dict()

    assert first == second
    assert first["transport_id"] == "TRANSPORT-ENV-TRANSPORT"
    assert validate_transport_binding(first)["valid"] is True


def test_transport_binding_fails_closed_when_incomplete() -> None:
    envelope = _envelope()
    runtime = create_runtime_binding(envelope).to_dict()
    binding = create_transport_binding(envelope=envelope, runtime_binding=runtime).to_dict()
    binding.pop("runtime_binding_hash")

    result = validate_transport_binding(binding)

    assert result["valid"] is False
    assert {"field": "runtime_binding_hash", "reason": "missing transport binding field"} in result["errors"]


def test_transport_binding_hash_mismatch_fails_closed() -> None:
    envelope = _envelope()
    runtime = create_runtime_binding(envelope).to_dict()
    binding = create_transport_binding(envelope=envelope, runtime_binding=runtime).to_dict()
    binding["transport_binding_sha256"] = "bad"

    result = validate_transport_binding(binding)

    assert result["valid"] is False
    assert {"field": "transport_binding_sha256", "reason": "transport binding hash mismatch"} in result["errors"]
