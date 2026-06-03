"""Tests for AIGOL_RUNTIME_PROGRESS_VISIBILITY_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.cli.aigol_cli import run_command
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.runtime_progress_visibility import (
    COMPLETED,
    DEFAULT_STAGE_MODEL,
    FAILED_CLOSED,
    PENDING,
    PROVIDER_PROPOSAL_PRODUCTION,
    RESOURCE_SELECTION,
    RUNNING,
    WAITING_FOR_PROVIDER,
    format_runtime_progress,
    format_runtime_status,
    progress_bar,
    record_runtime_progress_snapshot,
    reconstruct_runtime_progress_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


RUNTIME_ID = "RUNTIME-PROGRESS-000001"
STARTED_AT = "2026-06-03T12:00:00+00:00"


def _history() -> dict:
    return {
        "history_source": "RUNTIME_DURATION_HISTORY_V1",
        "runtime_duration_seconds": 90,
        "stage_durations": {
            stage: {
                "average_duration_seconds": 2,
                "last_duration_seconds": 2,
                "sample_count": 4,
            }
            for stage in DEFAULT_STAGE_MODEL
        },
    }


def _record(tmp_path, **overrides):
    data = {
        "runtime_id": RUNTIME_ID,
        "runtime_status": RUNNING,
        "current_stage": PROVIDER_PROPOSAL_PRODUCTION,
        "completed_stages": list(DEFAULT_STAGE_MODEL[:5]),
        "started_at": STARTED_AT,
        "snapshot_at": "2026-06-03T12:00:14+00:00",
        "current_activity": "Validating provider request packet",
        "duration_history": _history(),
        "replay_dir": tmp_path / RUNTIME_ID,
    }
    data.update(overrides)
    return record_runtime_progress_snapshot(**data)


def test_records_runtime_progress_snapshot_and_formats_operator_visibility(tmp_path) -> None:
    capture = _record(tmp_path)
    artifact = capture["runtime_progress_artifact"]
    reconstructed = reconstruct_runtime_progress_replay(tmp_path / RUNTIME_ID)
    rendered = format_runtime_progress(capture)

    assert artifact["runtime_status"] == RUNNING
    assert artifact["current_stage"] == PROVIDER_PROPOSAL_PRODUCTION
    assert artifact["progress_percent"] == 50
    assert artifact["elapsed_display"] == "00:00:14"
    assert artifact["eta"]["eta_status"] == "estimated"
    assert artifact["eta"]["estimated_remaining_display"] == "00:00:10"
    assert artifact["provider_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["authorization_created"] is False
    assert artifact["dispatch_requested"] is False
    assert artifact["execution_requested"] is False
    assert reconstructed["runtime_status"] == RUNNING
    assert reconstructed["stage_ordering_verified"] is True
    assert "[RUNNING]" in rendered
    assert "PROVIDER_PROPOSAL_PRODUCTION" in rendered
    assert "█████░░░░░ 50%" in rendered
    assert "Validating provider request packet" in rendered


def test_reconstructs_status_stage_and_timestamp_continuity(tmp_path) -> None:
    replay_dir = tmp_path / RUNTIME_ID
    _record(
        tmp_path,
        runtime_status=PENDING,
        current_stage="CONVERSATION",
        completed_stages=[],
        snapshot_at="2026-06-03T12:00:00+00:00",
        replay_dir=replay_dir,
    )
    _record(
        tmp_path,
        runtime_status=RUNNING,
        current_stage=RESOURCE_SELECTION,
        completed_stages=list(DEFAULT_STAGE_MODEL[:3]),
        snapshot_at="2026-06-03T12:00:08+00:00",
        replay_dir=replay_dir,
    )
    _record(
        tmp_path,
        runtime_status=WAITING_FOR_PROVIDER,
        current_stage=PROVIDER_PROPOSAL_PRODUCTION,
        completed_stages=list(DEFAULT_STAGE_MODEL[:5]),
        snapshot_at="2026-06-03T12:00:14+00:00",
        replay_dir=replay_dir,
    )

    reconstructed = reconstruct_runtime_progress_replay(replay_dir)

    assert reconstructed["runtime_status"] == WAITING_FOR_PROVIDER
    assert reconstructed["current_stage"] == PROVIDER_PROPOSAL_PRODUCTION
    assert reconstructed["replay_artifact_count"] == 3
    assert reconstructed["status_continuity_verified"] is True


def test_reconstruction_fails_closed_on_status_regression_after_terminal(tmp_path) -> None:
    replay_dir = tmp_path / RUNTIME_ID
    _record(
        tmp_path,
        runtime_status=COMPLETED,
        current_stage="HANDOFF",
        completed_stages=list(DEFAULT_STAGE_MODEL),
        snapshot_at="2026-06-03T12:00:20+00:00",
        replay_dir=replay_dir,
    )
    _record(
        tmp_path,
        runtime_status=RUNNING,
        current_stage="REPLAY_IMPROVEMENT",
        completed_stages=list(DEFAULT_STAGE_MODEL[:9]),
        snapshot_at="2026-06-03T12:00:21+00:00",
        replay_dir=replay_dir,
    )

    with pytest.raises(FailClosedRuntimeError, match="status continuity mismatch"):
        reconstruct_runtime_progress_replay(replay_dir)


def test_reconstruction_detects_timestamp_corruption(tmp_path) -> None:
    _record(tmp_path)
    _record(
        tmp_path,
        runtime_status=WAITING_FOR_PROVIDER,
        current_stage=PROVIDER_PROPOSAL_PRODUCTION,
        completed_stages=list(DEFAULT_STAGE_MODEL[:5]),
        snapshot_at="2026-06-03T12:00:15+00:00",
    )
    path = tmp_path / RUNTIME_ID / "001_runtime_progress_visibility_snapshot.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["snapshot_at"] = "2026-06-03T11:59:59+00:00"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="timestamp ordering mismatch"):
        reconstruct_runtime_progress_replay(tmp_path / RUNTIME_ID)


def test_unknown_eta_when_duration_history_is_incomplete(tmp_path) -> None:
    capture = _record(tmp_path, duration_history={"stage_durations": {}})

    assert capture["runtime_progress_artifact"]["eta"]["eta_status"] == "unknown"
    assert capture["runtime_progress_artifact"]["eta"]["estimated_remaining_display"] == "unknown"


def test_recording_invalid_stage_fails_closed_without_authority(tmp_path) -> None:
    capture = _record(tmp_path, current_stage="UNKNOWN_STAGE")

    assert capture["runtime_status"] == FAILED_CLOSED
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["authorization_created"] is False
    assert "current stage is not in stage model" in capture["failure_reason"]


def test_cli_runtime_progress_commands_are_read_only(tmp_path) -> None:
    _record(tmp_path)

    class Args:
        command = "runtime-progress"
        runtime_id = RUNTIME_ID
        replay_root = str(tmp_path)

    result = run_command(Args())

    assert result["runtime_status"] == RUNNING
    assert result["command"] == "aigol runtime-progress"
    assert format_runtime_status(result).startswith("[RUNNING]")


def test_progress_bar_is_deterministic() -> None:
    assert progress_bar(0) == "░░░░░░░░░░"
    assert progress_bar(70) == "███████░░░"
    assert progress_bar(100) == "██████████"


def test_runtime_visibility_has_no_provider_worker_or_execution_invocations() -> None:
    import aigol.runtime.runtime_progress_visibility as runtime

    source = inspect.getsource(runtime)

    assert "run_provider_attachment(" not in source
    assert "produce_provider_development_proposal(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
