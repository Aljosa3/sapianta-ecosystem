"""Tests for WORKER_INVOCATION_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.dispatch_runtime import dispatch_worker
from aigol.runtime.execution_request_runtime import create_execution_request
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.proposal_approval_runtime import decide_proposal_approval
from aigol.runtime.proposal_runtime import create_proposal
from aigol.runtime.ready_for_dispatch_runtime import mark_ready_for_dispatch
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.worker_invocation_runtime import (
    INVOKED,
    WORKER_INVOCATION_ARTIFACT_V1,
    WORKER_INVOCATION_RETURNED,
    WORKER_INVOCATION_VALIDATED,
    invoke_worker,
    reconstruct_worker_invocation_replay,
)
from aigol.runtime.worker_runtime import ASSIGNED, UNAVAILABLE, assign_worker, register_worker


CREATED_AT = "2026-06-01T11:00:00+00:00"
CANONICAL_CHAIN_ID = "CHAIN-20260601-INVOCATION-000001"
_MISSING = object()


def _proposal(tmp_path) -> dict:
    return create_proposal(
        proposal_id="PROPOSAL-INVOCATION-000001",
        proposal_type="CAPABILITY_PROPOSAL",
        proposal_source="CONVERSATION",
        proposal_text="Create a bounded worker invocation candidate.",
        created_at=CREATED_AT,
        replay_reference="REPLAY-PROPOSAL-INVOCATION-000001",
        replay_dir=tmp_path / "proposal",
    )["proposal_runtime_artifact"]


def _approval(tmp_path, proposal: dict) -> dict:
    return decide_proposal_approval(
        approval_id="APPROVAL-INVOCATION-000001",
        proposal_artifact=proposal,
        human_decision="APPROVE",
        decision_reason="Human operator approves invocation lineage.",
        operator_label="human-operator",
        created_at=CREATED_AT,
        replay_reference="REPLAY-APPROVAL-INVOCATION-000001",
        replay_dir=tmp_path / "approval",
    )["proposal_approval_artifact"]


def _execution_request(tmp_path, proposal: dict, approval: dict) -> dict:
    return create_execution_request(
        execution_request_id="EXECUTION-REQUEST-INVOCATION-000001",
        proposal_artifact=proposal,
        approval_artifact=approval,
        requested_by="AIGOL",
        created_at=CREATED_AT,
        request_type="CAPABILITY_EXECUTION_REQUEST",
        request_payload={
            "approved_action": "INVOKE_ONLY",
            "scope": "worker invocation without execution or completion",
        },
        replay_reference="REPLAY-EXECUTION-REQUEST-INVOCATION-000001",
        replay_dir=tmp_path / "execution_request",
    )


def _readiness(tmp_path) -> dict:
    proposal = _proposal(tmp_path)
    approval = _approval(tmp_path, proposal)
    request_capture = _execution_request(tmp_path, proposal, approval)
    return mark_ready_for_dispatch(
        readiness_id="READY-FOR-DISPATCH-INVOCATION-000001",
        execution_request_artifact=request_capture["execution_request_artifact"],
        execution_request_replay=request_capture["execution_request_replay"],
        approval_artifact=approval,
        validated_at=CREATED_AT,
        replay_reference="REPLAY-READY-FOR-DISPATCH-INVOCATION-000001",
        replay_dir=tmp_path / "readiness",
    )


def _worker(tmp_path) -> dict:
    return register_worker(
        worker_id="WORKER-INVOCATION-000001",
        worker_type="LOCAL_BOUNDED_CAPABILITY_WORKER",
        worker_version="1.0.0",
        declared_capabilities=["BOUNDARY_ARTIFACT_INVOCATION"],
        supported_request_types=["CAPABILITY_EXECUTION_REQUEST"],
        trust_boundary="LOCAL_BOUNDED_WORKER",
        created_at=CREATED_AT,
        replay_reference="REPLAY-WORKER-INVOCATION-000001",
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
        "worker_assignment_id": "WORKER-ASSIGNMENT-INVOCATION-000001",
        "worker_artifact": worker_capture["worker_artifact"],
        "readiness_artifact": readiness_capture["ready_for_dispatch_artifact"],
        "readiness_replay": readiness_capture["ready_for_dispatch_replay"],
        "assigned_by": "AIGOL",
        "assigned_at": CREATED_AT,
        "canonical_chain_id": CANONICAL_CHAIN_ID,
        "replay_reference": "REPLAY-WORKER-ASSIGNMENT-INVOCATION-000001",
        "replay_dir": tmp_path / "assignment",
    }
    args.update(overrides)
    capture = assign_worker(**args)
    capture["_readiness_capture"] = readiness_capture
    return capture


def _dispatch(tmp_path, **overrides) -> dict:
    assignment_capture = overrides.pop("assignment_capture", _MISSING)
    readiness_capture = overrides.pop("readiness_capture", _MISSING)
    if readiness_capture is _MISSING and assignment_capture is not _MISSING:
        readiness_capture = assignment_capture.get("_readiness_capture", _MISSING)
    if readiness_capture is _MISSING:
        readiness_capture = _readiness(tmp_path)
    if assignment_capture is _MISSING:
        assignment_capture = _assignment(tmp_path, readiness_capture=readiness_capture)
    args = {
        "dispatch_id": "DISPATCH-INVOCATION-000001",
        "worker_assignment_artifact": assignment_capture["worker_assignment_artifact"],
        "worker_assignment_replay": assignment_capture["worker_assignment_replay"],
        "readiness_artifact": readiness_capture["ready_for_dispatch_artifact"],
        "canonical_chain_id": CANONICAL_CHAIN_ID,
        "dispatched_by": "AIGOL",
        "dispatched_at": CREATED_AT,
        "replay_reference": "REPLAY-DISPATCH-INVOCATION-000001",
        "replay_dir": tmp_path / "dispatch",
    }
    args.update(overrides)
    return dispatch_worker(**args)


def _parameters(dispatch_capture: dict) -> dict:
    dispatch = dispatch_capture["dispatch_artifact"]
    return {
        "execution_request_reference": dispatch["execution_request_reference"],
        "request_type": dispatch["request_type"],
        "capability_id": dispatch["capability_id"],
        "payload_reference": "EXECUTION-REQUEST-PAYLOAD-INVOCATION-000001",
        "payload_hash": "sha256:payload-invocation-000001",
        "allowed_effects": ["INVOKE_BOUNDARY_ONLY"],
        "forbidden_effects": ["EXECUTE_WORK", "COMPLETE_WORK"],
    }


def _invocation(tmp_path, **overrides) -> dict:
    assignment_capture = overrides.pop("assignment_capture", _MISSING)
    dispatch_capture = overrides.pop("dispatch_capture", _MISSING)
    if assignment_capture is _MISSING:
        readiness_capture = _readiness(tmp_path)
        assignment_capture = _assignment(tmp_path, readiness_capture=readiness_capture)
    if dispatch_capture is _MISSING:
        dispatch_capture = _dispatch(tmp_path, assignment_capture=assignment_capture)
    args = {
        "worker_invocation_id": "WORKER-INVOCATION-000001",
        "dispatch_artifact": dispatch_capture["dispatch_artifact"],
        "dispatch_replay": dispatch_capture["dispatch_replay"],
        "worker_assignment_artifact": assignment_capture["worker_assignment_artifact"],
        "canonical_chain_id": CANONICAL_CHAIN_ID,
        "invocation_parameters": _parameters(dispatch_capture),
        "invoked_by": "AIGOL",
        "invoked_at": CREATED_AT,
        "replay_reference": "REPLAY-WORKER-INVOCATION-000001",
        "replay_dir": tmp_path / "invocation",
    }
    args.update(overrides)
    return invoke_worker(**args)


def test_worker_invocation_creates_replay_visible_artifact(tmp_path) -> None:
    readiness_capture = _readiness(tmp_path)
    assignment_capture = _assignment(tmp_path, readiness_capture=readiness_capture)
    dispatch_capture = _dispatch(tmp_path, assignment_capture=assignment_capture, readiness_capture=readiness_capture)
    capture = _invocation(tmp_path, assignment_capture=assignment_capture, dispatch_capture=dispatch_capture)
    invocation = capture["worker_invocation_artifact"]
    returned = capture["worker_invocation_replay"]
    reconstructed = reconstruct_worker_invocation_replay(tmp_path / "invocation")

    assert invocation["artifact_type"] == WORKER_INVOCATION_ARTIFACT_V1
    assert invocation["invocation_status"] == INVOKED
    assert invocation["canonical_chain_id"] == CANONICAL_CHAIN_ID
    assert invocation["dispatch_reference"] == "DISPATCH-INVOCATION-000001"
    assert invocation["provider_authority"] is False
    assert invocation["worker_self_invoked"] is False
    assert invocation["execution_started"] is False
    assert invocation["execution_performed"] is False
    assert invocation["completion_recorded"] is False
    assert returned["event_type"] == WORKER_INVOCATION_RETURNED
    assert reconstructed["invocation_status"] == INVOKED
    assert reconstructed["execution_started"] is False
    assert reconstructed["execution_performed"] is False


def test_worker_invocation_persists_replay_events(tmp_path) -> None:
    _invocation(tmp_path)

    validated = tmp_path / "invocation" / "000_worker_invocation_validated.json"
    returned = tmp_path / "invocation" / "001_worker_invocation_returned.json"
    assert validated.exists()
    assert returned.exists()
    assert json.loads(validated.read_text(encoding="utf-8"))["event_type"] == WORKER_INVOCATION_VALIDATED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == WORKER_INVOCATION_RETURNED


def test_invalid_dispatch_fails_closed(tmp_path) -> None:
    assignment_capture = _assignment(tmp_path)
    dispatch_capture = _dispatch(tmp_path, assignment_capture=assignment_capture)
    dispatch_capture["dispatch_artifact"]["dispatch_status"] = "CANCELLED"
    dispatch_capture["dispatch_artifact"].pop("artifact_hash")
    dispatch_capture["dispatch_artifact"]["artifact_hash"] = replay_hash(dispatch_capture["dispatch_artifact"])

    with pytest.raises(FailClosedRuntimeError, match="invalid dispatch status"):
        _invocation(tmp_path, assignment_capture=assignment_capture, dispatch_capture=dispatch_capture)


def test_worker_mismatch_fails_closed(tmp_path) -> None:
    assignment_capture = _assignment(tmp_path)
    dispatch_capture = _dispatch(tmp_path, assignment_capture=assignment_capture)
    assignment_capture["worker_assignment_artifact"]["worker_id"] = "OTHER"
    assignment_capture["worker_assignment_artifact"].pop("artifact_hash")
    assignment_capture["worker_assignment_artifact"]["artifact_hash"] = replay_hash(
        assignment_capture["worker_assignment_artifact"]
    )

    with pytest.raises(FailClosedRuntimeError, match="assignment hash mismatch"):
        _invocation(tmp_path, assignment_capture=assignment_capture, dispatch_capture=dispatch_capture)


def test_worker_unavailable_fails_closed(tmp_path) -> None:
    assignment_capture = _assignment(tmp_path)
    dispatch_capture = _dispatch(tmp_path, assignment_capture=assignment_capture)
    assignment_capture["worker_assignment_artifact"]["worker_state_after"] = UNAVAILABLE
    assignment_capture["worker_assignment_artifact"].pop("artifact_hash")
    assignment_capture["worker_assignment_artifact"]["artifact_hash"] = replay_hash(
        assignment_capture["worker_assignment_artifact"]
    )

    with pytest.raises(FailClosedRuntimeError, match="worker unavailable"):
        _invocation(tmp_path, assignment_capture=assignment_capture, dispatch_capture=dispatch_capture)


def test_duplicate_invocation_fails_closed(tmp_path) -> None:
    _invocation(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _invocation(tmp_path)


def test_chain_mismatch_fails_closed(tmp_path) -> None:
    assignment_capture = _assignment(tmp_path)
    dispatch_capture = _dispatch(tmp_path, assignment_capture=assignment_capture)

    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        _invocation(
            tmp_path,
            assignment_capture=assignment_capture,
            dispatch_capture=dispatch_capture,
            canonical_chain_id="CHAIN-20260601-OTHER",
        )


@pytest.mark.parametrize(
    "bad_parameters",
    [
        {},
        {"execute_now": True},
        {
            "execution_request_reference": "OTHER",
            "request_type": "CAPABILITY_EXECUTION_REQUEST",
            "capability_id": "BOUNDARY_ARTIFACT_INVOCATION",
            "payload_reference": "PAYLOAD",
            "payload_hash": "sha256:payload",
            "allowed_effects": [],
            "forbidden_effects": [],
        },
    ],
)
def test_parameter_validation_failure_fails_closed(tmp_path, bad_parameters: dict) -> None:
    assignment_capture = _assignment(tmp_path)
    dispatch_capture = _dispatch(tmp_path, assignment_capture=assignment_capture)

    with pytest.raises(FailClosedRuntimeError, match="invocation_parameters|authority-bearing|validation failure"):
        _invocation(
            tmp_path,
            assignment_capture=assignment_capture,
            dispatch_capture=dispatch_capture,
            invocation_parameters=bad_parameters,
        )


def test_corrupt_dispatch_replay_reference_fails_closed(tmp_path) -> None:
    assignment_capture = _assignment(tmp_path)
    dispatch_capture = _dispatch(tmp_path, assignment_capture=assignment_capture)
    dispatch_capture["dispatch_replay"]["dispatch_reference"] = "OTHER"
    dispatch_capture["dispatch_replay"].pop("artifact_hash")
    dispatch_capture["dispatch_replay"]["artifact_hash"] = replay_hash(dispatch_capture["dispatch_replay"])

    with pytest.raises(FailClosedRuntimeError, match="dispatch replay reference mismatch"):
        _invocation(tmp_path, assignment_capture=assignment_capture, dispatch_capture=dispatch_capture)


def test_replay_reconstruction_detects_artifact_corruption(tmp_path) -> None:
    _invocation(tmp_path)
    path = tmp_path / "invocation" / "000_worker_invocation_validated.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["execution_performed"] = True
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_worker_invocation_replay(tmp_path / "invocation")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _invocation(tmp_path)
    path = tmp_path / "invocation" / "001_worker_invocation_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "worker_invocation_validated"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_worker_invocation_replay(tmp_path / "invocation")


def test_replay_reconstruction_detects_chain_mismatch(tmp_path) -> None:
    _invocation(tmp_path)
    path = tmp_path / "invocation" / "001_worker_invocation_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["canonical_chain_id"] = "CHAIN-20260601-OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        reconstruct_worker_invocation_replay(tmp_path / "invocation")


def test_no_execution_completion_or_provider_surface_imports() -> None:
    import aigol.runtime.worker_invocation_runtime as worker_invocation_runtime

    source = inspect.getsource(worker_invocation_runtime)

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
