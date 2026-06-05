"""Tests for AIGOL_FIRST_END_TO_END_IMPLEMENTATION_GENERATION_EPOCH_V1."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command


ROOT = Path(__file__).resolve().parents[1]


def _args(tmp_path):
    parser = build_parser()
    return parser.parse_args(
        [
            "implementation",
            "epoch",
            "--request",
            "Create a minimal governed implementation candidate for operator epoch validation.",
            "--runtime-root",
            str(tmp_path / "epoch_replay"),
            "--workspace",
            str(tmp_path / "workspace"),
            "--created-at",
            "2026-06-05T20:00:00Z",
            "--actor-id",
            "human.operator",
        ]
    )


def test_implementation_generation_epoch_runs_through_cli_parser(tmp_path) -> None:
    result = run_command(_args(tmp_path))

    assert result["command"] == "aigol implementation epoch"
    assert result["epoch_status"] == "EPOCH_CERTIFIED"
    assert result["fail_closed"] is False
    assert result["epoch_hash"].startswith("sha256:")
    assert result["final_classification"] == (
        "AIGOL_FIRST_END_TO_END_IMPLEMENTATION_GENERATION_EPOCH_STATUS = "
        "CERTIFIED_WITH_OPERATOR_FRICTION"
    )
    assert "009_implementation_certification_artifact.json" in result["replay_files"]
    assert "010_usage_report.md" in result["replay_files"]
    assert "014_certification_report.md" in result["replay_files"]
    assert result["workspace_files"] == [
        "aigol/runtime/first_e2e_epoch_sample_worker.py",
        "governance/FIRST_E2E_EPOCH_SAMPLE_WORKER_V1.md",
        "tests/test_first_e2e_epoch_sample_worker.py",
    ]


def test_implementation_generation_epoch_reports_and_certifies_lineage(tmp_path) -> None:
    result = run_command(_args(tmp_path))
    runtime_root = Path(result["runtime_root"])
    certification = json.loads((runtime_root / "009_implementation_certification_artifact.json").read_text())

    assert certification["artifact_type"] == "IMPLEMENTATION_CERTIFICATION_ARTIFACT_V1"
    assert certification["certification_status"] == "IMPLEMENTATION_CERTIFIED"
    assert certification["certified_path_count"] == 3
    assert "certified implementation lifecycle" in (runtime_root / "010_usage_report.md").read_text()
    assert "Replay chain persisted" in (runtime_root / "011_replay_inspection_report.md").read_text()
    assert "operator friction remains visible" in (runtime_root / "012_operator_friction_analysis.md").read_text()
    assert "Provider-assisted candidate generation" in (runtime_root / "013_remaining_blockers_analysis.md").read_text()
    assert "AIGOL_FIRST_END_TO_END_IMPLEMENTATION_GENERATION_EPOCH_STATUS" in (
        runtime_root / "014_certification_report.md"
    ).read_text()


def test_implementation_generation_epoch_fails_closed_on_create_only_collision(tmp_path) -> None:
    first = run_command(_args(tmp_path / "first"))
    second_args = build_parser().parse_args(
        [
            "implementation",
            "epoch",
            "--request",
            "Create a minimal governed implementation candidate for operator epoch validation.",
            "--runtime-root",
            str(tmp_path / "second_replay"),
            "--workspace",
            first["workspace"],
            "--created-at",
            "2026-06-05T20:00:00Z",
        ]
    )
    second = run_command(second_args)

    assert second["epoch_status"] == "EPOCH_FAILED_CLOSED"
    assert second["fail_closed"] is True
    assert "CREATE_ONLY collision" in second["failure_reason"]


def test_implementation_generation_epoch_subprocess_entrypoint(tmp_path) -> None:
    result = subprocess.run(
        [
            "python",
            "-m",
            "aigol.cli.aigol_cli",
            "implementation",
            "epoch",
            "--request",
            "Create a minimal governed implementation candidate for operator epoch validation.",
            "--runtime-root",
            str(tmp_path / "epoch_replay"),
            "--workspace",
            str(tmp_path / "workspace"),
            "--created-at",
            "2026-06-05T20:00:00Z",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 0
    assert "AIGOL IMPLEMENTATION GENERATION EPOCH" in result.stdout
    assert "epoch_status: EPOCH_CERTIFIED" in result.stdout


def test_implementation_generation_epoch_renders_summary(tmp_path) -> None:
    rendered = render_command_result(run_command(_args(tmp_path)))

    assert "AIGOL IMPLEMENTATION GENERATION EPOCH" in rendered
    assert "final_classification: AIGOL_FIRST_END_TO_END_IMPLEMENTATION_GENERATION_EPOCH_STATUS" in rendered
