"""Tests for REPLAY_SUMMARY_COMMAND_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.filesystem_read_only_capability import FILESYSTEM_READ_ONLY_INSPECTION
from aigol.runtime.minimal_operator_entrypoint import READ_ONLY_RUNTIME_INSPECTION, run_minimal_operator_entrypoint
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_summary_command import render_replay_summary, summarize_operator_replay
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-29T06:00:00+00:00"


def _run_runtime(tmp_path, **overrides):
    args = {
        "operator_flow_id": "REPLAY-SUMMARY-FLOW-000001",
        "human_request": "Inspect bounded runtime metadata.",
        "target_capability": READ_ONLY_RUNTIME_INSPECTION,
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "operator_replay",
    }
    args.update(overrides)
    return run_minimal_operator_entrypoint(**args)


def _fs_fixture(tmp_path):
    root = tmp_path / "root"
    allowed = root / "allowed"
    allowed.mkdir(parents=True)
    target = allowed / "visible.txt"
    target.write_text("summary visible content", encoding="utf-8")
    return root, allowed, target


def test_replay_summary_view_contains_required_fields(tmp_path) -> None:
    _run_runtime(tmp_path)
    summary = summarize_operator_replay(replay_dir=tmp_path / "operator_replay", replay_id="REPLAY-000001")

    assert summary["replay_id"] == "REPLAY-000001"
    assert summary["status"] == "ACCEPTED"
    assert summary["capability"] == READ_ONLY_RUNTIME_INSPECTION
    assert summary["authorization_status"] == "AUTHORIZED"
    assert summary["verification_status"] == "VERIFIED"
    assert "human prompt completed" in summary["result_summary"]
    assert summary["timestamp_ordering"]["created_at"] == CREATED_AT
    assert summary["read_only_view"] is True


def test_replay_summary_renders_operator_view(tmp_path) -> None:
    _run_runtime(tmp_path)
    summary = summarize_operator_replay(replay_dir=tmp_path / "operator_replay")
    rendered = render_replay_summary(summary)

    assert "Replay ID: operator_replay" in rendered
    assert "Status: ACCEPTED" in rendered
    assert "Capability: READ_ONLY_RUNTIME_INSPECTION" in rendered
    assert "Authorization Status: AUTHORIZED" in rendered
    assert "Verification Status: VERIFIED" in rendered


def test_replay_summary_handles_rejected_flow(tmp_path) -> None:
    _run_runtime(tmp_path, authorize=False)
    summary = summarize_operator_replay(replay_dir=tmp_path / "operator_replay")

    assert summary["status"] == "REJECTED"
    assert summary["authorization_status"] == "FAILED_CLOSED"
    assert summary["verification_status"] == "VERIFIED"
    assert "failed closed" in summary["result_summary"]


def test_replay_summary_handles_filesystem_capability(tmp_path) -> None:
    root, allowed, target = _fs_fixture(tmp_path)
    _run_runtime(
        tmp_path,
        target_capability=FILESYSTEM_READ_ONLY_INSPECTION,
        human_request="Inspect an allowed file.",
        root_path=root,
        requested_path=target,
        allowed_paths=[allowed],
    )
    summary = summarize_operator_replay(replay_dir=tmp_path / "operator_replay")

    assert summary["capability"] == FILESYSTEM_READ_ONLY_INSPECTION
    assert summary["status"] == "ACCEPTED"


def test_replay_summary_detects_replay_corruption(tmp_path) -> None:
    _run_runtime(tmp_path)
    artifact_path = tmp_path / "operator_replay" / "003_governed_result.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["artifact"]["new_capability_created"] = True
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        summarize_operator_replay(replay_dir=tmp_path / "operator_replay")


def test_replay_summary_hash_is_deterministic(tmp_path) -> None:
    _run_runtime(tmp_path)
    summary = summarize_operator_replay(replay_dir=tmp_path / "operator_replay")
    without_hash = dict(summary)
    summary_hash = without_hash.pop("summary_hash")

    assert summary_hash == replay_hash(without_hash)


def test_render_rejects_tampered_summary(tmp_path) -> None:
    _run_runtime(tmp_path)
    summary = summarize_operator_replay(replay_dir=tmp_path / "operator_replay")
    summary["status"] = "REJECTED"

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        render_replay_summary(summary)


def test_no_new_runtime_surface_imports() -> None:
    import aigol.runtime.replay_summary_command as command

    source = inspect.getsource(command)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
