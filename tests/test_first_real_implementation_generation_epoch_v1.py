"""Tests for AIGOL_FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH_V1."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.provider.provider_proposal_envelope import create_provider_proposal_envelope
from aigol.runtime.first_real_implementation_generation_epoch_runtime import (
    REAL_PROVIDER_ID,
    REAL_PROVIDER_VERSION,
    run_first_real_implementation_generation_epoch,
)


ROOT = Path(__file__).resolve().parents[1]
REQUEST = "Create a real provider-generated implementation candidate for epoch validation."
CREATED_AT = "2026-06-05T21:00:00Z"


class AmbiguousProviderAdapter:
    provider_id = REAL_PROVIDER_ID
    provider_version = REAL_PROVIDER_VERSION

    def generate_proposal(self, request, *, proposal_id: str, timestamp: str):
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=request,
            response={
                "response_type": "REAL_PROVIDER_IMPLEMENTATION_CANDIDATE_V1",
                "implementation_purpose": "Ambiguous provider response.",
                "planned_functionality": ["missing generated artifacts"],
                "generated_files": [],
                "generated_tests": [],
                "validation_requirements": [],
                "known_gaps": ["ambiguous response"],
                "summary": "This response must fail closed.",
            },
            timestamp=timestamp,
        )


def _args(tmp_path):
    parser = build_parser()
    return parser.parse_args(
        [
            "implementation",
            "real-epoch",
            "--request",
            REQUEST,
            "--runtime-root",
            str(tmp_path / "real_epoch_replay"),
            "--workspace",
            str(tmp_path / "workspace"),
            "--created-at",
            CREATED_AT,
            "--actor-id",
            "human.operator",
            "--decision",
            "APPROVE",
            "--decision-reason",
            "Approve validated provider candidate.",
        ]
    )


def test_first_real_implementation_generation_epoch_runs_through_cli_parser(tmp_path) -> None:
    result = run_command(_args(tmp_path))

    assert result["command"] == "aigol implementation real-epoch"
    assert result["epoch_status"] == "REAL_EPOCH_CERTIFIED"
    assert result["fail_closed"] is False
    assert result["final_classification"] == "AIGOL_FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH_STATUS = CERTIFIED"
    assert "001_real_provider_proposal_envelope.json" in result["replay_files"]
    assert "007_interactive_operator_decision_artifact.json" in result["replay_files"]
    assert "011_implementation_certification_artifact.json" in result["replay_files"]
    assert result["workspace_files"] == [
        "aigol/runtime/first_real_epoch_provider_worker.py",
        "governance/FIRST_REAL_EPOCH_PROVIDER_WORKER_V1.md",
        "tests/test_first_real_epoch_provider_worker.py",
    ]


def test_first_real_implementation_generation_epoch_replay_contains_provider_and_certification(tmp_path) -> None:
    result = run_command(_args(tmp_path))
    runtime_root = Path(result["runtime_root"])
    provider = json.loads((runtime_root / "001_real_provider_proposal_envelope.json").read_text())
    manifest = json.loads((runtime_root / "003_implementation_manifest_artifact.json").read_text())
    summary = json.loads((runtime_root / "006_implementation_summary_artifact.json").read_text())
    decision = json.loads((runtime_root / "007_interactive_operator_decision_artifact.json").read_text())
    certification = json.loads((runtime_root / "011_implementation_certification_artifact.json").read_text())
    replay_report = json.loads((runtime_root / "012_replay_inspection_report.json").read_text())

    assert provider["provider_id"] == REAL_PROVIDER_ID
    assert provider["response"]["response_type"] == "REAL_PROVIDER_IMPLEMENTATION_CANDIDATE_V1"
    assert manifest["file_entries"][0]["target_path"] == "aigol/runtime/first_real_epoch_provider_worker.py"
    assert manifest["test_entries"][0]["target_path"] == "tests/test_first_real_epoch_provider_worker.py"
    assert summary["summary_status"] == "IMPLEMENTATION_SUMMARY_CREATED"
    assert certification["certification_status"] == "IMPLEMENTATION_CERTIFIED"
    assert certification["certified_path_count"] == 3
    assert decision["decision"] == "APPROVE"
    assert decision["approval_granted"] is True
    assert replay_report["implementation_certification_hash"] == certification["implementation_certification_hash"]
    assert replay_report["provider_output_trusted_before_validation"] is False
    assert replay_report["materialization_without_approval"] is False


def test_first_real_implementation_generation_epoch_materialized_files_run_generated_tests(tmp_path) -> None:
    result = run_command(_args(tmp_path))
    test_result = subprocess.run(
        ["python", "-m", "pytest", "tests/test_first_real_epoch_provider_worker.py"],
        cwd=result["workspace"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert test_result.returncode == 0


def test_first_real_implementation_generation_epoch_fails_closed_on_collision(tmp_path) -> None:
    first = run_command(_args(tmp_path / "first"))
    second = run_first_real_implementation_generation_epoch(
        human_request=REQUEST,
        runtime_root=tmp_path / "second_replay",
        workspace=first["workspace"],
        created_at=CREATED_AT,
        operator_decision="APPROVE",
        decision_reason="Approve first real epoch collision test.",
    )

    assert second["epoch_status"] == "REAL_EPOCH_FAILED_CLOSED"
    assert second["fail_closed"] is True
    assert "CREATE_ONLY collision" in second["failure_reason"]


def test_first_real_implementation_generation_epoch_fails_closed_on_ambiguous_provider_output(tmp_path) -> None:
    result = run_first_real_implementation_generation_epoch(
        human_request=REQUEST,
        runtime_root=tmp_path / "replay",
        workspace=tmp_path / "workspace",
        created_at=CREATED_AT,
        provider_adapter=AmbiguousProviderAdapter(),
    )

    assert result["epoch_status"] == "REAL_EPOCH_FAILED_CLOSED"
    assert result["fail_closed"] is True
    assert "generated_files must be a non-empty list" in result["failure_reason"]
    assert result["workspace_files"] == []


def test_first_real_implementation_generation_epoch_subprocess_entrypoint(tmp_path) -> None:
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
            str(tmp_path / "real_epoch_replay"),
            "--workspace",
            str(tmp_path / "workspace"),
            "--created-at",
            CREATED_AT,
            "--decision",
            "APPROVE",
            "--decision-reason",
            "Approve subprocess candidate.",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 0
    assert "AIGOL FIRST REAL IMPLEMENTATION GENERATION EPOCH" in result.stdout
    assert "epoch_status: REAL_EPOCH_CERTIFIED" in result.stdout


def test_first_real_implementation_generation_epoch_renders_summary(tmp_path) -> None:
    rendered = render_command_result(run_command(_args(tmp_path)))

    assert "AIGOL FIRST REAL IMPLEMENTATION GENERATION EPOCH" in rendered
    assert "AIGOL_FIRST_REAL_IMPLEMENTATION_GENERATION_EPOCH_STATUS = CERTIFIED" in rendered
