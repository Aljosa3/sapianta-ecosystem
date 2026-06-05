"""Tests for AIGOL_MULTI_PROVIDER_COMPETITIVE_PROPOSAL_RUNTIME_V1."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.runtime.multi_provider_competitive_proposal_runtime import (
    CompetitiveImplementationProviderAdapter,
    run_multi_provider_competitive_proposal_runtime,
)


ROOT = Path(__file__).resolve().parents[1]
REQUEST = "Create competing governed implementation candidates for operator selection."
CREATED_AT = "2026-06-05T23:00:00Z"


def _args(tmp_path, selection: str):
    return build_parser().parse_args(
        [
            "implementation",
            "compete",
            "--request",
            REQUEST,
            "--runtime-root",
            str(tmp_path / "competition_replay"),
            "--workspace",
            str(tmp_path / "workspace"),
            "--created-at",
            CREATED_AT,
            "--actor-id",
            "human.operator",
            "--selection",
            selection,
            "--decision-reason",
            f"Operator selected {selection}.",
        ]
    )


def test_multi_provider_competition_single_winner_materializes_only_selected_provider(tmp_path) -> None:
    result = run_command(_args(tmp_path, "PROVIDER_B"))
    runtime_root = Path(result["runtime_root"])
    decision = json.loads((runtime_root / "011_competitive_selection_decision_artifact.json").read_text())
    authorization = json.loads((runtime_root / "013_selected_filesystem_mutation_authorization_artifact.json").read_text())
    mutation = json.loads((runtime_root / "014_selected_filesystem_mutation_artifact.json").read_text())
    certification = json.loads((runtime_root / "015_selected_implementation_certification_artifact.json").read_text())
    replay = json.loads((runtime_root / "016_competitive_replay_artifact.json").read_text())

    assert result["competition_status"] == "MULTI_PROVIDER_COMPETITION_CERTIFIED"
    assert decision["decision"] == "SELECT_PROVIDER"
    assert decision["selected_provider_id"] == "PROVIDER_B"
    assert authorization["filesystem_mutation_authorized"] is True
    assert mutation["filesystem_mutated"] is True
    assert certification["certification_status"] == "IMPLEMENTATION_CERTIFIED"
    assert replay["selected_provider_id"] == "PROVIDER_B"
    assert replay["authorization_only_for_selected_provider"] is True
    assert result["workspace_files"] == [
        "aigol/runtime/multi_provider_selected_worker.py",
        "governance/MULTI_PROVIDER_SELECTED_WORKER_V1.md",
        "tests/test_multi_provider_selected_worker.py",
    ]
    worker = (Path(result["workspace"]) / "aigol/runtime/multi_provider_selected_worker.py").read_text()
    assert "'provider': 'PROVIDER_B'" in worker


def test_multi_provider_competition_reject_all_fails_closed_before_authorization(tmp_path) -> None:
    result = run_command(_args(tmp_path, "REJECT_ALL"))
    runtime_root = Path(result["runtime_root"])
    decision = json.loads((runtime_root / "011_competitive_selection_decision_artifact.json").read_text())

    assert result["competition_status"] == "MULTI_PROVIDER_REJECTED_FAILED_CLOSED"
    assert result["fail_closed"] is True
    assert decision["decision"] == "REJECT_ALL"
    assert "013_selected_filesystem_mutation_authorization_artifact.json" not in result["replay_files"]
    assert "014_selected_filesystem_mutation_artifact.json" not in result["replay_files"]
    assert result["workspace_files"] == []


def test_multi_provider_competition_abort_terminates_without_authorization(tmp_path) -> None:
    result = run_command(_args(tmp_path, "ABORT"))
    runtime_root = Path(result["runtime_root"])
    decision = json.loads((runtime_root / "011_competitive_selection_decision_artifact.json").read_text())

    assert result["competition_status"] == "MULTI_PROVIDER_ABORTED"
    assert result["fail_closed"] is False
    assert decision["decision"] == "ABORT"
    assert "013_selected_filesystem_mutation_authorization_artifact.json" not in result["replay_files"]
    assert "014_selected_filesystem_mutation_artifact.json" not in result["replay_files"]
    assert result["workspace_files"] == []


def test_multi_provider_competition_records_one_provider_validation_failure_and_selects_valid_winner(tmp_path) -> None:
    adapters = {
        "PROVIDER_A": CompetitiveImplementationProviderAdapter("PROVIDER_A", "valid conservative helper"),
        "PROVIDER_B": CompetitiveImplementationProviderAdapter(
            "PROVIDER_B",
            "invalid missing tests",
            invalid_tests=True,
        ),
        "PROVIDER_C": CompetitiveImplementationProviderAdapter("PROVIDER_C", "valid audit helper"),
    }
    result = run_multi_provider_competitive_proposal_runtime(
        human_request=REQUEST,
        runtime_root=tmp_path / "competition_replay",
        workspace=tmp_path / "workspace",
        created_at=CREATED_AT,
        selection="PROVIDER_C",
        decision_reason="Select valid provider C after provider B validation failed.",
        provider_adapters=adapters,
    )
    replay = result["competitive_replay"]
    provider_b = next(item for item in replay["proposal_summaries"] if item["provider_id"] == "PROVIDER_B")

    assert result["competition_status"] == "MULTI_PROVIDER_COMPETITION_CERTIFIED"
    assert provider_b["validation_status"] == "FAILED_VALIDATION"
    assert "generated_tests must be a non-empty list" in provider_b["failure_reason"]
    assert replay["selected_provider_id"] == "PROVIDER_C"
    worker = (Path(result["workspace"]) / "aigol/runtime/multi_provider_selected_worker.py").read_text()
    assert "'provider': 'PROVIDER_C'" in worker


def test_multi_provider_competition_subprocess_and_render(tmp_path) -> None:
    completed = subprocess.run(
        [
            "python",
            "-m",
            "aigol.cli.aigol_cli",
            "implementation",
            "compete",
            "--request",
            REQUEST,
            "--runtime-root",
            str(tmp_path / "competition_replay"),
            "--workspace",
            str(tmp_path / "workspace"),
            "--created-at",
            CREATED_AT,
            "--selection",
            "PROVIDER_A",
            "--decision-reason",
            "Select provider A.",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert completed.returncode == 0
    assert "AIGOL MULTI PROVIDER COMPETITIVE PROPOSAL" in completed.stdout
    assert "PROVIDER_A" in completed.stdout
    rendered = render_command_result(run_command(_args(tmp_path / "render", "PROVIDER_A")))
    assert "AIGOL_MULTI_PROVIDER_COMPETITIVE_PROPOSAL_RUNTIME_STATUS = CERTIFIED" in rendered
