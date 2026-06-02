"""Tests for RESULT_EVALUATION_RUNTIME_V1."""

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
from aigol.runtime.result_evaluation_runtime import (
    EVALUATED,
    RESULT_EVALUATION_ARTIFACT_V1,
    RESULT_EVALUATION_RECORDED,
    RESULT_EVALUATION_RETURNED,
    evaluate_result,
    reconstruct_result_evaluation_replay,
)
from aigol.runtime.result_runtime import capture_result
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from aigol.runtime.worker_invocation_runtime import invoke_worker
from aigol.runtime.worker_runtime import assign_worker, register_worker


CREATED_AT = "2026-06-02T11:00:00+00:00"
CANONICAL_CHAIN_ID = "CHAIN-20260602-RESULT-EVALUATION-000001"


def _proposal(tmp_path) -> dict:
    return create_proposal(
        proposal_id="PROPOSAL-RESULT-EVALUATION-000001",
        proposal_type="CAPABILITY_PROPOSAL",
        proposal_source="CONVERSATION",
        proposal_text="Evaluate a captured replay inspector result.",
        created_at=CREATED_AT,
        replay_reference="REPLAY-PROPOSAL-RESULT-EVALUATION-000001",
        replay_dir=tmp_path / "proposal",
    )["proposal_runtime_artifact"]


def _approval(tmp_path, proposal: dict) -> dict:
    return decide_proposal_approval(
        approval_id="APPROVAL-RESULT-EVALUATION-000001",
        proposal_artifact=proposal,
        human_decision="APPROVE",
        decision_reason="Human operator approves result evaluation lineage.",
        operator_label="human-operator",
        created_at=CREATED_AT,
        replay_reference="REPLAY-APPROVAL-RESULT-EVALUATION-000001",
        replay_dir=tmp_path / "approval",
    )["proposal_approval_artifact"]


def _execution_request(tmp_path, proposal: dict, approval: dict) -> dict:
    return create_execution_request(
        execution_request_id="EXECUTION-REQUEST-RESULT-EVALUATION-000001",
        proposal_artifact=proposal,
        approval_artifact=approval,
        requested_by="AIGOL",
        created_at=CREATED_AT,
        request_type="CAPABILITY_EXECUTION_REQUEST",
        request_payload={
            "approved_action": "EVALUATE_RESULT_ONLY",
            "scope": "result evaluation without approval or implementation",
        },
        replay_reference="REPLAY-EXECUTION-REQUEST-RESULT-EVALUATION-000001",
        replay_dir=tmp_path / "execution_request",
    )


def _readiness(tmp_path) -> dict:
    proposal = _proposal(tmp_path)
    approval = _approval(tmp_path, proposal)
    request_capture = _execution_request(tmp_path, proposal, approval)
    return mark_ready_for_dispatch(
        readiness_id="READY-FOR-DISPATCH-RESULT-EVALUATION-000001",
        execution_request_artifact=request_capture["execution_request_artifact"],
        execution_request_replay=request_capture["execution_request_replay"],
        approval_artifact=approval,
        validated_at=CREATED_AT,
        replay_reference="REPLAY-READY-FOR-DISPATCH-RESULT-EVALUATION-000001",
        replay_dir=tmp_path / "readiness",
    )


def _worker(tmp_path) -> dict:
    return register_worker(
        worker_id="WORKER-RESULT-EVALUATION-000001",
        worker_type="REPLAY_INSPECTOR_WORKER_V1",
        worker_version="1.0.0",
        declared_capabilities=["REPLAY_INSPECTION_READ_ONLY"],
        supported_request_types=["CAPABILITY_EXECUTION_REQUEST"],
        trust_boundary="LOCAL_BOUNDED_WORKER",
        created_at=CREATED_AT,
        replay_reference="REPLAY-WORKER-RESULT-EVALUATION-000001",
        replay_dir=tmp_path / "worker",
    )


def _assignment(tmp_path) -> dict:
    readiness_capture = _readiness(tmp_path)
    worker_capture = _worker(tmp_path)
    capture = assign_worker(
        worker_assignment_id="WORKER-ASSIGNMENT-RESULT-EVALUATION-000001",
        worker_artifact=worker_capture["worker_artifact"],
        readiness_artifact=readiness_capture["ready_for_dispatch_artifact"],
        readiness_replay=readiness_capture["ready_for_dispatch_replay"],
        assigned_by="AIGOL",
        assigned_at=CREATED_AT,
        canonical_chain_id=CANONICAL_CHAIN_ID,
        replay_reference="REPLAY-WORKER-ASSIGNMENT-RESULT-EVALUATION-000001",
        replay_dir=tmp_path / "assignment",
    )
    capture["_readiness_capture"] = readiness_capture
    return capture


def _dispatch(tmp_path, assignment_capture: dict) -> dict:
    return dispatch_worker(
        dispatch_id="DISPATCH-RESULT-EVALUATION-000001",
        worker_assignment_artifact=assignment_capture["worker_assignment_artifact"],
        worker_assignment_replay=assignment_capture["worker_assignment_replay"],
        readiness_artifact=assignment_capture["_readiness_capture"]["ready_for_dispatch_artifact"],
        canonical_chain_id=CANONICAL_CHAIN_ID,
        dispatched_by="AIGOL",
        dispatched_at=CREATED_AT,
        replay_reference="REPLAY-DISPATCH-RESULT-EVALUATION-000001",
        replay_dir=tmp_path / "dispatch",
    )


def _invocation(tmp_path, assignment_capture: dict, dispatch_capture: dict) -> dict:
    dispatch = dispatch_capture["dispatch_artifact"]
    return invoke_worker(
        worker_invocation_id="WORKER-INVOCATION-RESULT-EVALUATION-000001",
        dispatch_artifact=dispatch,
        dispatch_replay=dispatch_capture["dispatch_replay"],
        worker_assignment_artifact=assignment_capture["worker_assignment_artifact"],
        canonical_chain_id=CANONICAL_CHAIN_ID,
        invocation_parameters={
            "execution_request_reference": dispatch["execution_request_reference"],
            "request_type": dispatch["request_type"],
            "capability_id": dispatch["capability_id"],
            "payload_reference": "EXECUTION-REQUEST-PAYLOAD-RESULT-EVALUATION-000001",
            "payload_hash": "sha256:payload-result-evaluation-000001",
            "allowed_effects": ["RECORD_EXECUTION_START", "RECORD_COMPLETION", "CAPTURE_RESULT", "EVALUATE_RESULT"],
            "forbidden_effects": ["APPROVE_RESULT", "CREATE_IMPLEMENTATION_PLAN", "SELF_IMPROVE"],
        },
        invoked_by="AIGOL",
        invoked_at=CREATED_AT,
        replay_reference="REPLAY-WORKER-INVOCATION-RESULT-EVALUATION-000001",
        replay_dir=tmp_path / "invocation",
    )


def _execution(tmp_path, assignment_capture: dict, dispatch_capture: dict, invocation_capture: dict) -> dict:
    invocation = invocation_capture["worker_invocation_artifact"]
    return start_execution(
        execution_id="EXECUTION-RESULT-EVALUATION-000001",
        invocation_artifact=invocation,
        invocation_replay=invocation_capture["worker_invocation_replay"],
        dispatch_artifact=dispatch_capture["dispatch_artifact"],
        worker_assignment_artifact=assignment_capture["worker_assignment_artifact"],
        canonical_chain_id=CANONICAL_CHAIN_ID,
        execution_metadata={
            "execution_mode": "RESULT_EVALUATION_CHAIN",
            "runtime_boundary": "RESULT_EVALUATION_RUNTIME_V1_PRECONDITION",
        },
        execution_context={
            "worker_reference": invocation["worker_reference"],
            "request_type": invocation["request_type"],
            "capability_id": invocation["capability_id"],
        },
        started_by="AIGOL",
        started_at=CREATED_AT,
        replay_reference="REPLAY-EXECUTION-RESULT-EVALUATION-000001",
        replay_dir=tmp_path / "execution",
    )


def _completion(
    tmp_path,
    assignment_capture: dict,
    dispatch_capture: dict,
    invocation_capture: dict,
    execution_capture: dict,
) -> dict:
    return complete_execution(
        completion_id="COMPLETION-RESULT-EVALUATION-000001",
        execution_artifact=execution_capture["execution_artifact"],
        execution_replay=execution_capture["execution_replay"],
        invocation_artifact=invocation_capture["worker_invocation_artifact"],
        dispatch_artifact=dispatch_capture["dispatch_artifact"],
        worker_assignment_artifact=assignment_capture["worker_assignment_artifact"],
        canonical_chain_id=CANONICAL_CHAIN_ID,
        completion_metadata={
            "completion_mode": "RESULT_EVALUATION_PRECONDITION",
            "evaluation_handling": "OUT_OF_SCOPE_BEFORE_RESULT_EVALUATION_RUNTIME",
        },
        completed_by="AIGOL",
        completed_at=CREATED_AT,
        replay_reference="REPLAY-COMPLETION-RESULT-EVALUATION-000001",
        replay_dir=tmp_path / "completion",
    )


def _result(tmp_path) -> dict:
    assignment_capture = _assignment(tmp_path)
    dispatch_capture = _dispatch(tmp_path, assignment_capture)
    invocation_capture = _invocation(tmp_path, assignment_capture, dispatch_capture)
    execution_capture = _execution(tmp_path, assignment_capture, dispatch_capture, invocation_capture)
    completion_capture = _completion(tmp_path, assignment_capture, dispatch_capture, invocation_capture, execution_capture)
    worker_output = inspect_replay_worker(
        inspection_id="REPLAY-INSPECTION-RESULT-EVALUATION-000001",
        worker_id="WORKER-RESULT-EVALUATION-000001",
        canonical_chain_id=CANONICAL_CHAIN_ID,
        replay_references=[tmp_path / "completion"],
        inspection_scope="CHAIN_SUMMARY",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "worker_output",
    )["replay_inspection_report"]
    return capture_result(
        result_id="RESULT-EVALUATION-INPUT-000001",
        completion_artifact=completion_capture["completion_artifact"],
        completion_replay=completion_capture["completion_replay"],
        execution_artifact=execution_capture["execution_artifact"],
        worker_output=worker_output,
        canonical_chain_id=CANONICAL_CHAIN_ID,
        captured_by="AIGOL",
        captured_at=CREATED_AT,
        replay_reference="REPLAY-RESULT-EVALUATION-INPUT-000001",
        replay_dir=tmp_path / "result",
    )["result_artifact"]


def _observations() -> dict:
    return {
        "completeness_notes": "Result output is present and hash-bound.",
        "traceability_notes": "Result references execution, completion, and worker identity.",
        "replay_integrity_notes": "Result replay is available for reconstruction.",
        "limitation_notes": "Evaluation records observations only.",
    }


def _evaluation(tmp_path, **overrides) -> dict:
    result = overrides.pop("result_artifact", None)
    if result is None:
        result = _result(tmp_path)
    args = {
        "evaluation_id": "RESULT-EVALUATION-000001",
        "result_artifact": result,
        "canonical_chain_id": CANONICAL_CHAIN_ID,
        "evaluator_reference": "AIGOL-DETERMINISTIC-EVALUATOR-V1",
        "evaluation_source": "AIGOL_DETERMINISTIC",
        "evaluation_method": "CHAIN_AND_REPLAY_OBSERVATION_REVIEW",
        "evaluation_observations": _observations(),
        "improvement_recommended": True,
        "improvement_proposal_reference": None,
        "evaluated_by": "AIGOL",
        "evaluated_at": CREATED_AT,
        "replay_reference": "REPLAY-RESULT-EVALUATION-000001",
        "replay_dir": tmp_path / "evaluation",
    }
    args.update(overrides)
    return evaluate_result(**args)


def test_result_evaluation_runtime_creates_replay_visible_artifact(tmp_path) -> None:
    result = _result(tmp_path)
    capture = _evaluation(tmp_path, result_artifact=result)
    evaluation = capture["result_evaluation_artifact"]
    returned = capture["result_evaluation_replay"]
    reconstructed = reconstruct_result_evaluation_replay(tmp_path / "evaluation")

    assert evaluation["artifact_type"] == RESULT_EVALUATION_ARTIFACT_V1
    assert evaluation["evaluation_status"] == EVALUATED
    assert evaluation["canonical_chain_id"] == CANONICAL_CHAIN_ID
    assert evaluation["result_reference"] == result["result_id"]
    assert evaluation["result_hash"] == result["artifact_hash"]
    assert evaluation["worker_reference"] == "WORKER-RESULT-EVALUATION-000001"
    assert evaluation["improvement_recommended"] is True
    assert evaluation["improvement_proposal_reference"] is None
    assert evaluation["approval_authority"] is False
    assert evaluation["result_approved"] is False
    assert evaluation["implementation_plan_created"] is False
    assert evaluation["self_improvement_performed"] is False
    assert returned["event_type"] == RESULT_EVALUATION_RETURNED
    assert reconstructed["evaluation_status"] == EVALUATED
    assert reconstructed["implementation_plan_created"] is False


def test_result_evaluation_runtime_persists_replay_events(tmp_path) -> None:
    _evaluation(tmp_path)

    recorded = tmp_path / "evaluation" / "000_result_evaluation_recorded.json"
    returned = tmp_path / "evaluation" / "001_result_evaluation_returned.json"
    assert recorded.exists()
    assert returned.exists()
    assert json.loads(recorded.read_text(encoding="utf-8"))["event_type"] == RESULT_EVALUATION_RECORDED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == RESULT_EVALUATION_RETURNED


def test_invalid_result_fails_closed(tmp_path) -> None:
    result = _result(tmp_path)
    result["result_status"] = "CERTIFIED"
    result.pop("artifact_hash")
    result["artifact_hash"] = replay_hash(result)

    with pytest.raises(FailClosedRuntimeError, match="invalid result"):
        _evaluation(tmp_path, result_artifact=result)


def test_chain_mismatch_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        _evaluation(tmp_path, canonical_chain_id="CHAIN-OTHER")


def test_duplicate_evaluation_fails_closed(tmp_path) -> None:
    _evaluation(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _evaluation(tmp_path)


def test_corrupt_result_reference_fails_closed(tmp_path) -> None:
    result = _result(tmp_path)
    result["worker_output_hash"] = "sha256:corrupt-worker-output"
    result.pop("artifact_hash")
    result["artifact_hash"] = replay_hash(result)

    with pytest.raises(FailClosedRuntimeError, match="corrupt references"):
        _evaluation(tmp_path, result_artifact=result)


def test_invalid_evaluation_source_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="invalid evaluation source"):
        _evaluation(tmp_path, evaluation_source="WORKER_AUTHORITY")


def test_authority_bearing_observations_fail_closed(tmp_path) -> None:
    observations = _observations()
    observations["result_approval"] = "APPROVED"

    with pytest.raises(FailClosedRuntimeError, match="authority-bearing observations"):
        _evaluation(tmp_path, evaluation_observations=observations)


def test_improvement_proposal_reference_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="proposal creation is out of scope"):
        _evaluation(tmp_path, improvement_proposal_reference="IMPROVEMENT-PROPOSAL-000001")


def test_replay_reconstruction_detects_evaluation_corruption(tmp_path) -> None:
    _evaluation(tmp_path)
    path = tmp_path / "evaluation" / "000_result_evaluation_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["result_approved"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_result_evaluation_replay(tmp_path / "evaluation")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _evaluation(tmp_path)
    path = tmp_path / "evaluation" / "001_result_evaluation_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "result_evaluation_recorded"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_result_evaluation_replay(tmp_path / "evaluation")


def test_replay_reconstruction_detects_chain_mismatch(tmp_path) -> None:
    _evaluation(tmp_path)
    path = tmp_path / "evaluation" / "001_result_evaluation_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["canonical_chain_id"] = "CHAIN-OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        reconstruct_result_evaluation_replay(tmp_path / "evaluation")


def test_no_approval_implementation_reflection_or_process_surface_imports() -> None:
    import aigol.runtime.result_evaluation_runtime as result_evaluation_runtime

    source = inspect.getsource(result_evaluation_runtime)

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
