"""Tests for AIGOL_GOVERNED_TERMINATION_RUNTIME_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json

import pytest

from aigol.cli.aigol_cli import run_interactive_conversation
from aigol.runtime.governed_termination_runtime import (
    GOVERNED_TERMINATION_ARTIFACT_V1,
    SEPARATE_GOVERNED_REQUEST_REQUIRED,
    TERMINAL_OPERATION_STATE,
    TERMINATED,
    reconstruct_governed_termination_replay,
    terminate_reviewed_operation,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from test_post_execution_replay_review_runtime_v1 import _review
from test_worker_result_validation_runtime_v1 import CREATED_AT, _args, _input_sequence


def _terminate(tmp_path, *, prompt: str, suffix: str, review: dict | None = None) -> dict:
    if review is None:
        review = _review(tmp_path, prompt=prompt, suffix=suffix)
    return terminate_reviewed_operation(
        governed_termination_id=f"GOVERNED-TERMINATION-{suffix}",
        post_execution_replay_review_artifact=review["post_execution_replay_review_artifact"],
        post_execution_replay_review_replay_reference=review["post_execution_replay_review_replay_reference"],
        terminated_by="AIGOL_GOVERNANCE",
        terminated_at=CREATED_AT,
        replay_dir=tmp_path / f"governed_termination_{suffix}",
    )


def _rewrite_review_artifact(tmp_path, *, suffix: str, changes: dict) -> dict:
    path = tmp_path / f"post_execution_replay_review_{suffix}" / "002_review_artifact_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    artifact = wrapper["artifact"]
    artifact.update(changes)
    artifact.pop("artifact_hash", None)
    artifact["artifact_hash"] = replay_hash(artifact)
    wrapper.pop("replay_hash", None)
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    result_path = tmp_path / f"post_execution_replay_review_{suffix}" / "003_review_result_recorded.json"
    result_wrapper = json.loads(result_path.read_text(encoding="utf-8"))
    result_wrapper["artifact"]["post_execution_replay_review_hash"] = artifact["artifact_hash"]
    result_wrapper["artifact"].pop("artifact_hash", None)
    result_wrapper["artifact"]["artifact_hash"] = replay_hash(result_wrapper["artifact"])
    result_wrapper.pop("replay_hash", None)
    result_wrapper["replay_hash"] = replay_hash(result_wrapper)
    result_path.write_text(canonical_serialize(result_wrapper) + "\n", encoding="utf-8")
    return artifact


@pytest.mark.parametrize(
    ("prompt", "suffix"),
    [
        ("Create a filesystem worker.", "filesystem"),
        ("Create a monitoring worker.", "monitoring"),
        ("Improve trading strategy.", "trading"),
    ],
)
def test_review_completed_becomes_terminated(tmp_path, prompt: str, suffix: str) -> None:
    result = _terminate(tmp_path, prompt=prompt, suffix=suffix)
    artifact = result["governed_termination_artifact"]
    reconstructed = reconstruct_governed_termination_replay(tmp_path / f"governed_termination_{suffix}")

    assert result["termination_status"] == TERMINATED
    assert artifact["artifact_type"] == GOVERNED_TERMINATION_ARTIFACT_V1
    assert artifact["termination_status"] == TERMINATED
    assert artifact["terminal_operation_state"] == TERMINAL_OPERATION_STATE
    assert artifact["post_execution_replay_reviewed"] is True
    assert artifact["terminated"] is True
    assert artifact["governance_mutated"] is False
    assert artifact["replay_mutated"] is False
    assert artifact["future_improvement_intent_handoff_status"] == SEPARATE_GOVERNED_REQUEST_REQUIRED
    assert artifact["improvement_intent_created"] is False
    assert artifact["improvement_intent_handoff_executed"] is False
    assert reconstructed["termination_status"] == TERMINATED


def test_governed_termination_persists_replay_events(tmp_path) -> None:
    _terminate(tmp_path, prompt="Create a filesystem worker.", suffix="events")
    replay_dir = tmp_path / "governed_termination_events"

    assert (replay_dir / "000_termination_evidence_recorded.json").exists()
    assert (replay_dir / "001_termination_classification_recorded.json").exists()
    assert (replay_dir / "002_termination_artifact_recorded.json").exists()
    assert (replay_dir / "003_termination_result_recorded.json").exists()


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"review_status": "INVALID"}, "review"),
        ({"replay_integrity_assessment": "INVALID"}, "integrity"),
        ({"worker_id": "OTHER-WORKER"}, "worker"),
        ({"chain_id": "OTHER-CHAIN"}, "chain"),
        ({"governance_mutated": True}, "authority"),
        ({"terminated": True}, "already-terminated"),
    ],
)
def test_governed_termination_fails_closed_on_invalid_review(tmp_path, changes: dict, reason: str) -> None:
    suffix = f"drift-{reason}"
    review = _review(tmp_path, prompt="Create a filesystem worker.", suffix=suffix)
    review["post_execution_replay_review_artifact"] = _rewrite_review_artifact(
        tmp_path,
        suffix=suffix,
        changes=changes,
    )

    result = _terminate(tmp_path, prompt="Create a filesystem worker.", suffix=suffix, review=review)

    assert result["termination_status"] == "FAILED_CLOSED"
    assert result["governed_termination_artifact"] is None


def test_governed_termination_fails_closed_on_replay_corruption(tmp_path) -> None:
    review = _review(tmp_path, prompt="Create a filesystem worker.", suffix="corruption")
    path = tmp_path / "post_execution_replay_review_corruption" / "002_review_artifact_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_id"] = "CORRUPTED-WORKER"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    result = _terminate(tmp_path, prompt="Create a filesystem worker.", suffix="corruption", review=review)

    assert result["termination_status"] == "FAILED_CLOSED"
    assert "hash mismatch" in result["failure_reason"]


def test_governed_termination_is_append_only(tmp_path) -> None:
    review = _review(tmp_path, prompt="Create a filesystem worker.", suffix="append-only")
    first = _terminate(tmp_path, prompt="Create a filesystem worker.", suffix="append-only", review=review)
    second = _terminate(tmp_path, prompt="Create a filesystem worker.", suffix="append-only", review=review)

    assert first["termination_status"] == TERMINATED
    assert second["termination_status"] == "FAILED_CLOSED"
    assert "append-only runtime artifact already exists" in second["failure_reason"]


def test_governed_termination_reconstruction_detects_hash_mismatch(tmp_path) -> None:
    _terminate(tmp_path, prompt="Create a filesystem worker.", suffix="reconstruct")
    path = tmp_path / "governed_termination_reconstruct" / "002_termination_artifact_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_id"] = "CORRUPTED-WORKER"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_governed_termination_replay(tmp_path / "governed_termination_reconstruct")


def test_governed_termination_runtime_does_not_create_new_work_or_mutate() -> None:
    source = inspect.getsource(terminate_reviewed_operation)

    assert "create_improvement" not in source
    assert "authorize" not in source
    assert "dispatch" not in source
    assert "retry_execution" not in source
    assert "mutate_governance" not in source


def test_interactive_cli_reaches_terminated(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-CLI-GOVERNED-TERMINATION-000001"),
        input_func=_input_sequence(["Create a filesystem worker.", "exit"]),
        output_func=output.append,
    )

    assert result["post_execution_replay_reviewed"] is True
    assert result["terminated"] is True
    assert any("Post-Execution Replay Review" in chunk for chunk in output)
    assert any("Replay Review Status: REVIEW_COMPLETED" in chunk for chunk in output)
    assert any("Governed Termination" in chunk for chunk in output)
    assert any("Termination Status: TERMINATED" in chunk for chunk in output)
    assert any("Operation lifecycle closed." in chunk for chunk in output)
