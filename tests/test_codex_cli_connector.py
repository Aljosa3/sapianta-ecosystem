import json

from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.provider_connectors.codex_cli_connector import prepare_codex_cli_task, read_codex_cli_result
from sapianta_bridge.provider_connectors.connector_evidence import validate_connector_evidence
from sapianta_bridge.real_provider_transport.provider_transport_response import create_provider_transport_response


def _envelope():
    return create_execution_envelope(
        envelope_id="ENV-CODEX-CLI-CONNECTOR",
        provider_id="codex",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-CODEX-CLI-CONNECTOR",
        validation_requirements=["pytest"],
    ).to_dict()


def test_codex_cli_connector_prepares_task_without_invocation(tmp_path):
    prepared = prepare_codex_cli_task(envelope=_envelope(), connector_dir=tmp_path)

    assert prepared["connector_status"] == "PREPARED"
    assert prepared["connector_mode"] == "PREPARE_ONLY"
    assert prepared["codex_cli_invoked"] is False
    assert prepared["shell_execution_present"] is False
    assert prepared["network_execution_present"] is False
    assert validate_connector_evidence(prepared["connector_evidence"])["valid"] is True

    task_path = tmp_path / f"{prepared['provider_transport_request']['transport_id']}.codex-task.json"
    assert task_path.exists()
    task = json.loads(task_path.read_text(encoding="utf-8"))
    assert task["connector_id"] == prepared["connector_request"]["connector_id"]


def test_codex_cli_connector_reads_expected_result_artifact(tmp_path):
    prepared = prepare_codex_cli_task(envelope=_envelope(), connector_dir=tmp_path)
    transport_response = create_provider_transport_response(
        request=prepared["provider_transport_request"],
        result_payload={"execution_status": "SUCCESS", "artifacts_created": []},
    ).to_dict()
    result_path = tmp_path / f"{prepared['provider_transport_request']['transport_id']}.codex-result.json"
    result_path.write_text(json.dumps(transport_response, sort_keys=True, separators=(",", ":")), encoding="utf-8")

    result = read_codex_cli_result(
        connector_request=prepared["connector_request"],
        result_artifact_path=result_path,
    )

    assert result["connector_status"] == "SUCCESS"
    assert result["codex_cli_invoked"] is False
    assert result["connector_response"]["provider_id"] == "codex"
    assert result["connector_response"]["envelope_id"] == prepared["connector_request"]["envelope_id"]
    assert validate_connector_evidence(result["connector_evidence"])["valid"] is True


def test_codex_cli_connector_blocks_invalid_envelope(tmp_path):
    envelope = _envelope()
    envelope["replay_identity"] = ""

    prepared = prepare_codex_cli_task(envelope=envelope, connector_dir=tmp_path)

    assert prepared["connector_status"] == "BLOCKED"
    assert prepared["connector_evidence"]["codex_cli_invoked"] is False
    assert prepared["connector_evidence"]["replay_safe"] is False
