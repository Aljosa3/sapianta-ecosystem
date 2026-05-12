from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.approval.approval_queue import enqueue_advisory_proposal
from sapianta_bridge.approval.approval_reader import pending_approvals
from sapianta_bridge.approval.approval_storage import read_approval
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


def _reflection(config: TransportConfig) -> dict:
    append_replay_log(
        config.replay_log_path,
        replay_entry(
            task_id="TASK-001",
            execution_timestamp="2026-05-12T00:00:00+00:00",
            codex_exit_code=0,
            task_hash="a" * 64,
            result_hash="b" * 64,
            processing_duration_seconds=1.0,
            final_state="COMPLETED",
        ),
    )
    return generate_reflection(
        "TASK-001",
        config,
        timestamp="2026-05-12T00:00:01+00:00",
    )["reflection"]


def test_approval_storage_writes_pending_artifact(tmp_path: Path) -> None:
    config = _config(tmp_path)
    result = enqueue_advisory_proposal(
        _reflection(config),
        config=config,
        timestamp="2026-05-12T00:00:02+00:00",
    )
    path = Path(result["approval_path"])

    assert path.parent == config.runtime_root / "approval" / "pending"
    assert read_approval(path)["approval_id"] == result["approval"]["approval_id"]


def test_approval_history_append_only(tmp_path: Path) -> None:
    config = _config(tmp_path)
    reflection = _reflection(config)
    enqueue_advisory_proposal(
        reflection,
        config=config,
        timestamp="2026-05-12T00:00:02+00:00",
    )

    before = pending_approvals(config)
    after = pending_approvals(config)

    assert after == before
