from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.approval.approval_queue import (
    approve_approval,
    enqueue_advisory_proposal,
    reject_approval,
)
from sapianta_bridge.approval.approval_reader import approved_approvals, decision_history, rejected_approvals
from sapianta_bridge.reflection.reflection_engine import generate_reflection
from sapianta_bridge.transport.replay_log import append_replay_log, replay_entry
from sapianta_bridge.transport.transport_config import TransportConfig


def _config(tmp_path: Path) -> TransportConfig:
    config = TransportConfig(
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path / "workspace",
        quarantine_root=tmp_path / "quarantine",
    )
    config.ensure_directories()
    config.workspace.mkdir()
    return config


def _reflection(config: TransportConfig, task_id: str = "TASK-001") -> dict:
    append_replay_log(
        config.replay_log_path,
        replay_entry(
            task_id=task_id,
            execution_timestamp=f"2026-05-12T00:00:0{task_id[-1]}+00:00",
            codex_exit_code=0,
            task_hash="a" * 64,
            result_hash="b" * 64,
            processing_duration_seconds=1.0,
            final_state="COMPLETED",
        ),
    )
    return generate_reflection(
        task_id,
        config,
        timestamp=f"2026-05-12T00:00:1{task_id[-1]}+00:00",
    )["reflection"]


def test_approve_creates_immutable_decision_artifact(tmp_path: Path) -> None:
    config = _config(tmp_path)
    approval = enqueue_advisory_proposal(
        _reflection(config),
        config=config,
        timestamp="2026-05-12T00:00:02+00:00",
    )["approval"]

    result = approve_approval(
        approval["approval_id"],
        approved_by="human",
        reason="bounded observability improvement approved",
        config=config,
        timestamp="2026-05-12T00:00:03+00:00",
    )

    assert result["decision"]["decision"] == "APPROVED"
    assert result["decision"]["execution_authority_granted"] is False
    assert len(approved_approvals(config)) == 1
    assert len(decision_history(config)) == 1


def test_reject_creates_immutable_decision_artifact(tmp_path: Path) -> None:
    config = _config(tmp_path)
    approval = enqueue_advisory_proposal(
        _reflection(config),
        config=config,
        timestamp="2026-05-12T00:00:02+00:00",
    )["approval"]

    result = reject_approval(
        approval["approval_id"],
        approved_by="human",
        reason="proposal deferred",
        config=config,
        timestamp="2026-05-12T00:00:03+00:00",
    )

    assert result["decision"]["decision"] == "REJECTED"
    assert result["decision"]["execution_authority_granted"] is False
    assert len(rejected_approvals(config)) == 1
    assert len(decision_history(config)) == 1


def test_execution_authority_always_false(tmp_path: Path) -> None:
    config = _config(tmp_path)
    approval = enqueue_advisory_proposal(
        _reflection(config),
        config=config,
        timestamp="2026-05-12T00:00:02+00:00",
    )["approval"]

    result = approve_approval(
        approval["approval_id"],
        approved_by="human",
        reason="approval recorded without execution authority",
        config=config,
        timestamp="2026-05-12T00:00:03+00:00",
    )

    assert result["decision"]["execution_authority_granted"] is False
