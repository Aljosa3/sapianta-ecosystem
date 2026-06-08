"""Tests for EXECUTION_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.execution_runtime import (
    EXECUTING,
    EXECUTION_ARTIFACT_V1,
    EXECUTION_RETURNED,
    EXECUTION_STARTED,
    reconstruct_execution_replay,
    start_execution,
)
from aigol.runtime.dispatch_runtime import dispatch_worker
from aigol.runtime.execution_request_runtime import create_execution_request
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.proposal_approval_runtime import decide_proposal_approval
from aigol.runtime.proposal_runtime import create_proposal
from aigol.runtime.ready_for_dispatch_runtime import mark_ready_for_dispatch
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.worker_dispatch_runtime import WORKER_DISPATCHED, WORKER_DISPATCH_ARTIFACT_V1
from aigol.runtime.worker_invocation_runtime import invoke_worker
from aigol.runtime.worker_runtime import assign_worker, register_worker


CREATED_AT = "2026-06-01T12:00:00+00:00"
CANONICAL_CHAIN_ID = "CHAIN-20260601-EXECUTION-000001"


def _proposal(tmp_path) -> dict:
    return create_proposal(
        proposal_id="PROPOSAL-EXECUTION-000001",
        proposal_type="CAPABILITY_PROPOSAL",
        proposal_source="CONVERSATION",
        proposal_text="Create a bounded execution start candidate.",
        created_at=CREATED_AT,
        replay_reference="REPLAY-PROPOSAL-EXECUTION-000001",
        replay_dir=tmp_path / "proposal",
    )["proposal_runtime_artifact"]


def _approval(tmp_path, proposal: dict) -> dict:
    return decide_proposal_approval(
        approval_id="APPROVAL-EXECUTION-000001",
        proposal_artifact=proposal,
        human_decision="APPROVE",
        decision_reason="Human operator approves execution start lineage.",
        operator_label="human-operator",
        created_at=CREATED_AT,
        replay_reference="REPLAY-APPROVAL-EXECUTION-000001",
        replay_dir=tmp_path / "approval",
    )["proposal_approval_artifact"]


def _execution_request(tmp_path, proposal: dict, approval: dict) -> dict:
    return create_execution_request(
        execution_request_id="EXECUTION-REQUEST-EXECUTION-000001",
        proposal_artifact=proposal,
        approval_artifact=approval,
        requested_by="AIGOL",
        created_at=CREATED_AT,
        request_type="CAPABILITY_EXECUTION_REQUEST",
        request_payload={
            "approved_action": "START_EXECUTION_ONLY",
            "scope": "execution start without completion or result certification",
        },
        replay_reference="REPLAY-EXECUTION-REQUEST-EXECUTION-000001",
        replay_dir=tmp_path / "execution_request",
    )


def _readiness(tmp_path) -> dict:
    proposal = _proposal(tmp_path)
    approval = _approval(tmp_path, proposal)
    request_capture = _execution_request(tmp_path, proposal, approval)
    return mark_ready_for_dispatch(
        readiness_id="READY-FOR-DISPATCH-EXECUTION-000001",
        execution_request_artifact=request_capture["execution_request_artifact"],
        execution_request_replay=request_capture["execution_request_replay"],
        approval_artifact=approval,
        validated_at=CREATED_AT,
        replay_reference="REPLAY-READY-FOR-DISPATCH-EXECUTION-000001",
        replay_dir=tmp_path / "readiness",
    )


def _worker(tmp_path) -> dict:
    return register_worker(
        worker_id="WORKER-EXECUTION-000001",
        worker_type="LOCAL_BOUNDED_CAPABILITY_WORKER",
        worker_version="1.0.0",
        declared_capabilities=["BOUNDARY_ARTIFACT_INVOCATION"],
        supported_request_types=["CAPABILITY_EXECUTION_REQUEST"],
        trust_boundary="LOCAL_BOUNDED_WORKER",
        created_at=CREATED_AT,
        replay_reference="REPLAY-WORKER-EXECUTION-000001",
        replay_dir=tmp_path / "worker",
    )


def _assignment(tmp_path, *, readiness_capture: dict | None = None, worker_capture: dict | None = None) -> dict:
    if readiness_capture is None:
        readiness_capture = _readiness(tmp_path)
    if worker_capture is None:
        worker_capture = _worker(tmp_path)
    capture = assign_worker(
        worker_assignment_id="WORKER-ASSIGNMENT-EXECUTION-000001",
        worker_artifact=worker_capture["worker_artifact"],
        readiness_artifact=readiness_capture["ready_for_dispatch_artifact"],
        readiness_replay=readiness_capture["ready_for_dispatch_replay"],
        assigned_by="AIGOL",
        assigned_at=CREATED_AT,
        canonical_chain_id=CANONICAL_CHAIN_ID,
        replay_reference="REPLAY-WORKER-ASSIGNMENT-EXECUTION-000001",
        replay_dir=tmp_path / "assignment",
    )
    capture["_readiness_capture"] = readiness_capture
    return capture


def _dispatch(tmp_path, *, assignment_capture: dict, readiness_capture: dict | None = None) -> dict:
    if readiness_capture is None:
        readiness_capture = assignment_capture["_readiness_capture"]
    return dispatch_worker(
        dispatch_id="DISPATCH-EXECUTION-000001",
        worker_assignment_artifact=assignment_capture["worker_assignment_artifact"],
        worker_assignment_replay=assignment_capture["worker_assignment_replay"],
        readiness_artifact=readiness_capture["ready_for_dispatch_artifact"],
        canonical_chain_id=CANONICAL_CHAIN_ID,
        dispatched_by="AIGOL",
        dispatched_at=CREATED_AT,
        replay_reference="REPLAY-DISPATCH-EXECUTION-000001",
        replay_dir=tmp_path / "dispatch",
    )


def _parameters(dispatch_capture: dict) -> dict:
    dispatch = dispatch_capture["dispatch_artifact"]
    return {
        "execution_request_reference": dispatch["execution_request_reference"],
        "request_type": dispatch["request_type"],
        "capability_id": dispatch["capability_id"],
        "payload_reference": "EXECUTION-REQUEST-PAYLOAD-EXECUTION-000001",
        "payload_hash": "sha256:payload-execution-000001",
        "allowed_effects": ["RECORD_EXECUTION_START"],
        "forbidden_effects": ["COMPLETE_WORK", "CERTIFY_RESULT"],
    }


def _invocation(tmp_path, *, assignment_capture: dict, dispatch_capture: dict) -> dict:
    return invoke_worker(
        worker_invocation_id="WORKER-INVOCATION-EXECUTION-000001",
        dispatch_artifact=dispatch_capture["dispatch_artifact"],
        dispatch_replay=dispatch_capture["dispatch_replay"],
        worker_assignment_artifact=assignment_capture["worker_assignment_artifact"],
        canonical_chain_id=CANONICAL_CHAIN_ID,
        invocation_parameters=_parameters(dispatch_capture),
        invoked_by="AIGOL",
        invoked_at=CREATED_AT,
        replay_reference="REPLAY-WORKER-INVOCATION-EXECUTION-000001",
        replay_dir=tmp_path / "invocation",
    )


def _metadata() -> dict:
    return {
        "execution_mode": "START_ONLY",
        "runtime_boundary": "INVOKED_TO_EXECUTING",
        "result_handling": "OUT_OF_SCOPE",
    }


def _context(invocation_capture: dict) -> dict:
    invocation = invocation_capture["worker_invocation_artifact"]
    return {
        "worker_reference": invocation["worker_reference"],
        "request_type": invocation["request_type"],
        "capability_id": invocation["capability_id"],
        "allowed_effects": ["RECORD_EXECUTION_START"],
    }


def _execution(tmp_path, **overrides) -> dict:
    assignment_capture = overrides.pop("assignment_capture", None)
    dispatch_capture = overrides.pop("dispatch_capture", None)
    invocation_capture = overrides.pop("invocation_capture", None)
    if invocation_capture is None:
        if assignment_capture is None:
            assignment_capture = _assignment(tmp_path)
        if dispatch_capture is None:
            dispatch_capture = _dispatch(tmp_path, assignment_capture=assignment_capture)
        invocation_capture = _invocation(
            tmp_path,
            assignment_capture=assignment_capture,
            dispatch_capture=dispatch_capture,
        )
    if assignment_capture is None:
        assignment_capture = _assignment(tmp_path / "fallback_assignment")
    if dispatch_capture is None:
        dispatch_capture = _dispatch(tmp_path / "fallback_dispatch", assignment_capture=assignment_capture)
    args = {
        "execution_id": "EXECUTION-000001",
        "invocation_artifact": invocation_capture["worker_invocation_artifact"],
        "invocation_replay": invocation_capture["worker_invocation_replay"],
        "dispatch_artifact": dispatch_capture["dispatch_artifact"],
        "worker_assignment_artifact": assignment_capture["worker_assignment_artifact"],
        "canonical_chain_id": CANONICAL_CHAIN_ID,
        "execution_metadata": _metadata(),
        "execution_context": _context(invocation_capture),
        "started_by": "AIGOL",
        "started_at": CREATED_AT,
        "replay_reference": "REPLAY-EXECUTION-000001",
        "replay_dir": tmp_path / "execution",
    }
    args.update(overrides)
    return start_execution(**args)


def _current_assignment() -> dict:
    artifact = {
        "artifact_type": "WORKER_ASSIGNMENT_ARTIFACT_V1",
        "worker_runtime_version": "AIGOL_WORKER_ASSIGNMENT_RUNTIME_V1",
        "worker_assignment_id": "WORKER-ASSIGNMENT-CURRENT-000001",
        "assignment_status": "WORKER_ASSIGNED",
        "worker_id": "WORKER-CURRENT-000001",
        "worker_hash": "sha256:worker-current-000001",
        "worker_family": "FILESYSTEM_WORKER",
        "worker_role": "FILESYSTEM_MUTATION_WORKER",
        "capability_id": "FILESYSTEM_MUTATION_WORKER",
        "worker_invocation_request_reference": "WORKER-INVOCATION-REQUEST-CURRENT-000001",
        "worker_invocation_request_hash": "sha256:worker-invocation-request-current-000001",
        "authorization_reference": "AUTHORIZATION-CURRENT-000001",
        "authorization_hash": "sha256:authorization-current-000001",
        "execution_packet_reference": "EXECUTION-PACKET-CURRENT-000001",
        "execution_packet_hash": "sha256:execution-packet-current-000001",
        "allowed_outputs": ["execution start artifact"],
        "forbidden_operations": ["result certification", "repair", "retry"],
        "validation_requirements": ["replay lineage continuity"],
        "worker_state_before": "AVAILABLE",
        "worker_state_after": "ASSIGNED",
        "canonical_chain_id": CANONICAL_CHAIN_ID,
        "replay_reference": "REPLAY-AUTHORIZATION-CURRENT-000001",
        "replay_visible": True,
        "approval_created": False,
        "worker_assigned": True,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_started": False,
        "result_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _current_dispatch(assignment: dict) -> dict:
    artifact = {
        "artifact_type": WORKER_DISPATCH_ARTIFACT_V1,
        "runtime_version": "AIGOL_WORKER_DISPATCH_RUNTIME_V1",
        "worker_dispatch_id": "WORKER-DISPATCH-CURRENT-000001",
        "dispatch_status": WORKER_DISPATCHED,
        "worker_assignment_reference": assignment["worker_assignment_id"],
        "worker_assignment_hash": assignment["artifact_hash"],
        "worker_invocation_request_reference": assignment["worker_invocation_request_reference"],
        "worker_invocation_request_hash": assignment["worker_invocation_request_hash"],
        "authorization_reference": assignment["authorization_reference"],
        "authorization_hash": assignment["authorization_hash"],
        "execution_packet_reference": assignment["execution_packet_reference"],
        "execution_packet_hash": assignment["execution_packet_hash"],
        "worker_id": assignment["worker_id"],
        "worker_hash": assignment["worker_hash"],
        "worker_family": assignment["worker_family"],
        "worker_role": assignment["worker_role"],
        "allowed_outputs": assignment["allowed_outputs"],
        "forbidden_operations": assignment["forbidden_operations"],
        "validation_requirements": assignment["validation_requirements"],
        "dispatched_by": "AIGOL_GOVERNANCE",
        "dispatched_at": CREATED_AT,
        "assignment_status_before": "WORKER_ASSIGNED",
        "worker_state_before_dispatch": "ASSIGNED",
        "chain_id": CANONICAL_CHAIN_ID,
        "replay_reference": assignment["replay_reference"],
        "replay_visible": True,
        "approval_created": False,
        "worker_assigned": True,
        "worker_dispatched": True,
        "dispatch_requested": True,
        "worker_invoked": False,
        "execution_started": False,
        "result_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _current_invocation(dispatch: dict) -> dict:
    artifact = {
        "artifact_type": "WORKER_INVOCATION_ARTIFACT_V1",
        "runtime_version": "AIGOL_WORKER_INVOCATION_RUNTIME_V1",
        "worker_invocation_id": "WORKER-INVOCATION-CURRENT-000001",
        "invocation_status": "WORKER_INVOKED",
        "worker_dispatch_reference": dispatch["worker_dispatch_id"],
        "worker_dispatch_hash": dispatch["artifact_hash"],
        "worker_assignment_reference": dispatch["worker_assignment_reference"],
        "worker_assignment_hash": dispatch["worker_assignment_hash"],
        "worker_invocation_request_reference": dispatch["worker_invocation_request_reference"],
        "worker_invocation_request_hash": dispatch["worker_invocation_request_hash"],
        "authorization_reference": dispatch["authorization_reference"],
        "authorization_hash": dispatch["authorization_hash"],
        "execution_packet_reference": dispatch["execution_packet_reference"],
        "execution_packet_hash": dispatch["execution_packet_hash"],
        "worker_id": dispatch["worker_id"],
        "worker_hash": dispatch["worker_hash"],
        "worker_family": dispatch["worker_family"],
        "worker_role": dispatch["worker_role"],
        "allowed_outputs": dispatch["allowed_outputs"],
        "forbidden_operations": dispatch["forbidden_operations"],
        "validation_requirements": dispatch["validation_requirements"],
        "invoked_by": "AIGOL_GOVERNANCE",
        "invoked_at": CREATED_AT,
        "dispatch_status_before": dispatch["dispatch_status"],
        "worker_state_before_invocation": dispatch["worker_state_before_dispatch"],
        "chain_id": CANONICAL_CHAIN_ID,
        "replay_reference": dispatch["replay_reference"],
        "replay_visible": True,
        "approval_created": False,
        "worker_assigned": True,
        "worker_dispatched": True,
        "dispatch_requested": True,
        "worker_invoked": True,
        "execution_started": False,
        "result_created": False,
        "result_validated": False,
        "post_execution_replay_reviewed": False,
        "terminated": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _current_invocation_replay(invocation: dict) -> dict:
    artifact = {
        "artifact_type": "WORKER_INVOCATION_RESULT_ARTIFACT_V1",
        "runtime_version": "AIGOL_WORKER_INVOCATION_RUNTIME_V1",
        "invocation_result_id": f"{invocation['worker_invocation_id']}:RESULT",
        "invocation_status": invocation["invocation_status"],
        "worker_invocation_reference": invocation["worker_invocation_id"],
        "worker_invocation_hash": invocation["artifact_hash"],
        "worker_dispatch_reference": invocation["worker_dispatch_reference"],
        "worker_dispatch_hash": invocation["worker_dispatch_hash"],
        "worker_assignment_reference": invocation["worker_assignment_reference"],
        "worker_assignment_hash": invocation["worker_assignment_hash"],
        "worker_reference": invocation["worker_id"],
        "worker_hash": invocation["worker_hash"],
        "chain_id": invocation["chain_id"],
        "completed_at": CREATED_AT,
        "replay_visible": True,
        "approval_created": False,
        "worker_assigned": True,
        "worker_dispatched": True,
        "dispatch_requested": True,
        "worker_invoked": True,
        "execution_started": False,
        "result_created": False,
        "result_validated": False,
        "post_execution_replay_reviewed": False,
        "terminated": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _current_execution_context(invocation: dict) -> dict:
    return {
        "worker_reference": invocation["worker_id"],
        "request_type": "WORKER_INVOCATION_REQUEST",
        "capability_id": invocation["worker_role"],
        "allowed_effects": ["RECORD_EXECUTION_START"],
    }


def test_execution_runtime_creates_replay_visible_executing_artifact(tmp_path) -> None:
    assignment_capture = _assignment(tmp_path)
    dispatch_capture = _dispatch(tmp_path, assignment_capture=assignment_capture)
    invocation_capture = _invocation(
        tmp_path,
        assignment_capture=assignment_capture,
        dispatch_capture=dispatch_capture,
    )
    capture = _execution(
        tmp_path,
        assignment_capture=assignment_capture,
        dispatch_capture=dispatch_capture,
        invocation_capture=invocation_capture,
    )
    execution = capture["execution_artifact"]
    returned = capture["execution_replay"]
    reconstructed = reconstruct_execution_replay(tmp_path / "execution")

    assert execution["artifact_type"] == EXECUTION_ARTIFACT_V1
    assert execution["execution_status"] == EXECUTING
    assert execution["canonical_chain_id"] == CANONICAL_CHAIN_ID
    assert execution["worker_invocation_reference"] == "WORKER-INVOCATION-EXECUTION-000001"
    assert execution["dispatch_reference"] == "DISPATCH-EXECUTION-000001"
    assert execution["execution_started"] is True
    assert execution["completion_recorded"] is False
    assert execution["result_certified"] is False
    assert execution["self_improvement_performed"] is False
    assert execution["governance_mutated"] is False
    assert execution["replay_mutated"] is False
    assert returned["event_type"] == EXECUTION_RETURNED
    assert reconstructed["execution_status"] == EXECUTING
    assert reconstructed["completion_recorded"] is False
    assert reconstructed["result_certified"] is False


def test_execution_runtime_accepts_current_worker_invocation_chain(tmp_path) -> None:
    assignment = _current_assignment()
    dispatch = _current_dispatch(assignment)
    invocation = _current_invocation(dispatch)
    invocation_replay = _current_invocation_replay(invocation)

    capture = start_execution(
        execution_id="EXECUTION-CURRENT-000001",
        invocation_artifact=invocation,
        invocation_replay=invocation_replay,
        dispatch_artifact=dispatch,
        worker_assignment_artifact=assignment,
        canonical_chain_id=CANONICAL_CHAIN_ID,
        execution_metadata=_metadata(),
        execution_context=_current_execution_context(invocation),
        started_by="AIGOL",
        started_at=CREATED_AT,
        replay_reference="REPLAY-EXECUTION-CURRENT-000001",
        replay_dir=tmp_path / "execution_current",
    )
    execution = capture["execution_artifact"]
    reconstructed = reconstruct_execution_replay(tmp_path / "execution_current")

    assert execution["execution_status"] == EXECUTING
    assert execution["worker_invocation_reference"] == invocation["worker_invocation_id"]
    assert execution["dispatch_reference"] == dispatch["worker_dispatch_id"]
    assert execution["worker_reference"] == invocation["worker_id"]
    assert execution["execution_request_reference"] == invocation["worker_invocation_request_reference"]
    assert execution["request_type"] == "WORKER_INVOCATION_REQUEST"
    assert execution["capability_id"] == invocation["worker_role"]
    assert execution["completion_recorded"] is False
    assert execution["result_certified"] is False
    assert reconstructed["execution_status"] == EXECUTING


def test_execution_runtime_fails_closed_on_current_worker_invocation_lineage_mismatch(tmp_path) -> None:
    assignment = _current_assignment()
    dispatch = _current_dispatch(assignment)
    invocation = _current_invocation(dispatch)
    invocation_replay = _current_invocation_replay(invocation)
    invocation["worker_id"] = "OTHER-WORKER"
    invocation.pop("artifact_hash")
    invocation["artifact_hash"] = replay_hash(invocation)

    with pytest.raises(FailClosedRuntimeError, match="invocation replay hash mismatch"):
        start_execution(
            execution_id="EXECUTION-CURRENT-MISMATCH-000001",
            invocation_artifact=invocation,
            invocation_replay=invocation_replay,
            dispatch_artifact=dispatch,
            worker_assignment_artifact=assignment,
            canonical_chain_id=CANONICAL_CHAIN_ID,
            execution_metadata=_metadata(),
            execution_context=_current_execution_context(invocation),
            started_by="AIGOL",
            started_at=CREATED_AT,
            replay_reference="REPLAY-EXECUTION-CURRENT-MISMATCH-000001",
            replay_dir=tmp_path / "execution_current_mismatch",
        )


def test_execution_runtime_fails_closed_on_current_worker_invocation_authority_violation(tmp_path) -> None:
    assignment = _current_assignment()
    dispatch = _current_dispatch(assignment)
    invocation = _current_invocation(dispatch)
    invocation_replay = _current_invocation_replay(invocation)
    invocation["provider_authority"] = True
    invocation.pop("artifact_hash")
    invocation["artifact_hash"] = replay_hash(invocation)
    invocation_replay["worker_invocation_hash"] = invocation["artifact_hash"]
    invocation_replay.pop("artifact_hash")
    invocation_replay["artifact_hash"] = replay_hash(invocation_replay)

    with pytest.raises(FailClosedRuntimeError, match="provider authority introduced"):
        start_execution(
            execution_id="EXECUTION-CURRENT-AUTHORITY-000001",
            invocation_artifact=invocation,
            invocation_replay=invocation_replay,
            dispatch_artifact=dispatch,
            worker_assignment_artifact=assignment,
            canonical_chain_id=CANONICAL_CHAIN_ID,
            execution_metadata=_metadata(),
            execution_context=_current_execution_context(invocation),
            started_by="AIGOL",
            started_at=CREATED_AT,
            replay_reference="REPLAY-EXECUTION-CURRENT-AUTHORITY-000001",
            replay_dir=tmp_path / "execution_current_authority",
        )


def test_execution_runtime_persists_replay_events(tmp_path) -> None:
    _execution(tmp_path)

    started = tmp_path / "execution" / "000_execution_started.json"
    returned = tmp_path / "execution" / "001_execution_returned.json"
    assert started.exists()
    assert returned.exists()
    assert json.loads(started.read_text(encoding="utf-8"))["event_type"] == EXECUTION_STARTED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == EXECUTION_RETURNED


def test_invalid_invocation_state_fails_closed(tmp_path) -> None:
    assignment_capture = _assignment(tmp_path)
    dispatch_capture = _dispatch(tmp_path, assignment_capture=assignment_capture)
    invocation_capture = _invocation(tmp_path, assignment_capture=assignment_capture, dispatch_capture=dispatch_capture)
    invocation_capture["worker_invocation_artifact"]["invocation_status"] = "FAILED_INVOCATION"
    invocation_capture["worker_invocation_artifact"].pop("artifact_hash")
    invocation_capture["worker_invocation_artifact"]["artifact_hash"] = replay_hash(
        invocation_capture["worker_invocation_artifact"]
    )

    with pytest.raises(FailClosedRuntimeError, match="invalid invocation state"):
        _execution(
            tmp_path,
            assignment_capture=assignment_capture,
            dispatch_capture=dispatch_capture,
            invocation_capture=invocation_capture,
        )


def test_worker_mismatch_fails_closed(tmp_path) -> None:
    assignment_capture = _assignment(tmp_path)
    dispatch_capture = _dispatch(tmp_path, assignment_capture=assignment_capture)
    invocation_capture = _invocation(tmp_path, assignment_capture=assignment_capture, dispatch_capture=dispatch_capture)
    assignment_capture["worker_assignment_artifact"]["worker_id"] = "OTHER-WORKER"
    assignment_capture["worker_assignment_artifact"].pop("artifact_hash")
    assignment_capture["worker_assignment_artifact"]["artifact_hash"] = replay_hash(
        assignment_capture["worker_assignment_artifact"]
    )

    with pytest.raises(FailClosedRuntimeError, match="assignment hash mismatch"):
        _execution(
            tmp_path,
            assignment_capture=assignment_capture,
            dispatch_capture=dispatch_capture,
            invocation_capture=invocation_capture,
        )


def test_chain_mismatch_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        _execution(tmp_path, canonical_chain_id="CHAIN-20260601-OTHER")


def test_duplicate_execution_fails_closed(tmp_path) -> None:
    _execution(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _execution(tmp_path)


def test_corrupt_invocation_replay_reference_fails_closed(tmp_path) -> None:
    assignment_capture = _assignment(tmp_path)
    dispatch_capture = _dispatch(tmp_path, assignment_capture=assignment_capture)
    invocation_capture = _invocation(tmp_path, assignment_capture=assignment_capture, dispatch_capture=dispatch_capture)
    invocation_capture["worker_invocation_replay"]["dispatch_reference"] = "OTHER-DISPATCH"
    invocation_capture["worker_invocation_replay"].pop("artifact_hash")
    invocation_capture["worker_invocation_replay"]["artifact_hash"] = replay_hash(
        invocation_capture["worker_invocation_replay"]
    )

    with pytest.raises(FailClosedRuntimeError, match="dispatch continuity mismatch"):
        _execution(
            tmp_path,
            assignment_capture=assignment_capture,
            dispatch_capture=dispatch_capture,
            invocation_capture=invocation_capture,
        )


@pytest.mark.parametrize(
    ("field", "bad_value", "message"),
    [
        ("execution_metadata", {}, "execution_metadata is required"),
        ("execution_context", {}, "execution_context is required"),
        ("execution_metadata", {"result_payload": "not allowed"}, "authority-bearing execution_metadata"),
        ("execution_context", {"governance_mutation": True}, "authority-bearing execution_context"),
    ],
)
def test_invalid_execution_metadata_or_context_fails_closed(tmp_path, field: str, bad_value: dict, message: str) -> None:
    with pytest.raises(FailClosedRuntimeError, match=message):
        _execution(tmp_path, **{field: bad_value})


def test_replay_reconstruction_detects_artifact_corruption(tmp_path) -> None:
    _execution(tmp_path)
    path = tmp_path / "execution" / "000_execution_started.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["completion_recorded"] = True
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_execution_replay(tmp_path / "execution")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _execution(tmp_path)
    path = tmp_path / "execution" / "001_execution_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "execution_started"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_execution_replay(tmp_path / "execution")


def test_replay_reconstruction_detects_chain_mismatch(tmp_path) -> None:
    _execution(tmp_path)
    path = tmp_path / "execution" / "001_execution_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["canonical_chain_id"] = "CHAIN-20260601-OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        reconstruct_execution_replay(tmp_path / "execution")


def test_replay_reconstruction_detects_invalid_execution_state(tmp_path) -> None:
    _execution(tmp_path)
    path = tmp_path / "execution" / "000_execution_started.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["execution_status"] = "COMPLETED"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")
    returned_path = tmp_path / "execution" / "001_execution_returned.json"
    returned_wrapper = json.loads(returned_path.read_text(encoding="utf-8"))
    returned_wrapper["artifact"]["execution_hash"] = wrapper["artifact"]["artifact_hash"]
    returned_wrapper["artifact"].pop("artifact_hash")
    returned_wrapper["artifact"]["artifact_hash"] = replay_hash(returned_wrapper["artifact"])
    returned_wrapper.pop("replay_hash")
    returned_wrapper["replay_hash"] = replay_hash(returned_wrapper)
    returned_path.write_text(json.dumps(returned_wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="invalid execution state"):
        reconstruct_execution_replay(tmp_path / "execution")


def test_no_completion_result_provider_or_process_surface_imports() -> None:
    import aigol.runtime.execution_runtime as execution_runtime

    source = inspect.getsource(execution_runtime)

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
