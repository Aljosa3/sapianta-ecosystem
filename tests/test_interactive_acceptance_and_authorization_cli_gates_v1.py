"""Tests for AIGOL_INTERACTIVE_ACCEPTANCE_AND_AUTHORIZATION_CLI_GATES_V1."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from aigol.cli.aigol_cli import build_parser, run_command


ROOT = Path(__file__).resolve().parents[1]
REQUEST = "Create a provider generated implementation candidate requiring interactive approval."
CREATED_AT = "2026-06-05T22:00:00Z"


def _args(tmp_path, decision: str, reason: str):
    return build_parser().parse_args(
        [
            "implementation",
            "real-epoch",
            "--request",
            REQUEST,
            "--runtime-root",
            str(tmp_path / "replay"),
            "--workspace",
            str(tmp_path / "workspace"),
            "--created-at",
            CREATED_AT,
            "--actor-id",
            "human.operator",
            "--decision",
            decision,
            "--decision-reason",
            reason,
        ]
    )


def test_interactive_gate_approve_continues_to_authorization_materialization_and_certification(tmp_path) -> None:
    result = run_command(_args(tmp_path, "APPROVE", "Validated paths and hashes; approve CREATE_ONLY mutation."))
    runtime_root = Path(result["runtime_root"])
    decision = json.loads((runtime_root / "007_interactive_operator_decision_artifact.json").read_text())
    authorization = json.loads((runtime_root / "009_filesystem_mutation_authorization_artifact.json").read_text())
    mutation = json.loads((runtime_root / "010_filesystem_mutation_artifact.json").read_text())
    certification = json.loads((runtime_root / "011_implementation_certification_artifact.json").read_text())

    assert result["epoch_status"] == "REAL_EPOCH_CERTIFIED"
    assert decision["decision"] == "APPROVE"
    assert decision["approval_granted"] is True
    assert authorization["authorization_status"] == "FILESYSTEM_MUTATION_AUTHORIZED"
    assert mutation["mutation_status"] == "FILESYSTEM_MUTATION_COMPLETED"
    assert certification["certification_status"] == "IMPLEMENTATION_CERTIFIED"
    assert result["workspace_files"]


def test_interactive_gate_reject_fails_closed_before_authorization_or_materialization(tmp_path) -> None:
    result = run_command(_args(tmp_path, "REJECT", "Operator rejects provider candidate."))
    runtime_root = Path(result["runtime_root"])
    decision = json.loads((runtime_root / "007_interactive_operator_decision_artifact.json").read_text())

    assert result["epoch_status"] == "REAL_EPOCH_REJECTED_FAILED_CLOSED"
    assert result["fail_closed"] is True
    assert decision["decision"] == "REJECT"
    assert decision["rejection_recorded"] is True
    assert "009_filesystem_mutation_authorization_artifact.json" not in result["replay_files"]
    assert "010_filesystem_mutation_artifact.json" not in result["replay_files"]
    assert result["workspace_files"] == []


def test_interactive_gate_abort_terminates_without_authorization_or_materialization(tmp_path) -> None:
    result = run_command(_args(tmp_path, "ABORT", "Operator aborts pending implementation."))
    runtime_root = Path(result["runtime_root"])
    decision = json.loads((runtime_root / "007_interactive_operator_decision_artifact.json").read_text())

    assert result["epoch_status"] == "REAL_EPOCH_ABORTED"
    assert result["fail_closed"] is False
    assert decision["decision"] == "ABORT"
    assert decision["abort_recorded"] is True
    assert "009_filesystem_mutation_authorization_artifact.json" not in result["replay_files"]
    assert "010_filesystem_mutation_artifact.json" not in result["replay_files"]
    assert result["workspace_files"] == []


def test_interactive_gate_prompts_when_decision_flag_is_omitted(tmp_path) -> None:
    result = subprocess.run(
        [
            "python",
            "-m",
            "aigol.cli.aigol_cli",
            "implementation",
            "real-epoch",
            "--request",
            REQUEST,
            "--runtime-root",
            str(tmp_path / "replay"),
            "--workspace",
            str(tmp_path / "workspace"),
            "--created-at",
            CREATED_AT,
        ],
        cwd=str(ROOT),
        input="APPROVE\nApprove prompted checkpoint.\n",
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 0
    assert "AIGOL INTERACTIVE ACCEPTANCE CHECKPOINT" in result.stdout
    assert "affected_paths:" in result.stdout
    assert "epoch_status: REAL_EPOCH_CERTIFIED" in result.stdout
