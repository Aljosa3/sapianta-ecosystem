"""Tests for DISPATCH_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.dispatch_runtime import (
    DISPATCH_ARTIFACT_V1,
    DISPATCH_RETURNED,
    DISPATCH_VALIDATED,
    DISPATCHED,
    dispatch_worker,
    reconstruct_dispatch_replay,
)
from aigol.runtime.execution_request_runtime import create_execution_request
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.proposal_approval_runtime import decide_proposal_approval
from aigol.runtime.proposal_runtime import create_proposal
from aigol.runtime.ready_for_dispatch_runtime import mark_ready_for_dispatch
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.worker_runtime import ASSIGNED, UNAVAILABLE, assign_worker, register_worker


CREATED_AT = "2026-06-01T10:00:00+00:00"
CANONICAL_CHAIN_ID = "CHAIN-20260601-DISPATCH-000001"
_MISSING = object()


def _proposal(tmp_path) -> dict:
    return create_proposal(
        proposal_id="PROPOSAL-DISPATCH-000001",
        proposal_type="CAPABILITY_PROPOSAL",
        proposal_source="CONVERSATION",
        proposal_text="Create a bounded dispatch candidate.",
        created_at=CREATED_AT,
        replay_reference="REPLAY-PROPOSAL-DISPATCH-000001",
        replay_dir=tmp_path / "proposal",
    )["proposal_runtime_artifact"]


def _approval(tmp_path, proposal: dict) -> dict:
    return decide_proposal_approval(
        approval_id="APPROVAL-DISPATCH-000001",
        proposal_artifact=proposal,
        human_decision="APPROVE",
        decision_reason="Human operator approves dispatch lineage.",
        operator_label="human-operator",
        created_at=CREATED_AT,
        replay_reference="REPLAY-APPROVAL-DISPATCH-000001",
        replay_dir=tmp_path / "approval",
    )["proposal_approval_artifact"]


def _execution_request(tmp_path, proposal: dict, approval: dict) -> dict:
    return create_execution_request(
        execution_request_id="EXECUTION-REQUEST-DISPATCH-000001",
        proposal_artifact=proposal,
        approval_artifact=approval,
        requested_by="AIGOL",
        created_at=CREATED_AT,
        request_type="CAPABILITY_EXECUTION_REQUEST",
        request_payload={
            "approved_action": "DISPATCH_ONLY",
            "scope": "dispatch without invocation or execution",
        },
        replay_reference="REPLAY-EXECUTION-REQUEST-DISPATCH-000001",
        replay_dir=tmp_path / "execution_request",
    )


def _readiness(tmp_path) -> dict:
    proposal = _proposal(tmp_path)
    approval = _approval(tmp_path, proposal)
    request_capture = _execution_request(tmp_path, proposal, approval)
    return mark_ready_for_dispatch(
        readiness_id="READY-FOR-DISPATCH-DISPATCH-000001",
        execution_request_artifact=request_capture["execution_request_artifact"],
        execution_request_replay=request_capture["execution_request_replay"],
        approval_artifact=approval,
        validated_at=CREATED_AT,
        replay_reference="REPLAY-READY-FOR-DISPATCH-DISPATCH-000001",
        replay_dir=tmp_path / "readiness",
    )


def _worker(tmp_path) -> dict:
    return register_worker(
        worker_id="WORKER-DISPATCH-000001",
        worker_type="LOCAL_BOUNDED_CAPABILITY_WORKER",
        worker_version="1.0.0",
        declared_capabilities=["BOUNDARY_ARTIFACT_DISPATCH"],
        supported_request_types=["CAPABILITY_EXECUTION_REQUEST"],
        trust_boundary="LOCAL_BOUNDED_WORKER",
        created_at=CREATED_AT,
        replay_reference="REPLAY-WORKER-DISPATCH-000001",
        replay_dir=tmp_path / "worker",
    )


def _assignment(tmp_path, **overrides) -> dict:
    worker_capture = overrides.pop("worker_capture", _MISSING)
    readiness_capture = overrides.pop("readiness_capture", _MISSING)
    if worker_capture is _MISSING:
        worker_capture = _worker(tmp_path)
    if readiness_capture is _MISSING:
        readiness_capture = _readiness(tmp_path)
    args = {
        "worker_assignment_id": "WORKER-ASSIGNMENT-DISPATCH-000001",
        "worker_artifact": worker_capture["worker_artifact"],
        "readiness_artifact": readiness_capture["ready_for_dispatch_artifact"],
        "readiness_replay": readiness_capture["ready_for_dispatch_replay"],
        "assigned_by": "AIGOL",
        "assigned_at": CREATED_AT,
        "canonical_chain_id": CANONICAL_CHAIN_ID,
        "replay_reference": "REPLAY-WORKER-ASSIGNMENT-DISPATCH-000001",
        "replay_dir": tmp_path / "assignment",
    }
    args.update(overrides)
    return assign_worker(**args)


def _dispatch(tmp_path, **overrides) -> dict:
    assignment_capture = overrides.pop("assignment_capture", _MISSING)
    readiness_capture = overrides.pop("readiness_capture", _MISSING)
    if readiness_capture is _MISSING:
        readiness_capture = _readiness(tmp_path)
    if assignment_capture is _MISSING:
        worker_capture = _worker(tmp_path)
        assignment_capture = _assignment(
            tmp_path,
            worker_capture=worker_capture,
            readiness_capture=readiness_capture,
        )
    args = {
        "dispatch_id": "DISPATCH-000001",
        "worker_assignment_artifact": assignment_capture["worker_assignment_artifact"],
        "worker_assignment_replay": assignment_capture["worker_assignment_replay"],
        "readiness_artifact": readiness_capture["ready_for_dispatch_artifact"],
        "canonical_chain_id": CANONICAL_CHAIN_ID,
        "dispatched_by": "AIGOL",
        "dispatched_at": CREATED_AT,
        "replay_reference": "REPLAY-DISPATCH-000001",
        "replay_dir": tmp_path / "dispatch",
    }
    args.update(overrides)
    return dispatch_worker(**args)


def test_dispatch_creates_replay_visible_dispatch_artifact(tmp_path) -> None:
    readiness_capture = _readiness(tmp_path)
    worker_capture = _worker(tmp_path)
    assignment_capture = _assignment(
        tmp_path,
        worker_capture=worker_capture,
        readiness_capture=readiness_capture,
    )
    capture = _dispatch(tmp_path, assignment_capture=assignment_capture, readiness_capture=readiness_capture)
    dispatch = capture["dispatch_artifact"]
    returned = capture["dispatch_replay"]
    reconstructed = reconstruct_dispatch_replay(tmp_path / "dispatch")

    assert dispatch["artifact_type"] == DISPATCH_ARTIFACT_V1
    assert dispatch["dispatch_status"] == DISPATCHED
    assert dispatch["canonical_chain_id"] == CANONICAL_CHAIN_ID
    assert dispatch["worker_assignment_reference"] == "WORKER-ASSIGNMENT-DISPATCH-000001"
    assert dispatch["provider_authority"] is False
    assert dispatch["worker_self_dispatched"] is False
    assert dispatch["worker_invoked"] is False
    assert dispatch["execution_performed"] is False
    assert dispatch["completion_recorded"] is False
    assert returned["event_type"] == DISPATCH_RETURNED
    assert reconstructed["dispatch_status"] == DISPATCHED
    assert reconstructed["canonical_chain_id"] == CANONICAL_CHAIN_ID
    assert reconstructed["worker_invoked"] is False
    assert reconstructed["execution_performed"] is False


def test_dispatch_persists_replay_events(tmp_path) -> None:
    _dispatch(tmp_path)

    validated = tmp_path / "dispatch" / "000_dispatch_validated.json"
    returned = tmp_path / "dispatch" / "001_dispatch_returned.json"
    assert validated.exists()
    assert returned.exists()
    assert json.loads(validated.read_text(encoding="utf-8"))["event_type"] == DISPATCH_VALIDATED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == DISPATCH_RETURNED


def test_missing_assignment_fails_closed(tmp_path) -> None:
    readiness_capture = _readiness(tmp_path)
    assignment_capture = _assignment(tmp_path, readiness_capture=readiness_capture)

    with pytest.raises(FailClosedRuntimeError, match="worker assignment is required"):
        _dispatch(
            tmp_path,
            assignment_capture=assignment_capture,
            readiness_capture=readiness_capture,
            worker_assignment_artifact=None,
        )


def test_invalid_assignment_status_fails_closed(tmp_path) -> None:
    readiness_capture = _readiness(tmp_path)
    assignment_capture = _assignment(tmp_path, readiness_capture=readiness_capture)
    assignment_capture["worker_assignment_artifact"]["assignment_status"] = "CANCELLED"
    assignment_capture["worker_assignment_artifact"].pop("artifact_hash")
    assignment_capture["worker_assignment_artifact"]["artifact_hash"] = replay_hash(
        assignment_capture["worker_assignment_artifact"]
    )

    with pytest.raises(FailClosedRuntimeError, match="invalid assignment status"):
        _dispatch(tmp_path, assignment_capture=assignment_capture, readiness_capture=readiness_capture)


def test_worker_unavailable_fails_closed(tmp_path) -> None:
    readiness_capture = _readiness(tmp_path)
    assignment_capture = _assignment(tmp_path, readiness_capture=readiness_capture)
    assignment_capture["worker_assignment_artifact"]["worker_state_after"] = UNAVAILABLE
    assignment_capture["worker_assignment_artifact"].pop("artifact_hash")
    assignment_capture["worker_assignment_artifact"]["artifact_hash"] = replay_hash(
        assignment_capture["worker_assignment_artifact"]
    )

    with pytest.raises(FailClosedRuntimeError, match="worker unavailable"):
        _dispatch(tmp_path, assignment_capture=assignment_capture, readiness_capture=readiness_capture)


def test_duplicate_dispatch_fails_closed(tmp_path) -> None:
    _dispatch(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _dispatch(tmp_path)


def test_reference_corruption_fails_closed(tmp_path) -> None:
    readiness_capture = _readiness(tmp_path)
    assignment_capture = _assignment(tmp_path, readiness_capture=readiness_capture)
    assignment_capture["worker_assignment_replay"]["worker_assignment_reference"] = "OTHER"
    assignment_capture["worker_assignment_replay"].pop("artifact_hash")
    assignment_capture["worker_assignment_replay"]["artifact_hash"] = replay_hash(
        assignment_capture["worker_assignment_replay"]
    )

    with pytest.raises(FailClosedRuntimeError, match="assignment replay reference mismatch"):
        _dispatch(tmp_path, assignment_capture=assignment_capture, readiness_capture=readiness_capture)


def test_chain_mismatch_fails_closed(tmp_path) -> None:
    readiness_capture = _readiness(tmp_path)
    assignment_capture = _assignment(tmp_path, readiness_capture=readiness_capture)

    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        _dispatch(
            tmp_path,
            assignment_capture=assignment_capture,
            readiness_capture=readiness_capture,
            canonical_chain_id="CHAIN-20260601-OTHER",
        )


def test_assignment_without_chain_id_fails_closed(tmp_path) -> None:
    readiness_capture = _readiness(tmp_path)
    worker_capture = _worker(tmp_path)
    assignment_capture = _assignment(
        tmp_path,
        worker_capture=worker_capture,
        readiness_capture=readiness_capture,
        canonical_chain_id=None,
    )

    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        _dispatch(tmp_path, assignment_capture=assignment_capture, readiness_capture=readiness_capture)


def test_corrupt_readiness_fails_closed(tmp_path) -> None:
    readiness_capture = _readiness(tmp_path)
    assignment_capture = _assignment(tmp_path, readiness_capture=readiness_capture)
    readiness_capture["ready_for_dispatch_artifact"]["readiness_id"] = "OTHER"
    readiness_capture["ready_for_dispatch_artifact"].pop("artifact_hash")
    readiness_capture["ready_for_dispatch_artifact"]["artifact_hash"] = replay_hash(
        readiness_capture["ready_for_dispatch_artifact"]
    )

    with pytest.raises(FailClosedRuntimeError, match="readiness reference mismatch"):
        _dispatch(tmp_path, assignment_capture=assignment_capture, readiness_capture=readiness_capture)


def test_replay_reconstruction_detects_artifact_corruption(tmp_path) -> None:
    _dispatch(tmp_path)
    path = tmp_path / "dispatch" / "000_dispatch_validated.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_invoked"] = True
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_dispatch_replay(tmp_path / "dispatch")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _dispatch(tmp_path)
    path = tmp_path / "dispatch" / "001_dispatch_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "dispatch_validated"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_dispatch_replay(tmp_path / "dispatch")


def test_replay_reconstruction_detects_chain_mismatch(tmp_path) -> None:
    _dispatch(tmp_path)
    path = tmp_path / "dispatch" / "001_dispatch_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["canonical_chain_id"] = "CHAIN-20260601-OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        reconstruct_dispatch_replay(tmp_path / "dispatch")


def test_no_invocation_execution_or_completion_surface_imports() -> None:
    import aigol.runtime.dispatch_runtime as dispatch_runtime

    source = inspect.getsource(dispatch_runtime)

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
