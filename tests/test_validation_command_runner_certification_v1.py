"""Checks for AIGOL_VALIDATION_COMMAND_RUNNER_RUNTIME_CERTIFICATION_V1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CERTIFICATION = ROOT / ".github/governance/finalize/AIGOL_VALIDATION_COMMAND_RUNNER_RUNTIME_CERTIFICATION_V1.json"


def _load() -> dict:
    return json.loads(CERTIFICATION.read_text(encoding="utf-8"))


def test_validation_command_runner_certification_records_scope() -> None:
    certification = _load()
    scope = certification["certification_scope"]

    assert certification["artifact_type"] == "VALIDATION_COMMAND_RUNNER_RUNTIME_CERTIFICATION_V1"
    assert certification["certified_runtime"] == "AIGOL_VALIDATION_COMMAND_RUNNER_RUNTIME_V1"
    assert certification["certification_status"] == "CERTIFIED"
    assert scope["input_artifact"] == "VALIDATION_COMMAND_REQUEST_ARTIFACT_V1"
    assert scope["output_artifact"] == "VALIDATION_COMMAND_RESULT_ARTIFACT_V1"
    assert scope["allowlisted_commands"] == [
        "python -m pytest",
        "python -m py_compile",
        "python -m json.tool",
        "git diff --check",
    ]
    assert scope["arbitrary_shell_allowed"] is False
    assert scope["repair_allowed"] is False


def test_validation_command_runner_certification_preserves_governance_guarantees() -> None:
    certification = _load()
    guarantees = certification["governance_guarantees"]

    assert guarantees["validation_command_runner_implemented"] is True
    assert guarantees["allowlist_enforced"] is True
    assert guarantees["replay_preserved"] is True
    assert guarantees["arbitrary_execution_prevented"] is True
    assert guarantees["shell_false_required"] is True
    assert guarantees["repair_prevented"] is True
    assert guarantees["provider_invocation_prevented"] is True
    assert guarantees["worker_invocation_prevented"] is True
    assert guarantees["ready_for_supervised_validation_automation"] is True


def test_validation_command_runner_certification_final_outputs() -> None:
    certification = _load()
    outputs = certification["final_outputs"]

    assert outputs["VALIDATION_COMMAND_RUNNER_IMPLEMENTED"] == "YES"
    assert outputs["ALLOWLIST_ENFORCED"] == "YES"
    assert outputs["REPLAY_PRESERVED"] == "YES"
    assert outputs["ARBITRARY_EXECUTION_PREVENTED"] == "YES"
    assert outputs["READY_FOR_SUPERVISED_VALIDATION_AUTOMATION"] == "YES"
