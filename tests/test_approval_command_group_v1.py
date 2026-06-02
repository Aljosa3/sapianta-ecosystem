"""Tests for APPROVAL_COMMAND_GROUP_V1."""

from __future__ import annotations

import inspect
import json
import subprocess
from pathlib import Path

from aigol.cli import aigol_cli
from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.cli.commands import approval as approval_commands
from aigol.cli.commands.approval import (
    APPROVAL_COMMAND_GROUP_VERSION,
    approval_approved_command,
    approval_chain_command,
    approval_list_command,
    approval_pending_command,
    approval_rejected_command,
    approval_show_command,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash, write_json_immutable


ROOT = Path(__file__).resolve().parents[1]
CREATED_AT = "2026-06-02T14:00:00+00:00"
CANONICAL_CHAIN_ID = "CHAIN-20260602-APPROVAL-000001"


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


def _approval_replay(tmp_path) -> dict[str, dict]:
    proposal_approval = _artifact(
        artifact_type="PROPOSAL_APPROVAL_ARTIFACT_V1",
        approval_id="APPROVAL-PROPOSAL-000001",
        proposal_id="PROPOSAL-000001",
        proposal_hash="sha256:proposal",
        proposal_status_before="CREATED",
        human_decision="APPROVE",
        approval_status="APPROVED",
        decision_reason="Human operator approves proposal.",
        operator_label="human-operator",
        created_at=CREATED_AT,
        replay_reference="REPLAY-APPROVAL-PROPOSAL-000001",
        replay_visible=True,
        authority=False,
        provider_approval=False,
        worker_approval=False,
        automatic_approval=False,
        execution_requested=False,
        execution_request_created=False,
        provider_invoked=False,
        worker_invoked=False,
    )
    improvement_approval = _artifact(
        artifact_type="IMPROVEMENT_APPROVAL_ARTIFACT_V1",
        improvement_approval_id="APPROVAL-IMPROVEMENT-000001",
        canonical_chain_id=CANONICAL_CHAIN_ID,
        improvement_review_reference="REVIEW-000001",
        improvement_review_hash="sha256:review",
        improvement_proposal_reference="IMPROVEMENT-PROPOSAL-000001",
        improvement_proposal_hash="sha256:improvement-proposal",
        evaluation_reference="EVALUATION-000001",
        evaluation_hash="sha256:evaluation",
        result_reference="RESULT-000001",
        result_hash="sha256:result",
        worker_reference="WORKER-000001",
        decision="REJECTED",
        decision_reason="Human operator rejects implementation planning.",
        decision_reason_hash=replay_hash("Human operator rejects implementation planning."),
        decision_authority="HUMAN",
        human_authorization_reference="HUMAN-AUTH-000001",
        approval_status="REJECTED",
        implementation_authorized=False,
        implementation_reference=None,
        recorded_by="AIGOL",
        recorded_at=CREATED_AT,
        replay_reference="REPLAY-APPROVAL-IMPROVEMENT-000001",
        replay_visible=True,
        provider_authority=False,
        worker_authority=False,
        aigol_autonomous_approval=False,
        implementation_authority=False,
        self_improvement_authority=False,
        governance_mutation_authority=False,
        implementation_performed=False,
        execution_requested=False,
        worker_dispatched=False,
        worker_invoked=False,
        governance_mutated=False,
        replay_mutated=False,
        proposal_mutated=False,
        review_mutated=False,
        evaluation_mutated=False,
        result_mutated=False,
        execution_history_modified=False,
        self_modification_performed=False,
        self_improvement_performed=False,
    )
    _persist(
        tmp_path,
        "proposal_approval",
        "proposal_approval_decided",
        "PROPOSAL_APPROVED",
        proposal_approval,
    )
    _persist(
        tmp_path,
        "improvement_approval",
        "improvement_approval_recorded",
        "IMPROVEMENT_APPROVAL_RECORDED",
        improvement_approval,
    )
    return {
        "proposal_approval": proposal_approval,
        "improvement_approval": improvement_approval,
    }


def test_approval_list_shows_governed_approval_artifacts(tmp_path) -> None:
    _approval_replay(tmp_path)

    result = approval_list_command(replay_root=tmp_path)
    rendered = render_command_result(result)

    assert result["command"] == "aigol approval list"
    assert result["approval_command_group_version"] == APPROVAL_COMMAND_GROUP_VERSION
    assert result["status"] == "READY"
    assert result["approval_count"] == 2
    assert result["read_only"] is True
    assert result["execution_requested"] is False
    assert result["worker_dispatched"] is False
    assert result["worker_invoked"] is False
    assert "AIGOL APPROVAL" in rendered
    assert "APPROVAL-PROPOSAL-000001" in rendered


def test_approval_show_and_status_filters(tmp_path) -> None:
    _approval_replay(tmp_path)

    shown = approval_show_command(approval_id="APPROVAL-IMPROVEMENT-000001", replay_root=tmp_path)
    approved = approval_approved_command(replay_root=tmp_path)
    rejected = approval_rejected_command(replay_root=tmp_path)
    pending = approval_pending_command(replay_root=tmp_path)

    assert shown["approval_count"] == 1
    assert shown["approvals"][0]["approval_type"] == "IMPROVEMENT_APPROVAL"
    assert approved["approval_count"] == 1
    assert approved["approvals"][0]["approval_status"] == "APPROVED"
    assert rejected["approval_count"] == 1
    assert rejected["approvals"][0]["approval_status"] == "REJECTED"
    assert pending["approval_count"] == 0
    assert pending["status"] == "READY"


def test_approval_chain_filters_by_canonical_chain_id(tmp_path) -> None:
    _approval_replay(tmp_path)

    result = approval_chain_command(canonical_chain_id=CANONICAL_CHAIN_ID, replay_root=tmp_path)

    assert result["approval_count"] == 1
    assert result["approvals"][0]["approval_id"] == "APPROVAL-IMPROVEMENT-000001"
    assert result["approvals"][0]["canonical_chain_id"] == CANONICAL_CHAIN_ID


def test_parser_and_run_command_support_approval_chain(tmp_path) -> None:
    _approval_replay(tmp_path)
    parser = build_parser()
    args = parser.parse_args(
        [
            "approval",
            "chain",
            CANONICAL_CHAIN_ID,
            "--replay-root",
            str(tmp_path),
        ]
    )

    result = run_command(args)

    assert result["command"] == "aigol approval chain"
    assert result["approval_count"] == 1


def test_cli_entrypoint_outputs_approval_json(tmp_path) -> None:
    _approval_replay(tmp_path)

    result = subprocess.run(
        [
            "python",
            "-m",
            "aigol.cli.aigol_cli",
            "approval",
            "show",
            "APPROVAL-PROPOSAL-000001",
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
    assert payload["command"] == "aigol approval show"
    assert payload["approval_count"] == 1
    assert payload["approvals"][0]["approval_id"] == "APPROVAL-PROPOSAL-000001"


def test_approval_show_missing_fails_closed_without_authority(tmp_path) -> None:
    _approval_replay(tmp_path)

    result = approval_show_command(approval_id="MISSING-APPROVAL", replay_root=tmp_path)

    assert result["status"] == "FAILED_CLOSED"
    assert result["fail_closed"] is True
    assert result["execution_requested"] is False
    assert result["worker_dispatched"] is False
    assert result["worker_invoked"] is False
    assert "approval not found" in result["failure_reason"]


def test_approval_command_detects_corrupt_approval_replay(tmp_path) -> None:
    _approval_replay(tmp_path)
    path = tmp_path / "proposal_approval" / "000_proposal_approval_decided.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["approval_status"] = "REJECTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    result = approval_list_command(replay_root=tmp_path)

    assert result["status"] == "FAILED_CLOSED"
    assert result["fail_closed"] is True
    assert "hash mismatch" in result["failure_reason"]


def test_approval_command_group_has_no_dispatch_invocation_or_execution_surface() -> None:
    source = inspect.getsource(approval_commands)
    cli_source = inspect.getsource(aigol_cli)

    assert "decide_proposal_approval(" not in source
    assert "decide_improvement_approval(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "start_execution(" not in source
    assert "dispatch_worker(" not in cli_source
    assert "invoke_worker(" not in cli_source
