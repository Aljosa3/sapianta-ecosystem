from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sapianta_bridge.protocol.enforcement import enforce_artifact

from protocol_fixtures import valid_result, valid_task


def test_valid_task_artifact_passes() -> None:
    result = enforce_artifact(valid_task())
    assert result.allowed_to_continue is True
    assert result.to_dict()["artifact_type"] == "task"
    assert result.to_dict()["required_state"] == "VALIDATED"


def test_invalid_task_artifact_blocked() -> None:
    task = valid_task()
    del task["task_id"]
    result = enforce_artifact(task)
    assert result.allowed_to_continue is False
    assert result.required_state == "QUARANTINED"
    assert any(reason["field"] == "task_id" for reason in result.reasons)


def test_invalid_protocol_version_blocked() -> None:
    task = valid_task()
    task["protocol_version"] = "0.2"
    result = enforce_artifact(task)
    assert result.allowed_to_continue is False
    assert any(reason["field"] == "protocol_version" for reason in result.reasons)


def test_invalid_lifecycle_transition_blocked() -> None:
    task = valid_task()
    result = enforce_artifact(task, current_state="CREATED", next_state="EXECUTING")
    assert result.allowed_to_continue is False
    assert result.required_state == "QUARANTINED"
    assert any(reason["reason"] == "invalid lifecycle transition" for reason in result.reasons)


def test_hash_mismatch_quarantined() -> None:
    artifact = valid_result()
    artifact["artifact_hashes"]["result_sha256"] = "f" * 64
    result = enforce_artifact(artifact)
    assert result.allowed_to_continue is False
    assert result.required_state == "QUARANTINED"
    assert any(reason["reason"] == "hash mismatch" for reason in result.reasons)


def test_malformed_lineage_quarantined() -> None:
    artifact = valid_task()
    artifact["lineage"]["parent_task_id"] = ""
    result = enforce_artifact(artifact)
    assert result.allowed_to_continue is False
    assert result.required_state == "QUARANTINED"
    assert any(reason["field"] == "lineage.parent_task_id" for reason in result.reasons)


def test_unknown_artifact_quarantined() -> None:
    result = enforce_artifact({"protocol_version": "0.1", "unknown_id": "X"})
    assert result.allowed_to_continue is False
    assert result.artifact_type == "unknown"
    assert result.required_state == "QUARANTINED"


def test_deterministic_validation_output_stable_across_runs() -> None:
    task = valid_task()
    first = enforce_artifact(task).to_dict()
    second = enforce_artifact(task).to_dict()
    assert first == second
