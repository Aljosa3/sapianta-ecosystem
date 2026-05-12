from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.approval.approval_queue import enqueue_advisory_proposal
from sapianta_bridge.approval.approval_reader import (
    approval_history,
    approvals_for_reflection,
    approvals_for_task,
    pending_approvals,
)
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


def _snapshot(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): path.read_text(encoding="utf-8")
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_approval_reader_immutable(tmp_path: Path) -> None:
    config = _config(tmp_path)
    reflection = _reflection(config)
    enqueue_advisory_proposal(
        reflection,
        config=config,
        timestamp="2026-05-12T00:00:02+00:00",
    )
    before = _snapshot(config.runtime_root / "approval")

    assert len(pending_approvals(config)) == 1
    assert len(approval_history(config)) == 1
    assert len(approvals_for_task("TASK-001", config)) == 1
    assert len(approvals_for_reflection(reflection["reflection_id"], config)) == 1
    after = _snapshot(config.runtime_root / "approval")

    assert after == before
