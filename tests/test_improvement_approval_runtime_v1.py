"""Tests for IMPROVEMENT_APPROVAL_RUNTIME_V1."""

from __future__ import annotations

import importlib.util
import inspect
import json
from pathlib import Path

import pytest

from aigol.runtime.improvement_approval_runtime import (
    APPROVED,
    IMPROVEMENT_APPROVAL_ARTIFACT_V1,
    IMPROVEMENT_APPROVAL_RECORDED,
    IMPROVEMENT_APPROVAL_RETURNED,
    REJECTED,
    decide_improvement_approval,
    reconstruct_improvement_approval_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


_HELPERS_PATH = Path(__file__).with_name("test_improvement_review_runtime_v1.py")
_HELPERS_SPEC = importlib.util.spec_from_file_location("improvement_review_runtime_v1_helpers", _HELPERS_PATH)
assert _HELPERS_SPEC is not None
_HELPERS = importlib.util.module_from_spec(_HELPERS_SPEC)
assert _HELPERS_SPEC.loader is not None
_HELPERS_SPEC.loader.exec_module(_HELPERS)

CREATED_AT = _HELPERS.CREATED_AT
CANONICAL_CHAIN_ID = _HELPERS.CANONICAL_CHAIN_ID


def _review_and_proposal(tmp_path) -> tuple[dict, dict]:
    proposal = _HELPERS._proposal_artifact(tmp_path)
    review = _HELPERS._review(tmp_path, improvement_proposal_artifact=proposal)["improvement_review_artifact"]
    return review, proposal


def _approval(tmp_path, **overrides) -> dict:
    review, proposal = overrides.pop("review_and_proposal", (None, None))
    if review is None or proposal is None:
        review, proposal = _review_and_proposal(tmp_path)
    args = {
        "improvement_approval_id": "IMPROVEMENT-APPROVAL-000001",
        "improvement_review_artifact": review,
        "improvement_proposal_artifact": proposal,
        "canonical_chain_id": CANONICAL_CHAIN_ID,
        "decision": APPROVED,
        "decision_reason": "Human authority approves future implementation planning only.",
        "human_authorization_reference": "HUMAN-AUTH-IMPROVEMENT-APPROVAL-000001",
        "recorded_by": "AIGOL",
        "recorded_at": CREATED_AT,
        "replay_reference": "REPLAY-IMPROVEMENT-APPROVAL-000001",
        "replay_dir": tmp_path / "improvement_approval",
    }
    args.update(overrides)
    return decide_improvement_approval(**args)


def test_improvement_approval_runtime_creates_approved_artifact(tmp_path) -> None:
    review, proposal = _review_and_proposal(tmp_path)
    capture = _approval(tmp_path, review_and_proposal=(review, proposal))
    approval = capture["improvement_approval_artifact"]
    returned = capture["improvement_approval_replay"]
    reconstructed = reconstruct_improvement_approval_replay(tmp_path / "improvement_approval")

    assert approval["artifact_type"] == IMPROVEMENT_APPROVAL_ARTIFACT_V1
    assert approval["decision"] == APPROVED
    assert approval["approval_status"] == APPROVED
    assert approval["decision_authority"] == "HUMAN"
    assert approval["recorded_by"] == "AIGOL"
    assert approval["implementation_authorized"] is True
    assert approval["implementation_reference"] is None
    assert approval["implementation_performed"] is False
    assert approval["execution_requested"] is False
    assert approval["worker_dispatched"] is False
    assert approval["worker_invoked"] is False
    assert approval["governance_mutated"] is False
    assert approval["replay_mutated"] is False
    assert approval["improvement_review_reference"] == review["improvement_review_id"]
    assert approval["improvement_proposal_reference"] == proposal["improvement_proposal_id"]
    assert returned["event_type"] == IMPROVEMENT_APPROVAL_RETURNED
    assert reconstructed["decision"] == APPROVED
    assert reconstructed["implementation_authorized"] is True
    assert reconstructed["execution_requested"] is False


def test_improvement_approval_runtime_creates_rejected_artifact(tmp_path) -> None:
    capture = _approval(
        tmp_path,
        decision=REJECTED,
        decision_reason="Human authority rejects future implementation planning.",
    )
    approval = capture["improvement_approval_artifact"]
    reconstructed = reconstruct_improvement_approval_replay(tmp_path / "improvement_approval")

    assert approval["decision"] == REJECTED
    assert approval["approval_status"] == REJECTED
    assert approval["implementation_authorized"] is False
    assert reconstructed["decision"] == REJECTED
    assert reconstructed["implementation_authorized"] is False


def test_improvement_approval_runtime_persists_replay_events(tmp_path) -> None:
    _approval(tmp_path)

    recorded = tmp_path / "improvement_approval" / "000_improvement_approval_recorded.json"
    returned = tmp_path / "improvement_approval" / "001_improvement_approval_returned.json"
    assert recorded.exists()
    assert returned.exists()
    assert json.loads(recorded.read_text(encoding="utf-8"))["event_type"] == IMPROVEMENT_APPROVAL_RECORDED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == IMPROVEMENT_APPROVAL_RETURNED


def test_invalid_review_fails_closed(tmp_path) -> None:
    review, proposal = _review_and_proposal(tmp_path)
    review["review_status"] = "PENDING"
    review.pop("artifact_hash")
    review["artifact_hash"] = replay_hash(review)

    with pytest.raises(FailClosedRuntimeError, match="invalid review"):
        _approval(tmp_path, review_and_proposal=(review, proposal))


def test_invalid_decision_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="invalid decision"):
        _approval(tmp_path, decision="AUTO_APPROVED")


def test_chain_mismatch_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        _approval(tmp_path, canonical_chain_id="CHAIN-OTHER")


def test_duplicate_approval_fails_closed(tmp_path) -> None:
    _approval(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _approval(tmp_path)


def test_corrupt_review_references_fail_closed(tmp_path) -> None:
    review, proposal = _review_and_proposal(tmp_path)
    review["review_findings_hash"] = "sha256:corrupt-findings"
    review.pop("artifact_hash")
    review["artifact_hash"] = replay_hash(review)

    with pytest.raises(FailClosedRuntimeError, match="corrupt references"):
        _approval(tmp_path, review_and_proposal=(review, proposal))


def test_mismatched_proposal_reference_fails_closed(tmp_path) -> None:
    review, proposal = _review_and_proposal(tmp_path)
    proposal["improvement_proposal_id"] = "OTHER-PROPOSAL"
    proposal.pop("artifact_hash")
    proposal["artifact_hash"] = replay_hash(proposal)

    with pytest.raises(FailClosedRuntimeError, match="corrupt references"):
        _approval(tmp_path, review_and_proposal=(review, proposal))


def test_missing_human_authorization_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="human_authorization_reference is required"):
        _approval(tmp_path, human_authorization_reference="")


def test_review_with_implementation_authority_fails_closed(tmp_path) -> None:
    review, proposal = _review_and_proposal(tmp_path)
    review["implementation_authority"] = True
    review.pop("artifact_hash")
    review["artifact_hash"] = replay_hash(review)

    with pytest.raises(FailClosedRuntimeError, match="invalid review authority"):
        _approval(tmp_path, review_and_proposal=(review, proposal))


def test_replay_reconstruction_detects_approval_corruption(tmp_path) -> None:
    _approval(tmp_path)
    path = tmp_path / "improvement_approval" / "000_improvement_approval_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["execution_requested"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_improvement_approval_replay(tmp_path / "improvement_approval")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _approval(tmp_path)
    path = tmp_path / "improvement_approval" / "001_improvement_approval_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "improvement_approval_recorded"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_improvement_approval_replay(tmp_path / "improvement_approval")


def test_replay_reconstruction_detects_chain_mismatch(tmp_path) -> None:
    _approval(tmp_path)
    path = tmp_path / "improvement_approval" / "001_improvement_approval_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["canonical_chain_id"] = "CHAIN-OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        reconstruct_improvement_approval_replay(tmp_path / "improvement_approval")


def test_no_implementation_execution_request_or_process_surface_imports() -> None:
    import aigol.runtime.improvement_approval_runtime as improvement_approval_runtime

    source = inspect.getsource(improvement_approval_runtime)

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
