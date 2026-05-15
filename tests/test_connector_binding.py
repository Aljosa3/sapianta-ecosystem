from sapianta_bridge.provider_connectors.connector_binding import (
    create_connector_binding,
    validate_connector_binding,
)


def test_connector_binding_is_replay_safe_and_deterministic():
    binding = create_connector_binding(
        connector_id="PROVIDER-CONNECTOR-1",
        transport_id="PROVIDER-TRANSPORT-1",
        provider_id="codex",
        envelope_id="ENV-1",
        invocation_id="INV-1",
        replay_identity="REPLAY-1",
        task_artifact_path="/tmp/task.json",
        expected_result_artifact_path="/tmp/result.json",
    ).to_dict()

    again = create_connector_binding(
        connector_id="PROVIDER-CONNECTOR-1",
        transport_id="PROVIDER-TRANSPORT-1",
        provider_id="codex",
        envelope_id="ENV-1",
        invocation_id="INV-1",
        replay_identity="REPLAY-1",
        task_artifact_path="/tmp/task.json",
        expected_result_artifact_path="/tmp/result.json",
    ).to_dict()

    assert binding == again
    assert binding["immutable"] is True
    assert validate_connector_binding(binding)["valid"] is True


def test_connector_binding_rejects_mutated_path():
    binding = create_connector_binding(
        connector_id="PROVIDER-CONNECTOR-1",
        transport_id="PROVIDER-TRANSPORT-1",
        provider_id="codex",
        envelope_id="ENV-1",
        invocation_id="INV-1",
        replay_identity="REPLAY-1",
        task_artifact_path="/tmp/task.json",
        expected_result_artifact_path="/tmp/result.json",
    ).to_dict()
    binding["task_artifact_path"] = "/tmp/other-task.json"

    validation = validate_connector_binding(binding)

    assert validation["valid"] is False
    assert any(error["field"] == "binding_sha256" for error in validation["errors"])
