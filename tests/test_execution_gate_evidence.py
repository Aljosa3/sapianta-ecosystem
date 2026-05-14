from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.provider_connectors.codex_cli_connector import prepare_codex_cli_task
from sapianta_bridge.provider_connectors.execution_gate_controller import execute_through_execution_gate
from sapianta_bridge.provider_connectors.execution_gate_evidence import validate_execution_gate_evidence
from sapianta_bridge.provider_connectors.execution_gate_request import create_execution_gate_request


def _gate_result(tmp_path):
    envelope = create_execution_envelope(
        envelope_id="ENV-GATE-EVIDENCE",
        provider_id="codex",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-GATE-EVIDENCE",
        validation_requirements=["pytest"],
    ).to_dict()
    connector_request = prepare_codex_cli_task(envelope=envelope, connector_dir=tmp_path)["connector_request"]
    request = create_execution_gate_request(
        connector_request=connector_request,
        execution_authorized=True,
        approved_by="human",
        workspace_path=str(tmp_path),
        timeout_seconds=30,
    ).to_dict()
    return execute_through_execution_gate(request=request)


def test_execution_gate_evidence_is_replay_safe(tmp_path):
    result = _gate_result(tmp_path)
    evidence = result["execution_gate_evidence"]

    assert evidence["execution_authorized"] is True
    assert evidence["authorization_valid"] is True
    assert evidence["workspace_boundary_valid"] is True
    assert evidence["replay_safe"] is True
    assert validate_execution_gate_evidence(evidence)["valid"] is True


def test_execution_gate_evidence_rejects_forbidden_retry(tmp_path):
    evidence = _gate_result(tmp_path)["execution_gate_evidence"]
    evidence["retry_present"] = True

    validation = validate_execution_gate_evidence(evidence)

    assert validation["valid"] is False
    assert any(error["field"] == "retry_present" for error in validation["errors"])
