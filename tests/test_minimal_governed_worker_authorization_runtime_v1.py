from __future__ import annotations

import json

import pytest

from aigol.authorization.authorization_record import validate_authorization_record
from aigol.authorization.authorization_runtime import (
    FAILED_CLOSED,
    reconstruct_authorization_replay,
    authorize_worker_request,
)
from aigol.runtime.models import FailClosedRuntimeError


TIMESTAMP = "2026-05-31T12:00:00Z"


def _proposal(**overrides):
    proposal = {
        "proposal_id": "PROPOSAL-000001",
        "proposal_lineage": {
            "provider_id": "openai",
            "proposal_hash": "sha256:proposal",
        },
        "governance_review": "GOVERNANCE_REVIEW-000001",
    }
    proposal.update(overrides)
    return proposal


def _worker(**overrides):
    worker = {
        "worker_id": "EXTERNAL_RUNTIME_INSPECTION_WORKER",
        "domain": "infrastructure",
        "capability": "read_only_runtime_inspection",
    }
    worker.update(overrides)
    return worker


def _authorize(tmp_path, **overrides):
    args = {
        "authorization_id": "AUTHORIZATION-000001",
        "proposal": _proposal(),
        "worker_target": _worker(),
        "authorization_scope": "READ_ONLY_RUNTIME_INSPECTION",
        "authorization_timestamp": TIMESTAMP,
        "replay_dir": tmp_path,
    }
    args.update(overrides)
    return authorize_worker_request(**args)


def test_valid_authorization_record_created_and_replay_visible(tmp_path):
    capture = _authorize(tmp_path)
    record = capture["authorization_record"]
    replay = reconstruct_authorization_replay(tmp_path)

    assert record["authorization_id"] == "AUTHORIZATION-000001"
    assert record["proposal_id"] == "PROPOSAL-000001"
    assert record["worker_id"] == "EXTERNAL_RUNTIME_INSPECTION_WORKER"
    assert record["authorization_scope"] == "READ_ONLY_RUNTIME_INSPECTION"
    assert record["authorization_status"] == "AUTHORIZED"
    assert record["replay_visible"] is True
    assert validate_authorization_record(record) == record

    assert replay["who_proposed"] == "PROPOSAL-000001"
    assert replay["who_reviewed"] == "GOVERNANCE_REVIEW-000001"
    assert replay["who_authorized"] == "governed_authorization_runtime"
    assert replay["worker_authorized"] == "EXTERNAL_RUNTIME_INSPECTION_WORKER"
    assert replay["scope_authorized"] == "READ_ONLY_RUNTIME_INSPECTION"
    assert replay["authorization_timestamp"] == TIMESTAMP


def test_authorization_runtime_does_not_execute_dispatch_or_invoke_worker(tmp_path):
    capture = _authorize(tmp_path)

    for artifact_name in ("authorization_record", "authorization_created", "authorization_returned"):
        artifact = capture[artifact_name]
        assert artifact["worker_invoked"] is False
        assert artifact["dispatch_performed"] is False
        assert artifact["execution_performed"] is False


def test_missing_proposal_fails_closed(tmp_path):
    capture = _authorize(tmp_path, proposal={})

    assert capture["authorization_created"]["event_type"] == FAILED_CLOSED
    assert "proposal_id is required" in capture["authorization_created"]["failure_reason"]
    assert capture["authorization_created"]["worker_invoked"] is False


def test_unknown_worker_fails_closed(tmp_path):
    capture = _authorize(tmp_path, worker_target={})

    assert capture["authorization_created"]["event_type"] == FAILED_CLOSED
    assert "worker_id is required" in capture["authorization_created"]["failure_reason"]


def test_missing_scope_fails_closed(tmp_path):
    capture = _authorize(tmp_path, authorization_scope="")

    assert capture["authorization_created"]["event_type"] == FAILED_CLOSED
    assert "authorization_scope is required" in capture["authorization_created"]["failure_reason"]


def test_invalid_evidence_fails_closed(tmp_path):
    capture = _authorize(tmp_path, proposal=_proposal(provider_authority=True))

    assert capture["authorization_created"]["event_type"] == FAILED_CLOSED
    assert "forbidden authority field" in capture["authorization_created"]["failure_reason"]


def test_unbounded_scope_fails_closed(tmp_path):
    capture = _authorize(tmp_path, authorization_scope="all")

    assert capture["authorization_created"]["event_type"] == FAILED_CLOSED
    assert "authorization scope must be bounded" in capture["authorization_created"]["failure_reason"]


def test_malformed_authorization_record_fails_closed():
    record = {
        "record_type": "GOVERNED_WORKER_AUTHORIZATION_RECORD_V1",
        "authorization_id": "AUTHORIZATION-000001",
        "proposal_id": "PROPOSAL-000001",
        "worker_id": "EXTERNAL_RUNTIME_INSPECTION_WORKER",
        "authorization_scope": "READ_ONLY_RUNTIME_INSPECTION",
        "authorization_timestamp": TIMESTAMP,
        "authorization_status": "AUTHORIZED",
        "replay_visible": True,
        "governed_authorization": True,
        "provider_can_authorize": False,
        "proposal_can_authorize": False,
        "cognition_can_authorize": False,
        "replay_can_authorize": False,
        "worker_can_self_authorize": False,
        "worker_invoked": False,
        "dispatch_performed": False,
        "execution_performed": False,
        "authorization_hash": "sha256:bad",
    }

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        validate_authorization_record(record)


def test_replay_corruption_detection(tmp_path):
    _authorize(tmp_path)
    artifact_path = tmp_path / "000_authorization_created.json"
    wrapper = json.loads(artifact_path.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_id"] = "TAMPERED_WORKER"
    artifact_path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_authorization_replay(tmp_path)


def test_append_only_replay_violation_fails_closed(tmp_path):
    _authorize(tmp_path)
    second = _authorize(tmp_path)

    assert second["authorization_created"]["event_type"] == FAILED_CLOSED
    assert "append-only runtime artifact already exists" in second["authorization_created"]["failure_reason"]
