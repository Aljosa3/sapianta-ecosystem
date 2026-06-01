"""Tests for PROPOSAL_APPROVAL_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.proposal_approval_runtime import (
    APPROVED,
    EXPIRED,
    PROPOSAL_APPROVAL_ARTIFACT_V1,
    PROPOSAL_APPROVAL_EXPIRED,
    PROPOSAL_APPROVAL_RETURNED,
    PROPOSAL_APPROVED,
    PROPOSAL_REJECTED,
    REJECTED,
    decide_proposal_approval,
    reconstruct_proposal_approval_replay,
)
from aigol.runtime.proposal_runtime import create_proposal
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-01T01:00:00+00:00"
_MISSING = object()


def _proposal(tmp_path) -> dict:
    return create_proposal(
        proposal_id="PROPOSAL-APPROVAL-000001",
        proposal_type="CAPABILITY_PROPOSAL",
        proposal_source="CONVERSATION",
        proposal_text="Create a bounded candidate for human approval.",
        created_at=CREATED_AT,
        replay_reference="REPLAY-PROPOSAL-APPROVAL-000001",
        replay_dir=tmp_path / "proposal",
    )["proposal_runtime_artifact"]


def _approval(tmp_path, **overrides) -> dict:
    proposal_artifact = overrides.pop("proposal_artifact", _MISSING)
    if proposal_artifact is _MISSING:
        proposal_artifact = _proposal(tmp_path)
    args = {
        "approval_id": "APPROVAL-000001",
        "proposal_artifact": proposal_artifact,
        "human_decision": "APPROVE",
        "decision_reason": "Human operator approves proposal for later lifecycle handling.",
        "operator_label": "human-operator",
        "created_at": CREATED_AT,
        "replay_reference": "REPLAY-APPROVAL-000001",
        "replay_dir": tmp_path / "approval",
    }
    args.update(overrides)
    return decide_proposal_approval(**args)


@pytest.mark.parametrize(
    ("decision", "status", "event_type"),
    [
        ("APPROVE", APPROVED, PROPOSAL_APPROVED),
        ("REJECT", REJECTED, PROPOSAL_REJECTED),
        ("EXPIRE", EXPIRED, PROPOSAL_APPROVAL_EXPIRED),
    ],
)
def test_proposal_approval_records_human_decision(tmp_path, decision: str, status: str, event_type: str) -> None:
    capture = _approval(tmp_path, human_decision=decision)
    approval = capture["proposal_approval_artifact"]
    returned = capture["proposal_approval_replay"]
    reconstructed = reconstruct_proposal_approval_replay(tmp_path / "approval")

    assert approval["artifact_type"] == PROPOSAL_APPROVAL_ARTIFACT_V1
    assert approval["approval_status"] == status
    assert approval["proposal_status_before"] == "CREATED"
    assert approval["authority"] is False
    assert approval["provider_approval"] is False
    assert approval["worker_approval"] is False
    assert approval["automatic_approval"] is False
    assert approval["execution_requested"] is False
    assert approval["execution_request_created"] is False
    assert approval["provider_invoked"] is False
    assert approval["worker_invoked"] is False
    assert returned["event_type"] == PROPOSAL_APPROVAL_RETURNED
    assert reconstructed["approval_status"] == status

    path = tmp_path / "approval" / "000_proposal_approval_decided.json"
    assert json.loads(path.read_text(encoding="utf-8"))["event_type"] == event_type


def test_approval_replay_artifacts_are_persisted(tmp_path) -> None:
    _approval(tmp_path)

    decided = tmp_path / "approval" / "000_proposal_approval_decided.json"
    returned = tmp_path / "approval" / "001_proposal_approval_returned.json"
    assert decided.exists()
    assert returned.exists()


def test_missing_proposal_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="proposal is required"):
        _approval(tmp_path, proposal_artifact=None)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("approval_id", "", "approval_id is required"),
        ("human_decision", "", "human_decision is required"),
        ("decision_reason", "", "decision_reason is required"),
        ("operator_label", "", "operator_label is required"),
        ("created_at", "", "created_at is required"),
        ("replay_reference", "", "replay_reference is required"),
    ],
)
def test_missing_approval_fields_fail_closed(tmp_path, field: str, value: str, message: str) -> None:
    with pytest.raises(FailClosedRuntimeError, match=message):
        _approval(tmp_path, **{field: value})


def test_invalid_human_decision_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="invalid human decision"):
        _approval(tmp_path, human_decision="MAYBE")


def test_invalid_proposal_status_change_fails_closed(tmp_path) -> None:
    proposal = _proposal(tmp_path)
    proposal["status"] = "APPROVED"
    proposal.pop("artifact_hash")
    proposal["artifact_hash"] = replay_hash(proposal)

    with pytest.raises(FailClosedRuntimeError, match="invalid proposal status"):
        _approval(tmp_path, proposal_artifact=proposal)


def test_corrupt_proposal_fails_closed(tmp_path) -> None:
    proposal = _proposal(tmp_path)
    proposal["proposal_text"] = "tampered"

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        _approval(tmp_path, proposal_artifact=proposal)


def test_duplicate_approvals_fail_closed(tmp_path) -> None:
    _approval(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _approval(tmp_path)


def test_replay_reconstruction_detects_approval_corruption(tmp_path) -> None:
    _approval(tmp_path)
    path = tmp_path / "approval" / "000_proposal_approval_decided.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["approval_status"] = "REJECTED"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_proposal_approval_replay(tmp_path / "approval")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _approval(tmp_path)
    path = tmp_path / "approval" / "001_proposal_approval_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "proposal_approval_decided"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_proposal_approval_replay(tmp_path / "approval")


def test_replay_reconstruction_detects_reference_mismatch(tmp_path) -> None:
    _approval(tmp_path)
    path = tmp_path / "approval" / "001_proposal_approval_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["approval_reference"] = "OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="approval reference mismatch"):
        reconstruct_proposal_approval_replay(tmp_path / "approval")


def test_no_expanded_runtime_surface_imports() -> None:
    import aigol.runtime.proposal_approval_runtime as proposal_approval_runtime

    source = inspect.getsource(proposal_approval_runtime)

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
