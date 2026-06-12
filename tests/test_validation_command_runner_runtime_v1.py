"""Tests for AIGOL_VALIDATION_COMMAND_RUNNER_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from aigol.runtime.validation_command_runner_runtime import (
    FAILED_CLOSED,
    VALIDATION_COMMAND_COMPLETED,
    VALIDATION_COMMAND_FAILED,
    VALIDATION_COMMAND_REQUEST_ARTIFACT_V1,
    VALIDATION_COMMAND_RESULT_ARTIFACT_V1,
    create_validation_command_request,
    execute_validation_command,
    reconstruct_validation_command_replay,
)


CREATED_AT = "2026-06-12T00:00:00Z"


def _request(tmp_path, command: list[str], *, request_id: str = "VALIDATION-COMMAND-REQUEST-000001") -> dict:
    return create_validation_command_request(
        request_id=request_id,
        command=command,
        cwd=str(Path.cwd()),
        requested_by="HUMAN_OPERATOR",
        requested_at=CREATED_AT,
        replay_references=["replay/validation-command-request.json"],
        replay_hashes=[replay_hash({"request_id": request_id})],
        timeout_seconds=30,
    )


def test_validation_command_runner_executes_allowlisted_py_compile(tmp_path) -> None:
    source = tmp_path / "valid_module.py"
    source.write_text("VALUE = 1\n", encoding="utf-8")
    request = _request(tmp_path, ["python", "-m", "py_compile", str(source)])
    capture = execute_validation_command(
        request_artifact=request,
        executed_by="AIGOL_VALIDATION_COMMAND_RUNNER",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "py_compile_replay",
    )
    result = capture["validation_command_result_artifact"]
    reconstructed = reconstruct_validation_command_replay(tmp_path / "py_compile_replay")

    assert request["artifact_type"] == VALIDATION_COMMAND_REQUEST_ARTIFACT_V1
    assert capture["command_status"] == VALIDATION_COMMAND_COMPLETED
    assert capture["validation_command_runner_implemented"] is True
    assert capture["allowlist_enforced"] is True
    assert capture["replay_preserved"] is True
    assert capture["arbitrary_execution_prevented"] is True
    assert capture["ready_for_supervised_validation_automation"] is True
    assert result["artifact_type"] == VALIDATION_COMMAND_RESULT_ARTIFACT_V1
    assert result["exit_code"] == 0
    assert result["shell_execution_used"] is False
    assert result["repair_invoked"] is False
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert reconstructed["command_status"] == VALIDATION_COMMAND_COMPLETED
    assert reconstructed["allowlist_enforced"] is True
    assert reconstructed["replay_lineage_preserved"] is True


def test_validation_command_runner_captures_allowlisted_failure_without_repair(tmp_path) -> None:
    missing = tmp_path / "missing_module.py"
    request = _request(
        tmp_path,
        ["python", "-m", "py_compile", str(missing)],
        request_id="VALIDATION-COMMAND-REQUEST-FAILURE-000001",
    )
    capture = execute_validation_command(
        request_artifact=request,
        executed_by="AIGOL_VALIDATION_COMMAND_RUNNER",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "failure_replay",
    )
    result = capture["validation_command_result_artifact"]

    assert capture["command_status"] == VALIDATION_COMMAND_FAILED
    assert result["exit_code"] != 0
    assert result["stderr"]
    assert result["repair_invoked"] is False
    assert result["ready_for_supervised_validation_automation"] is True
    assert result["fail_closed_preserved"] is True


def test_validation_command_runner_blocks_non_allowlisted_command(tmp_path) -> None:
    artifact = {
        "artifact_type": VALIDATION_COMMAND_REQUEST_ARTIFACT_V1,
        "runtime_version": "AIGOL_VALIDATION_COMMAND_RUNNER_RUNTIME_V1",
        "request_id": "VALIDATION-COMMAND-REQUEST-BLOCKED-000001",
        "certification_status": "CERTIFIED_VALIDATION_COMMAND_REQUEST",
        "command": ["python", "-c", "print('blocked')"],
        "command_display": "python -c print('blocked')",
        "cwd": str(Path.cwd()),
        "requested_by": "HUMAN_OPERATOR",
        "requested_at": CREATED_AT,
        "timeout_seconds": 30,
        "replay_references": ["replay/blocked.json"],
        "replay_hashes": [replay_hash({"blocked": True})],
        "governance_authority": {
            "human_authority_preserved": True,
            "validation_only": True,
            "repair_allowed": False,
            "arbitrary_shell_allowed": False,
            "repository_mutation_allowed": False,
        },
        "allowlist": ["python -m pytest", "python -m py_compile", "python -m json.tool", "git diff --check"],
        "allowlist_enforced": True,
        "replay_lineage_preserved": True,
        "fail_closed_preserved": True,
        "arbitrary_execution_prevented": True,
        "replay_visible": True,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)

    capture = execute_validation_command(
        request_artifact=artifact,
        executed_by="AIGOL_VALIDATION_COMMAND_RUNNER",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "blocked_replay",
    )
    result = capture["validation_command_result_artifact"]

    assert capture["command_status"] == FAILED_CLOSED
    assert capture["allowlist_enforced"] is True
    assert capture["arbitrary_execution_prevented"] is True
    assert capture["ready_for_supervised_validation_automation"] is False
    assert result["exit_code"] is None
    assert "command is not allowlisted" in result["failure_reason"]


def test_validation_command_runner_rejects_shell_operator_in_command() -> None:
    with pytest.raises(FailClosedRuntimeError, match="shell operators are not allowed"):
        create_validation_command_request(
            request_id="VALIDATION-COMMAND-REQUEST-SHELL-000001",
            command=["python", "-m", "py_compile", "safe.py", "&&", "python", "-c", "print('bad')"],
            cwd=str(Path.cwd()),
            requested_by="HUMAN_OPERATOR",
            requested_at=CREATED_AT,
            replay_references=["replay/shell.json"],
            replay_hashes=[replay_hash({"shell": True})],
        )


def test_validation_command_runner_detects_corrupt_replay(tmp_path) -> None:
    source = tmp_path / "valid_module.py"
    source.write_text("VALUE = 1\n", encoding="utf-8")
    request = _request(
        tmp_path,
        ["python", "-m", "py_compile", str(source)],
        request_id="VALIDATION-COMMAND-REQUEST-CORRUPT-000001",
    )
    execute_validation_command(
        request_artifact=request,
        executed_by="AIGOL_VALIDATION_COMMAND_RUNNER",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt_replay",
    )
    path = tmp_path / "corrupt_replay" / "001_validation_command_result_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["allowlist_enforced"] = False
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_validation_command_replay(tmp_path / "corrupt_replay")


def test_validation_command_runner_runtime_uses_only_shell_false_subprocess() -> None:
    import aigol.runtime.validation_command_runner_runtime as runtime

    source = inspect.getsource(runtime)

    assert "shell=False" in source
    assert "shell=True" not in source
    assert "os.system" not in source
    assert "Popen" not in source
    assert "repair_invoked\": True" not in source
