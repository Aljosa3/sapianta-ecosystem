"""Tests for IMPROVEMENT_REVIEW_RUNTIME_V1."""

from __future__ import annotations

import importlib.util
import inspect
import json
from pathlib import Path

import pytest

from aigol.runtime.improvement_review_runtime import (
    IMPROVEMENT_REVIEW_ARTIFACT_V1,
    IMPROVEMENT_REVIEW_RECORDED,
    IMPROVEMENT_REVIEW_RETURNED,
    IMPROVEMENT_REVIEWED,
    reconstruct_improvement_review_replay,
    review_improvement_proposal,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


_HELPERS_PATH = Path(__file__).with_name("test_improvement_proposal_runtime_v1.py")
_HELPERS_SPEC = importlib.util.spec_from_file_location("improvement_proposal_runtime_v1_helpers", _HELPERS_PATH)
assert _HELPERS_SPEC is not None
_HELPERS = importlib.util.module_from_spec(_HELPERS_SPEC)
assert _HELPERS_SPEC.loader is not None
_HELPERS_SPEC.loader.exec_module(_HELPERS)

CREATED_AT = _HELPERS.CREATED_AT
CANONICAL_CHAIN_ID = _HELPERS.CANONICAL_CHAIN_ID


def _proposal_artifact(tmp_path) -> dict:
    return _HELPERS._proposal(tmp_path)["improvement_proposal_artifact"]


def _criteria() -> dict:
    return {
        "proposal_completeness": "required",
        "evidence_sufficiency": "required",
        "scope_bounded": "required",
        "approval_boundary_preserved": "required",
        "implementation_boundary_preserved": "required",
    }


def _findings() -> dict:
    return {
        "proposal_completeness_notes": "Proposal includes text, reason, scope, and constraints.",
        "evidence_sufficiency_notes": "Proposal references evaluation and result evidence.",
        "scope_and_constraint_notes": "Implementation remains out of scope.",
        "approval_readiness_recommendation": "Ready for future human approval review.",
        "known_gaps": ["Review is not approval.", "Implementation remains future-governed."],
    }


def _review(tmp_path, **overrides) -> dict:
    proposal = overrides.pop("improvement_proposal_artifact", None)
    if proposal is None:
        proposal = _proposal_artifact(tmp_path)
    args = {
        "improvement_review_id": "IMPROVEMENT-REVIEW-000001",
        "improvement_proposal_artifact": proposal,
        "canonical_chain_id": CANONICAL_CHAIN_ID,
        "review_source": "AIGOL_DETERMINISTIC_REVIEW",
        "review_method": "PROPOSAL_BOUNDARY_AND_EVIDENCE_REVIEW",
        "review_criteria": _criteria(),
        "review_findings": _findings(),
        "approval_recommended": True,
        "reviewed_by": "AIGOL",
        "reviewed_at": CREATED_AT,
        "replay_reference": "REPLAY-IMPROVEMENT-REVIEW-000001",
        "replay_dir": tmp_path / "improvement_review",
    }
    args.update(overrides)
    return review_improvement_proposal(**args)


def test_improvement_review_runtime_creates_replay_visible_review(tmp_path) -> None:
    proposal = _proposal_artifact(tmp_path)
    capture = _review(tmp_path, improvement_proposal_artifact=proposal)
    review = capture["improvement_review_artifact"]
    returned = capture["improvement_review_replay"]
    reconstructed = reconstruct_improvement_review_replay(tmp_path / "improvement_review")

    assert review["artifact_type"] == IMPROVEMENT_REVIEW_ARTIFACT_V1
    assert review["review_status"] == IMPROVEMENT_REVIEWED
    assert review["canonical_chain_id"] == CANONICAL_CHAIN_ID
    assert review["improvement_proposal_reference"] == proposal["improvement_proposal_id"]
    assert review["improvement_proposal_hash"] == proposal["artifact_hash"]
    assert review["evaluation_reference"] == proposal["evaluation_reference"]
    assert review["result_reference"] == proposal["result_reference"]
    assert review["worker_reference"] == proposal["worker_reference"]
    assert review["approval_recommended"] is True
    assert review["approval_reference"] is None
    assert review["approval_authority"] is False
    assert review["proposal_approved"] is False
    assert review["proposal_rejected"] is False
    assert review["implementation_authorized"] is False
    assert review["execution_requested"] is False
    assert returned["event_type"] == IMPROVEMENT_REVIEW_RETURNED
    assert reconstructed["review_status"] == IMPROVEMENT_REVIEWED
    assert reconstructed["implementation_applied"] is False


def test_improvement_review_runtime_persists_replay_events(tmp_path) -> None:
    _review(tmp_path)

    recorded = tmp_path / "improvement_review" / "000_improvement_review_recorded.json"
    returned = tmp_path / "improvement_review" / "001_improvement_review_returned.json"
    assert recorded.exists()
    assert returned.exists()
    assert json.loads(recorded.read_text(encoding="utf-8"))["event_type"] == IMPROVEMENT_REVIEW_RECORDED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == IMPROVEMENT_REVIEW_RETURNED


def test_invalid_proposal_fails_closed(tmp_path) -> None:
    proposal = _proposal_artifact(tmp_path)
    proposal["proposal_status"] = "APPROVED"
    proposal.pop("artifact_hash")
    proposal["artifact_hash"] = replay_hash(proposal)

    with pytest.raises(FailClosedRuntimeError, match="invalid proposal"):
        _review(tmp_path, improvement_proposal_artifact=proposal)


def test_chain_mismatch_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        _review(tmp_path, canonical_chain_id="CHAIN-OTHER")


def test_duplicate_review_fails_closed(tmp_path) -> None:
    _review(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _review(tmp_path)


def test_corrupt_proposal_references_fail_closed(tmp_path) -> None:
    proposal = _proposal_artifact(tmp_path)
    proposal["proposal_scope_hash"] = "sha256:corrupt-scope"
    proposal.pop("artifact_hash")
    proposal["artifact_hash"] = replay_hash(proposal)

    with pytest.raises(FailClosedRuntimeError, match="corrupt references"):
        _review(tmp_path, improvement_proposal_artifact=proposal)


def test_invalid_review_source_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="invalid review source"):
        _review(tmp_path, review_source="WORKER_AUTHORITY")


def test_authority_bearing_review_findings_fail_closed(tmp_path) -> None:
    findings = _findings()
    findings["proposal_approved"] = True

    with pytest.raises(FailClosedRuntimeError, match="authority-bearing review content"):
        _review(tmp_path, review_findings=findings)


def test_authority_bearing_review_criteria_fail_closed(tmp_path) -> None:
    criteria = _criteria()
    criteria["execution_requested"] = True

    with pytest.raises(FailClosedRuntimeError, match="authority-bearing review content"):
        _review(tmp_path, review_criteria=criteria)


def test_approval_recommendation_must_be_boolean(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="approval recommendation must be boolean"):
        _review(tmp_path, approval_recommended="YES")


def test_replay_reconstruction_detects_review_corruption(tmp_path) -> None:
    _review(tmp_path)
    path = tmp_path / "improvement_review" / "000_improvement_review_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["proposal_approved"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_improvement_review_replay(tmp_path / "improvement_review")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _review(tmp_path)
    path = tmp_path / "improvement_review" / "001_improvement_review_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "improvement_review_recorded"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_improvement_review_replay(tmp_path / "improvement_review")


def test_replay_reconstruction_detects_chain_mismatch(tmp_path) -> None:
    _review(tmp_path)
    path = tmp_path / "improvement_review" / "001_improvement_review_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["canonical_chain_id"] = "CHAIN-OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        reconstruct_improvement_review_replay(tmp_path / "improvement_review")


def test_no_approval_rejection_implementation_or_process_surface_imports() -> None:
    import aigol.runtime.improvement_review_runtime as improvement_review_runtime

    source = inspect.getsource(improvement_review_runtime)

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
