"""Tests for CLI_CHAIN_INSPECTION_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json
import os
import subprocess
from pathlib import Path

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cli.commands import chain_inspection
from aigol.cli.commands.chain_inspection import (
    CLI_CHAIN_INSPECTION_RUNTIME_VERSION,
    show_chain_command,
    show_chain_summary_command,
    show_execution_lifecycle_command,
    show_full_lineage_command,
    show_latest_chain_command,
    show_learning_lifecycle_command,
)
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


ROOT = Path(__file__).resolve().parents[1]
CREATED_AT = "2026-06-02T12:00:00+00:00"
CANONICAL_CHAIN_ID = "CHAIN-20260602-CLI-000001"


def _artifact(**values) -> dict:
    artifact = dict(values)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _persist(tmp_path, dirname: str, step: str, artifact: dict, *, index: int = 0) -> Path:
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": artifact.get("event_type") or step.upper(),
        "artifact": artifact,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    path = tmp_path / dirname / f"{index:03d}_{step}.json"
    write_json_immutable(path, wrapper)
    return path


def _chain(tmp_path, *, canonical_chain_id: str = CANONICAL_CHAIN_ID, created_at: str = CREATED_AT) -> dict[str, dict]:
    conversation = _artifact(
        event_type="CONVERSATION_RESPONSE_CREATED",
        conversation_id="CONVERSATION-CLI-000001",
        canonical_chain_id=canonical_chain_id,
        created_at=created_at,
        replay_visible=True,
    )
    router = _artifact(
        artifact_type="SOURCE_OF_TRUTH_ROUTER_SELECTION_ARTIFACT_V1",
        router_id="ROUTER-CLI-000001",
        canonical_chain_id=canonical_chain_id,
        created_at=created_at,
        selected_source="REPLAY",
        replay_visible=True,
    )
    approval = _artifact(
        artifact_type="IMPROVEMENT_APPROVAL_ARTIFACT_V1",
        improvement_approval_id="APPROVAL-CLI-000001",
        canonical_chain_id=canonical_chain_id,
        created_at=created_at,
        replay_visible=True,
    )
    plan = _artifact(
        artifact_type="IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1",
        implementation_plan_id="PLAN-CLI-000001",
        canonical_chain_id=canonical_chain_id,
        improvement_approval_reference=approval["improvement_approval_id"],
        improvement_approval_hash=approval["artifact_hash"],
        created_at=created_at,
        replay_visible=True,
    )
    request = _artifact(
        artifact_type="EXECUTION_REQUEST_ARTIFACT_V1",
        execution_request_id="REQUEST-CLI-000001",
        canonical_chain_id=canonical_chain_id,
        implementation_plan_reference=plan["implementation_plan_id"],
        implementation_plan_hash=plan["artifact_hash"],
        improvement_approval_reference=approval["improvement_approval_id"],
        improvement_approval_hash=approval["artifact_hash"],
        execution_request_source_type="IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1",
        created_at=created_at,
        replay_visible=True,
    )
    bridge = _artifact(
        artifact_type="IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINK_ARTIFACT_V1",
        bridge_id="BRIDGE-CLI-000001",
        canonical_chain_id=canonical_chain_id,
        execution_request_reference=request["execution_request_id"],
        execution_request_hash=request["artifact_hash"],
        implementation_plan_reference=plan["implementation_plan_id"],
        implementation_plan_hash=plan["artifact_hash"],
        created_at=created_at,
        replay_visible=True,
    )
    worker = _artifact(
        artifact_type="WORKER_ARTIFACT_V1",
        worker_id="WORKER-CLI-000001",
        canonical_chain_id=canonical_chain_id,
        created_at=created_at,
        replay_visible=True,
    )
    execution = _artifact(
        artifact_type="EXECUTION_ARTIFACT_V1",
        execution_id="EXECUTION-CLI-000001",
        canonical_chain_id=canonical_chain_id,
        execution_request_reference=request["execution_request_id"],
        worker_reference=worker["worker_id"],
        worker_hash=worker["artifact_hash"],
        started_at=created_at,
        replay_visible=True,
    )
    artifacts = {
        "conversation": conversation,
        "router": router,
        "approval": approval,
        "plan": plan,
        "request": request,
        "bridge": bridge,
        "worker": worker,
        "execution": execution,
    }
    for index, (name, artifact) in enumerate(artifacts.items()):
        _persist(tmp_path, name, name, artifact, index=index)
    return artifacts


def test_show_chain_command_uses_unified_reconstruction_and_renders_summary(tmp_path) -> None:
    replay_root = tmp_path / "replay"
    report_root = tmp_path / "reports"
    _chain(replay_root)

    result = show_chain_command(
        canonical_chain_id=CANONICAL_CHAIN_ID,
        replay_root=replay_root,
        report_root=report_root,
        created_at=CREATED_AT,
    )
    rendered = render_command_result(result)

    assert result["command"] == "aigol show-chain"
    assert result["cli_chain_inspection_runtime_version"] == CLI_CHAIN_INSPECTION_RUNTIME_VERSION
    assert result["status"] == "READY"
    assert result["reconstruction_status"] == "RECONSTRUCTED"
    assert result["source_replay_read_only"] is True
    assert result["inspection_report_persisted"] is False
    assert result["operationally_read_only"] is True
    assert result["conversation_present"] is True
    assert result["source_routing_present"] is True
    assert result["execution_requests_created"] is False
    assert result["workers_dispatched"] is False
    assert result["workers_invoked"] is False
    assert "AIGOL CHAIN INSPECTION" in rendered
    assert f"canonical_chain_id: {CANONICAL_CHAIN_ID}" in rendered


def test_all_chain_inspection_commands_are_supported(tmp_path) -> None:
    replay_root = tmp_path / "replay"
    _chain(replay_root)

    commands = [
        show_latest_chain_command(
            replay_root=replay_root,
            report_root=tmp_path / "latest_reports",
            created_at=CREATED_AT,
        ),
        show_execution_lifecycle_command(
            canonical_chain_id=CANONICAL_CHAIN_ID,
            replay_root=replay_root,
            report_root=tmp_path / "execution_reports",
            created_at=CREATED_AT,
        ),
        show_learning_lifecycle_command(
            canonical_chain_id=CANONICAL_CHAIN_ID,
            replay_root=replay_root,
            report_root=tmp_path / "learning_reports",
            created_at=CREATED_AT,
        ),
        show_full_lineage_command(
            canonical_chain_id=CANONICAL_CHAIN_ID,
            replay_root=replay_root,
            report_root=tmp_path / "lineage_reports",
            created_at=CREATED_AT,
        ),
        show_chain_summary_command(
            canonical_chain_id=CANONICAL_CHAIN_ID,
            replay_root=replay_root,
            report_root=tmp_path / "summary_reports",
            created_at=CREATED_AT,
        ),
    ]

    assert [command["status"] for command in commands] == ["READY"] * 5
    assert commands[0]["command"] == "aigol show-latest-chain"
    assert commands[1]["reconstruction_scope"] == "EXECUTION_LIFECYCLE"
    assert commands[2]["reconstruction_scope"] == "LEARNING_LIFECYCLE"
    assert commands[3]["reconstruction_scope"] == "FULL_LINEAGE"
    assert commands[4]["summary_only"] is True


def test_parser_and_run_command_support_show_full_lineage(tmp_path) -> None:
    replay_root = tmp_path / "replay"
    report_root = tmp_path / "reports"
    _chain(replay_root)
    parser = build_parser()

    args = parser.parse_args(
        [
            "show-full-lineage",
            CANONICAL_CHAIN_ID,
            "--replay-root",
            str(replay_root),
            "--report-root",
            str(report_root),
            "--created-at",
            CREATED_AT,
        ]
    )
    result = run_command(args)

    assert result["command"] == "aigol show-full-lineage"
    assert result["status"] == "READY"
    assert result["replay_evidence_artifact_count"] >= 8


def test_cli_entrypoint_outputs_json_summary(tmp_path) -> None:
    replay_root = tmp_path / "replay"
    report_root = tmp_path / "reports"
    _chain(replay_root)

    result = subprocess.run(
        [
            "python",
            "-m",
            "aigol.cli.aigol_cli",
            "show-chain-summary",
            CANONICAL_CHAIN_ID,
            "--replay-root",
            str(replay_root),
            "--report-root",
            str(report_root),
            "--created-at",
            CREATED_AT,
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
    assert payload["command"] == "aigol show-chain-summary"
    assert payload["status"] == "READY"
    assert payload["inspection_report_persisted"] is False
    assert payload["summary_only"] is True


def test_show_latest_chain_cli_is_repeatable_with_default_arguments(tmp_path) -> None:
    _chain(tmp_path)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)

    command = ["python", "-m", "aigol.cli.aigol_cli", "show-latest-chain", "--json"]
    first = subprocess.run(
        command,
        cwd=str(tmp_path),
        env=env,
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    second = subprocess.run(
        command,
        cwd=str(tmp_path),
        env=env,
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    first_payload = json.loads(first.stdout)
    second_payload = json.loads(second.stdout)

    assert first.returncode == 0
    assert second.returncode == 0
    assert first_payload["status"] == "READY"
    assert second_payload["status"] == "READY"
    assert first_payload["canonical_chain_id"] == CANONICAL_CHAIN_ID
    assert second_payload["canonical_chain_id"] == CANONICAL_CHAIN_ID
    assert first_payload["inspection_report_persisted"] is False
    assert second_payload["inspection_report_persisted"] is False
    assert not (tmp_path / ".aigol_chain_inspection_runtime").exists()


def test_fail_closed_reconstruction_is_displayed_to_operator(tmp_path) -> None:
    result = show_chain_command(
        canonical_chain_id="CHAIN-MISSING",
        replay_root=tmp_path / "missing_replay_root",
        report_root=tmp_path / "reports",
        created_at=CREATED_AT,
    )
    rendered = render_command_result(result)

    assert result["status"] == "FAILED_CLOSED"
    assert result["fail_closed"] is True
    assert result["workers_dispatched"] is False
    assert result["workers_invoked"] is False
    assert result["inspection_report_persisted"] is False
    assert "fail_closed: True" in rendered
    assert "replay root missing" in rendered


def test_chain_inspection_does_not_mutate_source_replay(tmp_path) -> None:
    replay_root = tmp_path / "replay"
    report_root = tmp_path / "reports"
    _chain(replay_root)
    source_file = replay_root / "execution" / "007_execution.json"
    before = source_file.read_text(encoding="utf-8")

    show_full_lineage_command(
        canonical_chain_id=CANONICAL_CHAIN_ID,
        replay_root=replay_root,
        report_root=report_root,
        created_at=CREATED_AT,
    )

    assert source_file.read_text(encoding="utf-8") == before
    assert not report_root.exists()


def test_chain_inspection_module_has_no_execution_authority_imports() -> None:
    source = inspect.getsource(chain_inspection)

    assert "create_execution_request(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "start_execution(" not in source
    assert "subprocess" not in source
    assert "import requests" not in source
    assert "socket" not in source
