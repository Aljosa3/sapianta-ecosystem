"""Tests for COMPLETION_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.completion_runtime import (
    COMPLETED,
    COMPLETION_ARTIFACT_V1,
    COMPLETION_RECORDED,
    COMPLETION_RETURNED,
    complete_execution,
    reconstruct_completion_replay,
)
from aigol.runtime.dispatch_runtime import dispatch_worker
from aigol.runtime.execution_request_runtime import create_execution_request
from aigol.runtime.execution_runtime import start_execution
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.proposal_approval_runtime import decide_proposal_approval
from aigol.runtime.proposal_runtime import create_proposal
from aigol.runtime.ready_for_dispatch_runtime import mark_ready_for_dispatch
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.worker_invocation_runtime import invoke_worker
from aigol.runtime.worker_runtime import assign_worker, register_worker


CREATED_AT = "2026-06-02T08:00:00+00:00"
CANONICAL_CHAIN_ID = "CHAIN-20260602-COMPLETION-000001"


def _proposal(tmp_path) -> dict:
    return create_proposal(
        proposal_id="PROPOSAL-COMPLETION-000001",
        proposal_type="CAPABILITY_PROPOSAL",
        proposal_source="CONVERSATION",
        proposal_text="Create a bounded completion record candidate.",
        created_at=CREATED_AT,
        replay_reference="REPLAY-PROPOSAL-COMPLETION-000001",
        replay_dir=tmp_path / "proposal",
    )["proposal_runtime_artifact"]


def _approval(tmp_path, proposal: dict) -> dict:
    return decide_proposal_approval(
        approval_id="APPROVAL-COMPLETION-000001",
        proposal_artifact=proposal,
        human_decision="APPROVE",
        decision_reason="Human operator approves completion lineage.",
        operator_label="human-operator",
        created_at=CREATED_AT,
        replay_reference="REPLAY-APPROVAL-COMPLETION-000001",
        replay_dir=tmp_path / "approval",
    )["proposal_approval_artifact"]


def _execution_request(tmp_path, proposal: dict, approval: dict) -> dict:
    return create_execution_request(
        execution_request_id="EXECUTION-REQUEST-COMPLETION-000001",
        proposal_artifact=proposal,
        approval_artifact=approval,
        requested_by="AIGOL",
        created_at=CREATED_AT,
        request_type="CAPABILITY_EXECUTION_REQUEST",
        request_payload={
            "approved_action": "RECORD_COMPLETION_ONLY",
            "scope": "completion record without result certification",
        },
        replay_reference="REPLAY-EXECUTION-REQUEST-COMPLETION-000001",
        replay_dir=tmp_path / "execution_request",
    )


def _readiness(tmp_path) -> dict:
    proposal = _proposal(tmp_path)
    approval = _approval(tmp_path, proposal)
    request_capture = _execution_request(tmp_path, proposal, approval)
    return mark_ready_for_dispatch(
        readiness_id="READY-FOR-DISPATCH-COMPLETION-000001",
        execution_request_artifact=request_capture["execution_request_artifact"],
        execution_request_replay=request_capture["execution_request_replay"],
        approval_artifact=approval,
        validated_at=CREATED_AT,
        replay_reference="REPLAY-READY-FOR-DISPATCH-COMPLETION-000001",
        replay_dir=tmp_path / "readiness",
    )


def _worker(tmp_path) -> dict:
    return register_worker(
        worker_id="WORKER-COMPLETION-000001",
        worker_type="LOCAL_BOUNDED_CAPABILITY_WORKER",
        worker_version="1.0.0",
        declared_capabilities=["BOUNDARY_ARTIFACT_COMPLETION"],
        supported_request_types=["CAPABILITY_EXECUTION_REQUEST"],
        trust_boundary="LOCAL_BOUNDED_WORKER",
        created_at=CREATED_AT,
        replay_reference="REPLAY-WORKER-COMPLETION-000001",
        replay_dir=tmp_path / "worker",
    )


def _assignment(tmp_path, *, readiness_capture: dict | None = None, worker_capture: dict | None = None) -> dict:
    if readiness_capture is None:
        readiness_capture = _readiness(tmp_path)
    if worker_capture is None:
        worker_capture = _worker(tmp_path)
    capture = assign_worker(
        worker_assignment_id="WORKER-ASSIGNMENT-COMPLETION-000001",
        worker_artifact=worker_capture["worker_artifact"],
        readiness_artifact=readiness_capture["ready_for_dispatch_artifact"],
        readiness_replay=readiness_capture["ready_for_dispatch_replay"],
        assigned_by="AIGOL",
        assigned_at=CREATED_AT,
        canonical_chain_id=CANONICAL_CHAIN_ID,
        replay_reference="REPLAY-WORKER-ASSIGNMENT-COMPLETION-000001",
        replay_dir=tmp_path / "assignment",
    )
    capture["_readiness_capture"] = readiness_capture
    return capture


def _dispatch(tmp_path, *, assignment_capture: dict, readiness_capture: dict | None = None) -> dict:
    if readiness_capture is None:
        readiness_capture = assignment_capture["_readiness_capture"]
    return dispatch_worker(
        dispatch_id="DISPATCH-COMPLETION-000001",
        worker_assignment_artifact=assignment_capture["worker_assignment_artifact"],
        worker_assignment_replay=assignment_capture["worker_assignment_replay"],
        readiness_artifact=readiness_capture["ready_for_dispatch_artifact"],
        canonical_chain_id=CANONICAL_CHAIN_ID,
        dispatched_by="AIGOL",
        dispatched_at=CREATED_AT,
        replay_reference="REPLAY-DISPATCH-COMPLETION-000001",
        replay_dir=tmp_path / "dispatch",
    )


def _parameters(dispatch_capture: dict) -> dict:
    dispatch = dispatch_capture["dispatch_artifact"]
    return {
        "execution_request_reference": dispatch["execution_request_reference"],
        "request_type": dispatch["request_type"],
        "capability_id": dispatch["capability_id"],
        "payload_reference": "EXECUTION-REQUEST-PAYLOAD-COMPLETION-000001",
        "payload_hash": "sha256:payload-completion-000001",
        "allowed_effects": ["RECORD_EXECUTION_START", "RECORD_COMPLETION"],
        "forbidden_effects": ["CERTIFY_RESULT", "ANALYZE_FAILURE"],
    }


def _invocation(tmp_path, *, assignment_capture: dict, dispatch_capture: dict) -> dict:
    return invoke_worker(
        worker_invocation_id="WORKER-INVOCATION-COMPLETION-000001",
        dispatch_artifact=dispatch_capture["dispatch_artifact"],
        dispatch_replay=dispatch_capture["dispatch_replay"],
        worker_assignment_artifact=assignment_capture["worker_assignment_artifact"],
        canonical_chain_id=CANONICAL_CHAIN_ID,
        invocation_parameters=_parameters(dispatch_capture),
        invoked_by="AIGOL",
        invoked_at=CREATED_AT,
        replay_reference="REPLAY-WORKER-INVOCATION-COMPLETION-000001",
        replay_dir=tmp_path / "invocation",
    )


def _execution(tmp_path, *, assignment_capture: dict, dispatch_capture: dict, invocation_capture: dict) -> dict:
    return start_execution(
        execution_id="EXECUTION-COMPLETION-000001",
        invocation_artifact=invocation_capture["worker_invocation_artifact"],
        invocation_replay=invocation_capture["worker_invocation_replay"],
        dispatch_artifact=dispatch_capture["dispatch_artifact"],
        worker_assignment_artifact=assignment_capture["worker_assignment_artifact"],
        canonical_chain_id=CANONICAL_CHAIN_ID,
        execution_metadata={
            "execution_mode": "START_ONLY_BEFORE_COMPLETION",
            "runtime_boundary": "EXECUTING_TO_COMPLETED",
        },
        execution_context={
            "worker_reference": invocation_capture["worker_invocation_artifact"]["worker_reference"],
            "request_type": invocation_capture["worker_invocation_artifact"]["request_type"],
            "capability_id": invocation_capture["worker_invocation_artifact"]["capability_id"],
        },
        started_by="AIGOL",
        started_at=CREATED_AT,
        replay_reference="REPLAY-EXECUTION-COMPLETION-000001",
        replay_dir=tmp_path / "execution",
    )


def _chain(tmp_path) -> dict:
    assignment_capture = _assignment(tmp_path)
    dispatch_capture = _dispatch(tmp_path, assignment_capture=assignment_capture)
    invocation_capture = _invocation(tmp_path, assignment_capture=assignment_capture, dispatch_capture=dispatch_capture)
    execution_capture = _execution(
        tmp_path,
        assignment_capture=assignment_capture,
        dispatch_capture=dispatch_capture,
        invocation_capture=invocation_capture,
    )
    return {
        "assignment_capture": assignment_capture,
        "dispatch_capture": dispatch_capture,
        "invocation_capture": invocation_capture,
        "execution_capture": execution_capture,
    }


def _completion(tmp_path, **overrides) -> dict:
    chain = overrides.pop("chain", None)
    if chain is None:
        chain = _chain(tmp_path)
    args = {
        "completion_id": "COMPLETION-000001",
        "execution_artifact": chain["execution_capture"]["execution_artifact"],
        "execution_replay": chain["execution_capture"]["execution_replay"],
        "invocation_artifact": chain["invocation_capture"]["worker_invocation_artifact"],
        "dispatch_artifact": chain["dispatch_capture"]["dispatch_artifact"],
        "worker_assignment_artifact": chain["assignment_capture"]["worker_assignment_artifact"],
        "canonical_chain_id": CANONICAL_CHAIN_ID,
        "completion_metadata": {
            "completion_mode": "RECORD_ONLY",
            "result_handling": "OUT_OF_SCOPE",
            "failure_handling": "OUT_OF_SCOPE_DECLARATION",
        },
        "completed_by": "AIGOL",
        "completed_at": CREATED_AT,
        "replay_reference": "REPLAY-COMPLETION-000001",
        "replay_dir": tmp_path / "completion",
    }
    args.update(overrides)
    return complete_execution(**args)


def test_completion_runtime_creates_replay_visible_completed_artifact(tmp_path) -> None:
    chain = _chain(tmp_path)
    capture = _completion(tmp_path, chain=chain)
    completion = capture["completion_artifact"]
    returned = capture["completion_replay"]
    reconstructed = reconstruct_completion_replay(tmp_path / "completion")

    assert completion["artifact_type"] == COMPLETION_ARTIFACT_V1
    assert completion["completion_status"] == COMPLETED
    assert completion["canonical_chain_id"] == CANONICAL_CHAIN_ID
    assert completion["execution_reference"] == "EXECUTION-COMPLETION-000001"
    assert completion["worker_invocation_reference"] == "WORKER-INVOCATION-COMPLETION-000001"
    assert completion["dispatch_reference"] == "DISPATCH-COMPLETION-000001"
    assert completion["completion_recorded"] is True
    assert completion["result_quality_evaluated"] is False
    assert completion["result_certified"] is False
    assert completion["failure_analysis_performed"] is False
    assert completion["self_improvement_performed"] is False
    assert completion["governance_mutated"] is False
    assert completion["replay_mutated"] is False
    assert completion["execution_history_modified"] is False
    assert returned["event_type"] == COMPLETION_RETURNED
    assert reconstructed["completion_status"] == COMPLETED
    assert reconstructed["result_certified"] is False


def test_completion_runtime_persists_replay_events(tmp_path) -> None:
    _completion(tmp_path)

    recorded = tmp_path / "completion" / "000_completion_recorded.json"
    returned = tmp_path / "completion" / "001_completion_returned.json"
    assert recorded.exists()
    assert returned.exists()
    assert json.loads(recorded.read_text(encoding="utf-8"))["event_type"] == COMPLETION_RECORDED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == COMPLETION_RETURNED


def test_invalid_execution_artifact_fails_closed(tmp_path) -> None:
    chain = _chain(tmp_path)
    execution = chain["execution_capture"]["execution_artifact"]
    execution["execution_status"] = "CANCELLED"
    execution.pop("artifact_hash")
    execution["artifact_hash"] = replay_hash(execution)

    with pytest.raises(FailClosedRuntimeError, match="invalid execution state"):
        _completion(tmp_path, chain=chain)


def test_worker_mismatch_fails_closed(tmp_path) -> None:
    chain = _chain(tmp_path)
    assignment = chain["assignment_capture"]["worker_assignment_artifact"]
    assignment["worker_id"] = "OTHER-WORKER"
    assignment.pop("artifact_hash")
    assignment["artifact_hash"] = replay_hash(assignment)

    with pytest.raises(FailClosedRuntimeError, match="assignment hash mismatch"):
        _completion(tmp_path, chain=chain)


def test_chain_mismatch_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        _completion(tmp_path, canonical_chain_id="CHAIN-20260602-OTHER")


def test_duplicate_completion_fails_closed(tmp_path) -> None:
    _completion(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _completion(tmp_path)


def test_corrupt_execution_replay_reference_fails_closed(tmp_path) -> None:
    chain = _chain(tmp_path)
    replay = chain["execution_capture"]["execution_replay"]
    replay["dispatch_reference"] = "OTHER-DISPATCH"
    replay.pop("artifact_hash")
    replay["artifact_hash"] = replay_hash(replay)

    with pytest.raises(FailClosedRuntimeError, match="dispatch continuity mismatch"):
        _completion(tmp_path, chain=chain)


@pytest.mark.parametrize(
    ("metadata", "message"),
    [
        ({}, "completion_metadata is required"),
        ({"result_quality": "good"}, "authority-bearing completion_metadata"),
        ({"self_improvement": True}, "authority-bearing completion_metadata"),
        ({"governance_mutation": True}, "authority-bearing completion_metadata"),
    ],
)
def test_invalid_completion_metadata_fails_closed(tmp_path, metadata: dict, message: str) -> None:
    with pytest.raises(FailClosedRuntimeError, match=message):
        _completion(tmp_path, completion_metadata=metadata)


def test_replay_reconstruction_detects_artifact_corruption(tmp_path) -> None:
    _completion(tmp_path)
    path = tmp_path / "completion" / "000_completion_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["result_certified"] = True
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_completion_replay(tmp_path / "completion")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _completion(tmp_path)
    path = tmp_path / "completion" / "001_completion_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "completion_recorded"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_completion_replay(tmp_path / "completion")


def test_replay_reconstruction_detects_chain_mismatch(tmp_path) -> None:
    _completion(tmp_path)
    path = tmp_path / "completion" / "001_completion_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["canonical_chain_id"] = "CHAIN-20260602-OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        reconstruct_completion_replay(tmp_path / "completion")


def test_replay_reconstruction_detects_invalid_completion_state(tmp_path) -> None:
    _completion(tmp_path)
    path = tmp_path / "completion" / "000_completion_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["completion_status"] = "FAILED"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")
    returned_path = tmp_path / "completion" / "001_completion_returned.json"
    returned_wrapper = json.loads(returned_path.read_text(encoding="utf-8"))
    returned_wrapper["artifact"]["completion_hash"] = wrapper["artifact"]["artifact_hash"]
    returned_wrapper["artifact"].pop("artifact_hash")
    returned_wrapper["artifact"]["artifact_hash"] = replay_hash(returned_wrapper["artifact"])
    returned_wrapper.pop("replay_hash")
    returned_wrapper["replay_hash"] = replay_hash(returned_wrapper)
    returned_path.write_text(json.dumps(returned_wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="invalid completion state"):
        reconstruct_completion_replay(tmp_path / "completion")


def test_no_result_failure_reflection_provider_or_process_surface_imports() -> None:
    import aigol.runtime.completion_runtime as completion_runtime

    source = inspect.getsource(completion_runtime)

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
