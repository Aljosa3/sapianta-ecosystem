from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.approval import approval_cli
from sapianta_bridge.approval.approval_queue import enqueue_advisory_proposal
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


def _args(config: TransportConfig, *command: str) -> list[str]:
    return [
        "--runtime-root",
        str(config.runtime_root),
        "--quarantine-root",
        str(config.quarantine_root),
        *command,
    ]


def _approval(config: TransportConfig) -> dict:
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
    reflection = generate_reflection(
        "TASK-001",
        config,
        timestamp="2026-05-12T00:00:01+00:00",
    )["reflection"]
    return enqueue_advisory_proposal(
        reflection,
        config=config,
        timestamp="2026-05-12T00:00:02+00:00",
    )["approval"]


def test_cli_pending_command_works(tmp_path: Path, capsys) -> None:
    config = _config(tmp_path)
    _approval(config)

    exit_code = approval_cli.main(_args(config, "pending"))
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert len(output) == 1
    assert output[0]["decision"] == "PENDING"


def test_cli_approve_command_works(tmp_path: Path, capsys) -> None:
    config = _config(tmp_path)
    approval = _approval(config)

    exit_code = approval_cli.main(
        _args(
            config,
            "approve",
            "--approval-id",
            approval["approval_id"],
            "--timestamp",
            "2026-05-12T00:00:03+00:00",
        )
    )
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["decision"]["decision"] == "APPROVED"
    assert output["decision"]["execution_authority_granted"] is False


def test_cli_reject_command_works(tmp_path: Path, capsys) -> None:
    config = _config(tmp_path)
    approval = _approval(config)

    exit_code = approval_cli.main(
        _args(
            config,
            "reject",
            "--approval-id",
            approval["approval_id"],
            "--timestamp",
            "2026-05-12T00:00:03+00:00",
        )
    )
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["decision"]["decision"] == "REJECTED"
    assert output["decision"]["execution_authority_granted"] is False
