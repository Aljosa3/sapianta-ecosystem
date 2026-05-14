from sapianta_bridge.active_invocation.invocation_binding import (
    create_invocation_binding,
    validate_invocation_binding,
)
from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope


def _envelope() -> dict:
    return create_execution_envelope(
        envelope_id="ENV-INV-BIND",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-INV-BIND",
        validation_requirements=["pytest"],
    ).to_dict()


def test_invocation_binding_is_replay_safe_and_valid() -> None:
    binding = create_invocation_binding(_envelope()).to_dict()
    validation = validate_invocation_binding(binding)

    assert validation["valid"] is True
    assert binding["replay_safe"] is True
    assert binding["immutable"] is True


def test_invocation_binding_fails_closed_on_identity_mutation() -> None:
    binding = create_invocation_binding(_envelope()).to_dict()
    binding["invocation_id"] = "INVOCATION-MUTATED"
    validation = validate_invocation_binding(binding)

    assert validation["valid"] is False
    assert {"field": "invocation_id", "reason": "invocation identity mismatch"} in validation["errors"]
