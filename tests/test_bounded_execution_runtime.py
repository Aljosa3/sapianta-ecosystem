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
        import os
        payload = {
            "argv": sys.argv[1:],
            "prompt": sys.argv[2],
            "home": os.environ.get("HOME"),
            "xdg_cache": os.environ.get("XDG_CACHE_HOME"),
            "xdg_config": os.environ.get("XDG_CONFIG_HOME"),
            "tmpdir": os.environ.get("TMPDIR"),
        }
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        """,
    )
    request = _gate_request(tmp_path)

    result = execute_bounded_codex(gate_request=request, codex_executable=str(codex))

    assert result["bounded_execution_status"] == "SUCCESS"
    capture = result["capture"]
    assert capture["completion_state"] == "COMPLETED"
    assert capture["process_state"] == "TERMINATED_COMPLETED"
    assert result["completion_classification"]["completion_state"] == "COMPLETED"
    assert result["process_classification"]["process_state"] == "TERMINATED_COMPLETED"
    stdout = json.loads(capture["stdout"])
    assert stdout["argv"][0] == "exec"
    assert "SAPIANTA_CODEX_VALIDATION_OK" in stdout["prompt"]
    assert "AIGOL_TASK_COMPLETE" in stdout["prompt"]
    assert result["runtime_validation"]["contract_used"] == "codex exec <bounded_prompt>"
    state = result["runtime_validation"]["runtime_state"]
    assert stdout["home"] == state["runtime_state_dir"]
    assert stdout["xdg_cache"].startswith(state["runtime_state_dir"])
    assert result["bounded_execution_evidence"]["runtime_state_valid"] is True
    assert result["bounded_execution_evidence"]["repo_root_state_allowed"] is False
    assert capture["stderr"] == ""
    assert capture["exit_code"] == 0
    assert result["bounded_execution_evidence"]["provider_id"] == "codex_cli"
    assert result["bounded_execution_evidence"]["orchestration_present"] is False
    assert result["bounded_execution_evidence"]["retry_present"] is False
    assert result["bounded_execution_evidence"]["routing_present"] is False
    assert result["bounded_execution_evidence"]["stdin_sealed"] is True


def test_bounded_execution_runtime_seals_stdin(tmp_path):
    codex = tmp_path / "codex"
    _write_codex_executable(
        codex,
        body="""\
        #!/usr/bin/env python3
        import sys
        print("stdin_empty=" + str(sys.stdin.read() == ""))
        """,
    )
    request = _gate_request(tmp_path)

    result = execute_bounded_codex(gate_request=request, codex_executable=str(codex))

    assert result["bounded_execution_status"] == "SUCCESS"
    assert "stdin_empty=True" in result["capture"]["stdout"]
    assert result["bounded_execution_evidence"]["stdin_sealed"] is True


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
    assert result["capture"]["completion_state"] == "TIMEOUT"
    assert result["capture"]["process_state"] == "TIMEOUT_NO_COMPLETION"
    assert result["capture"]["bounded_result_captured"] is False
    assert result["timeout_telemetry"]["timeout_exceeded"] is True


def test_bounded_execution_runtime_captures_marker_then_terminates(tmp_path):
    codex = tmp_path / "codex"
    _write_codex_executable(
        codex,
        body="""\
        #!/usr/bin/env python3
        import sys
        import time
        print("SAPIANTA_CODEX_VALIDATION_OK AIGOL_TASK_COMPLETE", flush=True)
        time.sleep(10)
        """,
    )
    request = _gate_request(tmp_path, timeout_seconds=1)

    result = execute_bounded_codex(gate_request=request, codex_executable=str(codex))

    assert result["bounded_execution_status"] == "RESULT_CAPTURED_WITH_TERMINATION"
    assert result["capture"]["process_state"] == "OUTPUT_COMPLETED_PROCESS_RUNNING"
    assert result["capture"]["completion_marker_detected"] is True
    assert result["capture"]["bounded_result_captured"] is True
    assert result["capture"]["graceful_termination_attempted"] is True
    assert result["bounded_execution_evidence"]["bounded_result_captured"] is True
    assert result["bounded_execution_evidence"]["retry_present"] is False


def test_bounded_execution_runtime_rejects_arbitrary_executable(tmp_path):
    request = _gate_request(tmp_path)

    validation = validate_bounded_execution_runtime_request(
        gate_request=request,
        codex_executable=os.environ.get("SHELL", "bash"),
    )

    assert validation["valid"] is False
    assert any(error["field"] == "codex_executable" for error in validation["errors"])


def test_bounded_execution_runtime_rejects_runtime_state_escape(tmp_path):
    request = _gate_request(tmp_path)

    validation = validate_bounded_execution_runtime_request(
        gate_request=request,
        codex_executable=str(tmp_path / "codex"),
        runtime_state_root=str(tmp_path / ".."),
    )

    assert validation["valid"] is False
    assert validation["runtime_state_valid"] is False
