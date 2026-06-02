"""Tests for REPLAY_INSPECTOR_WORKER_V1."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_inspector_worker import (
    CONTINUOUS,
    FAILED_CLOSED,
    INSPECTION_COMPLETED,
    REPLAY_INSPECTION_RECORDED,
    REPLAY_INSPECTION_REPORT_V1,
    REPLAY_INSPECTION_RETURNED,
    REPLAY_INSPECTOR_WORKER_VERSION,
    inspect_replay_worker,
    reconstruct_replay_inspector_worker_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash, write_json_immutable


CREATED_AT = "2026-06-02T09:00:00+00:00"
CANONICAL_CHAIN_ID = "CHAIN-20260602-REPLAY-INSPECTOR-000001"


def _artifact(artifact_type: str, artifact_id: str, **overrides) -> dict:
    artifact = {
        "artifact_type": artifact_type,
        "artifact_id": artifact_id,
        "canonical_chain_id": CANONICAL_CHAIN_ID,
        "provider_authority": False,
        "governance_authority": False,
        "worker_authority": False,
        "mutation_performed": False,
    }
    artifact.update(overrides)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _write_replay(path: Path, *artifacts: dict) -> None:
    for index, artifact in enumerate(artifacts):
        wrapper = {
            "replay_index": index,
            "replay_step": f"step_{index}",
            "artifact": artifact,
            "event_type": f"EVENT_{index}",
        }
        wrapper["replay_hash"] = replay_hash(wrapper)
        write_json_immutable(path / f"{index:03d}_step_{index}.json", wrapper)


def _replay_refs(tmp_path) -> list[Path]:
    proposal_dir = tmp_path / "proposal_replay"
    completion_dir = tmp_path / "completion_replay"
    _write_replay(
        proposal_dir,
        _artifact("PROPOSAL_RUNTIME_ARTIFACT_V1", "PROPOSAL-000001"),
        _artifact("PROPOSAL_RUNTIME_RETURNED_V1", "PROPOSAL-RETURNED-000001"),
    )
    _write_replay(
        completion_dir,
        _artifact("COMPLETION_ARTIFACT_V1", "COMPLETION-000001"),
    )
    return [proposal_dir, completion_dir]


def _inspect(tmp_path, **overrides) -> dict:
    replay_references = overrides.pop("replay_references", None)
    if replay_references is None:
        replay_references = _replay_refs(tmp_path)
    args = {
        "inspection_id": "REPLAY-INSPECTION-000001",
        "worker_id": "REPLAY-INSPECTOR-WORKER-000001",
        "canonical_chain_id": CANONICAL_CHAIN_ID,
        "replay_references": replay_references,
        "inspection_scope": "CHAIN_SUMMARY",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "inspection_replay",
    }
    args.update(overrides)
    return inspect_replay_worker(**args)


def test_replay_inspector_worker_creates_replay_visible_report(tmp_path) -> None:
    capture = _inspect(tmp_path)
    report = capture["replay_inspection_report"]
    returned = capture["replay_inspection_replay"]
    reconstructed = reconstruct_replay_inspector_worker_replay(tmp_path / "inspection_replay")

    assert report["artifact_type"] == REPLAY_INSPECTION_REPORT_V1
    assert report["worker_type"] == REPLAY_INSPECTOR_WORKER_VERSION
    assert report["inspection_status"] == INSPECTION_COMPLETED
    assert report["canonical_chain_id"] == CANONICAL_CHAIN_ID
    assert report["artifact_count"] == 3
    assert report["chain_continuity_status"] == CONTINUOUS
    assert report["provider_authority"] is False
    assert report["governance_authority"] is False
    assert report["worker_authority"] is False
    assert report["mutation_performed"] is False
    assert returned["event_type"] == REPLAY_INSPECTION_RETURNED
    assert reconstructed["inspection_status"] == INSPECTION_COMPLETED
    assert reconstructed["artifact_count"] == 3


def test_replay_inspector_worker_persists_replay_events(tmp_path) -> None:
    _inspect(tmp_path)

    recorded = tmp_path / "inspection_replay" / "000_replay_inspection_recorded.json"
    returned = tmp_path / "inspection_replay" / "001_replay_inspection_returned.json"
    assert recorded.exists()
    assert returned.exists()
    assert json.loads(recorded.read_text(encoding="utf-8"))["event_type"] == REPLAY_INSPECTION_RECORDED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == REPLAY_INSPECTION_RETURNED


def test_replay_inspector_worker_supports_file_references(tmp_path) -> None:
    refs = _replay_refs(tmp_path)
    file_ref = refs[0] / "000_step_0.json"

    capture = _inspect(
        tmp_path,
        replay_references=[file_ref],
        replay_dir=tmp_path / "file_reference_inspection",
    )

    assert capture["replay_inspection_report"]["inspection_status"] == INSPECTION_COMPLETED
    assert capture["replay_inspection_report"]["artifact_count"] == 1


def test_replay_inspector_worker_rejects_output_inside_inspected_replay(tmp_path) -> None:
    refs = _replay_refs(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="output path would modify inspected replay"):
        _inspect(
            tmp_path,
            replay_references=refs,
            replay_dir=refs[0] / "worker_output",
        )


def test_replay_inspector_worker_does_not_modify_inspected_replay(tmp_path) -> None:
    refs = _replay_refs(tmp_path)
    before = {
        path: path.read_text(encoding="utf-8")
        for ref in refs
        for path in sorted(ref.glob("*.json"))
    }

    _inspect(tmp_path, replay_references=refs)

    after = {path: path.read_text(encoding="utf-8") for path in before}
    assert after == before


def test_missing_replay_reference_fails_closed_without_report_write(tmp_path) -> None:
    missing = tmp_path / "missing"

    with pytest.raises(FailClosedRuntimeError, match="missing replay reference"):
        _inspect(
            tmp_path,
            replay_references=[missing],
            replay_dir=tmp_path / "missing_reference_inspection",
        )
    assert not (tmp_path / "missing_reference_inspection").exists()


def test_corrupt_replay_fails_closed_with_replay_visible_report(tmp_path) -> None:
    refs = _replay_refs(tmp_path)
    corrupt_path = refs[0] / "000_step_0.json"
    wrapper = json.loads(corrupt_path.read_text(encoding="utf-8"))
    wrapper["artifact"]["artifact_id"] = "TAMPERED"
    corrupt_path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    capture = _inspect(tmp_path, replay_references=refs)
    reconstructed = reconstruct_replay_inspector_worker_replay(tmp_path / "inspection_replay")

    assert capture["replay_inspection_report"]["inspection_status"] == FAILED_CLOSED
    assert "hash mismatch" in capture["replay_inspection_report"]["failure_reason"]
    assert reconstructed["inspection_status"] == FAILED_CLOSED


def test_chain_mismatch_fails_closed_with_replay_visible_report(tmp_path) -> None:
    refs = _replay_refs(tmp_path)
    path = refs[1] / "000_step_0.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["canonical_chain_id"] = "CHAIN-OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    capture = _inspect(tmp_path, replay_references=refs)

    assert capture["replay_inspection_report"]["inspection_status"] == FAILED_CLOSED
    assert "chain mismatch" in capture["replay_inspection_report"]["failure_reason"]


def test_reconstruction_detects_report_corruption(tmp_path) -> None:
    _inspect(tmp_path)
    path = tmp_path / "inspection_replay" / "000_replay_inspection_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["mutation_performed"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_replay_inspector_worker_replay(tmp_path / "inspection_replay")


def test_reconstruction_detects_replay_ordering_corruption(tmp_path) -> None:
    _inspect(tmp_path)
    path = tmp_path / "inspection_replay" / "001_replay_inspection_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "replay_inspection_recorded"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_replay_inspector_worker_replay(tmp_path / "inspection_replay")


def test_no_mutation_provider_or_process_surface_imports() -> None:
    import aigol.runtime.replay_inspector_worker as replay_inspector_worker

    source = inspect.getsource(replay_inspector_worker)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "openai" not in source.lower()
    assert "anthropic" not in source.lower()
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
