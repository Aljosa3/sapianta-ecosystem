import json
import os
import textwrap

from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.provider_connectors.bounded_execution_runtime import (
    execute_bounded_codex,
    validate_bounded_execution_runtime_request,
)
from sapianta_bridge.provider_connectors.codex_cli_connector import prepare_codex_cli_task
from sapianta_bridge.provider_connectors.execution_gate_request import (
    EXECUTION_GATE_OPERATION_CODEX_CLI_RUN,
    create_execution_gate_request,
)


def _write_codex_executable(path, *, body):
    path.write_text(textwrap.dedent(body), encoding="utf-8")
    path.chmod(path.stat().st_mode | 0o111)


def _gate_request(tmp_path, *, provider_id="codex_cli", authorized=True, timeout_seconds=30):
    envelope = create_execution_envelope(
        envelope_id=f"ENV-BOUNDED-RUNTIME-{provider_id}",
        provider_id=provider_id,
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity=f"REPLAY-BOUNDED-RUNTIME-{provider_id}",
        validation_requirements=["pytest"],
    ).to_dict()
    connector_request = prepare_codex_cli_task(envelope=envelope, connector_dir=tmp_path)["connector_request"]
    return create_execution_gate_request(
        connector_request=connector_request,
        execution_authorized=authorized,
        approved_by="human",
        workspace_path=str(tmp_path),
        timeout_seconds=timeout_seconds,
        operation=EXECUTION_GATE_OPERATION_CODEX_CLI_RUN,
    ).to_dict()


def test_bounded_execution_runtime_executes_fixed_codex_vector(tmp_path):
    codex = tmp_path / "codex"
    _write_codex_executable(
        codex,
        body="""\
        #!/usr/bin/env python3
        import json
        import sys
        payload = {"argv": sys.argv[1:], "prompt": sys.argv[2]}
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        """,
    )
    request = _gate_request(tmp_path)

    result = execute_bounded_codex(gate_request=request, codex_executable=str(codex))

    assert result["bounded_execution_status"] == "SUCCESS"
    capture = result["capture"]
    stdout = json.loads(capture["stdout"])
    assert stdout["argv"][0] == "exec"
    assert "SAPIANTA_CODEX_VALIDATION_OK" in stdout["prompt"]
    assert result["runtime_validation"]["contract_used"] == "codex exec <bounded_prompt>"
    assert capture["stderr"] == ""
    assert capture["exit_code"] == 0
    assert result["bounded_execution_evidence"]["provider_id"] == "codex_cli"
    assert result["bounded_execution_evidence"]["orchestration_present"] is False
    assert result["bounded_execution_evidence"]["retry_present"] is False
    assert result["bounded_execution_evidence"]["routing_present"] is False


def test_bounded_execution_runtime_requires_authorization(tmp_path):
    codex = tmp_path / "codex"
    _write_codex_executable(codex, body="#!/usr/bin/env python3\nprint('ok')\n")
    request = _gate_request(tmp_path, authorized=False)

    result = execute_bounded_codex(gate_request=request, codex_executable=str(codex))

    assert result["bounded_execution_status"] == "BLOCKED"
    assert result["runtime_validation"]["valid"] is False


def test_bounded_execution_runtime_blocks_provider_mismatch(tmp_path):
    codex = tmp_path / "codex"
    _write_codex_executable(codex, body="#!/usr/bin/env python3\nprint('ok')\n")
    request = _gate_request(tmp_path, provider_id="codex")

    validation = validate_bounded_execution_runtime_request(gate_request=request, codex_executable=str(codex))

    assert validation["valid"] is False
    assert validation["provider_identity_valid"] is False


def test_bounded_execution_runtime_handles_timeout(tmp_path):
    codex = tmp_path / "codex"
    _write_codex_executable(
        codex,
        body="""\
        #!/usr/bin/env python3
        import time
        time.sleep(2)
        """,
    )
    request = _gate_request(tmp_path, timeout_seconds=1)

    result = execute_bounded_codex(gate_request=request, codex_executable=str(codex))

    assert result["bounded_execution_status"] == "TIMEOUT"
    assert result["capture"]["timed_out"] is True
    assert result["capture"]["exit_code"] == 124


def test_bounded_execution_runtime_rejects_arbitrary_executable(tmp_path):
    request = _gate_request(tmp_path)

    validation = validate_bounded_execution_runtime_request(
        gate_request=request,
        codex_executable=os.environ.get("SHELL", "bash"),
    )

    assert validation["valid"] is False
    assert any(error["field"] == "codex_executable" for error in validation["errors"])
