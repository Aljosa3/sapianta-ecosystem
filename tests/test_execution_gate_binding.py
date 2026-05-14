from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.provider_connectors.codex_cli_connector import prepare_codex_cli_task
from sapianta_bridge.provider_connectors.execution_gate_binding import (
    create_execution_gate_binding,
    validate_execution_gate_binding,
)
from sapianta_bridge.provider_connectors.execution_gate_identity import create_execution_gate_identity


def _connector_request(tmp_path):
    envelope = create_execution_envelope(
        envelope_id="ENV-GATE-BINDING",
        provider_id="codex",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-GATE-BINDING",
        validation_requirements=["pytest"],
    ).to_dict()
    return prepare_codex_cli_task(envelope=envelope, connector_dir=tmp_path)["connector_request"]


def test_execution_gate_binding_is_replay_safe(tmp_path):
    request = _connector_request(tmp_path)
    identity = create_execution_gate_identity(connector_request=request).to_dict()
    binding = create_execution_gate_binding(
        execution_gate_id=identity["execution_gate_id"],
        connector_request=request,
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        operation="CAPTURE_CONNECTOR_TASK",
    ).to_dict()

    assert binding["provider_id"] == "codex"
    assert binding["immutable"] is True
    assert validate_execution_gate_binding(binding)["valid"] is True


def test_execution_gate_binding_rejects_timeout_mutation(tmp_path):
    request = _connector_request(tmp_path)
    identity = create_execution_gate_identity(connector_request=request).to_dict()
    binding = create_execution_gate_binding(
        execution_gate_id=identity["execution_gate_id"],
        connector_request=request,
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        operation="CAPTURE_CONNECTOR_TASK",
    ).to_dict()
    binding["timeout_seconds"] = 45

    validation = validate_execution_gate_binding(binding)

    assert validation["valid"] is False
    assert any(error["field"] == "binding_sha256" for error in validation["errors"])
