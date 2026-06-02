"""Tests for RESULT_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.completion_runtime import complete_execution
from aigol.runtime.dispatch_runtime import dispatch_worker
from aigol.runtime.execution_request_runtime import create_execution_request
from aigol.runtime.execution_runtime import start_execution
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.proposal_approval_runtime import decide_proposal_approval
from aigol.runtime.proposal_runtime import create_proposal
from aigol.runtime.ready_for_dispatch_runtime import mark_ready_for_dispatch
from aigol.runtime.replay_inspector_worker import inspect_replay_worker
from aigol.runtime.result_runtime import (
    RESULT_ARTIFACT_V1,
    RESULT_CAPTURED,
    RESULT_RECORDED,
    RESULT_RETURNED,
    capture_result,
    reconstruct_result_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from aigol.runtime.worker_invocation_runtime import invoke_worker
from aigol.runtime.worker_runtime import assign_worker, register_worker


CREATED_AT = "2026-06-02T10:00:00+00:00"
CANONICAL_CHAIN_ID = "CHAIN-20260602-RESULT-000001"


def _proposal(tmp_path) -> dict:
    return create_proposal(
        proposal_id="PROPOSAL-RESULT-000001",
        proposal_type="CAPABILITY_PROPOSAL",
        proposal_source="CONVERSATION",
        proposal_text="Capture replay inspector worker output as result.",
        created_at=CREATED_AT,
        replay_reference="REPLAY-PROPOSAL-RESULT-000001",
        replay_dir=tmp_path / "proposal",
    )["proposal_runtime_artifact"]


def _approval(tmp_path, proposal: dict) -> dict:
    return decide_proposal_approval(
        approval_id="APPROVAL-RESULT-000001",
        proposal_artifact=proposal,
        human_decision="APPROVE",
        decision_reason="Human operator approves result capture lineage.",
        operator_label="human-operator",
        created_at=CREATED_AT,
        replay_reference="REPLAY-APPROVAL-RESULT-000001",
        replay_dir=tmp_path / "approval",
    )["proposal_approval_artifact"]


def _execution_request(tmp_path, proposal: dict, approval: dict) -> dict:
    return create_execution_request(
        execution_request_id="EXECUTION-REQUEST-RESULT-000001",
        proposal_artifact=proposal,
        approval_artifact=approval,
        requested_by="AIGOL",
        created_at=CREATED_AT,
        request_type="CAPABILITY_EXECUTION_REQUEST",
        request_payload={
            "approved_action": "CAPTURE_RESULT_ONLY",
            "scope": "result capture without quality evaluation or certification",
        },
        replay_reference="REPLAY-EXECUTION-REQUEST-RESULT-000001",
        replay_dir=tmp_path / "execution_request",
    )


def _readiness(tmp_path) -> dict:
    proposal = _proposal(tmp_path)
    approval = _approval(tmp_path, proposal)
    request_capture = _execution_request(tmp_path, proposal, approval)
    return mark_ready_for_dispatch(
        readiness_id="READY-FOR-DISPATCH-RESULT-000001",
        execution_request_artifact=request_capture["execution_request_artifact"],
        execution_request_replay=request_capture["execution_request_replay"],
        approval_artifact=approval,
        validated_at=CREATED_AT,
        replay_reference="REPLAY-READY-FOR-DISPATCH-RESULT-000001",
        replay_dir=tmp_path / "readiness",
    )


def _worker(tmp_path) -> dict:
    return register_worker(
        worker_id="WORKER-RESULT-000001",
        worker_type="REPLAY_INSPECTOR_WORKER_V1",
        worker_version="1.0.0",
        declared_capabilities=["REPLAY_INSPECTION_READ_ONLY"],
        supported_request_types=["CAPABILITY_EXECUTION_REQUEST"],
        trust_boundary="LOCAL_BOUNDED_WORKER",
        created_at=CREATED_AT,
        replay_reference="REPLAY-WORKER-RESULT-000001",
        replay_dir=tmp_path / "worker",
    )


def _assignment(tmp_path, *, readiness_capture: dict | None = None, worker_capture: dict | None = None) -> dict:
    if readiness_capture is None:
        readiness_capture = _readiness(tmp_path)
    if worker_capture is None:
        worker_capture = _worker(tmp_path)
    capture = assign_worker(
        worker_assignment_id="WORKER-ASSIGNMENT-RESULT-000001",
        worker_artifact=worker_capture["worker_artifact"],
        readiness_artifact=readiness_capture["ready_for_dispatch_artifact"],
        readiness_replay=readiness_capture["ready_for_dispatch_replay"],
        assigned_by="AIGOL",
        assigned_at=CREATED_AT,
        canonical_chain_id=CANONICAL_CHAIN_ID,
        replay_reference="REPLAY-WORKER-ASSIGNMENT-RESULT-000001",
        replay_dir=tmp_path / "assignment",
    )
    capture["_readiness_capture"] = readiness_capture
    return capture


def _dispatch(tmp_path, *, assignment_capture: dict, readiness_capture: dict | None = None) -> dict:
    if readiness_capture is None:
        readiness_capture = assignment_capture["_readiness_capture"]
    return dispatch_worker(
        dispatch_id="DISPATCH-RESULT-000001",
        worker_assignment_artifact=assignment_capture["worker_assignment_artifact"],
        worker_assignment_replay=assignment_capture["worker_assignment_replay"],
        readiness_artifact=readiness_capture["ready_for_dispatch_artifact"],
        canonical_chain_id=CANONICAL_CHAIN_ID,
        dispatched_by="AIGOL",
        dispatched_at=CREATED_AT,
        replay_reference="REPLAY-DISPATCH-RESULT-000001",
        replay_dir=tmp_path / "dispatch",
    )


def _parameters(dispatch_capture: dict) -> dict:
    dispatch = dispatch_capture["dispatch_artifact"]
    return {
        "execution_request_reference": dispatch["execution_request_reference"],
        "request_type": dispatch["request_type"],
        "capability_id": dispatch["capability_id"],
        "payload_reference": "EXECUTION-REQUEST-PAYLOAD-RESULT-000001",
        "payload_hash": "sha256:payload-result-000001",
        "allowed_effects": ["RECORD_EXECUTION_START", "RECORD_COMPLETION", "CAPTURE_RESULT"],
        "forbidden_effects": ["CERTIFY_RESULT", "APPROVE_RESULT", "ANALYZE_FAILURE"],
    }


def _invocation(tmp_path, *, assignment_capture: dict, dispatch_capture: dict) -> dict:
    return invoke_worker(
        worker_invocation_id="WORKER-INVOCATION-RESULT-000001",
        dispatch_artifact=dispatch_capture["dispatch_artifact"],
        dispatch_replay=dispatch_capture["dispatch_replay"],
        worker_assignment_artifact=assignment_capture["worker_assignment_artifact"],
        canonical_chain_id=CANONICAL_CHAIN_ID,
        invocation_parameters=_parameters(dispatch_capture),
        invoked_by="AIGOL",
        invoked_at=CREATED_AT,
        replay_reference="REPLAY-WORKER-INVOCATION-RESULT-000001",
        replay_dir=tmp_path / "invocation",
    )


def _execution(tmp_path, *, assignment_capture: dict, dispatch_capture: dict, invocation_capture: dict) -> dict:
    return start_execution(
        execution_id="EXECUTION-RESULT-000001",
        invocation_artifact=invocation_capture["worker_invocation_artifact"],
        invocation_replay=invocation_capture["worker_invocation_replay"],
        dispatch_artifact=dispatch_capture["dispatch_artifact"],
        worker_assignment_artifact=assignment_capture["worker_assignment_artifact"],
        canonical_chain_id=CANONICAL_CHAIN_ID,
        execution_metadata={
            "execution_mode": "RESULT_CAPTURE_CHAIN",
            "runtime_boundary": "RESULT_RUNTIME_V1_PRECONDITION",
        },
        execution_context={
            "worker_reference": invocation_capture["worker_invocation_artifact"]["worker_reference"],
            "request_type": invocation_capture["worker_invocation_artifact"]["request_type"],
            "capability_id": invocation_capture["worker_invocation_artifact"]["capability_id"],
        },
        started_by="AIGOL",
        started_at=CREATED_AT,
        replay_reference="REPLAY-EXECUTION-RESULT-000001",
        replay_dir=tmp_path / "execution",
    )


def _completion(
    tmp_path,
    *,
    assignment_capture: dict,
    dispatch_capture: dict,
    invocation_capture: dict,
    execution_capture: dict,
) -> dict:
    return complete_execution(
        completion_id="COMPLETION-RESULT-000001",
        execution_artifact=execution_capture["execution_artifact"],
        execution_replay=execution_capture["execution_replay"],
        invocation_artifact=invocation_capture["worker_invocation_artifact"],
        dispatch_artifact=dispatch_capture["dispatch_artifact"],
        worker_assignment_artifact=assignment_capture["worker_assignment_artifact"],
        canonical_chain_id=CANONICAL_CHAIN_ID,
        completion_metadata={
            "completion_mode": "RESULT_CAPTURE_PRECONDITION",
            "result_handling": "OUT_OF_SCOPE_BEFORE_RESULT_RUNTIME",
        },
        completed_by="AIGOL",
        completed_at=CREATED_AT,
        replay_reference="REPLAY-COMPLETION-RESULT-000001",
        replay_dir=tmp_path / "completion",
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
    completion_capture = _completion(
        tmp_path,
        assignment_capture=assignment_capture,
        dispatch_capture=dispatch_capture,
        invocation_capture=invocation_capture,
        execution_capture=execution_capture,
    )
    worker_output = inspect_replay_worker(
        inspection_id="REPLAY-INSPECTION-RESULT-000001",
        worker_id="WORKER-RESULT-000001",
        canonical_chain_id=CANONICAL_CHAIN_ID,
        replay_references=[tmp_path / "completion"],
        inspection_scope="CHAIN_SUMMARY",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "worker_output",
    )["replay_inspection_report"]
    return {
        "assignment_capture": assignment_capture,
        "dispatch_capture": dispatch_capture,
        "invocation_capture": invocation_capture,
        "execution_capture": execution_capture,
        "completion_capture": completion_capture,
        "worker_output": worker_output,
    }


def _result(tmp_path, **overrides) -> dict:
    chain = overrides.pop("chain", None)
    if chain is None:
        chain = _chain(tmp_path)
    args = {
        "result_id": "RESULT-000001",
        "completion_artifact": chain["completion_capture"]["completion_artifact"],
        "completion_replay": chain["completion_capture"]["completion_replay"],
        "execution_artifact": chain["execution_capture"]["execution_artifact"],
        "worker_output": chain["worker_output"],
        "canonical_chain_id": CANONICAL_CHAIN_ID,
        "captured_by": "AIGOL",
        "captured_at": CREATED_AT,
        "replay_reference": "REPLAY-RESULT-000001",
        "replay_dir": tmp_path / "result",
    }
    args.update(overrides)
    return capture_result(**args)


def test_result_runtime_captures_worker_output_as_replay_visible_result(tmp_path) -> None:
    chain = _chain(tmp_path)
    capture = _result(tmp_path, chain=chain)
    result = capture["result_artifact"]
    returned = capture["result_replay"]
    reconstructed = reconstruct_result_replay(tmp_path / "result")

    assert result["artifact_type"] == RESULT_ARTIFACT_V1
    assert result["result_status"] == RESULT_CAPTURED
    assert result["canonical_chain_id"] == CANONICAL_CHAIN_ID
    assert result["execution_reference"] == "EXECUTION-RESULT-000001"
    assert result["completion_reference"] == "COMPLETION-RESULT-000001"
    assert result["worker_reference"] == "WORKER-RESULT-000001"
    assert result["worker_output_reference"] == "REPLAY-INSPECTION-RESULT-000001"
    assert result["worker_output_hash"] == chain["worker_output"]["artifact_hash"]
    assert result["result_quality_evaluated"] is False
    assert result["result_approved"] is False
    assert result["result_certified"] is False
    assert result["failure_analysis_performed"] is False
    assert result["reflection_performed"] is False
    assert result["self_improvement_performed"] is False
    assert returned["event_type"] == RESULT_RETURNED
    assert reconstructed["result_status"] == RESULT_CAPTURED
    assert reconstructed["result_certified"] is False


def test_result_runtime_persists_replay_events(tmp_path) -> None:
    _result(tmp_path)

    captured = tmp_path / "result" / "000_result_captured.json"
    returned = tmp_path / "result" / "001_result_returned.json"
    assert captured.exists()
    assert returned.exists()
    assert json.loads(captured.read_text(encoding="utf-8"))["event_type"] == RESULT_RECORDED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == RESULT_RETURNED


def test_invalid_completion_fails_closed(tmp_path) -> None:
    chain = _chain(tmp_path)
    completion = chain["completion_capture"]["completion_artifact"]
    completion["completion_status"] = "CANCELLED"
    completion.pop("artifact_hash")
    completion["artifact_hash"] = replay_hash(completion)

    with pytest.raises(FailClosedRuntimeError, match="invalid completion"):
        _result(tmp_path, chain=chain)


def test_invalid_execution_fails_closed(tmp_path) -> None:
    chain = _chain(tmp_path)
    execution = chain["execution_capture"]["execution_artifact"]
    execution["execution_status"] = "CANCELLED"
    execution.pop("artifact_hash")
    execution["artifact_hash"] = replay_hash(execution)

    with pytest.raises(FailClosedRuntimeError, match="invalid execution"):
        _result(tmp_path, chain=chain)


def test_worker_mismatch_fails_closed(tmp_path) -> None:
    chain = _chain(tmp_path)
    output = chain["worker_output"]
    output["worker_id"] = "OTHER-WORKER"
    output.pop("artifact_hash")
    output["artifact_hash"] = replay_hash(output)

    with pytest.raises(FailClosedRuntimeError, match="worker mismatch"):
        _result(tmp_path, chain=chain)


def test_chain_mismatch_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        _result(tmp_path, canonical_chain_id="CHAIN-OTHER")


def test_duplicate_result_fails_closed(tmp_path) -> None:
    _result(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _result(tmp_path)


def test_corrupt_completion_replay_fails_closed(tmp_path) -> None:
    chain = _chain(tmp_path)
    replay = chain["completion_capture"]["completion_replay"]
    replay["worker_reference"] = "OTHER-WORKER"
    replay.pop("artifact_hash")
    replay["artifact_hash"] = replay_hash(replay)

    with pytest.raises(FailClosedRuntimeError, match="worker mismatch"):
        _result(tmp_path, chain=chain)


def test_authority_bearing_worker_output_fails_closed(tmp_path) -> None:
    chain = _chain(tmp_path)
    output = chain["worker_output"]
    output["result_certification"] = "CERTIFIED"
    output.pop("artifact_hash")
    output["artifact_hash"] = replay_hash(output)

    with pytest.raises(FailClosedRuntimeError, match="authority-bearing worker output"):
        _result(tmp_path, chain=chain)


def test_replay_reconstruction_detects_result_corruption(tmp_path) -> None:
    _result(tmp_path)
    path = tmp_path / "result" / "000_result_captured.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["result_certified"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_result_replay(tmp_path / "result")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _result(tmp_path)
    path = tmp_path / "result" / "001_result_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "result_captured"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_result_replay(tmp_path / "result")


def test_replay_reconstruction_detects_chain_mismatch(tmp_path) -> None:
    _result(tmp_path)
    path = tmp_path / "result" / "001_result_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["canonical_chain_id"] = "CHAIN-OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        reconstruct_result_replay(tmp_path / "result")


def test_no_quality_approval_failure_reflection_or_process_surface_imports() -> None:
    import aigol.runtime.result_runtime as result_runtime

    source = inspect.getsource(result_runtime)

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
