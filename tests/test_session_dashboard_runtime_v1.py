"""Tests for SESSION_DASHBOARD_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json
import subprocess
from pathlib import Path

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cli.commands import dashboard as dashboard_commands
from aigol.cli.commands.dashboard import (
    SESSION_DASHBOARD_RUNTIME_VERSION,
    dashboard_approvals_command,
    dashboard_bridges_command,
    dashboard_chains_command,
    dashboard_command,
    dashboard_execution_command,
    dashboard_learning_command,
    dashboard_summary_command,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash, write_json_immutable


ROOT = Path(__file__).resolve().parents[1]
CREATED_AT = "2026-06-02T16:00:00+00:00"
CANONICAL_CHAIN_ID = "CHAIN-20260602-DASHBOARD-000001"


def _artifact(**values) -> dict:
    artifact = dict(values)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _persist(tmp_path, dirname: str, step: str, event_type: str, artifact: dict, *, index: int = 0) -> Path:
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": event_type,
        "artifact": artifact,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    path = tmp_path / dirname / f"{index:03d}_{step}.json"
    write_json_immutable(path, wrapper)
    return path


def _dashboard_replay(tmp_path) -> dict[str, Path]:
    approval = _artifact(
        artifact_type="PROPOSAL_APPROVAL_ARTIFACT_V1",
        approval_id="APPROVAL-PENDING-000001",
        proposal_id="PROPOSAL-000001",
        human_decision="PENDING",
        approval_status="PENDING",
        created_at=CREATED_AT,
        replay_reference="REPLAY-APPROVAL-PENDING-000001",
        replay_visible=True,
        execution_requested=False,
        execution_request_created=False,
        worker_invoked=False,
    )
    bridge = _artifact(
        artifact_type="IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINK_ARTIFACT_V1",
        bridge_id="BRIDGE-PENDING-000001",
        execution_request_reference=None,
        execution_request_hash=None,
        implementation_plan_reference="PLAN-000001",
        implementation_plan_hash="sha256:plan",
        improvement_approval_reference="IMPROVEMENT-APPROVAL-000001",
        improvement_approval_hash="sha256:approval",
        canonical_chain_id=CANONICAL_CHAIN_ID,
        human_authorization_reference="HUMAN-AUTH-PENDING",
        requested_by="AIGOL",
        created_at=CREATED_AT,
        authorization_status="PENDING",
        replay_reference="REPLAY-BRIDGE-PENDING-000001",
        replay_visible=True,
        execution_request_created=False,
        automatic_execution_request=False,
        automatic_authorization=False,
        worker_dispatched=False,
        worker_invoked=False,
        execution_performed=False,
        governance_mutated=False,
        replay_mutated=False,
    )
    request = _artifact(
        artifact_type="EXECUTION_REQUEST_ARTIFACT_V1",
        execution_request_id="EXECUTION-REQUEST-DASHBOARD-000001",
        execution_request_source_type="IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1",
        canonical_chain_id=CANONICAL_CHAIN_ID,
        status="CREATED",
        created_at=CREATED_AT,
        replay_visible=True,
        worker_dispatched=False,
        worker_invoked=False,
        execution_performed=False,
        governance_mutated=False,
        replay_mutated=False,
    )
    learning = _artifact(
        artifact_type="IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1",
        implementation_plan_id="PLAN-000001",
        canonical_chain_id=CANONICAL_CHAIN_ID,
        created_at=CREATED_AT,
        replay_visible=True,
        execution_request_created=False,
        worker_dispatched=False,
        worker_invoked=False,
        governance_mutated=False,
        replay_mutated=False,
    )
    paths = {
        "approval": _persist(tmp_path, "approval", "approval_pending", "PROPOSAL_APPROVAL_PENDING", approval),
        "bridge": _persist(tmp_path, "bridge", "bridge_pending", "IMPLEMENTATION_PLAN_EXECUTION_REQUEST_PENDING", bridge),
        "request": _persist(
            tmp_path,
            "execution_request",
            "execution_request_created",
            "IMPLEMENTATION_PLAN_EXECUTION_REQUEST_CREATED",
            request,
        ),
        "learning": _persist(
            tmp_path,
            "learning",
            "improvement_implementation_plan_created",
            "IMPROVEMENT_IMPLEMENTATION_PLAN_CREATED",
            learning,
        ),
    }
    return paths


def test_dashboard_summary_aggregates_operator_state(tmp_path) -> None:
    _dashboard_replay(tmp_path)

    result = dashboard_command(replay_root=tmp_path)
    rendered = render_command_result(result)

    assert result["command"] == "aigol dashboard"
    assert result["session_dashboard_runtime_version"] == SESSION_DASHBOARD_RUNTIME_VERSION
    assert result["status"] == "READY"
    assert result["latest_chain_id"] == CANONICAL_CHAIN_ID
    assert result["counts"]["pending_approvals"] == 1
    assert result["counts"]["pending_bridges"] == 1
    assert result["counts"]["recent_execution_requests"] == 1
    assert result["counts"]["recent_learning_artifacts"] == 1
    assert result["read_only"] is True
    assert result["execution_requests_created"] is False
    assert result["worker_dispatched"] is False
    assert result["worker_invoked"] is False
    assert "approval pending" in result["suggested_safe_next_actions"]
    assert "AIGOL DASHBOARD" in rendered


def test_dashboard_subcommands_are_supported(tmp_path) -> None:
    _dashboard_replay(tmp_path)

    results = [
        dashboard_summary_command(replay_root=tmp_path),
        dashboard_approvals_command(replay_root=tmp_path),
        dashboard_bridges_command(replay_root=tmp_path),
        dashboard_chains_command(replay_root=tmp_path),
        dashboard_learning_command(replay_root=tmp_path),
        dashboard_execution_command(replay_root=tmp_path),
    ]

    assert [result["status"] for result in results] == ["READY"] * 6
    assert [result["section"] for result in results] == [
        "summary",
        "approvals",
        "bridges",
        "chains",
        "learning",
        "execution",
    ]


def test_parser_and_run_command_support_dashboard_bridges(tmp_path) -> None:
    _dashboard_replay(tmp_path)
    parser = build_parser()
    args = parser.parse_args(["dashboard", "bridges", "--replay-root", str(tmp_path)])

    result = run_command(args)

    assert result["command"] == "aigol dashboard bridges"
    assert result["counts"]["pending_bridges"] == 1


def test_cli_entrypoint_outputs_dashboard_json(tmp_path) -> None:
    _dashboard_replay(tmp_path)

    result = subprocess.run(
        [
            "python",
            "-m",
            "aigol.cli.aigol_cli",
            "dashboard",
            "summary",
            "--replay-root",
            str(tmp_path),
            "--json",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload["command"] == "aigol dashboard summary"
    assert payload["latest_chain_id"] == CANONICAL_CHAIN_ID


def test_dashboard_does_not_mutate_source_replay(tmp_path) -> None:
    paths = _dashboard_replay(tmp_path)
    before = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}

    dashboard_command(replay_root=tmp_path)

    assert {name: path.read_text(encoding="utf-8") for name, path in paths.items()} == before


def test_dashboard_detects_corrupt_relevant_replay(tmp_path) -> None:
    paths = _dashboard_replay(tmp_path)
    wrapper = json.loads(paths["learning"].read_text(encoding="utf-8"))
    wrapper["artifact"]["canonical_chain_id"] = "CHAIN-CORRUPT"
    paths["learning"].write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    result = dashboard_command(replay_root=tmp_path)

    assert result["status"] == "FAILED_CLOSED"
    assert result["fail_closed"] is True
    assert "hash mismatch" in result["failure_reason"]
    assert result["worker_invoked"] is False
    assert result["execution_performed"] is False


def test_dashboard_runtime_has_no_dispatch_invocation_or_execution_surface() -> None:
    source = inspect.getsource(dashboard_commands)
    cli_source = inspect.getsource(aigol_cli)

    assert "create_execution_request(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "start_execution(" not in source
    assert "dispatch_worker(" not in cli_source
    assert "invoke_worker(" not in cli_source
