from sapianta_bridge.provider_connectors.connector_identity import (
    create_connector_identity,
    validate_connector_identity,
)


def test_connector_identity_is_deterministic_and_prepare_only():
    first = create_connector_identity(provider_id="codex", replay_identity="REPLAY-1").to_dict()
    second = create_connector_identity(provider_id="codex", replay_identity="REPLAY-1").to_dict()

    assert first == second
    assert first["connector_mode"] == "PREPARE_ONLY"
    assert first["connector_is_provider_router"] is False
    assert validate_connector_identity(first)["valid"] is True


def test_connector_identity_rejects_execution_mode():
    identity = create_connector_identity(provider_id="codex", replay_identity="REPLAY-1").to_dict()
    identity["connector_mode"] = "ACTIVE_LOCAL_CONNECTOR"

    validation = validate_connector_identity(identity)

    assert validation["valid"] is False
    assert any(error["field"] == "connector_mode" for error in validation["errors"])
