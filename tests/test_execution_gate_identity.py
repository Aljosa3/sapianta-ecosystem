from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.provider_connectors.codex_cli_connector import prepare_codex_cli_task
from sapianta_bridge.provider_connectors.execution_gate_identity import (
    create_execution_gate_identity,
    validate_execution_gate_identity,
)


def _connector_request(tmp_path):
    envelope = create_execution_envelope(
        envelope_id="ENV-GATE-IDENTITY",
        provider_id="codex",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-GATE-IDENTITY",
        validation_requirements=["pytest"],
    ).to_dict()
    return prepare_codex_cli_task(envelope=envelope, connector_dir=tmp_path)["connector_request"]


def test_execution_gate_identity_is_deterministic(tmp_path):
    request = _connector_request(tmp_path)
    first = create_execution_gate_identity(connector_request=request).to_dict()
    second = create_execution_gate_identity(connector_request=request).to_dict()

    assert first == second
    assert first["provider_id"] == "codex"
    assert first["immutable"] is True
    assert validate_execution_gate_identity(first)["valid"] is True


def test_execution_gate_identity_rejects_mutation(tmp_path):
    identity = create_execution_gate_identity(connector_request=_connector_request(tmp_path)).to_dict()
    identity["provider_id"] = "claude"

    validation = validate_execution_gate_identity(identity)

    assert validation["valid"] is False
    assert any(error["field"] == "execution_gate_id" for error in validation["errors"])
