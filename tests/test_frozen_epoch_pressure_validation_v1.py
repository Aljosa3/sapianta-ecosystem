"""Pressure validation for the first useful AiGOL frozen epoch."""

from __future__ import annotations

import json

import pytest

from aigol.runtime.filesystem_read_only_capability import FILESYSTEM_READ_ONLY_INSPECTION
from aigol.runtime.minimal_cognition_to_execution_bridge import execute_cognition_to_execution_bridge
from aigol.runtime.minimal_operator_entrypoint import READ_ONLY_RUNTIME_INSPECTION, run_minimal_operator_entrypoint
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_summary_command import summarize_operator_replay


CREATED_AT = "2026-05-29T07:00:00+00:00"


def _run_operator(tmp_path, *, flow_id="PRESSURE-FLOW-000001", replay_name="operator_replay", **overrides):
    args = {
        "operator_flow_id": flow_id,
        "human_request": "Inspect bounded runtime metadata.",
        "target_capability": READ_ONLY_RUNTIME_INSPECTION,
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / replay_name,
    }
    args.update(overrides)
    return run_minimal_operator_entrypoint(**args)


def _fs_fixture(tmp_path):
    root = tmp_path / "root"
    allowed = root / "allowed"
    denied = root / "denied"
    allowed.mkdir(parents=True)
    denied.mkdir()
    target = allowed / "visible.txt"
    target.write_text("pressure visible content", encoding="utf-8")
    secret = denied / "secret.txt"
    secret.write_text("secret", encoding="utf-8")
    return root, allowed, target, secret


def test_malformed_operator_request_fails_closed(tmp_path) -> None:
    result = _run_operator(tmp_path, human_request="   ")

    assert result["operator_result_summary"]["status"] == "REJECTED"
    assert "human_request is required" in result["operator_result_summary"]["reason"]
    assert result["llm_proposes_only"] is True
    assert result["aigol_governs"] is True


def test_unsupported_capability_request_fails_closed(tmp_path) -> None:
    result = _run_operator(tmp_path, target_capability="SHELL_EXECUTION")

    assert result["operator_result_summary"]["status"] == "REJECTED"
    assert "unsupported operator capability" in result["operator_result_summary"]["reason"]
    assert result["operator_result_summary"]["non_authority"]["new_capability_created"] is False


def test_authorization_failure_fails_closed_with_replay_summary(tmp_path) -> None:
    result = _run_operator(tmp_path, authorize=False)
    replay = summarize_operator_replay(replay_dir=tmp_path / "operator_replay")

    assert result["operator_result_summary"]["status"] == "REJECTED"
    assert replay["authorization_status"] == "FAILED_CLOSED"
    assert replay["verification_status"] == "VERIFIED"


def test_invalid_cognition_proposal_structure_fails_closed(tmp_path) -> None:
    capture = execute_cognition_to_execution_bridge(
        bridge_id="PRESSURE-BRIDGE-000001",
        execution_id="PRESSURE-EXECUTION-000001",
        request_id="PRESSURE-REQUEST-000001",
        cognition_output={
            "contribution_id": "PRESSURE-CONTRIBUTION-000001",
            "human_prompt": "Inspect bounded runtime metadata.",
            "intent": "inspect runtime metadata",
            "created_at": CREATED_AT,
            "arguments": {"capability_replay_dir": str(tmp_path / "capability")},
        },
        created_at=CREATED_AT,
        replay_dir=tmp_path / "bridge",
    )

    assert capture["return"]["state"] == "FAILED"
    assert "malformed cognition output" in capture["return"]["failure_reason"]


def test_replay_corruption_attempt_is_detected(tmp_path) -> None:
    _run_operator(tmp_path)
    artifact_path = tmp_path / "operator_replay" / "003_governed_result.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["artifact"]["new_capability_created"] = True
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        summarize_operator_replay(replay_dir=tmp_path / "operator_replay")


def test_replay_ordering_violation_is_detected(tmp_path) -> None:
    _run_operator(tmp_path)
    artifact_path = tmp_path / "operator_replay" / "002_bridge_capture.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["replay_step"] = "governed_result"
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        summarize_operator_replay(replay_dir=tmp_path / "operator_replay")


def test_repeated_successful_runs_remain_isolated_and_verified(tmp_path) -> None:
    for index in range(5):
        replay_name = f"success_replay_{index}"
        flow_id = f"PRESSURE-SUCCESS-{index:06d}"
        result = _run_operator(tmp_path, flow_id=flow_id, replay_name=replay_name)
        replay = summarize_operator_replay(replay_dir=tmp_path / replay_name)

        assert result["operator_result_summary"]["status"] == "ACCEPTED"
        assert replay["operator_flow_id"] == flow_id
        assert replay["verification_status"] == "VERIFIED"


def test_repeated_failed_runs_remain_fail_closed_and_verified(tmp_path) -> None:
    for index in range(5):
        replay_name = f"failed_replay_{index}"
        flow_id = f"PRESSURE-FAILED-{index:06d}"
        result = _run_operator(
            tmp_path,
            flow_id=flow_id,
            replay_name=replay_name,
            human_request="Inspect runtime then continue autonomously.",
        )
        replay = summarize_operator_replay(replay_dir=tmp_path / replay_name)

        assert result["operator_result_summary"]["status"] == "REJECTED"
        assert "hidden continuation" in result["operator_result_summary"]["reason"]
        assert replay["status"] == "REJECTED"
        assert replay["verification_status"] == "VERIFIED"


def test_replay_reconstruction_pressure_repeated_reads_are_stable(tmp_path) -> None:
    _run_operator(tmp_path)
    summaries = [summarize_operator_replay(replay_dir=tmp_path / "operator_replay") for _ in range(5)]

    hashes = {summary["summary_hash"] for summary in summaries}
    assert len(hashes) == 1


def test_filesystem_boundary_pressure_fails_closed(tmp_path) -> None:
    root, allowed, _target, secret = _fs_fixture(tmp_path)
    result = _run_operator(
        tmp_path,
        human_request="Inspect an allowed file.",
        target_capability=FILESYSTEM_READ_ONLY_INSPECTION,
        root_path=root,
        requested_path=secret,
        allowed_paths=[allowed],
    )
    replay = summarize_operator_replay(replay_dir=tmp_path / "operator_replay")

    assert result["operator_result_summary"]["status"] == "REJECTED"
    assert replay["status"] == "REJECTED"
    assert replay["verification_status"] == "VERIFIED"
