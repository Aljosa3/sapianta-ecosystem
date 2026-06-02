"""Tests for IMPROVEMENT_PROPOSAL_RUNTIME_V1."""

from __future__ import annotations

import importlib.util
import inspect
import json
from pathlib import Path

import pytest

from aigol.runtime.improvement_proposal_runtime import (
    IMPROVEMENT_PROPOSAL_ARTIFACT_V1,
    IMPROVEMENT_PROPOSAL_CREATED,
    IMPROVEMENT_PROPOSAL_RETURNED,
    IMPROVEMENT_PROPOSED,
    create_improvement_proposal,
    reconstruct_improvement_proposal_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


_HELPERS_PATH = Path(__file__).with_name("test_result_evaluation_runtime_v1.py")
_HELPERS_SPEC = importlib.util.spec_from_file_location("result_evaluation_runtime_v1_helpers", _HELPERS_PATH)
assert _HELPERS_SPEC is not None
_HELPERS = importlib.util.module_from_spec(_HELPERS_SPEC)
assert _HELPERS_SPEC.loader is not None
_HELPERS_SPEC.loader.exec_module(_HELPERS)

CREATED_AT = _HELPERS.CREATED_AT
CANONICAL_CHAIN_ID = _HELPERS.CANONICAL_CHAIN_ID


def _evaluation_artifact(tmp_path) -> dict:
    return _HELPERS._evaluation(tmp_path)["result_evaluation_artifact"]


def _scope() -> dict:
    return {
        "target_boundary": "RESULT_EVALUATION_RUNTIME_V1",
        "allowed_change": "Add bounded follow-up review notes.",
        "excluded_changes": ["approval", "implementation", "execution_request"],
    }


def _constraints() -> dict:
    return {
        "approval_required": True,
        "implementation_authorized": False,
        "execution_requested": False,
        "replay_mutation_allowed": False,
    }


def _proposal(tmp_path, **overrides) -> dict:
    evaluation = overrides.pop("evaluation_artifact", None)
    if evaluation is None:
        evaluation = _evaluation_artifact(tmp_path)
    args = {
        "improvement_proposal_id": "IMPROVEMENT-PROPOSAL-000001",
        "evaluation_artifact": evaluation,
        "canonical_chain_id": CANONICAL_CHAIN_ID,
        "proposal_source": "RESULT_EVALUATION",
        "proposal_text": "Add a bounded follow-up review note for the evaluated result.",
        "proposal_reason": "Evaluation recommended improvement based on replay-visible observations.",
        "proposal_scope": _scope(),
        "proposal_constraints": _constraints(),
        "created_by": "AIGOL",
        "created_at": CREATED_AT,
        "replay_reference": "REPLAY-IMPROVEMENT-PROPOSAL-000001",
        "replay_dir": tmp_path / "improvement_proposal",
    }
    args.update(overrides)
    return create_improvement_proposal(**args)


def test_improvement_proposal_runtime_creates_replay_visible_proposal(tmp_path) -> None:
    evaluation = _evaluation_artifact(tmp_path)
    capture = _proposal(tmp_path, evaluation_artifact=evaluation)
    proposal = capture["improvement_proposal_artifact"]
    returned = capture["improvement_proposal_replay"]
    reconstructed = reconstruct_improvement_proposal_replay(tmp_path / "improvement_proposal")

    assert proposal["artifact_type"] == IMPROVEMENT_PROPOSAL_ARTIFACT_V1
    assert proposal["proposal_status"] == IMPROVEMENT_PROPOSED
    assert proposal["canonical_chain_id"] == CANONICAL_CHAIN_ID
    assert proposal["evaluation_reference"] == evaluation["evaluation_id"]
    assert proposal["evaluation_hash"] == evaluation["artifact_hash"]
    assert proposal["result_reference"] == evaluation["result_reference"]
    assert proposal["worker_reference"] == evaluation["worker_reference"]
    assert proposal["approval_required"] is True
    assert proposal["approval_reference"] is None
    assert proposal["implementation_authorized"] is False
    assert proposal["implementation_reference"] is None
    assert proposal["proposal_approved"] is False
    assert proposal["review_performed"] is False
    assert proposal["execution_requested"] is False
    assert returned["event_type"] == IMPROVEMENT_PROPOSAL_RETURNED
    assert reconstructed["proposal_status"] == IMPROVEMENT_PROPOSED
    assert reconstructed["implementation_applied"] is False


def test_improvement_proposal_runtime_persists_replay_events(tmp_path) -> None:
    _proposal(tmp_path)

    created = tmp_path / "improvement_proposal" / "000_improvement_proposal_created.json"
    returned = tmp_path / "improvement_proposal" / "001_improvement_proposal_returned.json"
    assert created.exists()
    assert returned.exists()
    assert json.loads(created.read_text(encoding="utf-8"))["event_type"] == IMPROVEMENT_PROPOSAL_CREATED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == IMPROVEMENT_PROPOSAL_RETURNED


def test_invalid_evaluation_fails_closed(tmp_path) -> None:
    evaluation = _evaluation_artifact(tmp_path)
    evaluation["evaluation_status"] = "FAILED"
    evaluation.pop("artifact_hash")
    evaluation["artifact_hash"] = replay_hash(evaluation)

    with pytest.raises(FailClosedRuntimeError, match="invalid evaluation"):
        _proposal(tmp_path, evaluation_artifact=evaluation)


def test_evaluation_without_improvement_recommendation_fails_closed(tmp_path) -> None:
    evaluation = _evaluation_artifact(tmp_path)
    evaluation["improvement_recommended"] = False
    evaluation.pop("artifact_hash")
    evaluation["artifact_hash"] = replay_hash(evaluation)

    with pytest.raises(FailClosedRuntimeError, match="improvement was not recommended"):
        _proposal(tmp_path, evaluation_artifact=evaluation)


def test_chain_mismatch_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        _proposal(tmp_path, canonical_chain_id="CHAIN-OTHER")


def test_duplicate_proposal_fails_closed(tmp_path) -> None:
    _proposal(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _proposal(tmp_path)


def test_corrupt_evaluation_references_fail_closed(tmp_path) -> None:
    evaluation = _evaluation_artifact(tmp_path)
    evaluation["evaluation_observations_hash"] = "sha256:corrupt-observations"
    evaluation.pop("artifact_hash")
    evaluation["artifact_hash"] = replay_hash(evaluation)

    with pytest.raises(FailClosedRuntimeError, match="corrupt references"):
        _proposal(tmp_path, evaluation_artifact=evaluation)


def test_invalid_proposal_source_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="invalid proposal source"):
        _proposal(tmp_path, proposal_source="WORKER_AUTHORITY")


def test_authority_bearing_scope_fails_closed(tmp_path) -> None:
    scope = _scope()
    scope["execution_requested"] = True

    with pytest.raises(FailClosedRuntimeError, match="authority-bearing proposal content"):
        _proposal(tmp_path, proposal_scope=scope)


def test_authority_bearing_text_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="authority-bearing proposal text"):
        _proposal(tmp_path, proposal_text="Approve automatically and execute now.")


def test_replay_reconstruction_detects_proposal_corruption(tmp_path) -> None:
    _proposal(tmp_path)
    path = tmp_path / "improvement_proposal" / "000_improvement_proposal_created.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["proposal_approved"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_improvement_proposal_replay(tmp_path / "improvement_proposal")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _proposal(tmp_path)
    path = tmp_path / "improvement_proposal" / "001_improvement_proposal_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "improvement_proposal_created"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_improvement_proposal_replay(tmp_path / "improvement_proposal")


def test_replay_reconstruction_detects_chain_mismatch(tmp_path) -> None:
    _proposal(tmp_path)
    path = tmp_path / "improvement_proposal" / "001_improvement_proposal_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["canonical_chain_id"] = "CHAIN-OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        reconstruct_improvement_proposal_replay(tmp_path / "improvement_proposal")


def test_no_approval_review_implementation_or_process_surface_imports() -> None:
    import aigol.runtime.improvement_proposal_runtime as improvement_proposal_runtime

    source = inspect.getsource(improvement_proposal_runtime)

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
