"""Tests for IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_RUNTIME_V1."""

from __future__ import annotations

import importlib.util
import inspect
import json
from pathlib import Path

import pytest

from aigol.runtime.execution_request_runtime import CREATED_STATUS, EXECUTION_REQUEST_ARTIFACT_V1
from aigol.runtime.implementation_plan_to_execution_request_runtime import (
    IMPLEMENTATION_PLAN_EXECUTION_REQUEST_CREATED,
    IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINK_ARTIFACT_V1,
    IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINKED,
    create_implementation_plan_execution_request,
    reconstruct_implementation_plan_execution_request_replay,
)
from aigol.runtime.improvement_approval_runtime import REJECTED
from aigol.runtime.improvement_implementation_runtime import (
    IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


_HELPERS_PATH = Path(__file__).with_name("test_improvement_implementation_runtime_v1.py")
_HELPERS_SPEC = importlib.util.spec_from_file_location("improvement_implementation_runtime_v1_helpers", _HELPERS_PATH)
assert _HELPERS_SPEC is not None
_HELPERS = importlib.util.module_from_spec(_HELPERS_SPEC)
assert _HELPERS_SPEC.loader is not None
_HELPERS_SPEC.loader.exec_module(_HELPERS)

CREATED_AT = _HELPERS.CREATED_AT
CANONICAL_CHAIN_ID = _HELPERS.CANONICAL_CHAIN_ID
_MISSING = object()


def _approval_and_plan(tmp_path, **approval_overrides) -> tuple[dict, dict]:
    approval = _HELPERS._approval_artifact(tmp_path, **approval_overrides)
    plan = _HELPERS._plan(tmp_path, improvement_approval_artifact=approval)[
        "improvement_implementation_plan_artifact"
    ]
    return approval, plan


def _payload() -> dict:
    return {
        "approved_action": "CREATE_GOVERNED_IMPLEMENTATION_REQUEST",
        "source": "implementation plan",
        "plan_scope": "bounded future implementation request creation only",
        "constraints": [
            "no dispatch",
            "no invocation",
            "no execution",
            "no governance mutation",
            "no replay mutation",
        ],
    }


def _bridge(tmp_path, **overrides) -> dict:
    approval = overrides.pop("improvement_approval_artifact", _MISSING)
    plan = overrides.pop("implementation_plan_artifact", _MISSING)
    if approval is _MISSING or plan is _MISSING:
        approval, plan = _approval_and_plan(tmp_path)
    args = {
        "bridge_id": "IMPLEMENTATION-PLAN-EXECUTION-REQUEST-LINK-000001",
        "execution_request_id": "EXECUTION-REQUEST-FROM-IMPLEMENTATION-PLAN-000001",
        "implementation_plan_artifact": plan,
        "improvement_approval_artifact": approval,
        "canonical_chain_id": CANONICAL_CHAIN_ID,
        "human_authorization_reference": "HUMAN-EXECUTION-REQUEST-AUTHORIZATION-000001",
        "requested_by": "AIGOL",
        "created_at": CREATED_AT,
        "request_type": "CAPABILITY_EXECUTION_REQUEST",
        "request_payload": _payload(),
        "replay_reference": "REPLAY-IMPLEMENTATION-PLAN-EXECUTION-REQUEST-000001",
        "replay_dir": tmp_path / "implementation_plan_execution_request",
    }
    args.update(overrides)
    return create_implementation_plan_execution_request(**args)


def test_bridge_creates_execution_request_and_link_from_approved_plan(tmp_path) -> None:
    approval, plan = _approval_and_plan(tmp_path)
    capture = _bridge(tmp_path, improvement_approval_artifact=approval, implementation_plan_artifact=plan)
    request = capture["execution_request_artifact"]
    link = capture["implementation_plan_execution_request_link_artifact"]
    reconstructed = reconstruct_implementation_plan_execution_request_replay(
        tmp_path / "implementation_plan_execution_request"
    )

    assert request["artifact_type"] == EXECUTION_REQUEST_ARTIFACT_V1
    assert request["execution_request_source_type"] == IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1
    assert request["implementation_plan_reference"] == plan["implementation_plan_id"]
    assert request["implementation_plan_hash"] == plan["artifact_hash"]
    assert request["improvement_approval_reference"] == approval["improvement_approval_id"]
    assert request["improvement_approval_hash"] == approval["artifact_hash"]
    assert request["canonical_chain_id"] == CANONICAL_CHAIN_ID
    assert request["human_authorization_reference"] == "HUMAN-EXECUTION-REQUEST-AUTHORIZATION-000001"
    assert request["status"] == CREATED_STATUS
    assert request["automatic_authorization"] is False
    assert request["worker_dispatched"] is False
    assert request["worker_invoked"] is False
    assert request["execution_performed"] is False
    assert link["artifact_type"] == IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINK_ARTIFACT_V1
    assert link["execution_request_created"] is True
    assert link["execution_request_reference"] == request["execution_request_id"]
    assert link["execution_request_hash"] == request["artifact_hash"]
    assert link["automatic_execution_request"] is False
    assert reconstructed["execution_request_id"] == request["execution_request_id"]
    assert reconstructed["execution_request_created"] is True
    assert reconstructed["worker_dispatched"] is False
    assert reconstructed["execution_performed"] is False


def test_bridge_persists_replay_events(tmp_path) -> None:
    _bridge(tmp_path)

    created = tmp_path / "implementation_plan_execution_request" / (
        "000_implementation_plan_execution_request_created.json"
    )
    linked = tmp_path / "implementation_plan_execution_request" / (
        "001_implementation_plan_execution_request_linked.json"
    )
    assert created.exists()
    assert linked.exists()
    assert json.loads(created.read_text(encoding="utf-8"))["event_type"] == (
        IMPLEMENTATION_PLAN_EXECUTION_REQUEST_CREATED
    )
    assert json.loads(linked.read_text(encoding="utf-8"))["event_type"] == IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINKED


def test_missing_plan_fails_closed(tmp_path) -> None:
    approval, _plan = _approval_and_plan(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="plan is required"):
        _bridge(tmp_path, improvement_approval_artifact=approval, implementation_plan_artifact=None)


def test_invalid_plan_fails_closed(tmp_path) -> None:
    approval, plan = _approval_and_plan(tmp_path)
    plan["plan_status"] = "FAILED_CLOSED"
    plan.pop("artifact_hash")
    plan["artifact_hash"] = replay_hash(plan)

    with pytest.raises(FailClosedRuntimeError, match="invalid implementation plan"):
        _bridge(tmp_path, improvement_approval_artifact=approval, implementation_plan_artifact=plan)


def test_rejected_approval_fails_closed_before_plan_creation(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="approval must be APPROVED"):
        _approval_and_plan(tmp_path, decision=REJECTED, decision_reason="Rejected bridge creation.")


def test_rejected_approval_fails_closed_at_bridge(tmp_path) -> None:
    approval, plan = _approval_and_plan(tmp_path)
    approval["decision"] = REJECTED
    approval["approval_status"] = REJECTED
    approval["implementation_authorized"] = False
    approval.pop("artifact_hash")
    approval["artifact_hash"] = replay_hash(approval)

    with pytest.raises(FailClosedRuntimeError, match="approval must be APPROVED"):
        _bridge(tmp_path, improvement_approval_artifact=approval, implementation_plan_artifact=plan)


def test_chain_mismatch_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        _bridge(tmp_path, canonical_chain_id="CHAIN-OTHER")


def test_approval_reference_mismatch_fails_closed(tmp_path) -> None:
    approval, plan = _approval_and_plan(tmp_path)
    approval["improvement_approval_id"] = "OTHER-APPROVAL"
    approval.pop("artifact_hash")
    approval["artifact_hash"] = replay_hash(approval)

    with pytest.raises(FailClosedRuntimeError, match="approval reference mismatch"):
        _bridge(tmp_path, improvement_approval_artifact=approval, implementation_plan_artifact=plan)


def test_duplicate_bridge_fails_closed(tmp_path) -> None:
    _bridge(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _bridge(tmp_path)


def test_missing_explicit_human_authorization_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="human_authorization_reference is required"):
        _bridge(tmp_path, human_authorization_reference="")


def test_upstream_plan_authorization_is_not_enough_for_execution_request(tmp_path) -> None:
    approval, plan = _approval_and_plan(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="explicit execution authorization is required"):
        _bridge(
            tmp_path,
            improvement_approval_artifact=approval,
            implementation_plan_artifact=plan,
            human_authorization_reference=plan["human_authorization_reference"],
        )


def test_automatic_execution_request_marker_fails_closed(tmp_path) -> None:
    approval, plan = _approval_and_plan(tmp_path)
    plan["execution_request_created"] = True
    plan.pop("artifact_hash")
    plan["artifact_hash"] = replay_hash(plan)

    with pytest.raises(FailClosedRuntimeError, match="automatic execution request creation detected"):
        _bridge(tmp_path, improvement_approval_artifact=approval, implementation_plan_artifact=plan)


def test_authority_bearing_payload_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="authority-bearing request payload"):
        _bridge(tmp_path, request_payload={"worker_command": "run"})


def test_authority_bearing_payload_text_fails_closed(tmp_path) -> None:
    payload = _payload()
    payload["note"] = "Dispatch worker now."

    with pytest.raises(FailClosedRuntimeError, match="authority-bearing request payload"):
        _bridge(tmp_path, request_payload=payload)


def test_replay_reconstruction_detects_request_corruption(tmp_path) -> None:
    _bridge(tmp_path)
    path = tmp_path / "implementation_plan_execution_request" / (
        "000_implementation_plan_execution_request_created.json"
    )
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_dispatched"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_implementation_plan_execution_request_replay(
            tmp_path / "implementation_plan_execution_request"
        )


def test_replay_reconstruction_detects_ordering_corruption(tmp_path) -> None:
    _bridge(tmp_path)
    path = tmp_path / "implementation_plan_execution_request" / (
        "001_implementation_plan_execution_request_linked.json"
    )
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["replay_step"] = "implementation_plan_execution_request_created"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_implementation_plan_execution_request_replay(
            tmp_path / "implementation_plan_execution_request"
        )


def test_replay_reconstruction_detects_chain_mismatch(tmp_path) -> None:
    _bridge(tmp_path)
    path = tmp_path / "implementation_plan_execution_request" / (
        "001_implementation_plan_execution_request_linked.json"
    )
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["canonical_chain_id"] = "CHAIN-OTHER"
    wrapper["artifact"].pop("artifact_hash")
    wrapper["artifact"]["artifact_hash"] = replay_hash(wrapper["artifact"])
    wrapper.pop("replay_hash")
    wrapper["replay_hash"] = replay_hash(wrapper)
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="chain mismatch"):
        reconstruct_implementation_plan_execution_request_replay(
            tmp_path / "implementation_plan_execution_request"
        )


def test_no_dispatch_execution_or_process_surface_imports() -> None:
    import aigol.runtime.implementation_plan_to_execution_request_runtime as bridge_runtime

    source = inspect.getsource(bridge_runtime)

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
