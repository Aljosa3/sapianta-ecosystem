"""Tests for the first executable G4 governed self-development session."""

from __future__ import annotations

import json

import pytest

from aigol.runtime.g4_first_executable_governed_self_development_session import (
    ADVISORY_ONLY_CHECKPOINT_PASSED,
    BLOCKED_PENDING_GOVERNANCE,
    DEFAULT_SELF_DEVELOPMENT_REQUEST,
    G4_SELF_DEVELOPMENT_SESSION_VERSION,
    SCENARIO_ID,
    SESSION_RECORDED,
    reconstruct_g4_first_executable_self_development_session_replay,
    run_g4_first_executable_governed_self_development_session,
)
from aigol.runtime.models import FailClosedRuntimeError


CREATED_AT = "2026-06-30T00:00:00Z"


def _run(tmp_path, *, operator_response: str = "confirm") -> dict:
    return run_g4_first_executable_governed_self_development_session(
        session_id="G4-04-SESSION-001",
        operator_request=DEFAULT_SELF_DEVELOPMENT_REQUEST,
        operator_response=operator_response,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "g4_session",
    )


def test_g4_first_self_development_session_executes_without_mutation(tmp_path) -> None:
    capture = _run(tmp_path)
    summary = capture["summary_artifact"]

    assert capture["runtime_version"] == G4_SELF_DEVELOPMENT_SESSION_VERSION
    assert capture["session_status"] == SESSION_RECORDED
    assert capture["scenario_id"] == SCENARIO_ID
    assert capture["canonical_response_class"] == "CONFIRMATION"
    assert capture["governance_checkpoint_status"] == ADVISORY_ONLY_CHECKPOINT_PASSED
    assert capture["execution_intent_status"] == BLOCKED_PENDING_GOVERNANCE
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["execution_authorized"] is False
    assert capture["repository_mutated"] is False
    assert capture["deployment_performed"] is False
    assert capture["copy_paste_workflow_used"] is False
    assert summary["request_hash"].startswith("sha256:")
    assert summary["scaffold_summary_hash"].startswith("sha256:")
    assert summary["governance_fixture_hash"].startswith("sha256:")
    assert summary["replay_fixture_hash"].startswith("sha256:")


def test_g4_first_self_development_session_replay_reconstructs_complete_path(tmp_path) -> None:
    _run(tmp_path, operator_response="continue")

    replay = reconstruct_g4_first_executable_self_development_session_replay(tmp_path / "g4_session")

    assert replay["runtime_version"] == G4_SELF_DEVELOPMENT_SESSION_VERSION
    assert replay["session_status"] == SESSION_RECORDED
    assert replay["scenario_id"] == SCENARIO_ID
    assert replay["scaffold_status"] == "G4_GOVERNED_DEVELOPMENT_LOOP_SCAFFOLD_RECORDED"
    assert replay["canonical_response_class"] == "CONTINUATION"
    assert replay["governance_checkpoint_status"] == ADVISORY_ONLY_CHECKPOINT_PASSED
    assert replay["execution_intent_status"] == BLOCKED_PENDING_GOVERNANCE
    assert replay["replay_artifact_count"] == 6
    assert replay["scaffold_replay_artifact_count"] == 10
    assert "scaffold_advisory_execution_intent" in replay["replay_checkpoints"]
    assert replay["provider_invoked"] is False
    assert replay["worker_invoked"] is False
    assert replay["execution_authorized"] is False
    assert replay["repository_mutated"] is False
    assert replay["deployment_performed"] is False
    assert replay["copy_paste_workflow_used"] is False
    assert replay["replay_hash"].startswith("sha256:")


@pytest.mark.parametrize(
    ("operator_response", "expected_class"),
    [
        ("please clarify", "CLARIFICATION"),
        ("modify scope", "MODIFICATION"),
        ("reject", "REJECTION"),
    ],
)
def test_g4_first_self_development_session_maps_operator_responses(
    tmp_path,
    operator_response: str,
    expected_class: str,
) -> None:
    capture = run_g4_first_executable_governed_self_development_session(
        session_id=f"G4-04-SESSION-{expected_class}",
        operator_request=DEFAULT_SELF_DEVELOPMENT_REQUEST,
        operator_response=operator_response,
        created_at=CREATED_AT,
        replay_dir=tmp_path / expected_class.lower(),
    )

    assert capture["canonical_response_class"] == expected_class
    assert capture["execution_intent_status"] == BLOCKED_PENDING_GOVERNANCE
    assert capture["repository_mutated"] is False


def test_g4_first_self_development_session_rejects_unmapped_response(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="does not map"):
        _run(tmp_path, operator_response="sounds interesting")


def test_g4_first_self_development_session_replay_tampering_fails_closed(tmp_path) -> None:
    _run(tmp_path)
    path = tmp_path / "g4_session" / "005_self_development_session_summary_recorded.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["artifact"]["repository_mutated"] = True
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_g4_first_executable_self_development_session_replay(tmp_path / "g4_session")
