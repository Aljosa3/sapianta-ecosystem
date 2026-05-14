from sapianta_bridge.real_provider_transport.provider_transport_binding import (
    create_provider_transport_binding,
    validate_provider_transport_binding,
)


def test_provider_transport_binding_is_deterministic() -> None:
    first = create_provider_transport_binding(
        provider_id="deterministic_mock",
        envelope_id="ENV-BIND",
        invocation_id="INVOCATION-BIND",
        replay_identity="REPLAY-BIND",
    ).to_dict()
    second = create_provider_transport_binding(
        provider_id="deterministic_mock",
        envelope_id="ENV-BIND",
        invocation_id="INVOCATION-BIND",
        replay_identity="REPLAY-BIND",
    ).to_dict()

    assert first["transport_id"] == second["transport_id"]
    assert validate_provider_transport_binding(first)["valid"] is True


def test_provider_transport_binding_rejects_mutation() -> None:
    binding = create_provider_transport_binding(
        provider_id="deterministic_mock",
        envelope_id="ENV-BIND",
        invocation_id="INVOCATION-BIND",
        replay_identity="REPLAY-BIND",
    ).to_dict()
    binding["transport_id"] = "MUTATED"

    assert validate_provider_transport_binding(binding)["valid"] is False
