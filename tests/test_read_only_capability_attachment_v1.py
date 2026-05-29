"""Tests for FIRST_READ_ONLY_CAPABILITY_ATTACHMENT_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.providers.metadata_inspection_provider import MetadataInspectionProvider
from aigol.runtime.read_only_capability_attachment import (
    AUTHORIZED,
    EXECUTED,
    FAILED,
    READ_ONLY_RUNTIME_INSPECTION,
    REQUESTED,
    TERMINATED,
    VALIDATED,
    authorize_read_only_capability,
    create_read_only_capability_request,
    execute_read_only_capability,
    reconstruct_read_only_capability_replay,
    validate_read_only_capability_request,
)


CREATED_AT = "2026-05-29T01:00:00+00:00"


def _provider() -> MetadataInspectionProvider:
    return MetadataInspectionProvider(timestamp_provider=lambda: CREATED_AT)


def _run(tmp_path, **overrides) -> dict:
    args = {
        "execution_id": "READONLY-EXECUTION-000001",
        "request_id": "READONLY-REQUEST-000001",
        "created_at": CREATED_AT,
        "replay_dir": tmp_path,
        "provider": _provider(),
    }
    args.update(overrides)
    return execute_read_only_capability(**args)


def test_read_only_capability_executes_through_bounded_lifecycle(tmp_path) -> None:
    capture = _run(tmp_path)
    replay = reconstruct_read_only_capability_replay(tmp_path)

    assert capture["termination"]["state"] == TERMINATED
    assert capture["execution"]["capability_id"] == READ_ONLY_RUNTIME_INSPECTION
    assert capture["execution"]["read_only"] is True
    assert capture["execution"]["write_performed"] is False
    assert capture["execution"]["network_performed"] is False
    assert replay["lifecycle_transitions"] == [REQUESTED, VALIDATED, AUTHORIZED, EXECUTED, TERMINATED]
    assert replay["final_status"] == TERMINATED
    assert replay["bounded_capability"] is True


def test_execution_outcome_contains_required_evidence(tmp_path) -> None:
    capture = _run(tmp_path)
    execution = capture["execution"]

    assert execution["execution_id"] == "READONLY-EXECUTION-000001"
    assert execution["capability_id"] == READ_ONLY_RUNTIME_INSPECTION
    assert execution["authorization_hash"] == capture["authorization"]["artifact_hash"]
    assert execution["execution_evidence"]["operation"] == "inspect_runtime"
    assert execution["execution_evidence_hash"] == execution["execution_evidence"]["evidence_hash"]
    assert execution["final_status"] == EXECUTED


def test_replay_artifacts_are_append_only(tmp_path) -> None:
    _run(tmp_path)

    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _run(tmp_path)


def test_runtime_artifacts_are_deterministic(tmp_path) -> None:
    first = _run(tmp_path / "first")
    second = _run(tmp_path / "second")

    assert first == second


def test_unauthorized_capability_fails_closed(tmp_path) -> None:
    capture = _run(tmp_path, authorize=False)
    replay = reconstruct_read_only_capability_replay(tmp_path)

    assert capture["termination"]["state"] == FAILED
    assert "authorization missing" in capture["termination"]["failure_reason"]
    assert replay["lifecycle_transitions"] == [REQUESTED, VALIDATED, FAILED, FAILED, FAILED]


def test_invalid_capability_classification_fails_closed(tmp_path) -> None:
    capture = _run(tmp_path, capability_id="FILESYSTEM_WRITE")

    assert capture["termination"]["state"] == FAILED
    assert "invalid capability classification" in capture["termination"]["failure_reason"]


def test_boundary_violation_fails_closed() -> None:
    request = create_read_only_capability_request(
        execution_id="READONLY-EXECUTION-000001",
        request_id="READONLY-REQUEST-000001",
        capability_id=READ_ONLY_RUNTIME_INSPECTION,
        created_at=CREATED_AT,
    )
    request["write"] = True
    request_without_hash = dict(request)
    request_without_hash.pop("artifact_hash")
    from aigol.runtime.transport.serialization import replay_hash

    request["artifact_hash"] = replay_hash(request_without_hash)

    with pytest.raises(FailClosedRuntimeError, match="boundary violation"):
        validate_read_only_capability_request(request)


def test_authorization_requires_validated_state() -> None:
    request = create_read_only_capability_request(
        execution_id="READONLY-EXECUTION-000001",
        request_id="READONLY-REQUEST-000001",
        capability_id=READ_ONLY_RUNTIME_INSPECTION,
        created_at=CREATED_AT,
    )

    with pytest.raises(FailClosedRuntimeError, match="VALIDATED"):
        authorize_read_only_capability(request)


def test_replay_discontinuity_detected(tmp_path) -> None:
    _run(tmp_path)
    artifact_path = tmp_path / "003_execution.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["artifact"]["write_performed"] = True
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_read_only_capability_replay(tmp_path)


def test_replay_ordering_corruption_detected(tmp_path) -> None:
    _run(tmp_path)
    artifact_path = tmp_path / "002_authorization.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["replay_step"] = "execution"
    artifact_path.write_text(json.dumps(artifact, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="ordering mismatch"):
        reconstruct_read_only_capability_replay(tmp_path)


def test_validation_preserves_constitutional_guarantees() -> None:
    request = create_read_only_capability_request(
        execution_id="READONLY-EXECUTION-000001",
        request_id="READONLY-REQUEST-000001",
        capability_id=READ_ONLY_RUNTIME_INSPECTION,
        created_at=CREATED_AT,
    )
    validation = validate_read_only_capability_request(request)

    assert validation["state"] == VALIDATED
    assert validation["capability_classification"] == "READ_ONLY"
    assert validation["replay_centrality_preserved"] is True
    assert validation["constitutional_freeze_preserved"] is True
    assert validation["mutation_detected"] is False


def test_no_mutating_runtime_imports() -> None:
    import aigol.runtime.read_only_capability_attachment as attachment

    source = inspect.getsource(attachment)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
