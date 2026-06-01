"""Tests for READY_FOR_DISPATCH_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.execution_request_runtime import create_execution_request
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.proposal_approval_runtime import decide_proposal_approval
from aigol.runtime.proposal_runtime import create_proposal
from aigol.runtime.ready_for_dispatch_runtime import (
    READY_FOR_DISPATCH,
    READY_FOR_DISPATCH_ARTIFACT_V1,
    READY_FOR_DISPATCH_RETURNED,
    READY_FOR_DISPATCH_VALIDATED,
    mark_ready_for_dispatch,
    reconstruct_ready_for_dispatch_replay,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-01T08:00:00+00:00"
_MISSING = object()


def _proposal(tmp_path, suffix: str = "000001") -> dict:
    return create_proposal(
        proposal_id=f"PROPOSAL-READY-FOR-DISPATCH-{suffix}",
        proposal_type="CAPABILITY_PROPOSAL",
        proposal_source="CONVERSATION",
        proposal_text="Create a bounded candidate for readiness validation.",
        created_at=CREATED_AT,
        replay_reference=f"REPLAY-PROPOSAL-READY-FOR-DISPATCH-{suffix}",
        replay_dir=tmp_path / f"proposal_{suffix}",
    )["proposal_runtime_artifact"]


def _approval(tmp_path, proposal: dict, human_decision: str = "APPROVE", suffix: str = "000001") -> dict:
    return decide_proposal_approval(
        approval_id=f"APPROVAL-READY-FOR-DISPATCH-{human_decision}-{suffix}",
        proposal_artifact=proposal,
        human_decision=human_decision,
        decision_reason="Human operator approves readiness-bound execution request lineage.",
        operator_label="human-operator",
        created_at=CREATED_AT,
        replay_reference=f"REPLAY-APPROVAL-READY-FOR-DISPATCH-{human_decision}-{suffix}",
        replay_dir=tmp_path / f"approval_{human_decision.lower()}_{suffix}",
    )["proposal_approval_artifact"]


def _execution_request(tmp_path, **overrides) -> dict:
    proposal_artifact = overrides.pop("proposal_artifact", _MISSING)
    approval_artifact = overrides.pop("approval_artifact", _MISSING)
    if proposal_artifact is _MISSING:
        proposal_artifact = _proposal(tmp_path)
    if approval_artifact is _MISSING:
        approval_artifact = _approval(tmp_path, proposal_artifact)
    args = {
        "execution_request_id": "EXECUTION-REQUEST-READY-FOR-DISPATCH-000001",
        "proposal_artifact": proposal_artifact,
        "approval_artifact": approval_artifact,
        "requested_by": "AIGOL",
        "created_at": CREATED_AT,
        "request_type": "CAPABILITY_EXECUTION_REQUEST",
        "request_payload": {
            "approved_action": "VALIDATE_READINESS_ONLY",
            "scope": "ready for dispatch validation without worker assignment",
        },
        "replay_reference": "REPLAY-EXECUTION-REQUEST-READY-FOR-DISPATCH-000001",
        "replay_dir": tmp_path / "execution_request",
    }
    args.update(overrides)
    return create_execution_request(**args)


def _readiness(tmp_path, **overrides) -> dict:
    request_capture = overrides.pop("request_capture", _MISSING)
    approval_artifact = overrides.pop("approval_artifact", _MISSING)
    if request_capture is _MISSING:
        proposal = _proposal(tmp_path)
        approval_artifact = _approval(tmp_path, proposal)
        request_capture = _execution_request(
            tmp_path,
            proposal_artifact=proposal,
            approval_artifact=approval_artifact,
        )
    elif approval_artifact is _MISSING:
        raise AssertionError("approval_artifact is required when request_capture is supplied")
    args = {
        "readiness_id": "READY-FOR-DISPATCH-000001",
        "execution_request_artifact": request_capture["execution_request_artifact"],
        "execution_request_replay": request_capture["execution_request_replay"],
        "approval_artifact": approval_artifact,
        "validated_at": CREATED_AT,
        "replay_reference": "REPLAY-READY-FOR-DISPATCH-000001",
        "replay_dir": tmp_path / "readiness",
    }
    args.update(overrides)
    return mark_ready_for_dispatch(**args)


def test_readiness_marks_created_execution_request_ready_for_dispatch(tmp_path) -> None:
    proposal = _proposal(tmp_path)
    approval = _approval(tmp_path, proposal)
    request_capture = _execution_request(tmp_path, proposal_artifact=proposal, approval_artifact=approval)
    capture = _readiness(tmp_path, request_capture=request_capture, approval_artifact=approval)
    readiness = capture["ready_for_dispatch_artifact"]
    returned = capture["ready_for_dispatch_replay"]
    reconstructed = reconstruct_ready_for_dispatch_replay(tmp_path / "readiness")

    assert readiness["artifact_type"] == READY_FOR_DISPATCH_ARTIFACT_V1
    assert readiness["readiness_status"] == READY_FOR_DISPATCH
    assert readiness["execution_request_reference"] == "EXECUTION-REQUEST-READY-FOR-DISPATCH-000001"
    assert readiness["validated_by"] == "AIGOL"
    assert readiness["provider_authority"] is False
    assert readiness["worker_assigned"] is False
    assert readiness["worker_dispatched"] is False
    assert readiness["worker_invoked"] is False
    assert readiness["execution_performed"] is False
    assert returned["event_type"] == READY_FOR_DISPATCH_RETURNED
    assert reconstructed["status"] == READY_FOR_DISPATCH
    assert reconstructed["worker_assigned"] is False
    assert reconstructed["execution_performed"] is False


def test_readiness_persists_replay_events(tmp_path) -> None:
    _readiness(tmp_path)

    validated = tmp_path / "readiness" / "000_ready_for_dispatch_validated.json"
    returned = tmp_path / "readiness" / "001_ready_for_dispatch_returned.json"
    assert validated.exists()
    assert returned.exists()
    assert json.loads(validated.read_text(encoding="utf-8"))["event_type"] == READY_FOR_DISPATCH_VALIDATED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == READY_FOR_DISPATCH_RETURNED


def test_missing_execution_request_fails_closed(tmp_path) -> None:
    proposal = _proposal(tmp_path)
    approval = _approval(tmp_path, proposal)
    request_capture = _execution_request(tmp_path, proposal_artifact=proposal, approval_artifact=approval)

    with pytest.raises(FailClosedRuntimeError, match="execution request is required"):
        _readiness(
            tmp_path,
            request_capture=request_capture,
            approval_artifact=approval,
            execution_request_artifact=None,
        )


def test_missing_execution_request_replay_fails_closed(tmp_path) -> None:
    proposal = _proposal(tmp_path)
    approval = _approval(tmp_path, proposal)
    request_capture = _execution_request(tmp_path, proposal_artifact=proposal, approval_artifact=approval)

    with pytest.raises(FailClosedRuntimeError, match="execution request replay is required"):
        _readiness(
            tmp_path,
            request_capture=request_capture,
            approval_artifact=approval,
            execution_request_replay=None,
        )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("readiness_id", "", "readiness_id is required"),
        ("validated_by", "PROVIDER", "validated_by must be AIGOL"),
        ("validated_at", "", "validated_at is required"),
        ("replay_reference", "", "replay_reference is required"),
    ],
)
def test_missing_or_invalid_readiness_fields_fail_closed(tmp_path, field: str, value: str, message: str) -> None:
    with pytest.raises(FailClosedRuntimeError, match=message):
        _readiness(tmp_path, **{field: value})


def test_invalid_execution_request_status_fails_closed(tmp_path) -> None:
    proposal = _proposal(tmp_path)
    approval = _approval(tmp_path, proposal)
    request_capture = _execution_request(tmp_path, proposal_artifact=proposal, approval_artifact=approval)
    request_capture["execution_request_artifact"]["status"] = READY_FOR_DISPATCH
    request_capture["execution_request_artifact"].pop("artifact_hash")
    request_capture["execution_request_artifact"]["artifact_hash"] = replay_hash(
        request_capture["execution_request_artifact"]
    )

    with pytest.raises(FailClosedRuntimeError, match="invalid execution request status"):
        _readiness(tmp_path, request_capture=request_capture, approval_artifact=approval)


def test_approval_mismatch_fails_closed(tmp_path) -> None:
    proposal = _proposal(tmp_path)
    approval = _approval(tmp_path, proposal)
    request_capture = _execution_request(tmp_path, proposal_artifact=proposal, approval_artifact=approval)
    other_proposal = _proposal(tmp_path, suffix="000002")
    other_approval = _approval(tmp_path, other_proposal, suffix="000002")

    with pytest.raises(FailClosedRuntimeError, match="approval reference mismatch"):
        _readiness(tmp_path, request_capture=request_capture, approval_artifact=other_approval)


def test_non_approved_approval_fails_closed(tmp_path) -> None:
    proposal = _proposal(tmp_path)
    rejected = _approval(tmp_path, proposal, human_decision="REJECT")
    approved = _approval(tmp_path, proposal, human_decision="APPROVE", suffix="000002")
    request_capture = _execution_request(tmp_path, proposal_artifact=proposal, approval_artifact=approved)
    rejected["approval_id"] = request_capture["execution_request_artifact"]["approval_reference"]
    rejected["proposal_hash"] = request_capture["execution_request_artifact"]["proposal_hash"]
    rejected.pop("artifact_hash")
    rejected["artifact_hash"] = request_capture["execution_request_artifact"]["approval_hash"]

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        _readiness(tmp_path, request_capture=request_capture, approval_artifact=rejected)


def test_corrupt_execution_request_fails_closed(tmp_path) -> None:
    proposal = _proposal(tmp_path)
    approval = _approval(tmp_path, proposal)
    request_capture = _execution_request(tmp_path, proposal_artifact=proposal, approval_artifact=approval)
    request_capture["execution_request_artifact"]["request_payload"]["approved_action"] = "tampered"

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        _readiness(tmp_path, request_capture=request_capture, approval_artifact=approval)


def test_corrupt_execution_request_replay_fails_closed(tmp_path) -> None:
    proposal = _proposal(tmp_path)
    approval = _approval(tmp_path, proposal)
    request_capture = _execution_request(tmp_path, proposal_artifact=proposal, approval_artifact=approval)
    request_capture["execution_request_replay"]["execution_request_reference"] = "OTHER"
    request_capture["execution_request_replay"].pop("artifact_hash")
    request_capture["execution_request_replay"]["artifact_hash"] = replay_hash(
        request_capture["execution_request_replay"]
    )

    with pytest.raises(FailClosedRuntimeError, match="reference mismatch"):
        _readiness(tmp_path, request_capture=request_capture, approval_artifact=approval)


def test_duplicate_readiness_replay_fails_closed(tmp_path) -> None:
    _readiness(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _readiness(tmp_path)


def test_replay_reconstruction_detects_artifact_corruption(tmp_path) -> None:
    _readiness(tmp_path)
    path = tmp_path / "readiness" / "000_ready_for_dispatch_validated.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_dispatched"] = True
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_ready_for_dispatch_replay(tmp_path / "readiness")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _readiness(tmp_path)
    path = tmp_path / "readiness" / "001_ready_for_dispatch_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "ready_for_dispatch_validated"
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_ready_for_dispatch_replay(tmp_path / "readiness")


def test_replay_reconstruction_detects_reference_mismatch(tmp_path) -> None:
    _readiness(tmp_path)
    path = tmp_path / "readiness" / "001_ready_for_dispatch_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["readiness_reference"] = "OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="reference mismatch"):
        reconstruct_ready_for_dispatch_replay(tmp_path / "readiness")


def test_no_worker_dispatch_or_execution_surface_imports() -> None:
    import aigol.runtime.ready_for_dispatch_runtime as ready_for_dispatch_runtime

    source = inspect.getsource(ready_for_dispatch_runtime)

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
