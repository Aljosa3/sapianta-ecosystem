from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.runtime.runtime_binding import (
    create_runtime_binding,
    validate_runtime_binding,
)


def _envelope() -> dict:
    return create_execution_envelope(
        envelope_id="ENV-RUNTIME",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-RUNTIME",
        validation_requirements=["pytest"],
    ).to_dict()


def test_runtime_binding_is_deterministic_and_valid() -> None:
    first = create_runtime_binding(_envelope()).to_dict()
    second = create_runtime_binding(_envelope()).to_dict()

    assert first == second
    assert validate_runtime_binding(first)["valid"] is True
    assert validate_runtime_binding(first)["immutable_during_execution"] is True


def test_runtime_binding_fails_closed_when_incomplete() -> None:
    binding = create_runtime_binding(_envelope()).to_dict()
    binding.pop("provider_id")

    result = validate_runtime_binding(binding)

    assert result["valid"] is False
    assert {"field": "provider_id", "reason": "missing runtime binding field"} in result["errors"]


def test_runtime_binding_hash_mismatch_fails_closed() -> None:
    binding = create_runtime_binding(_envelope()).to_dict()
    binding["binding_sha256"] = "bad"

    result = validate_runtime_binding(binding)

    assert result["valid"] is False
    assert {"field": "binding_sha256", "reason": "runtime binding hash mismatch"} in result["errors"]
