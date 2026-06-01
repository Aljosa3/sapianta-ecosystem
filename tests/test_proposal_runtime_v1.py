"""Tests for PROPOSAL_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.proposal_runtime import (
    CREATED,
    PROPOSAL_RUNTIME_ARTIFACT_V1,
    PROPOSAL_RUNTIME_CREATED,
    PROPOSAL_RUNTIME_RETURNED,
    create_proposal,
    reconstruct_proposal_replay,
)


CREATED_AT = "2026-06-01T00:00:00+00:00"


def _proposal(tmp_path, **overrides) -> dict:
    args = {
        "proposal_id": "PROPOSAL-RUNTIME-000001",
        "proposal_type": "CAPABILITY_PROPOSAL",
        "proposal_source": "CONVERSATION",
        "proposal_text": "Create a bounded candidate for later governed inspection.",
        "created_at": CREATED_AT,
        "created_by": "AIGOL",
        "status": CREATED,
        "replay_reference": "REPLAY-PROPOSAL-RUNTIME-000001",
        "replay_dir": tmp_path / "proposal_runtime",
    }
    args.update(overrides)
    return create_proposal(**args)


def test_proposal_runtime_creates_created_artifact(tmp_path) -> None:
    capture = _proposal(tmp_path)
    proposal = capture["proposal_runtime_artifact"]
    returned = capture["proposal_runtime_replay"]
    reconstructed = reconstruct_proposal_replay(tmp_path / "proposal_runtime")

    assert proposal["artifact_type"] == PROPOSAL_RUNTIME_ARTIFACT_V1
    assert proposal["proposal_id"] == "PROPOSAL-RUNTIME-000001"
    assert proposal["proposal_type"] == "CAPABILITY_PROPOSAL"
    assert proposal["proposal_source"] == "CONVERSATION"
    assert proposal["created_by"] == "AIGOL"
    assert proposal["status"] == CREATED
    assert proposal["authority"] is False
    assert proposal["approval_created"] is False
    assert proposal["execution_requested"] is False
    assert proposal["provider_authority"] is False
    assert proposal["provider_invoked"] is False
    assert proposal["worker_invoked"] is False
    assert returned["event_type"] == PROPOSAL_RUNTIME_RETURNED
    assert reconstructed["status"] == CREATED
    assert reconstructed["replay_visible"] is True


def test_proposal_runtime_persists_replay_events(tmp_path) -> None:
    _proposal(tmp_path)

    created = tmp_path / "proposal_runtime" / "000_proposal_runtime_created.json"
    returned = tmp_path / "proposal_runtime" / "001_proposal_runtime_returned.json"
    assert created.exists()
    assert returned.exists()
    assert json.loads(created.read_text(encoding="utf-8"))["event_type"] == PROPOSAL_RUNTIME_CREATED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == PROPOSAL_RUNTIME_RETURNED


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("proposal_id", "", "proposal_id is required"),
        ("proposal_type", "", "proposal_type is required"),
        ("proposal_source", "", "proposal_source is required"),
        ("proposal_text", "", "proposal_text is required"),
        ("created_at", "", "created_at is required"),
        ("created_by", "", "created_by is required"),
        ("replay_reference", "", "replay_reference is required"),
    ],
)
def test_missing_mandatory_fields_fail_closed(tmp_path, field: str, value: str, message: str) -> None:
    with pytest.raises(FailClosedRuntimeError, match=message):
        _proposal(tmp_path, **{field: value})


def test_invalid_status_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="invalid status"):
        _proposal(tmp_path, status="APPROVED")


def test_invalid_type_and_source_fail_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="invalid proposal_type"):
        _proposal(tmp_path, proposal_type="UNKNOWN")

    with pytest.raises(FailClosedRuntimeError, match="invalid proposal_source"):
        _proposal(tmp_path, proposal_source="UNKNOWN")


def test_non_aigol_creator_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="creator must be AIGOL"):
        _proposal(tmp_path, created_by="PROVIDER")


def test_duplicate_replay_id_fails_closed(tmp_path) -> None:
    _proposal(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _proposal(tmp_path)


def test_replay_reconstruction_detects_artifact_corruption(tmp_path) -> None:
    _proposal(tmp_path)
    path = tmp_path / "proposal_runtime" / "000_proposal_runtime_created.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["status"] = "APPROVED"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_proposal_replay(tmp_path / "proposal_runtime")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _proposal(tmp_path)
    path = tmp_path / "proposal_runtime" / "001_proposal_runtime_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "proposal_runtime_created"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_proposal_replay(tmp_path / "proposal_runtime")


def test_replay_reconstruction_detects_reference_mismatch(tmp_path) -> None:
    _proposal(tmp_path)
    path = tmp_path / "proposal_runtime" / "001_proposal_runtime_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["proposal_reference"] = "OTHER"
    wrapper["artifact"].pop("artifact_hash")
    from aigol.runtime.transport.serialization import replay_hash

    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="reference mismatch"):
        reconstruct_proposal_replay(tmp_path / "proposal_runtime")


def test_no_expanded_runtime_surface_imports() -> None:
    import aigol.runtime.proposal_runtime as proposal_runtime

    source = inspect.getsource(proposal_runtime)

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
