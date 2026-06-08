"""Tests for AIGOL_POST_EXECUTION_REPLAY_REVIEW_RUNTIME_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json

import pytest

from aigol.cli.aigol_cli import run_interactive_conversation
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.post_execution_replay_review_runtime import (
    INTEGRITY_VERIFIED,
    POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1,
    REVIEW_COMPLETED,
    reconstruct_post_execution_replay_review,
    review_validated_worker_result,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from test_worker_result_validation_runtime_v1 import (
    CREATED_AT,
    _args,
    _execution_bound_result_capture,
    _input_sequence,
    _validate,
)


def _review(tmp_path, *, prompt: str, suffix: str, validation: dict | None = None) -> dict:
    if validation is None:
        validation = _validate(tmp_path, prompt=prompt, suffix=suffix)
    return review_validated_worker_result(
        post_execution_replay_review_id=f"POST-EXECUTION-REPLAY-REVIEW-{suffix}",
        worker_result_validation_artifact=validation["worker_result_validation_artifact"],
        worker_result_validation_replay_reference=validation["worker_result_validation_replay_reference"],
        reviewed_by="AIGOL_GOVERNANCE",
        reviewed_at=CREATED_AT,
        replay_dir=tmp_path / f"post_execution_replay_review_{suffix}",
    )


def _rewrite_validation_artifact(tmp_path, *, suffix: str, changes: dict) -> dict:
    path = tmp_path / f"result_validation_{suffix}" / "002_validation_artifact_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    artifact = wrapper["artifact"]
    artifact.update(changes)
    artifact.pop("artifact_hash", None)
    artifact["artifact_hash"] = replay_hash(artifact)
    wrapper.pop("replay_hash", None)
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    result_path = tmp_path / f"result_validation_{suffix}" / "003_validation_result_recorded.json"
    result_wrapper = json.loads(result_path.read_text(encoding="utf-8"))
    result_wrapper["artifact"]["worker_result_validation_hash"] = artifact["artifact_hash"]
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
def test_result_validated_becomes_review_completed(tmp_path, prompt: str, suffix: str) -> None:
    result = _review(tmp_path, prompt=prompt, suffix=suffix)
    artifact = result["post_execution_replay_review_artifact"]
    reconstructed = reconstruct_post_execution_replay_review(tmp_path / f"post_execution_replay_review_{suffix}")

    assert result["review_status"] == REVIEW_COMPLETED
    assert artifact["artifact_type"] == POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1
    assert artifact["review_status"] == REVIEW_COMPLETED
    assert artifact["result_validated"] is True
    assert artifact["post_execution_replay_reviewed"] is True
    assert artifact["terminated"] is False
    assert artifact["replay_integrity_assessment"] == INTEGRITY_VERIFIED
    assert artifact["authority_integrity_assessment"] == INTEGRITY_VERIFIED
    assert artifact["execution_integrity_assessment"] == INTEGRITY_VERIFIED
    assert artifact["validation_integrity_assessment"] == INTEGRITY_VERIFIED
    assert reconstructed["review_status"] == REVIEW_COMPLETED


def test_post_execution_replay_review_persists_replay_events(tmp_path) -> None:
    _review(tmp_path, prompt="Create a filesystem worker.", suffix="events")
    replay_dir = tmp_path / "post_execution_replay_review_events"

    assert (replay_dir / "000_review_evidence_recorded.json").exists()
    assert (replay_dir / "001_review_classification_recorded.json").exists()
    assert (replay_dir / "002_review_artifact_recorded.json").exists()
    assert (replay_dir / "003_review_result_recorded.json").exists()


def test_post_execution_replay_review_accepts_execution_bound_result_validation(tmp_path) -> None:
    capture = _execution_bound_result_capture(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="execution-bound",
    )
    validation = _validate(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="execution-bound",
        capture=capture,
    )

    result = _review(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="execution-bound",
        validation=validation,
    )
    artifact = result["post_execution_replay_review_artifact"]
    reconstructed = reconstruct_post_execution_replay_review(
        tmp_path / "post_execution_replay_review_execution-bound"
    )

    assert result["review_status"] == REVIEW_COMPLETED
    assert artifact["execution_reference"] == "EXECUTION-execution-bound"
    assert artifact["execution_hash"] == capture["_execution_capture"]["execution_artifact"]["artifact_hash"]
    assert artifact["execution_status"] == "EXECUTING"
    assert artifact["execution_started"] is True
    assert artifact["post_execution_replay_reviewed"] is True
    assert artifact["terminated"] is False
    assert result["review_evidence_artifact"]["lineage_checks"]["execution_binding_lineage"] is True
    assert reconstructed["execution_reference"] == artifact["execution_reference"]
    assert reconstructed["execution_started"] is True


def test_post_execution_replay_review_fails_closed_on_execution_binding_drift(tmp_path) -> None:
    capture = _execution_bound_result_capture(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="execution-binding-drift",
    )
    validation = _validate(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="execution-binding-drift",
        capture=capture,
    )
    validation["worker_result_validation_artifact"] = _rewrite_validation_artifact(
        tmp_path,
        suffix="execution-binding-drift",
        changes={"execution_hash": "sha256:other-execution"},
    )

    result = _review(
        tmp_path,
        prompt="Create a filesystem worker.",
        suffix="execution-binding-drift",
        validation=validation,
    )

    assert result["review_status"] == "FAILED_CLOSED"
    assert result["post_execution_replay_review_artifact"] is None
    assert "lineage continuity invalid" in result["failure_reason"]


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"worker_id": "OTHER-WORKER"}, "worker"),
        ({"execution_packet_reference": "OTHER-PACKET"}, "packet"),
        ({"chain_id": "OTHER-CHAIN"}, "chain"),
        ({"governance_mutated": True}, "authority"),
        ({"validation_status": "INVALID"}, "validation"),
    ],
)
def test_post_execution_replay_review_fails_closed_on_chain_drift(tmp_path, changes: dict, reason: str) -> None:
    suffix = f"drift-{reason}"
    validation = _validate(tmp_path, prompt="Create a filesystem worker.", suffix=suffix)
    validation["worker_result_validation_artifact"] = _rewrite_validation_artifact(
        tmp_path,
        suffix=suffix,
        changes=changes,
    )

    result = _review(tmp_path, prompt="Create a filesystem worker.", suffix=suffix, validation=validation)

    assert result["review_status"] == "FAILED_CLOSED"
    assert result["post_execution_replay_review_artifact"] is None


def test_post_execution_replay_review_fails_closed_on_replay_corruption(tmp_path) -> None:
    validation = _validate(tmp_path, prompt="Create a filesystem worker.", suffix="corruption")
    path = tmp_path / "result_validation_corruption" / "002_validation_artifact_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_id"] = "CORRUPTED-WORKER"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    result = _review(tmp_path, prompt="Create a filesystem worker.", suffix="corruption", validation=validation)

    assert result["review_status"] == "FAILED_CLOSED"
    assert "hash mismatch" in result["failure_reason"]


def test_post_execution_replay_review_reconstruction_detects_hash_mismatch(tmp_path) -> None:
    _review(tmp_path, prompt="Create a filesystem worker.", suffix="reconstruct")
    path = tmp_path / "post_execution_replay_review_reconstruct" / "002_review_artifact_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_id"] = "CORRUPTED-WORKER"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_post_execution_replay_review(tmp_path / "post_execution_replay_review_reconstruct")


def test_post_execution_replay_review_runtime_does_not_retry_mutate_or_terminate() -> None:
    source = inspect.getsource(review_validated_worker_result)

    assert "TERMINATED" not in source
    assert "retry_execution" not in source
    assert "create_improvement" not in source
    assert "mutate_governance" not in source


def test_interactive_cli_reaches_post_execution_replay_review(tmp_path) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path, session_id="SESSION-CLI-POST-EXECUTION-REPLAY-REVIEW-000001"),
        input_func=_input_sequence(["Create a filesystem worker.", "exit"]),
        output_func=output.append,
    )

    assert result["worker_result_validated"] is True
    assert result["post_execution_replay_reviewed"] is True
    assert any("Worker Result Validation" in chunk for chunk in output)
    assert any("Validation Status: RESULT_VALIDATED" in chunk for chunk in output)
    assert any("Post-Execution Replay Review" in chunk for chunk in output)
    assert any("Replay Review Status: REVIEW_COMPLETED" in chunk for chunk in output)
    assert any("Termination is a separate downstream stage." in chunk for chunk in output)
