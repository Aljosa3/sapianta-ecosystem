"""Tests for WORKER_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.execution_request_runtime import create_execution_request
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.proposal_approval_runtime import decide_proposal_approval
from aigol.runtime.proposal_runtime import create_proposal
from aigol.runtime.ready_for_dispatch_runtime import mark_ready_for_dispatch
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.worker_runtime import (
    ASSIGNED,
    AVAILABLE,
    UNAVAILABLE,
    WORKER_ARTIFACT_V1,
    WORKER_ASSIGNED,
    WORKER_ASSIGNMENT_ARTIFACT_V1,
    WORKER_ASSIGNMENT_RETURNED,
    WORKER_REGISTERED,
    WORKER_REGISTRATION_RETURNED,
    assign_worker,
    reconstruct_worker_assignment_replay,
    reconstruct_worker_registration_replay,
    register_worker,
)


CREATED_AT = "2026-06-01T09:00:00+00:00"
_MISSING = object()


def _proposal(tmp_path) -> dict:
    return create_proposal(
        proposal_id="PROPOSAL-WORKER-000001",
        proposal_type="CAPABILITY_PROPOSAL",
        proposal_source="CONVERSATION",
        proposal_text="Create a bounded worker assignment candidate.",
        created_at=CREATED_AT,
        replay_reference="REPLAY-PROPOSAL-WORKER-000001",
        replay_dir=tmp_path / "proposal",
    )["proposal_runtime_artifact"]


def _approval(tmp_path, proposal: dict) -> dict:
    return decide_proposal_approval(
        approval_id="APPROVAL-WORKER-000001",
        proposal_artifact=proposal,
        human_decision="APPROVE",
        decision_reason="Human operator approves worker assignment lineage.",
        operator_label="human-operator",
        created_at=CREATED_AT,
        replay_reference="REPLAY-APPROVAL-WORKER-000001",
        replay_dir=tmp_path / "approval",
    )["proposal_approval_artifact"]


def _execution_request(tmp_path, proposal: dict, approval: dict) -> dict:
    return create_execution_request(
        execution_request_id="EXECUTION-REQUEST-WORKER-000001",
        proposal_artifact=proposal,
        approval_artifact=approval,
        requested_by="AIGOL",
        created_at=CREATED_AT,
        request_type="CAPABILITY_EXECUTION_REQUEST",
        request_payload={
            "approved_action": "ASSIGN_WORKER_ONLY",
            "scope": "worker assignment without dispatch or execution",
        },
        replay_reference="REPLAY-EXECUTION-REQUEST-WORKER-000001",
        replay_dir=tmp_path / "execution_request",
    )


def _readiness(tmp_path) -> dict:
    proposal = _proposal(tmp_path)
    approval = _approval(tmp_path, proposal)
    request_capture = _execution_request(tmp_path, proposal, approval)
    return mark_ready_for_dispatch(
        readiness_id="READY-FOR-DISPATCH-WORKER-000001",
        execution_request_artifact=request_capture["execution_request_artifact"],
        execution_request_replay=request_capture["execution_request_replay"],
        approval_artifact=approval,
        validated_at=CREATED_AT,
        replay_reference="REPLAY-READY-FOR-DISPATCH-WORKER-000001",
        replay_dir=tmp_path / "readiness",
    )


def _worker(tmp_path, **overrides) -> dict:
    args = {
        "worker_id": "WORKER-000001",
        "worker_type": "LOCAL_BOUNDED_CAPABILITY_WORKER",
        "worker_version": "1.0.0",
        "declared_capabilities": ["BOUNDARY_ARTIFACT_ASSIGNMENT"],
        "supported_request_types": ["CAPABILITY_EXECUTION_REQUEST"],
        "trust_boundary": "LOCAL_BOUNDED_WORKER",
        "created_at": CREATED_AT,
        "replay_reference": "REPLAY-WORKER-000001",
        "replay_dir": tmp_path / "worker",
    }
    args.update(overrides)
    return register_worker(**args)


def _assignment(tmp_path, **overrides) -> dict:
    worker_capture = overrides.pop("worker_capture", _MISSING)
    readiness_capture = overrides.pop("readiness_capture", _MISSING)
    if worker_capture is _MISSING:
        worker_capture = _worker(tmp_path)
    if readiness_capture is _MISSING:
        readiness_capture = _readiness(tmp_path)
    args = {
        "worker_assignment_id": "WORKER-ASSIGNMENT-000001",
        "worker_artifact": worker_capture["worker_artifact"],
        "readiness_artifact": readiness_capture["ready_for_dispatch_artifact"],
        "readiness_replay": readiness_capture["ready_for_dispatch_replay"],
        "assigned_by": "AIGOL",
        "assigned_at": CREATED_AT,
        "replay_reference": "REPLAY-WORKER-ASSIGNMENT-000001",
        "replay_dir": tmp_path / "assignment",
    }
    args.update(overrides)
    return assign_worker(**args)


def test_worker_registration_creates_available_worker_artifact(tmp_path) -> None:
    capture = _worker(tmp_path)
    worker = capture["worker_artifact"]
    returned = capture["worker_registration_replay"]
    reconstructed = reconstruct_worker_registration_replay(tmp_path / "worker")

    assert worker["artifact_type"] == WORKER_ARTIFACT_V1
    assert worker["state"] == AVAILABLE
    assert worker["provider_authority"] is False
    assert worker["self_authorization"] is False
    assert worker["worker_dispatched"] is False
    assert worker["execution_performed"] is False
    assert returned["event_type"] == WORKER_REGISTRATION_RETURNED
    assert reconstructed["worker_id"] == "WORKER-000001"
    assert reconstructed["state"] == AVAILABLE


def test_worker_registration_persists_replay_events(tmp_path) -> None:
    _worker(tmp_path)

    registered = tmp_path / "worker" / "000_worker_registered.json"
    returned = tmp_path / "worker" / "001_worker_registration_returned.json"
    assert registered.exists()
    assert returned.exists()
    assert json.loads(registered.read_text(encoding="utf-8"))["event_type"] == WORKER_REGISTERED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == WORKER_REGISTRATION_RETURNED


def test_worker_assignment_from_ready_for_dispatch_artifact(tmp_path) -> None:
    worker_capture = _worker(tmp_path)
    readiness_capture = _readiness(tmp_path)
    capture = _assignment(tmp_path, worker_capture=worker_capture, readiness_capture=readiness_capture)
    assignment = capture["worker_assignment_artifact"]
    returned = capture["worker_assignment_replay"]
    reconstructed = reconstruct_worker_assignment_replay(tmp_path / "assignment")

    assert assignment["artifact_type"] == WORKER_ASSIGNMENT_ARTIFACT_V1
    assert assignment["assignment_status"] == ASSIGNED
    assert assignment["worker_state_before"] == AVAILABLE
    assert assignment["worker_state_after"] == ASSIGNED
    assert assignment["provider_authority"] is False
    assert assignment["worker_self_assigned"] is False
    assert assignment["worker_dispatched"] is False
    assert assignment["worker_invoked"] is False
    assert assignment["execution_performed"] is False
    assert assignment["completion_recorded"] is False
    assert returned["event_type"] == WORKER_ASSIGNMENT_RETURNED
    assert reconstructed["assignment_status"] == ASSIGNED
    assert reconstructed["worker_dispatched"] is False
    assert reconstructed["execution_performed"] is False


def test_worker_assignment_persists_replay_events(tmp_path) -> None:
    _assignment(tmp_path)

    assigned = tmp_path / "assignment" / "000_worker_assigned.json"
    returned = tmp_path / "assignment" / "001_worker_assignment_returned.json"
    assert assigned.exists()
    assert returned.exists()
    assert json.loads(assigned.read_text(encoding="utf-8"))["event_type"] == WORKER_ASSIGNED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == WORKER_ASSIGNMENT_RETURNED


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("worker_id", "", "worker_id is required"),
        ("worker_type", "", "worker_type is required"),
        ("worker_version", "", "worker_version is required"),
        ("declared_capabilities", [], "declared_capabilities are required"),
        ("supported_request_types", [], "supported_request_types are required"),
        ("trust_boundary", "UNBOUNDED", "invalid trust boundary"),
        ("state", "EXECUTING", "invalid worker state"),
    ],
)
def test_invalid_worker_registration_fails_closed(tmp_path, field: str, value, message: str) -> None:
    with pytest.raises(FailClosedRuntimeError, match=message):
        _worker(tmp_path, **{field: value})


def test_missing_worker_fails_closed(tmp_path) -> None:
    readiness_capture = _readiness(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="worker is required"):
        _assignment(tmp_path, worker_artifact=None, readiness_capture=readiness_capture)


@pytest.mark.parametrize("state", [UNAVAILABLE, ASSIGNED])
def test_worker_unavailable_fails_closed(tmp_path, state: str) -> None:
    worker_capture = _worker(tmp_path, state=state)
    readiness_capture = _readiness(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="worker unavailable"):
        _assignment(tmp_path, worker_capture=worker_capture, readiness_capture=readiness_capture)


def test_invalid_readiness_artifact_fails_closed(tmp_path) -> None:
    worker_capture = _worker(tmp_path)
    readiness_capture = _readiness(tmp_path)
    readiness_capture["ready_for_dispatch_artifact"]["readiness_status"] = "CREATED"
    readiness_capture["ready_for_dispatch_artifact"].pop("artifact_hash")
    readiness_capture["ready_for_dispatch_artifact"]["artifact_hash"] = replay_hash(
        readiness_capture["ready_for_dispatch_artifact"]
    )

    with pytest.raises(FailClosedRuntimeError, match="invalid readiness status"):
        _assignment(tmp_path, worker_capture=worker_capture, readiness_capture=readiness_capture)


def test_corrupt_readiness_reference_fails_closed(tmp_path) -> None:
    worker_capture = _worker(tmp_path)
    readiness_capture = _readiness(tmp_path)
    readiness_capture["ready_for_dispatch_replay"]["readiness_reference"] = "OTHER"
    readiness_capture["ready_for_dispatch_replay"].pop("artifact_hash")
    readiness_capture["ready_for_dispatch_replay"]["artifact_hash"] = replay_hash(
        readiness_capture["ready_for_dispatch_replay"]
    )

    with pytest.raises(FailClosedRuntimeError, match="readiness replay reference mismatch"):
        _assignment(tmp_path, worker_capture=worker_capture, readiness_capture=readiness_capture)


def test_unsupported_request_type_fails_closed(tmp_path) -> None:
    worker_capture = _worker(tmp_path, supported_request_types=["OTHER_REQUEST"])
    readiness_capture = _readiness(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="unsupported request type"):
        _assignment(tmp_path, worker_capture=worker_capture, readiness_capture=readiness_capture)


def test_duplicate_assignment_fails_closed(tmp_path) -> None:
    _assignment(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _assignment(tmp_path)


def test_provider_authority_worker_fails_closed(tmp_path) -> None:
    worker_capture = _worker(tmp_path)
    readiness_capture = _readiness(tmp_path)
    worker_capture["worker_artifact"]["provider_authority"] = True
    worker_capture["worker_artifact"].pop("artifact_hash")
    worker_capture["worker_artifact"]["artifact_hash"] = replay_hash(worker_capture["worker_artifact"])

    with pytest.raises(FailClosedRuntimeError, match="provider authority introduced"):
        _assignment(tmp_path, worker_capture=worker_capture, readiness_capture=readiness_capture)


def test_replay_reconstruction_detects_registration_corruption(tmp_path) -> None:
    _worker(tmp_path)
    path = tmp_path / "worker" / "000_worker_registered.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["state"] = UNAVAILABLE
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_worker_registration_replay(tmp_path / "worker")


def test_replay_reconstruction_detects_assignment_corruption(tmp_path) -> None:
    _assignment(tmp_path)
    path = tmp_path / "assignment" / "000_worker_assigned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_dispatched"] = True
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_worker_assignment_replay(tmp_path / "assignment")


def test_replay_reconstruction_detects_assignment_ordering_corruption(tmp_path) -> None:
    _assignment(tmp_path)
    path = tmp_path / "assignment" / "001_worker_assignment_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "worker_assigned"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_worker_assignment_replay(tmp_path / "assignment")


def test_no_dispatch_execution_or_provider_surface_imports() -> None:
    import aigol.runtime.worker_runtime as worker_runtime

    source = inspect.getsource(worker_runtime)

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
