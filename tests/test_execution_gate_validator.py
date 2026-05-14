from pathlib import Path

from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.provider_connectors.codex_cli_connector import prepare_codex_cli_task
from sapianta_bridge.provider_connectors.execution_gate_request import create_execution_gate_request
from sapianta_bridge.provider_connectors.execution_gate_validator import validate_execution_gate_request


def _connector_request(tmp_path, *, envelope_id="ENV-GATE-VALIDATOR"):
    envelope = create_execution_envelope(
        envelope_id=envelope_id,
        provider_id="codex",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity=f"REPLAY-{envelope_id}",
        validation_requirements=["pytest"],
    ).to_dict()
    return prepare_codex_cli_task(envelope=envelope, connector_dir=tmp_path)["connector_request"]


def test_execution_gate_validator_rejects_provider_mismatch(tmp_path):
    request = create_execution_gate_request(
        connector_request=_connector_request(tmp_path),
        execution_authorized=True,
        approved_by="human",
        workspace_path=str(tmp_path),
        timeout_seconds=30,
    ).to_dict()
    request["provider_id"] = "claude"

    validation = validate_execution_gate_request(request)

    assert validation["valid"] is False
    assert any("mismatch" in error["reason"] for error in validation["errors"])


def test_execution_gate_validator_rejects_workspace_escape(tmp_path):
    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside"
    workspace.mkdir()
    outside.mkdir()
    connector_request = _connector_request(outside, envelope_id="ENV-GATE-WORKSPACE")
    request = create_execution_gate_request(
        connector_request=connector_request,
        execution_authorized=True,
        approved_by="human",
        workspace_path=str(workspace),
        timeout_seconds=30,
    ).to_dict()

    validation = validate_execution_gate_request(request)

    assert validation["valid"] is False
    assert validation["workspace_boundary_valid"] is False
    assert any(error["field"] == "artifact_path" for error in validation["errors"])


def test_execution_gate_validator_rejects_parent_traversal(tmp_path):
    request = create_execution_gate_request(
        connector_request=_connector_request(tmp_path),
        execution_authorized=True,
        approved_by="human",
        workspace_path=str(Path(tmp_path) / ".."),
        timeout_seconds=30,
    ).to_dict()

    validation = validate_execution_gate_request(request)

    assert validation["valid"] is False
    assert any(error["field"] == "workspace_path" for error in validation["errors"])


def test_execution_gate_validator_rejects_orchestration_flag(tmp_path):
    request = create_execution_gate_request(
        connector_request=_connector_request(tmp_path),
        execution_authorized=True,
        approved_by="human",
        workspace_path=str(tmp_path),
        timeout_seconds=30,
    ).to_dict()
    request["orchestration_present"] = True

    validation = validate_execution_gate_request(request)

    assert validation["valid"] is False
    assert any(error["field"] == "orchestration_present" for error in validation["errors"])
