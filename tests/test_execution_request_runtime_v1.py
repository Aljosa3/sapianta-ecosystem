"""Tests for EXECUTION_REQUEST_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.execution_request_runtime import (
    CREATED_STATUS,
    EXECUTION_REQUEST_ARTIFACT_V1,
    EXECUTION_REQUEST_CREATED,
    EXECUTION_REQUEST_RETURNED,
    create_execution_request,
    reconstruct_execution_request_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.proposal_approval_runtime import decide_proposal_approval
from aigol.runtime.proposal_runtime import create_proposal
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-01T07:00:00+00:00"
_MISSING = object()


def _proposal(tmp_path) -> dict:
    return create_proposal(
        proposal_id="PROPOSAL-EXECUTION-REQUEST-000001",
        proposal_type="CAPABILITY_PROPOSAL",
        proposal_source="CONVERSATION",
        proposal_text="Create a bounded candidate for execution request derivation.",
        created_at=CREATED_AT,
        replay_reference="REPLAY-PROPOSAL-EXECUTION-REQUEST-000001",
        replay_dir=tmp_path / "proposal",
    )["proposal_runtime_artifact"]


def _approval(tmp_path, proposal: dict, human_decision: str = "APPROVE") -> dict:
    return decide_proposal_approval(
        approval_id=f"APPROVAL-{human_decision}-000001",
        proposal_artifact=proposal,
        human_decision=human_decision,
        decision_reason="Human operator records approval disposition for execution request boundary.",
        operator_label="human-operator",
        created_at=CREATED_AT,
        replay_reference=f"REPLAY-APPROVAL-{human_decision}-000001",
        replay_dir=tmp_path / f"approval_{human_decision.lower()}",
    )["proposal_approval_artifact"]


def _request(tmp_path, **overrides) -> dict:
    proposal_artifact = overrides.pop("proposal_artifact", _MISSING)
    approval_artifact = overrides.pop("approval_artifact", _MISSING)
    if proposal_artifact is _MISSING:
        proposal_artifact = _proposal(tmp_path)
    if approval_artifact is _MISSING:
        approval_artifact = _approval(tmp_path, proposal_artifact)
    args = {
        "execution_request_id": "EXECUTION-REQUEST-000001",
        "proposal_artifact": proposal_artifact,
        "approval_artifact": approval_artifact,
        "requested_by": "AIGOL",
        "created_at": CREATED_AT,
        "request_type": "CAPABILITY_EXECUTION_REQUEST",
        "request_payload": {
            "approved_action": "CREATE_BOUNDARY_ARTIFACT",
            "scope": "execution request creation only",
        },
        "status": CREATED_STATUS,
        "replay_reference": "REPLAY-EXECUTION-REQUEST-000001",
        "replay_dir": tmp_path / "execution_request",
    }
    args.update(overrides)
    return create_execution_request(**args)


def test_execution_request_creates_created_artifact_from_approved_proposal(tmp_path) -> None:
    capture = _request(tmp_path)
    request = capture["execution_request_artifact"]
    returned = capture["execution_request_replay"]
    reconstructed = reconstruct_execution_request_replay(tmp_path / "execution_request")

    assert request["artifact_type"] == EXECUTION_REQUEST_ARTIFACT_V1
    assert request["execution_request_id"] == "EXECUTION-REQUEST-000001"
    assert request["requested_by"] == "AIGOL"
    assert request["request_type"] == "CAPABILITY_EXECUTION_REQUEST"
    assert request["status"] == CREATED_STATUS
    assert request["replay_visible"] is True
    assert request["provider_authority"] is False
    assert request["worker_dispatched"] is False
    assert request["worker_invoked"] is False
    assert request["execution_performed"] is False
    assert returned["event_type"] == EXECUTION_REQUEST_RETURNED
    assert reconstructed["status"] == CREATED_STATUS
    assert reconstructed["worker_dispatched"] is False
    assert reconstructed["execution_performed"] is False


def test_execution_request_persists_replay_events(tmp_path) -> None:
    _request(tmp_path)

    created = tmp_path / "execution_request" / "000_execution_request_created.json"
    returned = tmp_path / "execution_request" / "001_execution_request_returned.json"
    assert created.exists()
    assert returned.exists()
    assert json.loads(created.read_text(encoding="utf-8"))["event_type"] == EXECUTION_REQUEST_CREATED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == EXECUTION_REQUEST_RETURNED


def test_missing_proposal_fails_closed(tmp_path) -> None:
    proposal = _proposal(tmp_path)
    approval = _approval(tmp_path, proposal)

    with pytest.raises(FailClosedRuntimeError, match="proposal is required"):
        _request(tmp_path, proposal_artifact=None, approval_artifact=approval)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("execution_request_id", "", "execution_request_id is required"),
        ("requested_by", "", "requested_by is required"),
        ("created_at", "", "created_at is required"),
        ("request_type", "", "request_type is required"),
        ("replay_reference", "", "replay_reference is required"),
    ],
)
def test_missing_execution_request_fields_fail_closed(tmp_path, field: str, value: str, message: str) -> None:
    with pytest.raises(FailClosedRuntimeError, match=message):
        _request(tmp_path, **{field: value})


def test_created_proposal_without_approved_approval_fails_closed(tmp_path) -> None:
    proposal = _proposal(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="approval is required"):
        _request(tmp_path, proposal_artifact=proposal, approval_artifact=None)


@pytest.mark.parametrize("decision", ["REJECT", "EXPIRE"])
def test_rejected_and_expired_proposals_fail_closed(tmp_path, decision: str) -> None:
    proposal = _proposal(tmp_path)
    approval = _approval(tmp_path, proposal, human_decision=decision)

    with pytest.raises(FailClosedRuntimeError, match="invalid proposal state"):
        _request(tmp_path, proposal_artifact=proposal, approval_artifact=approval)


def test_invalid_proposal_state_fails_closed(tmp_path) -> None:
    proposal = _proposal(tmp_path)
    approval = _approval(tmp_path, proposal)
    proposal["status"] = "REJECTED"
    proposal.pop("artifact_hash")
    proposal["artifact_hash"] = replay_hash(proposal)

    with pytest.raises(FailClosedRuntimeError, match="invalid proposal state"):
        _request(tmp_path, proposal_artifact=proposal, approval_artifact=approval)


def test_corrupt_proposal_fails_closed(tmp_path) -> None:
    proposal = _proposal(tmp_path)
    approval = _approval(tmp_path, proposal)
    proposal["proposal_text"] = "tampered"

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        _request(tmp_path, proposal_artifact=proposal, approval_artifact=approval)


def test_reference_mismatch_fails_closed(tmp_path) -> None:
    proposal = _proposal(tmp_path)
    approval = _approval(tmp_path, proposal)
    approval["proposal_id"] = "OTHER"
    approval.pop("artifact_hash")
    approval["artifact_hash"] = replay_hash(approval)

    with pytest.raises(FailClosedRuntimeError, match="proposal reference mismatch"):
        _request(tmp_path, proposal_artifact=proposal, approval_artifact=approval)


def test_duplicate_request_replay_fails_closed(tmp_path) -> None:
    _request(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _request(tmp_path)


def test_authority_bearing_payload_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="authority-bearing request payload"):
        _request(tmp_path, request_payload={"worker_command": "run"})


def test_replay_reconstruction_detects_artifact_corruption(tmp_path) -> None:
    _request(tmp_path)
    path = tmp_path / "execution_request" / "000_execution_request_created.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["status"] = "READY_FOR_DISPATCH"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_execution_request_replay(tmp_path / "execution_request")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _request(tmp_path)
    path = tmp_path / "execution_request" / "001_execution_request_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "execution_request_created"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_execution_request_replay(tmp_path / "execution_request")


def test_replay_reconstruction_detects_reference_mismatch(tmp_path) -> None:
    _request(tmp_path)
    path = tmp_path / "execution_request" / "001_execution_request_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["execution_request_reference"] = "OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="reference mismatch"):
        reconstruct_execution_request_replay(tmp_path / "execution_request")


def test_no_expanded_runtime_surface_imports() -> None:
    import aigol.runtime.execution_request_runtime as execution_request_runtime

    source = inspect.getsource(execution_request_runtime)

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
