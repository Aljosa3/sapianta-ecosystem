"""Tests for IMPROVEMENT_IMPLEMENTATION_RUNTIME_V1."""

from __future__ import annotations

import importlib.util
import inspect
import json
from pathlib import Path

import pytest

from aigol.runtime.improvement_approval_runtime import REJECTED
from aigol.runtime.improvement_implementation_runtime import (
    IMPLEMENTATION_PLAN_CREATED,
    IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1,
    IMPROVEMENT_IMPLEMENTATION_PLAN_CREATED,
    IMPROVEMENT_IMPLEMENTATION_PLAN_RETURNED,
    create_improvement_implementation_plan,
    reconstruct_improvement_implementation_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


_HELPERS_PATH = Path(__file__).with_name("test_improvement_approval_runtime_v1.py")
_HELPERS_SPEC = importlib.util.spec_from_file_location("improvement_approval_runtime_v1_helpers", _HELPERS_PATH)
assert _HELPERS_SPEC is not None
_HELPERS = importlib.util.module_from_spec(_HELPERS_SPEC)
assert _HELPERS_SPEC.loader is not None
_HELPERS_SPEC.loader.exec_module(_HELPERS)

CREATED_AT = _HELPERS.CREATED_AT
CANONICAL_CHAIN_ID = _HELPERS.CANONICAL_CHAIN_ID


def _approval_artifact(tmp_path, **overrides) -> dict:
    return _HELPERS._approval(tmp_path, **overrides)["improvement_approval_artifact"]


def _scope() -> dict:
    return {
        "future_execution_path": "Plan may later feed a governed execution request boundary.",
        "future_workers": ["bounded implementation worker", "replay inspector worker"],
        "excluded_actions": ["code mutation", "execution request creation", "worker dispatch"],
    }


def _constraints() -> dict:
    return {
        "execution_request_boundary": "future separate runtime",
        "implementation_boundary": "not performed by implementation plan",
        "code_mutation_boundary": "not allowed in implementation plan",
        "governance_mutation_boundary": "not allowed in implementation plan",
        "replay_mutation_boundary": "not allowed in implementation plan",
    }


def _plan(tmp_path, **overrides) -> dict:
    approval = overrides.pop("improvement_approval_artifact", None)
    if approval is None:
        approval = _approval_artifact(tmp_path)
    args = {
        "implementation_plan_id": "IMPROVEMENT-IMPLEMENTATION-PLAN-000001",
        "improvement_approval_artifact": approval,
        "canonical_chain_id": CANONICAL_CHAIN_ID,
        "plan_source": "AIGOL_DETERMINISTIC_PLANNING",
        "plan_text": "Describe future implementation steps and validation without executing them.",
        "plan_scope": _scope(),
        "plan_constraints": _constraints(),
        "planned_artifact_targets": [
            "aigol/runtime/future_boundary.py",
            "tests/test_future_boundary.py",
            "governance/FUTURE_BOUNDARY_EVIDENCE.json",
        ],
        "planned_validation": [
            "python -m pytest tests/test_future_boundary.py",
            "git diff --check",
        ],
        "created_by": "AIGOL",
        "created_at": CREATED_AT,
        "replay_reference": "REPLAY-IMPROVEMENT-IMPLEMENTATION-PLAN-000001",
        "replay_dir": tmp_path / "improvement_implementation_plan",
    }
    args.update(overrides)
    return create_improvement_implementation_plan(**args)


def test_improvement_implementation_runtime_creates_replay_visible_plan(tmp_path) -> None:
    approval = _approval_artifact(tmp_path)
    capture = _plan(tmp_path, improvement_approval_artifact=approval)
    plan = capture["improvement_implementation_plan_artifact"]
    returned = capture["improvement_implementation_plan_replay"]
    reconstructed = reconstruct_improvement_implementation_replay(tmp_path / "improvement_implementation_plan")

    assert plan["artifact_type"] == IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1
    assert plan["plan_status"] == IMPLEMENTATION_PLAN_CREATED
    assert plan["canonical_chain_id"] == CANONICAL_CHAIN_ID
    assert plan["improvement_approval_reference"] == approval["improvement_approval_id"]
    assert plan["improvement_approval_hash"] == approval["artifact_hash"]
    assert plan["implementation_authorized"] is True
    assert plan["execution_request_created"] is False
    assert plan["execution_request_reference"] is None
    assert plan["implementation_performed"] is False
    assert plan["code_mutated"] is False
    assert plan["worker_dispatched"] is False
    assert plan["worker_invoked"] is False
    assert returned["event_type"] == IMPROVEMENT_IMPLEMENTATION_PLAN_RETURNED
    assert reconstructed["plan_status"] == IMPLEMENTATION_PLAN_CREATED
    assert reconstructed["execution_request_created"] is False
    assert reconstructed["implementation_performed"] is False


def test_improvement_implementation_runtime_persists_replay_events(tmp_path) -> None:
    _plan(tmp_path)

    created = tmp_path / "improvement_implementation_plan" / "000_improvement_implementation_plan_created.json"
    returned = tmp_path / "improvement_implementation_plan" / "001_improvement_implementation_plan_returned.json"
    assert created.exists()
    assert returned.exists()
    assert json.loads(created.read_text(encoding="utf-8"))["event_type"] == IMPROVEMENT_IMPLEMENTATION_PLAN_CREATED
    assert json.loads(returned.read_text(encoding="utf-8"))["event_type"] == IMPROVEMENT_IMPLEMENTATION_PLAN_RETURNED


def test_rejected_approval_fails_closed(tmp_path) -> None:
    approval = _approval_artifact(tmp_path, decision=REJECTED, decision_reason="Rejected for implementation planning.")

    with pytest.raises(FailClosedRuntimeError, match="approval must be APPROVED"):
        _plan(tmp_path, improvement_approval_artifact=approval)


def test_invalid_approval_fails_closed(tmp_path) -> None:
    approval = _approval_artifact(tmp_path)
    approval["approval_status"] = "PENDING"
    approval.pop("artifact_hash")
    approval["artifact_hash"] = replay_hash(approval)

    with pytest.raises(FailClosedRuntimeError, match="approval must be APPROVED"):
        _plan(tmp_path, improvement_approval_artifact=approval)


def test_chain_mismatch_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        _plan(tmp_path, canonical_chain_id="CHAIN-OTHER")


def test_duplicate_implementation_plan_fails_closed(tmp_path) -> None:
    _plan(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _plan(tmp_path)


def test_corrupt_approval_references_fail_closed(tmp_path) -> None:
    approval = _approval_artifact(tmp_path)
    approval["decision_reason_hash"] = "sha256:corrupt-reason"
    approval.pop("artifact_hash")
    approval["artifact_hash"] = replay_hash(approval)

    with pytest.raises(FailClosedRuntimeError, match="corrupt references"):
        _plan(tmp_path, improvement_approval_artifact=approval)


def test_invalid_plan_source_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="invalid plan source"):
        _plan(tmp_path, plan_source="WORKER_AUTHORITY")


def test_authority_bearing_plan_scope_fails_closed(tmp_path) -> None:
    scope = _scope()
    scope["execution_request_created"] = True

    with pytest.raises(FailClosedRuntimeError, match="authority-bearing plan content"):
        _plan(tmp_path, plan_scope=scope)


def test_authority_bearing_plan_constraints_fails_closed(tmp_path) -> None:
    constraints = _constraints()
    constraints["code_mutated"] = True

    with pytest.raises(FailClosedRuntimeError, match="authority-bearing plan content"):
        _plan(tmp_path, plan_constraints=constraints)


def test_authority_bearing_plan_text_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="authority-bearing plan text"):
        _plan(tmp_path, plan_text="Write code now and create execution request now.")


def test_replay_reconstruction_detects_plan_corruption(tmp_path) -> None:
    _plan(tmp_path)
    path = tmp_path / "improvement_implementation_plan" / "000_improvement_implementation_plan_created.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["code_mutated"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_improvement_implementation_replay(tmp_path / "improvement_implementation_plan")


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _plan(tmp_path)
    path = tmp_path / "improvement_implementation_plan" / "001_improvement_implementation_plan_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "improvement_implementation_plan_created"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_improvement_implementation_replay(tmp_path / "improvement_implementation_plan")


def test_replay_reconstruction_detects_chain_mismatch(tmp_path) -> None:
    _plan(tmp_path)
    path = tmp_path / "improvement_implementation_plan" / "001_improvement_implementation_plan_returned.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["canonical_chain_id"] = "CHAIN-OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        reconstruct_improvement_implementation_replay(tmp_path / "improvement_implementation_plan")


def test_no_code_mutation_execution_request_or_process_surface_imports() -> None:
    import aigol.runtime.improvement_implementation_runtime as improvement_implementation_runtime

    source = inspect.getsource(improvement_implementation_runtime)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "import requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "openai" not in source.lower()
    assert "anthropic" not in source.lower()
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
