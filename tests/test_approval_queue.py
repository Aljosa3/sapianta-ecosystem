from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.approval.approval_models import ApprovalError
from sapianta_bridge.approval.approval_queue import (
    approve_approval,
    build_approval_artifact,
    enqueue_advisory_proposal,
)
from sapianta_bridge.approval.approval_reader import pending_approvals
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


def _append_completed(config: TransportConfig, task_id: str = "TASK-001") -> None:
    append_replay_log(
        config.replay_log_path,
        replay_entry(
            task_id=task_id,
            execution_timestamp="2026-05-12T00:00:00+00:00",
            codex_exit_code=0,
            task_hash="a" * 64,
            result_hash="b" * 64,
            processing_duration_seconds=1.0,
            final_state="COMPLETED",
        ),
    )


def _reflection(config: TransportConfig) -> dict:
    _append_completed(config)
    return generate_reflection(
        "TASK-001",
        config,
        timestamp="2026-05-12T00:00:01+00:00",
    )["reflection"]


def test_approval_artifact_deterministic(tmp_path: Path) -> None:
    config = _config(tmp_path)
    reflection = _reflection(config)
    proposal = reflection["advisory_proposals"][0]

    first = build_approval_artifact(
        reflection,
        proposal,
        timestamp="2026-05-12T00:00:02+00:00",
    )
    second = build_approval_artifact(
        reflection,
        proposal,
        timestamp="2026-05-12T00:00:02+00:00",
    )

    assert first == second
    assert first["decision"] == "PENDING"
    assert first["allowed_to_execute_automatically"] is False


def test_enqueue_preserves_lineage(tmp_path: Path) -> None:
    config = _config(tmp_path)
    reflection = _reflection(config)

    result = enqueue_advisory_proposal(
        reflection,
        config=config,
        timestamp="2026-05-12T00:00:02+00:00",
    )
    approval = result["approval"]

    assert approval["source_reflection_id"] == reflection["reflection_id"]
    assert approval["source_task_id"] == reflection["source_task_id"]
    assert approval["lineage"] == {
        "source_reflection_id": reflection["reflection_id"],
        "source_task_id": reflection["source_task_id"],
    }


def test_duplicate_approval_blocked(tmp_path: Path) -> None:
    config = _config(tmp_path)
    reflection = _reflection(config)
    enqueue_advisory_proposal(
        reflection,
        config=config,
        timestamp="2026-05-12T00:00:02+00:00",
    )

    with pytest.raises(ApprovalError) as exc_info:
        enqueue_advisory_proposal(
            reflection,
            config=config,
            timestamp="2026-05-12T00:00:03+00:00",
        )

    assert exc_info.value.field == "approval_id"


def test_malformed_reflection_blocked(tmp_path: Path) -> None:
    config = _config(tmp_path)

    with pytest.raises(ApprovalError) as exc_info:
        enqueue_advisory_proposal(
            {"reflection_id": "REFLECTION-001"},
            config=config,
            timestamp="2026-05-12T00:00:02+00:00",
        )

    assert exc_info.value.field == "timestamp"


def test_replay_safe_ordering_preserved(tmp_path: Path) -> None:
    config = _config(tmp_path)
    reflection = _reflection(config)
    second_reflection = dict(reflection)
    second_reflection["reflection_id"] = "REFLECTION-SECOND"
    enqueue_advisory_proposal(
        second_reflection,
        config=config,
        timestamp="2026-05-12T00:00:03+00:00",
    )
    enqueue_advisory_proposal(
        reflection,
        config=config,
        timestamp="2026-05-12T00:00:02+00:00",
    )

    approvals = pending_approvals(config)

    assert [approval["timestamp"] for approval in approvals] == [
        "2026-05-12T00:00:02+00:00",
        "2026-05-12T00:00:03+00:00",
    ]


def test_no_transport_invocation_introduced(tmp_path: Path) -> None:
    config = _config(tmp_path)
    reflection = _reflection(config)
    result = enqueue_advisory_proposal(
        reflection,
        config=config,
        timestamp="2026-05-12T00:00:02+00:00",
    )

    approve_approval(
        result["approval"]["approval_id"],
        approved_by="human",
        reason="bounded governance checkpoint approved",
        config=config,
        timestamp="2026-05-12T00:00:03+00:00",
    )

    assert list(config.tasks_dir.glob("*.json")) == []
    assert list(config.processing_dir.glob("*.json")) == []
