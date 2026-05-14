import textwrap

from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.provider_connectors.bounded_execution_evidence import validate_bounded_execution_evidence
from sapianta_bridge.provider_connectors.bounded_execution_runtime import execute_bounded_codex
from sapianta_bridge.provider_connectors.codex_cli_connector import prepare_codex_cli_task
from sapianta_bridge.provider_connectors.execution_gate_request import (
    EXECUTION_GATE_OPERATION_CODEX_CLI_RUN,
    create_execution_gate_request,
)


def _write_codex(path):
    path.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            print("bounded-codex-ok")
            """
        ),
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | 0o111)


def _request(tmp_path):
    envelope = create_execution_envelope(
        envelope_id="ENV-BOUNDED-EVIDENCE",
        provider_id="codex_cli",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-BOUNDED-EVIDENCE",
        validation_requirements=["pytest"],
    ).to_dict()
    connector_request = prepare_codex_cli_task(envelope=envelope, connector_dir=tmp_path)["connector_request"]
    return create_execution_gate_request(
        connector_request=connector_request,
        execution_authorized=True,
        approved_by="human",
        workspace_path=str(tmp_path),
        timeout_seconds=30,
        operation=EXECUTION_GATE_OPERATION_CODEX_CLI_RUN,
    ).to_dict()


def test_bounded_execution_evidence_is_replay_safe(tmp_path):
    codex = tmp_path / "codex"
    _write_codex(codex)

    result = execute_bounded_codex(gate_request=_request(tmp_path), codex_executable=str(codex))
    evidence = result["bounded_execution_evidence"]

    assert evidence["execution_name"] == "FIRST_BOUNDED_REAL_CODEX_EXECUTION_V1"
    assert evidence["provider_id"] == "codex_cli"
    assert evidence["runtime_valid"] is True
    assert evidence["capture_immutable"] is True
    assert evidence["replay_safe"] is True
    assert validate_bounded_execution_evidence(evidence)["valid"] is True


def test_bounded_execution_evidence_rejects_forbidden_routing(tmp_path):
    codex = tmp_path / "codex"
    _write_codex(codex)
    evidence = execute_bounded_codex(
        gate_request=_request(tmp_path),
        codex_executable=str(codex),
    )["bounded_execution_evidence"]
    evidence["routing_present"] = True

    validation = validate_bounded_execution_evidence(evidence)

    assert validation["valid"] is False
    assert any(error["field"] == "routing_present" for error in validation["errors"])
